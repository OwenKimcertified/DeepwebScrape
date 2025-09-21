from ..base import BaseAnalyzer
from Repository.metaStore import MongoMetaStore

from bs4 import BeautifulSoup
import html, re
    
class AnalyzeCuba(BaseAnalyzer):
    """랜섬웨어 CUBA 도메인 분석기"""
    def __init__(self, domain_url: str):
        super().__init__(domain_url)
        self.meta_store = MongoMetaStore.get_instance()
        
    def targetCheck(self, page: str, sha256: str = "") -> bool:
        soup = BeautifulSoup(page, "html.parser")
        company_blocks = soup.find_all("div", class_="col-xs-12")
        domain, url = self.meta_store.get_domain_and_url(sha256) or ("", "")
        if domain == self.domain_url and "/ajax/page_free/" in url and company_blocks:
            return True
        return False

    def extract_company_name(self, block) -> str:
        """회사명 추출 로직 개선"""
        # URL에서 회사명 추출 
        a_tag = block.select_one("div.list-text > a")
        if a_tag and a_tag.get("href"):
            href = a_tag.get("href")
            if "/company/" in href:
                company_name = href.split("/company/")[-1]
                # 'ohagin'을 'Ohagin'으로, 'schultheis-ins'를 'Schultheis Ins'로 변환
                return company_name.replace("-", " ").title()
        
        # 이미지에서 회사명 추출
        img_tag = block.select_one("div.list-img img")
        if img_tag and img_tag.get("src"):
            src = img_tag.get("src")
            # /content.images/ohagin-transparent-logo.png -> ohagin
            filename = src.split("/")[-1].split(".")[0]
            # 로고 관련 단어 제거
            company_name = re.sub(r'-(logo|transparent|tv)$', '', filename, flags=re.IGNORECASE)
            if company_name and company_name not in ['bezimyanniy']: 
                return company_name.title()
        
        return ""

    def parse(self, page: str, sha256: str, sitename: str) -> list:
        results = []
        seen = set()

        try:
            soup = BeautifulSoup(page, "html.parser")
            company_blocks = soup.find_all("div", class_="col-xs-12")

            for block in company_blocks:
                a_tag = block.select_one("div.list-text > a")
                if not a_tag:
                    continue

                # 개선된 회사명 추출
                victim_name = self.extract_company_name(block)
                if not victim_name:
                    continue

                # 설명 텍스트 정리
                full_text = a_tag.get_text(separator=" ", strip=True)
                full_text = html.unescape(full_text)
                full_text = re.sub(r'\s+', ' ', full_text)  # 연속된 공백 제거
                

                description = full_text
                description = description.replace('\n', ' ').replace('\r', ' ')
                description = re.sub(r'\s+', ' ', description).strip()
                
                result = {
                    "sha256": sha256,
                    "sitename": sitename,
                    "company": victim_name,
                    "description": description,
                    "link": a_tag.get("href", "").strip(),
                }
                
                result_key = tuple(result.values())
                if result_key not in seen:
                    seen.add(result_key)
                    results.append(result)
                    
        except Exception as e:
            print(f"[ERROR][CUBA] Parse 실패 - {sha256}: {e}")

        return results