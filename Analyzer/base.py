

class BaseAnalyzer:
    def __init__(self, domain_url: str):
        self.domain_url = domain_url

    def targetCheck(self, page: str) -> bool:
        raise NotImplementedError

    def parse(self, page: str, sha256: str, sitename: str) -> list:
        raise NotImplementedError