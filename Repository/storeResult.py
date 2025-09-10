from Repository.metaStore import MongoMetaStore
from Interface.models import *
from Utils.uuid import SnowflakeGenerator

class RansomwareResultStore:
    def __init__(self, machine_id: int = 1, rebuild: bool = False):
        self.meta_store = MongoMetaStore.get_instance()
        self.db = self.meta_store.db
        self.id_generator = SnowflakeGenerator(machine_id)
        self.collection_name = "rebuild_ransomware" if rebuild else "ransomware"

    def _prepare(self, raw_dicts: list[dict]) -> list[RansomwareResult]:
        sha_list = [r["sha256"] for r in raw_dicts]
        ts_map = self.meta_store.get_timestamp_map(sha_list)
        prepared = []

        for r in raw_dicts:
            sha256 = r["sha256"]
            timestamp = ts_map.get(sha256)
            if not timestamp:
                continue
            
            rid = self.id_generator.generate_id()
            prepared.append(RansomwareResult(
                _id=rid,
                sha256=sha256,
                sitename=r["sitename"],
                company=r["company"],
                description=r["description"],
                link=r.get("link", ""),
                timestamp=timestamp,
            ))
        return prepared

    def store_batch(self, raw_dicts: list[dict]):
        docs = self._prepare(raw_dicts)
        if docs:
            self.db[self.collection_name].insert_many([d.to_dict() for d in docs])


class ForumUserResultStore:
    def __init__(self, machine_id: int = 1, rebuild: bool = False):
        self.meta_store = MongoMetaStore.get_instance()
        self.db = self.meta_store.db
        self.id_generator = SnowflakeGenerator(machine_id)
        self.collection_name = "rebuild_forum_user" if rebuild else "forum_user"

    def _prepare(self, raw_dicts: list[dict]) -> list[ForumUserResult]:
        sha_list = [r["sha256"] for r in raw_dicts]
        ts_map = self.meta_store.get_timestamp_map(sha_list)
        prepared = []

        for r in raw_dicts:
            sha256 = r["sha256"]
            timestamp = ts_map.get(sha256)
            if not timestamp:
                continue
            rid = self.id_generator.generate_id()
            prepared.append(ForumUserResult(
                _id=rid,
                sha256=sha256,
                domain=r["domain"],
                username=r["username"],
                user_id=r["user_id"],
                user_title=r["user_title"],
                reputation=r["reputation"],
                posts=r["posts"],
                threads=r["threads"],
                joined=r["joined"],
                awards=r["awards"],
                telegram=r["telegram"],
                timestamp=timestamp,
            ))
        return prepared

    def store_batch(self, raw_dicts: list[dict]):
        docs = self._prepare(raw_dicts)
        if docs:
            self.db[self.collection_name].insert_many([d.to_dict() for d in docs])


class ForumPostResultStore:
    def __init__(self, machine_id: int = 1, rebuild: bool = False):
        self.meta_store = MongoMetaStore.get_instance()
        self.db = self.meta_store.db
        self.id_generator = SnowflakeGenerator(machine_id)
        self.collection_name = "rebuild_forum_post" if rebuild else "forum_post"

    def _prepare(self, raw_dicts: list[dict]) -> list[ForumPostResult]:
        sha_list = [r["sha256"] for r in raw_dicts]
        ts_map = self.meta_store.get_timestamp_map(sha_list)
        prepared = []

        for r in raw_dicts:
            sha256 = r["sha256"]
            timestamp = ts_map.get(sha256)
            if not timestamp:
                continue
            rid = self.id_generator.generate_id()
            prepared.append(ForumPostResult(
                _id=rid,
                sha256=sha256,
                domain=r["domain"],
                thread_title=r["thread_title"],
                post_no=r["post_no"],
                username=r["username"],
                user_id=r["user_id"],
                author_title=r["author_title"],
                reputation=r["reputation"],
                posts=r["posts"],
                threads=r["threads"],
                joined=r["joined"],
                post_date=r["post_date"],
                content=r["content"],
                urls=r["urls"],
                emails=r["emails"],
                signature=r["signature"],
                timestamp=timestamp,
            ))
        return prepared

    def store_batch(self, raw_dicts: list[dict]):
        docs = self._prepare(raw_dicts)
        if docs:
            self.db[self.collection_name].insert_many([d.to_dict() for d in docs])


# from Repository.metaStore import MongoMetaStore
# from Interface.models import *
# from Utils.uuid import SnowflakeGenerator

# class RansomwareResultStore:
#     def __init__(self, machine_id: int = 1, rebuild: bool = False):
#         self.meta_store = MongoMetaStore.get_instance()
#         self.db = self.meta_store.db
#         self.id_generator = SnowflakeGenerator(machine_id)
#         self.collection_name = "rebuild_ransomware" if rebuild else "ransomware"

#     def _prepare(self, raw_dicts: list[dict]) -> list[RansomwareResult]:
#         prepared = []
#         for r in raw_dicts:
#             sha256 = r["sha256"]
#             timestamp = self.meta_store.get_timestamp(sha256)
#             if not timestamp:
#                 continue
#             rid = self.id_generator.generate_id()
#             prepared.append(RansomwareResult(
#                 _id=rid,
#                 sha256=sha256,
#                 sitename=r["sitename"],
#                 company=r["company"],
#                 description=r["description"],
#                 link=r.get("link", ""),
#                 timestamp=timestamp,
#             ))
#         return prepared

#     # Ransomeware의 경우 유효한 분석 결과는 중복 제거 없이 모두 저장
#     def store_batch(self, raw_dicts: list[dict]):
#         docs = self._prepare(raw_dicts)
#         if docs:
#             self.db[self.collection_name].insert_many([d.to_dict() for d in docs])


# class ForumUserResultStore:
#     def __init__(self, machine_id: int = 1, rebuild: bool = False):
#         self.meta_store = MongoMetaStore.get_instance()
#         self.db = self.meta_store.db
#         self.id_generator = SnowflakeGenerator(machine_id)
#         self.collection_name = "rebuild_forum_user" if rebuild else "forum_user"

#     def _prepare(self, raw_dicts: list[dict]) -> list[ForumUserResult]:
#         prepared = []
#         for r in raw_dicts:
#             sha256 = r["sha256"]
#             timestamp = self.meta_store.get_timestamp(sha256)
#             if not timestamp:
#                 continue
#             rid = self.id_generator.generate_id()
#             prepared.append(ForumUserResult(
#                 _id=rid,
#                 sha256=sha256,
#                 domain=r["domain"],
#                 username=r["username"],
#                 user_id=r["user_id"],
#                 user_title=r["user_title"],
#                 reputation=r["reputation"],
#                 posts=r["posts"],
#                 threads=r["threads"],
#                 joined=r["joined"],
#                 awards=r["awards"],
#                 telegram=r["telegram"],
#                 timestamp=timestamp,
#             ))
#         return prepared

#     def store_batch(self, raw_dicts: list[dict]):
#         docs = self._prepare(raw_dicts)
#         if docs:
#             self.db[self.collection_name].insert_many([d.to_dict() for d in docs])


# class ForumPostResultStore:
#     def __init__(self, machine_id: int = 1, rebuild: bool = False):
#         self.meta_store = MongoMetaStore.get_instance()
#         self.db = self.meta_store.db
#         self.id_generator = SnowflakeGenerator(machine_id)
#         self.collection_name = "rebuild_forum_post" if rebuild else "forum_post"

#     def _prepare(self, raw_dicts: list[dict]) -> list[ForumPostResult]:
#         prepared = []
#         for r in raw_dicts:
#             sha256 = r["sha256"]
#             timestamp = self.meta_store.get_timestamp(sha256)
#             if not timestamp:
#                 continue
#             rid = self.id_generator.generate_id()
#             prepared.append(ForumPostResult(
#                 _id=rid,
#                 sha256=sha256,
#                 domain=r["domain"],
#                 thread_title=r["thread_title"],
#                 post_no=r["post_no"],
#                 username=r["username"],
#                 user_id=r["user_id"],
#                 author_title=r["author_title"],
#                 reputation=r["reputation"],
#                 posts=r["posts"],
#                 threads=r["threads"],
#                 joined=r["joined"],
#                 post_date=r["post_date"],
#                 content=r["content"],
#                 urls=r["urls"],
#                 emails=r["emails"],
#                 signature=r["signature"],
#                 timestamp=timestamp,
#             ))
#         return prepared

#     def store_batch(self, raw_dicts: list[dict]):
#         docs = self._prepare(raw_dicts)
#         if docs:
#             self.db[self.collection_name].insert_many([d.to_dict() for d in docs])