from Interface.domain import AnalyzerType
from Repository.storeResult import *
from Router.domain import DomainClassifier

class DomainAnalyzeService:
    def __init__(self, rebuild: bool = False):
        self.ransom_store = RansomwareResultStore(rebuild=rebuild)
        self.user_store = ForumUserResultStore(rebuild=rebuild)
        self.post_store = ForumPostResultStore(rebuild=rebuild)

    def get_target_data(self, sha256, html) -> list[tuple]:
        return DomainClassifier.get_analyze_target(sha256, html)
    
    def update_stats(self, stats, analyzer_type, sitename, count):
        if analyzer_type not in stats:
            stats[analyzer_type] = {}
        stats[analyzer_type][sitename] = stats[analyzer_type].get(sitename, 0) + count

    def store_results(self, analyzer_type, results):
        # 타입별로 적절한 저장소에 저장
        if analyzer_type == AnalyzerType.RANSOMWARE:
            self.ransom_store.store_batch(results)
        elif analyzer_type == AnalyzerType.FORUM_USER:
            self.user_store.store_batch(results)
        elif analyzer_type == AnalyzerType.FORUM_POST:
            self.post_store.store_batch(results)

    def process_analysis(
        self,
        analyze_service,
        sha256,
        html,
        analyzer_type,
        domain_url,
        sitename
    ):
        results = analyze_service.analyze(
            analyzer_type, domain_url, html, sha256, sitename
        )
        if not results:
            return