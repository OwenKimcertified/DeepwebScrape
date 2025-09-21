from ..base import BaseAnalyzer
from bs4 import BeautifulSoup
from Repository.metaStore import MongoMetaStore

import re

class AnalyzeForumPost(BaseAnalyzer):
    def __init__(self, domain_url: str):
        super().__init__(domain_url)
        self.meta_store = MongoMetaStore.get_instance()
        # 중복 제거를 위해 sha256+post_no, sha256+user_id 조합 저장
        self.seen_posts = set()


    def targetCheck(self, page: str, sha256: str) -> bool:
        # 메타스토어에서 original request URL 확인
        domain, url = self.meta_store.get_domain_and_url(sha256) or ("", "")
        # 도메인 일치 확인
        if domain != self.domain_url:
            return False

        # "/Thread-" 로 시작하는 스레드 페이지만 다음으로 넘김
        if not url.split(domain, 1)[-1].startswith("/Thread-"):
            return False

        # 포스트 및 사용자 블록이 있는지 확인
        return 'post_body' in page and 'post__author' in page


    def parse(self, page: str, sha256: str, sitename: str) -> list:
        soup = BeautifulSoup(page, 'html.parser')
        results = []

        thread_title_el = soup.select_one('.thread-info__name')
        thread_title = thread_title_el.get_text(strip=True) if thread_title_el else ''
        posts = soup.select('div[id^="post_"]')

        for post in posts:
            author_profile_link = post.select_one('.post__user-profile a')
            username = author_profile_link.get_text(strip=True) if author_profile_link else ''

            user_id = ''
            profile_link = post.select_one('a[href*="member.php?action=profile&uid"]')
            if profile_link and 'uid=' in profile_link['href']:
                uid_match = re.search(r'uid=(\d+)', profile_link['href'])
                if uid_match:
                    user_id = uid_match.group(1)

            author_title_el = post.select_one('.post__user-title')
            author_title = author_title_el.get_text(strip=True) if author_title_el else ''

            stats = {}
            for bit in post.select('.post__stats-bit'):
                lbl = bit.select_one('span.float_left').get_text(strip=True).rstrip(':')
                val = bit.select_one('span.float_right').get_text(strip=True)
                stats[lbl.lower()] = val
            reputation = stats.get('reputation', '')
            post_count = stats.get('posts', '')
            thread_count = stats.get('threads', '')
            joined = stats.get('joined', '')

            post_no_el = post.select_one('.post_head .float_right a strong')
            post_no = post_no_el.get_text(strip=True).lstrip('#') if post_no_el else ''

            date_el = post.select_one('.post_date')
            post_date = date_el.get_text(strip=True) if date_el else ''

            content_el = post.select_one('.post_body')
            content = content_el.get_text('\n', strip=True) if content_el else ''
            urls = re.findall(r'https?://\S+', content)
            emails = re.findall(r'[\w\.-]+@[\w\.-]+', content)

            sig_el = post.select_one('.signature')
            signature = sig_el.get_text('\n', strip=True) if sig_el else ''

            key = (sha256, post_no, user_id)
            if key in self.seen_posts:
                continue
            self.seen_posts.add(key)

            results.append({
                'sha256': sha256,
                'domain': sitename,
                'thread_title': thread_title,
                'post_no': post_no,
                'username': username,
                'user_id': user_id,
                'author_title': author_title,
                'reputation': reputation,
                'posts': post_count,
                'threads': thread_count,
                'joined': joined,
                'post_date': post_date,
                'content': content,
                'urls': urls,
                'emails': emails,
                'signature': signature,
            })

        return results