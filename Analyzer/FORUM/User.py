from ..base import BaseAnalyzer
from bs4 import BeautifulSoup
from Repository.metaStore import MongoMetaStore

import re

class AnalyzeForumUser(BaseAnalyzer):
    def __init__(self, domain_url: str):
        super().__init__(domain_url)
        self.meta_store = MongoMetaStore.get_instance()
        # 중복 제거를 위해 sha256+post_no, sha256+user_id 조합 저장
        self.seen_users = set()

    def targetCheck(self, page: str, sha256: str) -> bool:
        # 메타스토어에서 original request URL 확인
        domain, url = self.meta_store.get_domain_and_url(sha256) or ("", "")
        # 도메인 일치 확인
        if domain != self.domain_url:
            return False

        # "/Thread-" 로 시작하는 스레드 페이지만 다음으로 넘김
        if not url.split(domain, 1)[-1].startswith("/Thread-"):
            return False

        return True
    
    def parse(self, page: str, sha256: str, sitename: str) -> list:
        soup = BeautifulSoup(page, 'html.parser')
        results = []

        blocks = soup.select('.post__author')
        for block in blocks:
            user_el = block.select_one('.post__user-profile a')
            username = user_el.get_text(strip=True) if user_el else ''

            user_id = ''
            profile_anchor = block.select_one('a[href*="member.php?action=profile&uid"]')
            if profile_anchor:
                m = re.search(r'uid=(\d+)', profile_anchor['href'])
                if m:
                    user_id = m.group(1)

            if not user_id:
                continue

            title_el = block.select_one('.post__user-title')
            user_title = title_el.get_text(strip=True) if title_el else ''

            stats = {}
            for bit in block.select('.post__stats-bit'):
                lbl = bit.select_one('span.float_left').get_text(strip=True).rstrip(':')
                val = bit.select_one('span.float_right').get_text(strip=True)
                stats[lbl.lower()] = val
            reputation = stats.get('reputation', '')
            posts = stats.get('posts', '')
            threads = stats.get('threads', '')
            joined = stats.get('joined', '')

            avatar_el = block.select_one('.post__user-profile + a img')
            avatar_url = avatar_el['src'] if avatar_el else ''

            # 변경: awards 존재 여부 boolean으로 저장
            awards = True if block.select('.post__user-awards img') else False

            tg = ''
            tg_el = block.select_one('.socialsites__icon a[href*="t.me"]')
            if tg_el:
                tg = tg_el['href']

            key = (sha256, user_id)
            if key in self.seen_users:
                continue
            self.seen_users.add(key)

            results.append({
                'sha256': sha256,
                'domain': sitename,
                'username': username,
                'user_id': user_id,
                'user_title': user_title,
                'reputation': reputation,
                'posts': posts,
                'threads': threads,
                'joined': joined,
                'awards': awards,
                'telegram': tg,
            })

        return results