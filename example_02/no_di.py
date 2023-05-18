# database.py
from pymongo import MongoClient


class MongoClient:
    def __init__(self) -> None:
        self.client = None
        self.db = None
    
    def connect(self) -> None:
        try:
            self.client = MongoClient(...)
            self.db = self.client["My_database"]
        except Exception as e:
            raise ConnectionError(f"Cannot connect to database: {repr(e)}")

    def get_document(self, document_id: str, coll: str) -> dict:
        document = self.db[coll].find_one({"_id": document_id})
        return document


# client.py
from database import MongoClient
from typing import List


class APP:
    def __init__(self) -> None:
        self._mongo_db_client = MongoClient()
    
    def get_documents_from_ids(self, documents_id: List[str]) -> dict:
        products = {}
        for document_id in documents_id:
            products[document_id] = self._mongo_db_client.get_document(document_id, "example_coll")
        return products
