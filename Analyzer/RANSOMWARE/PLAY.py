from ..base import BaseAnalyzer
from bs4 import BeautifulSoup

import re

class AnalyzePlay(BaseAnalyzer):
    def __init__(self, domain_url: str):
        super().__init__(domain_url)

    def targetCheck(self, page: str, sha256: str = "") -> bool:
        if 'class="watermark">PLAY' in page:
            return True
        return False

    def parse(self, page: str, sha256: str, sitename: str) -> list:
        soup = BeautifulSoup(page, "html.parser")
        results = []
        seen = set()

        news_blocks = soup.find_all("th", class_="News")
        for block in news_blocks:
            try:
                company = block.get_text(separator="\n", strip=True).split("\n")[0].strip()

                raw_text = block.get_text(" ", strip=True)
                raw_text = re.sub(r"\s+", " ", raw_text)

                # 정규표현식으로 필요한 정보 추출
                views = re.search(r"views:\s*([\d,]+)", raw_text)
                views = views.group(1) if views else ""

                added = re.search(r"added:\s*([\d\-]+)", raw_text)
                added = added.group(1) if added else ""

                pub_date = re.search(r"publication date:\s*([\d\-]+)", raw_text)
                pub_date = pub_date.group(1) if pub_date else ""

                info = re.search(r"information:\s*(.+?)comment:", raw_text)
                info_text = info.group(1).strip() if info else ""

                comment = re.search(r"comment:\s*(.+?)DOWNLOAD LINKS:", raw_text)
                comment_text = comment.group(1).strip() if comment else ""

                link_match = re.search(r"(http[s]?://[^\s]+)", raw_text)
                link = link_match.group(1).strip() if link_match else ""

                password_match = re.search(r"password:\s*([^\s,]+)", raw_text)
                password = password_match.group(1).strip() if password_match else ""

                description = None

                key = (sha256, company, link)
                if key in seen:
                    continue
                seen.add(key)

                results.append({
                    "sha256": sha256,
                    "sitename": sitename,
                    "company": company,
                    "description": description,
                    "link": link,
                    "views": views,
                    "added": added,
                    "publication_date": pub_date,
                    "password": password
                })

            except Exception as e:
                print(f"[ERROR][PLAY] block 파싱 실패: {e}")

        return results