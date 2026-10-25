import os
import sys
import json
from dotenv import load_dotenv


load_dotenv()
MONGO_DB_URL=os.getenv("MONGO_DB_URL")

import certifi
ca=certifi.where()
import pandas as pd
import numpy as np
import pymongo
from networksecurity.logging.logger import logging
from networksecurity.exception.exception import NetworkSecurityException

class NetworkDataExtract():
    def __init__(self):
        try:
            pass
        except Exception as e :
            raise NetworkSecurityException(e,sys)
    def csv_to_json_convertor(self,file_path):
        try:
            data=pd.read_csv(file_path)
            data.reset_index(drop=True,inplace=True)
            records=data.to_dict(orient="records")
            return records
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    def insert_data_mongodb(self,records,database,collection):
        try:
            if not MONGO_DB_URL:
                raise RuntimeError(
                    "MONGO_DB_URL environment variable is not set. Please set it in your .env file or environment."
                )
            self.database=database
            self.collection=collection
            self.records=records

            self.mongo_client=pymongo.MongoClient(MONGO_DB_URL, tlsCAFile=ca)
            self.database=self.mongo_client[self.database]
            self.collection=self.database[self.collection]
            self.collection.insert_many(self.records)
            return(len(self.records))
        
        except Exception as e:
            raise NetworkSecurityException(e,sys)
if __name__=="__main__":
    FILE_PATH="Network_Data/phisingData.csv"
    DATABASE="RahulAI"
    Collection="NetworkData"
    networkobj=NetworkDataExtract()
    records=networkobj.csv_to_json_convertor(file_path=FILE_PATH)
    print(records)
    no_of_records=networkobj.insert_data_mongodb(records,DATABASE,Collection)
    print(no_of_records)
        



