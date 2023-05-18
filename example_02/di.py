# database.py
import abc

from pymongo import MongoClient


class DataBaseClient(abc.ABC):
    @abc.abstractmethod
    def connect(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_document(self, document_id: str) -> dict:
        raise NotImplementedError()


class MongoClient(DataBaseClient):
    def __init__(self, ...) -> None:
        self.client = None
        self.coll = None
        self.db = None
    
    def connect(self) -> None:
        try:
            self.client = MongoClient(...)
            self.db = self.client["My_database"]
        except Exception as e:
            raise ConnectionError(f"Cannot connect to database: {repr(e)}")

    def select_collection(self, coll: str) -> None:
        self.coll = coll

    def get_document(self, document_id: str) -> dict:
        document = self.coll.find_one({"_id": document_id})
        return document


# client.py
from database import DataBaseClient
from typing import List


class APP:
    def __init__(self, client: DataBaseClient) -> None:
        self.client = client
    
    def get_documents_from_ids(self, documents_id: List[str]) -> dict:
        products = {}
        for document_id in documents_id:
            products[document_id] = self.client.get_document(document_id)
        return products

client = MongoClient(...)
my_app = APP(client)
documents = my_app.get_documents_from_ids(["1", "2", "3"])
