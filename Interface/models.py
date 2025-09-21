from dataclasses import dataclass, asdict, field
from datetime import datetime

@dataclass
class RansomwareResult:
    sha256: str
    sitename: str
    company: str
    description: str
    link: str = ""
    timestamp: datetime = None
    _id: int = field(default=None)
      
    def to_dict(self) -> dict:
        return asdict(self)
    
@dataclass
class ForumPostResult:
    sha256: str
    domain: str
    thread_title: str
    post_no: str
    username: str
    user_id: str
    author_title: str
    reputation: str
    posts: str
    threads: str
    joined: str
    post_date: str
    content: str
    urls: list
    emails: list
    signature: str
    timestamp: datetime = None
    _id: int = field(default=None)
    
    def to_dict(self) -> dict:
        return asdict(self)

@dataclass
class ForumUserResult:
    sha256: str
    domain: str
    username: str
    user_id: str
    user_title: str
    reputation: str
    posts: str
    threads: str
    joined: str
    awards: bool
    telegram: str
    timestamp: datetime = None
    _id: int = field(default=None)

    def to_dict(self) -> dict:
        return asdict(self)