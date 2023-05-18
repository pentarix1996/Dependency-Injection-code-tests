# database.py
import abc
import csv

from pymongo import MongoClient


class BaseClient(abc.ABC):
    @abc.abstractmethod
    def get_document(self, document_id: str) -> dict:
        raise NotImplementedError()


class MongoClient(BaseClient):
    def __init__(self, ...):
        self.client = None
        self.coll = None
        self.db = None

    def connect(self):
        try:
            self.client = MongoClient(...)
            self.db = self.client["My_database"]
        except Exception as e:
            raise ConnectionError(f"Cannot connect to database: {repr(e)}")

    def select_collection(self, coll: str):
        self.coll = coll

    def get_document(self, document_id: str) -> dict:
        document = self.coll.find_one({"_id": document_id})
        return document


class CSVReader(BaseClient):
    def __init__(self, file_name: str):
        self.file_name = file_name

    def get_document(self, document_id: str):
        document = {}
        with open(self.file_name, newline='') as csv_file:
            spamreader = csv.DictReader(csv_file)
            for row in spamreader:
                if row['document_id'] == document_id:
                    document[document_id] = row['content']
                    break
        return document


class CacheReader(BaseClient):
    def __init__(self, client: BaseClient):
        self.cache: dict = {}
        self.client = client
    
    def get_document(self, document_id: str) -> dict:
        if document_id not in self.cache:
            self.cache[document_id] = self.client.get_document(document_id)
        document = self.cache[document_id]
        return document


# cliente.py
from typing import Dict, List, Any
from database import MongoClient, CacheReader, BaseClient, CSVReader


class APP:
    def __init__(self, client: BaseClient):
        self.client = client
    
    def get_documents_from_ids(self, documents_id: List[str]) -> dict:
        products = {}
        for document_id in documents_id:
            products[document_id] = self.client.get_document(document_id)
        return products

    @classmethod
    def create_app_use_mongo(cls, use_cache: bool, db_client_config: Dict[str, Any]) -> 'APP':
        client = MongoClient(**db_client_config)
        if use_cache:
            cache = CacheReader(client)
            return cls(cache)
        return cls(client)

    @classmethod
    def create_app_use_csvreader(cls, use_cache: bool, csv_reader_config: Dict[str, Any]) -> 'APP':
        client = CSVReader(**csv_reader_config)
        if use_cache:
            cache = CacheReader(client)
            return cls(cache)
        return cls(client)


# Sin cache Mongo
mongo_config = {....}
my_app = APP.create_app_use_mongo(use_cache=False, mongo_config)
# Con cache CSV
csv_config = {....}
my_cached_app = APP.create_app_use_csvreader(use_cache=True, csv_config)
documents = my_cached_app.get_documents_from_ids(["1", "2", "3"])


# tests.py
from unittest import mock
import pytest
from typing import Dict


def mock_get_document_mongo(_, document_id: str) -> Dict:
    return {"test_field": f"Test_document_{document_id}"}


@pytest.fixture
def mongo_client_mock():
    client_mock = mock.create_autospec(MongoClient)
    client_mock.coll.find_one = mock_get_document_mongo
    return client_mock


@pytest.fixture
def csv_client_mock():
    client_mock = mock.create_autospec(CSVReader)
    client_mock.file_name = "My_file.csv"
    return client_mock


def test_instance_app_mongo():
    db_conf = {...}
    expected_client = MongoClient(**db_conf)
    my_app = APP.create_app_use_mongo(MongoClient(db_conf=db_conf, use_cache=False))
    assert my_app.client == expected_client
    

def test_instance_app_mongo_cache():
    db_conf = {...}
    expected_client = CacheReader(MongoClient(**db_conf))
    my_app = APP.create_app_use_mongo(MongoClient(db_conf=db_conf, use_cache=True))
    assert my_app.client == expected_client


def test_instance_app_csv():
    csv_conf = {"file_name": "My_file.csv"}
    expected_client = CSVReader(**csv_conf)
    my_app = APP.create_app_use_csvreader(use_cache=False, csv_reader_config=csv_conf)
    assert my_app.client == expected_client


def test_instance_app_csv_cache():
    csv_conf = {"file_name": "My_file.csv"}
    expected_client = CacheReader(CSVReader(**csv_conf))
    my_app = APP.create_app_use_csvreader(use_cache=True, csv_reader_config=csv_conf)
    assert my_app.client == expected_client


@pytest.mark.parametrize(
        ["mock_client"],
        [(mongo_client_mock), (csv_client_mock)]
)
def test_app_mongo_get_file(mock_client):
    my_app = APP(mock_client)
    documents = my_app.get_documents_from_ids(["1", "2", "3"])

    expected_documents = {
        "1": {"test_field": "Test_document_1"},
        "2": {"test_field": "Test_document_2"},
        "3": {"test_field": "Test_document_3"}
    }
    assert documents == expected_documents
