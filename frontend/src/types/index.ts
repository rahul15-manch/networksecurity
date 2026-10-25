export type FeatureValue = -1 | 0 | 1;

export interface PhishingFeatures {
  having_IP_Address: number;
  URL_Length: number;
  Shortining_Service: number;
  having_At_Symbol: number;
  double_slash_redirecting: number;
  Prefix_Suffix: number;
  having_Sub_Domain: number;
  SSLfinal_State: number;
  Domain_registeration_length: number;
  Favicon: number;
  port: number;
  HTTPS_token: number;
  Request_URL: number;
  URL_of_Anchor: number;
  Links_in_tags: number;
  SFH: number;
  Submitting_to_email: number;
  Abnormal_URL: number;
  Redirect: number; // strictly 0 or 1
  on_mouseover: number;
  RightClick: number;
  popUpWidnow: number;
  Iframe: number;
  age_of_domain: number;
  DNSRecord: number;
  web_traffic: number;
  Page_Rank: number;
  Google_Index: number;
  Links_pointing_to_page: number;
  Statistical_report: number;
  [key: string]: number;
}

export interface PredictionResponse {
  prediction: "phishing" | "legitimate" | string;
  class_id: 0 | 1;
  model_score: number | null;
}

export interface ExtractionStageInfo {
  status: 'success' | 'partial' | 'failed' | 'heuristic_baseline' | 'unsupported';
  count?: number;
  details?: string;
  reason?: string;
  error?: string;
}

export interface URLPredictionRequest {
  url: string;
  allow_heuristics?: boolean;
  fetch_network?: boolean;
}

export interface URLPredictionResponse {
  status: 'success' | 'unsupported_features';
  url: string;
  prediction: 'phishing' | 'legitimate' | string | null;
  class_id: 0 | 1 | null;
  model_score: number | null;
  feature_coverage: 'complete' | 'heuristic' | 'incomplete';
  extracted_count: number;
  total_expected: number;
  features: Record<string, number>;
  stages: Record<string, ExtractionStageInfo>;
  unsupported_features: string[];
  warnings: string[];
  message?: string;
}

export type UnifiedResult = (PredictionResponse | URLPredictionResponse) & {
  status?: string;
  url?: string;
  feature_coverage?: string;
  stages?: Record<string, ExtractionStageInfo>;
  unsupported_features?: string[];
  warnings?: string[];
  message?: string;
};


export interface HealthResponse {
  status: "healthy" | "degraded" | string;
  model_loaded: boolean;
  version: string;
  supported_features_count: number;
}

export interface FeatureMeta {
  key: keyof PhishingFeatures;
  label: string;
  category: "Lexical & URL" | "Security & SSL" | "Domain & DNS" | "Page Content & Scripting";
  description: string;
  allowedValues: number[];
  options: { value: number; label: string; meaning: "phishing" | "suspicious" | "legitimate" }[];
}

export const FEATURE_METADATA: FeatureMeta[] = [
  // Lexical & URL
  {
    key: "having_IP_Address",
    label: "IP Address in URL",
    category: "Lexical & URL",
    description: "Whether the hostname is an IP address instead of a domain.",
    allowedValues: [-1, 1],
    options: [
      { value: -1, label: "-1 : IP Used (Phishing)", meaning: "phishing" },
      { value: 1, label: "+1 : Domain Name (Legitimate)", meaning: "legitimate" },
    ],
  },
  {
    key: "URL_Length",
    label: "URL Length",
    category: "Lexical & URL",
    description: "Length of the target URL string.",
    allowedValues: [-1, 0, 1],
    options: [
      { value: -1, label: "-1 : Long URL >=75 (Phishing)", meaning: "phishing" },
      { value: 0, label: "0 : Moderate Length (Suspicious)", meaning: "suspicious" },
      { value: 1, label: "+1 : Standard Length <54 (Legitimate)", meaning: "legitimate" },
    ],
  },
  {
    key: "Shortining_Service",
    label: "URL Shortener",
    category: "Lexical & URL",
    description: "Domain uses a shortening service like bit.ly, tinyurl.",
    allowedValues: [-1, 1],
    options: [
      { value: -1, label: "-1 : Shortener Used (Phishing)", meaning: "phishing" },
      { value: 1, label: "+1 : Direct URL (Legitimate)", meaning: "legitimate" },
    ],
  },
  {
    key: "having_At_Symbol",
    label: "@ Symbol in URL",
    category: "Lexical & URL",
    description: "Contains '@' symbol causing browsers to ignore preceding text.",
    allowedValues: [-1, 1],
    options: [
      { value: -1, label: "-1 : '@' Present (Phishing)", meaning: "phishing" },
      { value: 1, label: "+1 : No '@' (Legitimate)", meaning: "legitimate" },
    ],
  },
  {
    key: "double_slash_redirecting",
    label: "// Redirect in Path",
    category: "Lexical & URL",
    description: "Presence of '//' in the URL path forwarding the user.",
    allowedValues: [-1, 1],
    options: [
      { value: -1, label: "-1 : '//' in Path (Phishing)", meaning: "phishing" },
      { value: 1, label: "+1 : Normal (Legitimate)", meaning: "legitimate" },
    ],
  },
  {
    key: "Prefix_Suffix",
    label: "Hyphen in Domain",
    category: "Lexical & URL",
    description: "Domain name contains a '-' prefix/suffix separating words.",
    allowedValues: [-1, 1],
    options: [
      { value: -1, label: "-1 : Hyphenated (Phishing)", meaning: "phishing" },
      { value: 1, label: "+1 : No Hyphen (Legitimate)", meaning: "legitimate" },
    ],
  },
  {
    key: "having_Sub_Domain",
    label: "Subdomain Depth",
    category: "Lexical & URL",
    description: "Number of sub-dots in hostname.",
    allowedValues: [-1, 0, 1],
    options: [
      { value: -1, label: "-1 : Multiple Subdomains (Phishing)", meaning: "phishing" },
      { value: 0, label: "0 : Single Subdomain (Suspicious)", meaning: "suspicious" },
      { value: 1, label: "+1 : Root / None (Legitimate)", meaning: "legitimate" },
    ],
  },
  {
    key: "Abnormal_URL",
    label: "Abnormal Hostname",
    category: "Lexical & URL",
    description: "Host is not included in URL identity or WHOIS match.",
    allowedValues: [-1, 1],
    options: [
      { value: -1, label: "-1 : Hostname Mismatch (Phishing)", meaning: "phishing" },
      { value: 1, label: "+1 : Standard Hostname (Legitimate)", meaning: "legitimate" },
    ],
  },

  // Security & SSL
  {
    key: "SSLfinal_State",
    label: "SSL / TLS Certificate State",
    category: "Security & SSL",
    description: "Issuer trust, age, and validity of HTTPS certificate.",
    allowedValues: [-1, 0, 1],
    options: [
      { value: -1, label: "-1 : No SSL / Untrusted (Phishing)", meaning: "phishing" },
      { value: 0, label: "0 : Suspicious Issuer (Warning)", meaning: "suspicious" },
      { value: 1, label: "+1 : Valid Trusted CA (Legitimate)", meaning: "legitimate" },
    ],
  },
  {
    key: "HTTPS_token",
    label: "HTTPS Token in Domain",
    category: "Security & SSL",
    description: "Tricks users by placing 'https' inside domain name text.",
    allowedValues: [-1, 1],
    options: [
      { value: -1, label: "-1 : 'https' in Domain (Phishing)", meaning: "phishing" },
      { value: 1, label: "+1 : Legitimate HTTPS protocol", meaning: "legitimate" },
    ],
  },
  {
    key: "port",
    label: "Non-Standard Port",
    category: "Security & SSL",
    description: "Service running on open non-standard ports (e.g. 8080, 21, 666).",
    allowedValues: [-1, 1],
    options: [
      { value: -1, label: "-1 : Non-Standard Port (Phishing)", meaning: "phishing" },
      { value: 1, label: "+1 : Standard Port 80/443 (Legitimate)", meaning: "legitimate" },
    ],
  },
  {
    key: "SFH",
    label: "Server Form Handler (SFH)",
    category: "Security & SSL",
    description: "Action URL destination of HTML login/input forms.",
    allowedValues: [-1, 0, 1],
    options: [
      { value: -1, label: "-1 : Empty or about:blank (Phishing)", meaning: "phishing" },
      { value: 0, label: "0 : Different External Domain (Suspicious)", meaning: "suspicious" },
      { value: 1, label: "+1 : Same Domain (Legitimate)", meaning: "legitimate" },
    ],
  },

  // Domain & DNS
  {
    key: "Domain_registeration_length",
    label: "Domain Registration Length",
    category: "Domain & DNS",
    description: "Remaining duration before domain expiration.",
    allowedValues: [-1, 1],
    options: [
      { value: -1, label: "-1 : <= 1 Year (Phishing)", meaning: "phishing" },
      { value: 1, label: "+1 : > 1 Year (Legitimate)", meaning: "legitimate" },
    ],
  },
  {
    key: "age_of_domain",
    label: "Age of Domain",
    category: "Domain & DNS",
    description: "Time elapsed since initial domain creation in WHOIS.",
    allowedValues: [-1, 1],
    options: [
      { value: -1, label: "-1 : < 6 Months Old (Phishing)", meaning: "phishing" },
      { value: 1, label: "+1 : >= 6 Months Old (Legitimate)", meaning: "legitimate" },
    ],
  },
  {
    key: "DNSRecord",
    label: "DNS Record Existence",
    category: "Domain & DNS",
    description: "Whether active A/CNAME records resolve in global DNS.",
    allowedValues: [-1, 1],
    options: [
      { value: -1, label: "-1 : No DNS Record (Phishing)", meaning: "phishing" },
      { value: 1, label: "+1 : Active DNS Record (Legitimate)", meaning: "legitimate" },
    ],
  },
  {
    key: "Page_Rank",
    label: "Google PageRank",
    category: "Domain & DNS",
    description: "Search engine authority and importance ranking.",
    allowedValues: [-1, 1],
    options: [
      { value: -1, label: "-1 : Low / Zero Rank (Phishing)", meaning: "phishing" },
      { value: 1, label: "+1 : Established Rank (Legitimate)", meaning: "legitimate" },
    ],
  },
  {
    key: "Google_Index",
    label: "Indexed in Google",
    category: "Domain & DNS",
    description: "Whether domain is indexed by search crawlers.",
    allowedValues: [-1, 1],
    options: [
      { value: -1, label: "-1 : Not Indexed (Phishing)", meaning: "phishing" },
      { value: 1, label: "+1 : Indexed (Legitimate)", meaning: "legitimate" },
    ],
  },

  // Page Content & Scripting
  {
    key: "Favicon",
    label: "Favicon Origin",
    category: "Page Content & Scripting",
    description: "Favicon icon loaded from external third-party domain.",
    allowedValues: [-1, 1],
    options: [
      { value: -1, label: "-1 : External Domain (Phishing)", meaning: "phishing" },
      { value: 1, label: "+1 : Same Domain (Legitimate)", meaning: "legitimate" },
    ],
  },
  {
    key: "Request_URL",
    label: "External Media / Objects Ratio",
    category: "Page Content & Scripting",
    description: "Percentage of images, audio, and scripts loaded externally.",
    allowedValues: [-1, 1],
    options: [
      { value: -1, label: "-1 : >= 61% External (Phishing)", meaning: "phishing" },
      { value: 1, label: "+1 : < 22% External (Legitimate)", meaning: "legitimate" },
    ],
  },
  {
    key: "URL_of_Anchor",
    label: "Anchor Links Destination",
    category: "Page Content & Scripting",
    description: "Percentage of <a> tags pointing to external or dummy destinations.",
    allowedValues: [-1, 0, 1],
    options: [
      { value: -1, label: "-1 : > 67% External / Dummy (Phishing)", meaning: "phishing" },
      { value: 0, label: "0 : 31% - 67% External (Suspicious)", meaning: "suspicious" },
      { value: 1, label: "+1 : < 31% External (Legitimate)", meaning: "legitimate" },
    ],
  },
  {
    key: "Links_in_tags",
    label: "Links in <Meta>, <Script>, <Link>",
    category: "Page Content & Scripting",
    description: "Proportion of metadata tags referencing external domains.",
    allowedValues: [-1, 0, 1],
    options: [
      { value: -1, label: "-1 : > 81% External (Phishing)", meaning: "phishing" },
      { value: 0, label: "0 : 17% - 81% External (Suspicious)", meaning: "suspicious" },
      { value: 1, label: "+1 : < 17% External (Legitimate)", meaning: "legitimate" },
    ],
  },
  {
    key: "Submitting_to_email",
    label: "Mailto: in Form Submission",
    category: "Page Content & Scripting",
    description: "HTML form sends credentials to 'mailto:' mail address.",
    allowedValues: [-1, 1],
    options: [
      { value: -1, label: "-1 : Submits to Email (Phishing)", meaning: "phishing" },
      { value: 1, label: "+1 : Standard Server Handler (Legitimate)", meaning: "legitimate" },
    ],
  },
  {
    key: "Redirect",
    label: "Redirect Count",
    category: "Page Content & Scripting",
    description: "HTTP forwarding hops (0: Phishing redirect chain, 1: Normal direct).",
    allowedValues: [0, 1],
    options: [
      { value: 0, label: "0 : Suspicious Redirect Chain (Phishing)", meaning: "phishing" },
      { value: 1, label: "1 : Direct / <= 1 Redirect (Legitimate)", meaning: "legitimate" },
    ],
  },
  {
    key: "on_mouseover",
    label: "Mouseover Status Bar Alteration",
    category: "Page Content & Scripting",
    description: "JavaScript alters browser status bar on link hover.",
    allowedValues: [-1, 1],
    options: [
      { value: -1, label: "-1 : Status Bar Altered (Phishing)", meaning: "phishing" },
      { value: 1, label: "+1 : Standard Behavior (Legitimate)", meaning: "legitimate" },
    ],
  },
  {
    key: "RightClick",
    label: "Right-Click Disabled",
    category: "Page Content & Scripting",
    description: "Context menu right-click event blocked by script.",
    allowedValues: [-1, 1],
    options: [
      { value: -1, label: "-1 : Right-Click Disabled (Phishing)", meaning: "phishing" },
      { value: 1, label: "+1 : Right-Click Allowed (Legitimate)", meaning: "legitimate" },
    ],
  },
  {
    key: "popUpWidnow",
    label: "Popup Window with Form",
    category: "Page Content & Scripting",
    description: "Prompts credentials inside an unverified popup window.",
    allowedValues: [-1, 1],
    options: [
      { value: -1, label: "-1 : Credential Popup (Phishing)", meaning: "phishing" },
      { value: 1, label: "+1 : In-Page Login (Legitimate)", meaning: "legitimate" },
    ],
  },
  {
    key: "Iframe",
    label: "Invisible IFrame",
    category: "Page Content & Scripting",
    description: "Uses borderless/hidden iframe to clickjack or hide content.",
    allowedValues: [-1, 1],
    options: [
      { value: -1, label: "-1 : Hidden Iframe Used (Phishing)", meaning: "phishing" },
      { value: 1, label: "+1 : No Suspicious Iframe (Legitimate)", meaning: "legitimate" },
    ],
  },
  {
    key: "web_traffic",
    label: "Alexa Web Traffic Ranking",
    category: "Page Content & Scripting",
    description: "Global web traffic volume and domain popularity tier.",
    allowedValues: [-1, 0, 1],
    options: [
      { value: -1, label: "-1 : No / Negligible Traffic (Phishing)", meaning: "phishing" },
      { value: 0, label: "0 : Moderate Traffic (Suspicious)", meaning: "suspicious" },
      { value: 1, label: "+1 : Top 100,000 Site (Legitimate)", meaning: "legitimate" },
    ],
  },
  {
    key: "Links_pointing_to_page",
    label: "Inbound Links Count",
    category: "Page Content & Scripting",
    description: "Number of external web domains linking to this page.",
    allowedValues: [-1, 0, 1],
    options: [
      { value: -1, label: "-1 : Zero Links (Phishing)", meaning: "phishing" },
      { value: 0, label: "0 : 1 - 2 Links (Suspicious)", meaning: "suspicious" },
      { value: 1, label: "+1 : Multiple Links (Legitimate)", meaning: "legitimate" },
    ],
  },
  {
    key: "Statistical_report",
    label: "Threat Intelligence Report",
    category: "Page Content & Scripting",
    description: "Flagged on PhishTank, StopBadware, or threat blocklists.",
    allowedValues: [-1, 1],
    options: [
      { value: -1, label: "-1 : Flagged on Blocklist (Phishing)", meaning: "phishing" },
      { value: 1, label: "+1 : Clean Record (Legitimate)", meaning: "legitimate" },
    ],
  },
];

export interface PresetTemplate {
  id: string;
  name: string;
  tag: string;
  description: string;
  features: PhishingFeatures;
}

// Presets for easy demonstration and regression testing
export const PRESETS: Record<string, PresetTemplate> = {
  phishing: {
    id: "phishing",
    name: "Credential Harvester (High Risk)",
    tag: "Phishing Sample",
    description: "Simulates an aggressive phishing landing page with IP host, invalid SSL, external form handler, and blocked right-click.",
    features: {
      having_IP_Address: -1,
      URL_Length: -1,
      Shortining_Service: -1,
      having_At_Symbol: -1,
      double_slash_redirecting: -1,
      Prefix_Suffix: -1,
      having_Sub_Domain: -1,
      SSLfinal_State: -1,
      Domain_registeration_length: -1,
      Favicon: -1,
      port: -1,
      HTTPS_token: -1,
      Request_URL: -1,
      URL_of_Anchor: -1,
      Links_in_tags: -1,
      SFH: -1,
      Submitting_to_email: -1,
      Abnormal_URL: -1,
      Redirect: 0, // 0 for phishing
      on_mouseover: -1,
      RightClick: -1,
      popUpWidnow: -1,
      Iframe: -1,
      age_of_domain: -1,
      DNSRecord: -1,
      web_traffic: -1,
      Page_Rank: -1,
      Google_Index: -1,
      Links_pointing_to_page: -1,
      Statistical_report: -1,
    },
  },
  legitimate: {
    id: "legitimate",
    name: "Enterprise Banking Portal (Safe)",
    tag: "Legitimate Sample",
    description: "Represents an established corporate domain with trusted CA certificate, multi-year registration, high traffic, and valid DNS.",
    features: {
      having_IP_Address: 1,
      URL_Length: 1,
      Shortining_Service: 1,
      having_At_Symbol: 1,
      double_slash_redirecting: 1,
      Prefix_Suffix: 1,
      having_Sub_Domain: 1,
      SSLfinal_State: 1,
      Domain_registeration_length: 1,
      Favicon: 1,
      port: 1,
      HTTPS_token: 1,
      Request_URL: 1,
      URL_of_Anchor: 1,
      Links_in_tags: 1,
      SFH: 1,
      Submitting_to_email: 1,
      Abnormal_URL: 1,
      Redirect: 1, // 1 for legitimate
      on_mouseover: 1,
      RightClick: 1,
      popUpWidnow: 1,
      Iframe: 1,
      age_of_domain: 1,
      DNSRecord: 1,
      web_traffic: 1,
      Page_Rank: 1,
      Google_Index: 1,
      Links_pointing_to_page: 1,
      Statistical_report: 1,
    },
  },
  suspicious: {
    id: "suspicious",
    name: "Ambiguous Newly Registered Domain",
    tag: "Edge Case",
    description: "New domain with mixed indicators: valid SSL certificate but young domain age, moderate traffic rank, and external anchors.",
    features: {
      having_IP_Address: 1,
      URL_Length: 0,
      Shortining_Service: 1,
      having_At_Symbol: 1,
      double_slash_redirecting: 1,
      Prefix_Suffix: -1,
      having_Sub_Domain: 0,
      SSLfinal_State: 0,
      Domain_registeration_length: -1,
      Favicon: 1,
      port: 1,
      HTTPS_token: 1,
      Request_URL: -1,
      URL_of_Anchor: 0,
      Links_in_tags: 0,
      SFH: 0,
      Submitting_to_email: 1,
      Abnormal_URL: 1,
      Redirect: 1,
      on_mouseover: 1,
      RightClick: 1,
      popUpWidnow: 1,
      Iframe: 1,
      age_of_domain: -1,
      DNSRecord: 1,
      web_traffic: 0,
      Page_Rank: -1,
      Google_Index: 1,
      Links_pointing_to_page: 0,
      Statistical_report: 1,
    },
  },
};
