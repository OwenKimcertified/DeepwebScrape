from Interface.domain import *
from Repository.metaStore import MongoMetaStore
import asyncio, aiofiles, os, re

RAW_DIR = "raw"

class RawReader:
    """RAW 파일 데이터 읽기"""
    @staticmethod
    async def read_file(sha256: str) -> str:
        dir_name = sha256[:2]
        file_path = os.path.join(RAW_DIR, dir_name, sha256)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        async with aiofiles.open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return await f.read()

    # @staticmethod
    # def read_raw_html(sha256: str) -> str:
    #     dir_name = sha256[:2]
    #     file_path = os.path.join(RAW_DIR, dir_name, sha256)

    #     if not os.path.exists(file_path):
    #         raise FileNotFoundError(f"File not found: {file_path}")

    #     with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
    #         return f.read()

    @staticmethod
    def iter_all_sha256():
        for i in os.listdir(RAW_DIR):
            subdir = os.path.join(RAW_DIR, i)
            if not os.path.isdir(subdir):
                continue
            for file in os.listdir(subdir):
                yield file

class DomainClassifier:
    """메타스토어 기반 분석 도메인 판단"""

    @staticmethod
    def get_analyze_target(sha256: str, html: str) -> list[tuple]:
        """
        HTML + MongoDB 기반 후보 분석기 모두 추출 
        return: list of (AnalyzerType, sitename, domain_url)
        """
        results = set()

        # HTML 기반 후보 추출
        if 'post_body' in html and 'post__author' in html:
            results.add((AnalyzerType.FORUM_POST, DomainInfo.BREACHED_POST.value[2], DomainInfo.BREACHED_POST.value[0]))

        if 'post__user-profile' in html and re.search(r'uid=\d+', html):
            results.add((AnalyzerType.FORUM_USER, DomainInfo.BREACHED_USER.value[2], DomainInfo.BREACHED_USER.value[0]))

        # ransomware 후보 HTML 기반
        for domain in DomainInfo:
            domain_str, analyzer_type, sitename = domain.value
            if domain_str in html:
                results.add((analyzer_type, sitename, domain_str))

        # Mongo 기반 fallback도 함께 사용
        domain, url = MongoMetaStore.get_instance().get_domain_and_url(sha256) or ("", "")
        for domain_enum in DomainInfo:
            domain_str, analyzer_type, sitename = domain_enum.value
            if domain_str == domain:
                if analyzer_type == AnalyzerType.FORUM_USER and "/Thread-" not in url:
                    results.add((analyzer_type, sitename, domain_str))
                elif analyzer_type == AnalyzerType.FORUM_POST and "/Thread-" in url:
                    results.add((analyzer_type, sitename, domain_str))
                elif analyzer_type == AnalyzerType.RANSOMWARE:
                    results.add((analyzer_type, sitename, domain_str))

        return list(results)