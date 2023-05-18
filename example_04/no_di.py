# database.py
from pymongo import MongoClient


class MongoClient:
    def __init__(self, use_cache: bool, ...) -> None:
        self.client = None
        self.db = None
        self.cache: dict = {}
        self.use_cache = use_cache
    
    def connect(self) -> None:
        try:
            self.client = MongoClient(...)
            self.db = self.client["My_database"]
        except Exception as e:
            raise ConnectionError(f"Cannot connect to database: {repr(e)}")

    def get_document(self, document_id: str, coll: str) -> dict:
        if self.use_cache:
            if document_id not in self.cache:
                self.cache[document_id] = self.db[coll].find_one({"_id": document_id})
            document = self.cache[document_id]
        else:
            document = self.db[coll].find_one({"_id": document_id})
        return document



# csvreader.py
import csv
from typing import Dict


class CSVReader:
    def __init__(self, use_cache: bool) -> None:
        self.cache: dict = {}
        self.use_cache = use_cache

    def get_document(self, file_name: str) -> Dict:
        document = {}
        if self.use_cache:
            if file_name not in self.cache:
                self.cache[file_name] = self._read_document(file_name)
            document = self.cache[file_name]
        else:
            document = self._read_document(file_name)
        return document

    def _read_document(self, file_name: str) -> Dict:
        document = {}
        with open(file_name, newline='') as csv_file:
            spamreader = csv.DictReader(csv_file)
            for row in spamreader:
                document[row['document_id']] = row['content']
        return document


# client.py
from database import MongoClient
from csvreader import CSVReader
from typing import List, Dict, Any


class APP:
    def __init__(
        self,
        use_cache: bool,
        use_mongo: bool,
        use_csvreader: bool,
        db_conf: Dict[str, Any]
    ) -> None:
        self.use_cache = use_cache
        self.use_mongo = use_mongo
        self.use_csvreader = use_csvreader
        if self.use_mongo:
            self.mongo_db_client = MongoClient(use_cache=self.use_cache, **db_config)
        if self.use_csvreader:
            self.csvreader = CSVReader(use_cache=self.use_cache)
    
    def get_documents_from_ids(self, documents_id: List[str]) -> dict:
        documents = {}
        if self.use_mongo:
            for document_id in documents_id:
                documents[document_id] = self.mongo_db_client.get_document(document_id, "example_collection")
        return documents
    
    def get_documents_from_file(self, document_name: str) -> dict:
        documents = {}
        if self.use_csvreader:
            documents[document_name] = self.csvreader.get_document(document_name)
        return documents


db_conf = {...}
my_app = APP(use_cache=True, use_mongo=False, use_csvreader=True, db_conf=db_conf)
documents = my_app.get_documents_from_file("My_file_name")
