import unittest
import urllib.parse
from unittest.mock import patch, MagicMock
from networksecurity.components.url_feature_extractor import (
    URLFeatureExtractor,
    validate_and_sanitize_url,
    SSRFSecurityViolation,
    InvalidURLFormatError,
    STAGE_URL_LEXICAL,
    STAGE_DNS_TLS,
    STAGE_HTML_CONTENT,
    STAGE_EXTERNAL_INTEL,
)
from networksecurity.utils.ml_utils.model.estimator import EXPECTED_FEATURES
from networksecurity.constants.training_pipeline import TARGET_COLUMN


class TestURLValidationAndSSRF(unittest.TestCase):
    """
    Unit tests for URL syntax validation and server-side request forgery (SSRF) protections.
    """

    def test_reject_empty_or_non_string(self):
        with self.assertRaises(InvalidURLFormatError):
            validate_and_sanitize_url("")
        with self.assertRaises(InvalidURLFormatError):
            validate_and_sanitize_url("   ")

    def test_reject_unsupported_schemes(self):
        unsupported = [
            "ftp://files.example.com",
            "file:///etc/passwd",
            "javascript:alert(1)",
            "data:text/html,<script>alert(1)</script>",
            "gopher://gopher.example.com",
        ]
        for url in unsupported:
            with self.assertRaises(InvalidURLFormatError, msg=f"Should reject {url}"):
                validate_and_sanitize_url(url, enforce_public_dns=False)

    def test_reject_embedded_credentials(self):
        with self.assertRaises(SSRFSecurityViolation):
            validate_and_sanitize_url("http://admin:secret@malicious.com", enforce_public_dns=False)
        with self.assertRaises(SSRFSecurityViolation):
            validate_and_sanitize_url("https://user:password@target.org", enforce_public_dns=False)

    def test_reject_localhost_domains(self):
        local_hosts = [
            "http://localhost/admin",
            "http://test.localhost:8080",
            "http://service.local",
            "http://internal.service.internal",
        ]
        for url in local_hosts:
            with self.assertRaises(SSRFSecurityViolation, msg=f"Should block {url}"):
                validate_and_sanitize_url(url, enforce_public_dns=False)

    def test_reject_loopback_and_private_ips(self):
        prohibited_ips = [
            "http://127.0.0.1",
            "http://127.0.0.2:8000",
            "http://10.0.0.1",
            "http://172.16.0.1",
            "http://192.168.1.1",
            "http://169.254.169.254/latest/meta-data", # AWS metadata
            "http://0.0.0.0:80",
        ]
        for url in prohibited_ips:
            with self.assertRaises(SSRFSecurityViolation, msg=f"Should block prohibited IP {url}"):
                validate_and_sanitize_url(url, enforce_public_dns=True)

    def test_valid_public_urls_accepted(self):
        meta = validate_and_sanitize_url("https://example.com/login?step=1", enforce_public_dns=False)
        self.assertEqual(meta["scheme"], "https")
        self.assertEqual(meta["hostname"], "example.com")
        self.assertEqual(meta["port"], 443)
        self.assertEqual(meta["path"], "/login")


class TestLexicalFeatureExtraction(unittest.TestCase):
    """
    Unit tests for all 10 URL lexical features and their exact domain boundaries.
    """

    def setUp(self):
        self.extractor = URLFeatureExtractor()

    def test_having_ip_address_detection(self):
        # IP as host -> -1 (phishing)
        res_ip = self.extractor.extract_features("http://192.0.2.1/login", allow_heuristics=True, fetch_network=False)
        self.assertEqual(res_ip["features"]["having_IP_Address"], -1)

        # Domain name -> 1 (legitimate)
        res_domain = self.extractor.extract_features("https://example.com", allow_heuristics=True, fetch_network=False)
        self.assertEqual(res_domain["features"]["having_IP_Address"], 1)

    def test_url_length_boundaries(self):
        # < 54 chars -> 1 (legitimate)
        short_url = "https://short.com"
        res_short = self.extractor.extract_features(short_url, allow_heuristics=True, fetch_network=False)
        self.assertEqual(res_short["features"]["URL_Length"], 1)

        # 54 to 75 chars -> 0 (suspicious)
        medium_url = "https://example.com/" + "a" * 35  # exactly 55 chars
        res_med = self.extractor.extract_features(medium_url, allow_heuristics=True, fetch_network=False)
        self.assertEqual(res_med["features"]["URL_Length"], 0)

        # > 75 chars -> -1 (phishing)
        long_url = "https://example.com/" + "a" * 60  # 80 chars
        res_long = self.extractor.extract_features(long_url, allow_heuristics=True, fetch_network=False)
        self.assertEqual(res_long["features"]["URL_Length"], -1)

    def test_shortening_service_detection(self):
        res_short = self.extractor.extract_features("http://bit.ly/3xYzA", allow_heuristics=True, fetch_network=False)
        self.assertEqual(res_short["features"]["Shortining_Service"], -1)

        res_direct = self.extractor.extract_features("https://github.com", allow_heuristics=True, fetch_network=False)
        self.assertEqual(res_direct["features"]["Shortining_Service"], 1)

    def test_having_at_symbol_detection(self):
        res_at = self.extractor.extract_features("https://example.com/login?ref=user@test", allow_heuristics=True, fetch_network=False)
        self.assertEqual(res_at["features"]["having_At_Symbol"], -1)

        res_clean = self.extractor.extract_features("https://example.com/login", allow_heuristics=True, fetch_network=False)
        self.assertEqual(res_clean["features"]["having_At_Symbol"], 1)

    def test_double_slash_redirecting(self):
        # '//' appears in the path after protocol
        res_slash = self.extractor.extract_features("http://example.com//redirect", allow_heuristics=True, fetch_network=False)
        self.assertEqual(res_slash["features"]["double_slash_redirecting"], -1)

        # Clean path
        res_clean = self.extractor.extract_features("http://example.com/path/to/resource", allow_heuristics=True, fetch_network=False)
        self.assertEqual(res_clean["features"]["double_slash_redirecting"], 1)

    def test_prefix_suffix_hyphen(self):
        res_hyphen = self.extractor.extract_features("https://secure-login-bank.com", allow_heuristics=True, fetch_network=False)
        self.assertEqual(res_hyphen["features"]["Prefix_Suffix"], -1)

        res_clean = self.extractor.extract_features("https://google.com", allow_heuristics=True, fetch_network=False)
        self.assertEqual(res_clean["features"]["Prefix_Suffix"], 1)

    def test_having_sub_domain(self):
        # 1 dot -> 1
        res_1 = self.extractor.extract_features("https://example.com", allow_heuristics=True, fetch_network=False)
        self.assertEqual(res_1["features"]["having_Sub_Domain"], 1)

        # 2 dots -> 0
        res_2 = self.extractor.extract_features("https://login.example.com", allow_heuristics=True, fetch_network=False)
        self.assertEqual(res_2["features"]["having_Sub_Domain"], 0)

        # > 2 dots -> -1
        res_3 = self.extractor.extract_features("https://a.b.login.example.com", allow_heuristics=True, fetch_network=False)
        self.assertEqual(res_3["features"]["having_Sub_Domain"], -1)

    def test_port_detection(self):
        # Standard port 80/443
        res_std = self.extractor.extract_features("https://example.com:443", allow_heuristics=True, fetch_network=False)
        self.assertEqual(res_std["features"]["port"], 1)

        # Non-standard port 21
        res_nonstd = self.extractor.extract_features("http://example.com:21", allow_heuristics=True, fetch_network=False)
        self.assertEqual(res_nonstd["features"]["port"], -1)

    def test_https_token_in_hostname(self):
        res_token = self.extractor.extract_features("http://https-secure-portal.com", allow_heuristics=True, fetch_network=False)
        self.assertEqual(res_token["features"]["HTTPS_token"], -1)

        res_clean = self.extractor.extract_features("https://normal-domain.com", allow_heuristics=True, fetch_network=False)
        self.assertEqual(res_clean["features"]["HTTPS_token"], 1)


class TestHTMLFeatureExtraction(unittest.TestCase):
    """
    Unit tests for DOM and behavioral HTML feature extraction.
    """

    def setUp(self):
        self.extractor = URLFeatureExtractor()

    def test_html_parsing_identifies_phishing_signatures(self):
        phish_html = """
        <!DOCTYPE html>
        <html>
        <head>
          <link rel="icon" href="http://foreign-domain.com/evil.ico" />
        </head>
        <body>
          <form action="mailto:stealer@hack.com"></form>
          <a href="#">Dummy 1</a>
          <a href="javascript:void(0)">Dummy 2</a>
          <a href="http://other.com/phish">Dummy 3</a>
          <script>
            window.status = "Trusted Bank";
            document.oncontextmenu = function() { return false; };
            var p = prompt("Enter Password");
          </script>
          <iframe frameborder="0" src="http://secret.com"></iframe>
        </body>
        </html>
        """
        res = self.extractor.extract_features(
            "http://example.com/login",
            allow_heuristics=True,
            fetch_network=False,
            mock_html=phish_html,
            mock_dns=True,
        )
        feats = res["features"]
        self.assertEqual(feats["Favicon"], -1)
        self.assertEqual(feats["Submitting_to_email"], -1)
        self.assertEqual(feats["on_mouseover"], -1)
        self.assertEqual(feats["RightClick"], -1)
        self.assertEqual(feats["popUpWidnow"], -1)
        self.assertEqual(feats["Iframe"], -1)
        self.assertEqual(feats["URL_of_Anchor"], -1)

    def test_html_parsing_identifies_legitimate_signatures(self):
        clean_html = """
        <!DOCTYPE html>
        <html>
        <head>
          <link rel="icon" href="/favicon.ico" />
        </head>
        <body>
          <form action="/auth/login" method="POST"></form>
          <a href="/about">About Us</a>
          <a href="/contact">Contact</a>
          <a href="/privacy">Privacy</a>
          <img src="/logo.png" />
        </body>
        </html>
        """
        res = self.extractor.extract_features(
            "https://example.com",
            allow_heuristics=True,
            fetch_network=False,
            mock_html=clean_html,
            mock_dns=True,
        )
        feats = res["features"]
        self.assertEqual(feats["Favicon"], 1)
        self.assertEqual(feats["SFH"], 1)
        self.assertEqual(feats["Submitting_to_email"], 1)
        self.assertEqual(feats["on_mouseover"], 1)
        self.assertEqual(feats["RightClick"], 1)
        self.assertEqual(feats["popUpWidnow"], 1)
        self.assertEqual(feats["Iframe"], 1)
        self.assertEqual(feats["URL_of_Anchor"], 1)


class TestFeatureVectorIntegrity(unittest.TestCase):
    """
    Unit tests ensuring exact schema conformity, feature ordering, and target exclusion.
    """

    def setUp(self):
        self.extractor = URLFeatureExtractor()

    def test_exact_feature_ordering_and_count(self):
        res = self.extractor.extract_features("https://example.com", allow_heuristics=True, fetch_network=False)
        self.assertEqual(res["feature_coverage"], "heuristic")
        self.assertEqual(len(res["features"]), 30)
        self.assertEqual(list(res["features"].keys()), EXPECTED_FEATURES)

    def test_target_column_strictly_excluded(self):
        res = self.extractor.extract_features("https://example.com", allow_heuristics=True, fetch_network=False)
        self.assertNotIn(TARGET_COLUMN, res["features"])
        self.assertNotIn("Result", res["features"])

    def test_allowed_value_domains(self):
        res = self.extractor.extract_features("https://example.com", allow_heuristics=True, fetch_network=False)
        feats = res["features"]
        for col in EXPECTED_FEATURES:
            val = feats[col]
            if col == "Redirect":
                self.assertIn(val, (0, 1), msg=f"{col} must be in [0, 1]")
            else:
                self.assertIn(val, (-1, 0, 1), msg=f"{col} must be in [-1, 0, 1]")

    def test_unsupported_features_when_heuristics_disabled(self):
        res = self.extractor.extract_features("https://example.com", allow_heuristics=False, fetch_network=False)
        self.assertEqual(res["feature_coverage"], "incomplete")
        self.assertTrue(len(res["unsupported_features"]) > 0)
        self.assertIn("web_traffic", res["unsupported_features"])
        self.assertIn("Page_Rank", res["unsupported_features"])

    def test_default_heuristics_is_false_in_extractor(self):
        # Default extract_features call without allow_heuristics should default to False (strict mode)
        res = self.extractor.extract_features("https://example.com", fetch_network=False)
        self.assertEqual(res["feature_coverage"], "incomplete")
        self.assertTrue(len(res["unsupported_features"]) > 0)

    def test_password_field_without_sfh_sets_phishing_indicator(self):
        # A page containing password/credential fields without a declared server form action
        sample_html = "<div><label>Username</label><input type='text'/></div><div><label>Password</label><input type='password'/></div>"
        res = self.extractor.extract_features(
            "https://example.com/login",
            allow_heuristics=True,
            fetch_network=False,
            mock_html=sample_html,
            mock_dns=True,
        )
        self.assertEqual(res["features"]["SFH"], -1)

    def test_safe_fetch_page_decompresses_gzip_content(self):
        import gzip
        raw_html = b"<!DOCTYPE html><html><body><input type='password' name='passwd'/></body></html>"
        gzipped_payload = gzip.compress(raw_html)

        mock_resp = MagicMock()
        mock_resp.status = 200
        def mock_getheader(h, default=""):
            hl = h.lower()
            if hl == "content-encoding":
                return "gzip"
            if hl == "content-type":
                return "text/html; charset=utf-8"
            return default

        mock_resp.getheader.side_effect = mock_getheader
        mock_resp.read.return_value = gzipped_payload

        mock_conn = MagicMock()
        mock_conn.getresponse.return_value = mock_resp

        with patch("http.client.HTTPSConnection", return_value=mock_conn):
            with patch("networksecurity.components.url_feature_extractor.validate_and_sanitize_url", return_value={"scheme": "https", "hostname": "example.com", "port": 443, "path": "/test", "target_ip": "93.184.216.34", "parsed": urllib.parse.urlparse("https://example.com/test")}):
                html, redirects, err = self.extractor.safe_fetch_page("https://example.com/test", "example.com")
                self.assertIsNotNone(html)
                self.assertIn("passwd", html)
                self.assertIsNone(err)

    def test_safebrowsing_test_fixture_refuses_unsupported_prediction_in_strict_mode(self):
        # Regression test for testsafebrowsing fixture URL under default strict mode
        res = self.extractor.extract_features(
            "https://testsafebrowsing.appspot.com/s/phishing.html",
            fetch_network=False,
        )
        self.assertEqual(res["feature_coverage"], "incomplete")
        self.assertTrue(len(res["unsupported_features"]) > 0)
        self.assertGreater(res["missing_count"], 0)

    def test_feature_status_and_evidence_tracking(self):
        # Verify feature_details tracks status, evidence_source, and explanation
        res = self.extractor.extract_features(
            "https://example.com",
            allow_heuristics=True,
            fetch_network=False,
        )
        details = res["feature_details"]
        self.assertEqual(len(details), 30)
        for feat_name, meta in details.items():
            self.assertIn("status", meta)
            self.assertIn("value", meta)
            self.assertIn("evidence_source", meta)
            self.assertIn("explanation", meta)
            self.assertIn(meta["status"], ["observed", "externally_verified", "estimated", "missing"])

        # Lexical features must be observed
        self.assertEqual(details["URL_Length"]["status"], "observed")
        self.assertEqual(details["having_IP_Address"]["status"], "observed")

        # External intel features in heuristic mode must be estimated
        self.assertEqual(details["web_traffic"]["status"], "estimated")
        self.assertEqual(details["Page_Rank"]["status"], "estimated")
        self.assertEqual(details["Statistical_report"]["status"], "estimated")

    def test_missing_external_features_receive_neutral_defaults_not_optimistic_ones(self):
        res = self.extractor.extract_features(
            "https://example.com",
            allow_heuristics=True,
            fetch_network=False,
        )
        feats = res["features"]
        # Statistical_report must NOT be optimistically 1 (safe); neutral baseline is 0
        self.assertEqual(feats["Statistical_report"], 0)
        # Google_Index must NOT be optimistically 1; neutral baseline is 0
        self.assertEqual(feats["Google_Index"], 0)
        # age_of_domain neutral baseline is 0
        self.assertEqual(feats["age_of_domain"], 0)
        # web_traffic neutral baseline is 0
        self.assertEqual(feats["web_traffic"], 0)
        # Page_Rank neutral baseline is -1 (unranked)
        self.assertEqual(feats["Page_Rank"], -1)

    def test_dom_elements_absent_receive_neutral_baselines_not_legitimate_credit(self):
        # Empty page with 0 anchors, 0 media, 0 favicon must NOT get 1 (legitimate)
        empty_html = "<html><body><p>Just text</p></body></html>"
        res = self.extractor.extract_features(
            "https://example.com",
            allow_heuristics=True,
            fetch_network=False,
            mock_html=empty_html,
            mock_dns=True,
        )
        feats = res["features"]
        details = res["feature_details"]
        # When 0 anchors exist, URL_of_Anchor must be 0 (neutral), NOT 1 (legitimate)
        self.assertEqual(feats["URL_of_Anchor"], 0)
        self.assertEqual(details["URL_of_Anchor"]["status"], "estimated")
        # Request_URL with 0 media must be 0 (neutral), NOT 1
        self.assertEqual(feats["Request_URL"], 0)
        # Favicon with 0 favicon tags must be 0 (neutral), NOT 1
        self.assertEqual(feats["Favicon"], 0)


if __name__ == "__main__":
    unittest.main()
