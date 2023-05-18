# database.py
import abc
import csv

from pymongo import MongoClient
from mysql.connector import connect, Error


class BaseClient(abc.ABC):
    @abc.abstractmethod
    def get_document(self, document_id: str) -> dict:
        raise NotImplementedError()


class MySQLClient(BaseClient):
    def __init__(self, ...) -> None:
        self.client = None
        self.host = None
        self.user = None
        self.password = None
        self.database = None
        self.table = None
    
    def select_table(self, table_name: str) -> None:
        self.table = table_name
    
    def get_document(self, document_id: str) -> dict:
        document = {}
        try:
            with connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            ) as conn:
                query = f"SELECT * from {self.table} where document_id == {document_id}"
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    result = cursor.fetchall()
                    for row in result:
                        document[document_id] = row
        except Error as e:
            raise ConnectionError(f"Cannot get the document: {repr(e)}")
        return document


class MongoClient(BaseClient):
    def __init__(self, next_resp: BaseClient, ...):
        self.next_resp = next_resp
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
        if not document:
            document = self.next_resp.get_document(document_id)
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
    def create_app_chain_responsability(
        cls,
        use_cache: bool,
        db_client_config: Dict[str, Any],
        csv_reader_config: Dict[str, Any]
    ) -> 'APP':
        client = MongoClient(CSVReader(**csv_reader_config), **db_client_config)
        if use_cache:
            cache = CacheReader(client)
            return cls(cache)
        return cls(client)

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


# Con Mongodb
mongo_config = {....}
mongo_client = MongoClient(**mongo_config)
my_app = APP(mongo_client)
# Con CSV
csv_config = {....}
csv_client = CSVReader(**csv_config)
my_app = APP(csv_client)
# Con MySQL
sql_config = {....}
sql_client = MySQLClient(**sql_config)
my_app = APP(sql_client)