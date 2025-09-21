from ..base import BaseAnalyzer
from bs4 import BeautifulSoup
from Repository.metaStore import MongoMetaStore
import html, re


class AnalyzeAkira(BaseAnalyzer):
    def __init__(self, domain_url: str):
        super().__init__(domain_url)
        self.meta_store = MongoMetaStore.get_instance()
        
    def targetCheck(self, page: str, sha256: str = "") -> bool:
        domain, _ = self.meta_store.get_domain_and_url(sha256) or ("", "")

        # 도메인 검사
        if not domain == self.domain_url:
            return False

        try:
            soup = BeautifulSoup(page, 'html.parser')
            full_text = soup.get_text()
            return "guest@akira:~$ leaks" in full_text or "+--------------+" in full_text
        except Exception as e:
            print(f"[ERROR][AKIRA] HTML 분석 실패: {e}")
            return False

    def parse(self, page: str, sha256: str, sitename: str) -> list:
        results = []
        seen = set()

        # 매번 새로 초기화
        victim_name_parts = []
        description_parts = []
        parsing = False

        try:
            soup = BeautifulSoup(page, "html.parser")
            divs = soup.find_all("div")

            for div in divs:
                text = div.get_text().replace("\xa0", " ").strip()

                if "guest@akira:~$ leaks" in text:
                    parsing = True
                    continue
                if text.startswith("guest@akira:~$") and "leaks" not in text:
                    parsing = False
                    continue
                if not parsing or not text.startswith("|") or text.count("|") < 2:
                    continue

                cols = [html.unescape(col.strip()) for col in text.split("|")[1:-1]]
                if len(cols) < 2:
                    continue

                name_col = cols[0]
                desc_col = cols[1]
                
                if ("name" in name_col.lower() or "desc" in desc_col.lower() or 
                    "name" == name_col.strip().lower() or "desc" == desc_col.strip().lower() or
                    "----" in name_col or "----" in desc_col):
                    continue
                
                is_name_blank = name_col.strip() == ""
                is_next_victim = not is_name_blank and victim_name_parts and description_parts and len(description_parts) > 3

                if is_next_victim:
                    victim_name = "".join(victim_name_parts).strip()
                    description = "".join(description_parts).strip()
                    result = {
                        "sha256": sha256,
                        "sitename": sitename,
                        "company": victim_name,
                        "description": description,
                    }
                    result_key = tuple(result.values())
                    if result_key not in seen:
                        results.append(result)
                        seen.add(result_key)

                    # 다음 victim을 위해 초기화
                    victim_name_parts = []
                    description_parts = []

                if not is_name_blank:
                    victim_name_parts.append(name_col)

                if desc_col:
                    description_parts.append(desc_col)

            if victim_name_parts and description_parts:
                victim_name = "".join(victim_name_parts).strip()
                description = "".join(description_parts).strip()
                description = description.replace('\n', ' ').replace('\r', ' ')
                description = re.sub(r'\s+', ' ', description).strip()
                
                result = {
                    "sha256": sha256,
                    "sitename": sitename,
                    "company": victim_name,
                    "description": description,
                }
                result_key = tuple(result.values())
                if result_key not in seen:
                    results.append(result)
                    seen.add(result_key)

            return results

        except Exception as e:
            print(f" ERROR: {e}")
            return []