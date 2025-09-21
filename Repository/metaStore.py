
from pymongo import MongoClient
from pymongo.collection import Collection
from typing import Optional
from config import *

from datetime import datetime

class MongoMetaStore:
    _instance = None  # 싱글톤
    def __init__(self, mongo_url=HOST, db_name=DB):
        self.client = MongoClient(mongo_url)
        self.db = self.client[db_name]
        self.meta: Collection = self.db[COLLECTION]

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = MongoMetaStore()
        return cls._instance

    def get_domain_and_url(self, sha256: str) -> Optional[tuple[str, str]]:
        doc = self.meta.find_one({"sha256": sha256})
        if not doc:
            return None
        request = doc.get("request", {})
        domain = request.get("domain", "").strip()
        url = request.get("url", "").strip()
        return domain, url

    def get_timestamp_map(self, sha256_list: list[str]) -> dict[str, datetime]:
        cursor = self.db.test_meta.find(
            {"sha256": {"$in": sha256_list}},
            {"sha256": 1, "timestamp_store": 1}
        )
        return {
            doc["sha256"]: doc["timestamp_store"]
            for doc in cursor
            if "timestamp_store" in doc
        }