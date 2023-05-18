# database.py
import abc

from pymongo import MongoClient


class BaseClient(abc.ABC):

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

    def _select_collection(self, coll: str) -> None:
        self.coll = coll
    
    def get_document(self, document_id: str) -> dict:
        document = self.coll.find_one({"_id": document_id})
        return document


class CacheReader(BaseClient):
    def __init__(self, client: BaseClient) -> None:
        self.cache: dict = {}
        self.client = client
    
    def get_document(self, document_id: str) -> dict:
        if document_id not in self.cache:
            self.cache[document_id] = self.client.get_document(document_id)
        document = self.cache[document_id]
        return document


# client.py
from database import DataBaseClient
from typing import List, Dict, Any


class APP:
    def __init__(self, client: DataBaseClient) -> None:
        self.client = client
    
    def get_documents_from_ids(self, documents_id: List[str]) -> dict:
        products = {}
        for document_id in documents_id:
            products[document_id] = self.client.get_document(document_id)
        return products

    @classmethod
    def create_app_use_mongo(cls, db_conf: Dict[str, Any], use_cache: bool) -> 'APP':
        client = MongoClient(**db_conf)
        if use_cache:
            cache = CacheReader(client)
            return cls(cache)
        return cls(client)


# Sin Cache
db_conf = {....}
my_app = APP.create_app_use_mongo(db_conf, use_cache=False)
documents = my_app.get_documents_from_ids(["1", "2", "3"])
# Con Cache
my_cached_app = APP.create_app_use_mongo(db_conf, use_cache=True)
documents = my_app.get_documents_from_ids(["1", "2", "3"])
