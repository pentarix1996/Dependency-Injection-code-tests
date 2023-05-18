# database.py
from pymongo import MongoClient


class MongoClient:
    def __init__(self, use_cache: bool) -> None:
        self.client = None
        self.db = None
        self.cache: dict = None
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


# client.py
from database import MongoClient
from typing import List


class APP:
    def __init__(self, use_cache: bool) -> None:
        self.use_cache = use_cache
        self._mongo_db_client = MongoClient(use_cache=self.use_cache)
    
    def get_documents_from_ids(self, documents_id: List[str]) -> dict:
        products = {}
        for document_id in documents_id:
            products[document_id] = self._mongo_db_client.get_document(document_id, "example_coll")
        return products

my_app = APP(use_cache=True)
documents = my_app.get_documents_from_ids(["1", "2", "3"])
