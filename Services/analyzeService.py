from Interface.domain import AnalyzerType
import Analyzer.RANSOMWARE as Ransomware
import Analyzer.FORUM as Forum

class AnalyzeService:
    """도메인에 맞는 분석기 라우팅"""
        
    def create_analyzer(self, analyzer_type: AnalyzerType, domain_url: str):
        """분석기 타입에 따라 새로운 인스턴스 생성"""
        # 랜섬웨어 케이스이면
        if analyzer_type == AnalyzerType.RANSOMWARE:
            # AKIRA
            if 'akira' in domain_url:
                return Ransomware.AnalyzeAkira(domain_url)
            # CUBA
            elif "cuba" in domain_url:
                return Ransomware.AnalyzeCuba(domain_url)
            # PLAY
            elif "mbrlkbtq5" in domain_url:
                return Ransomware.AnalyzePlay(domain_url)

        elif analyzer_type == AnalyzerType.FORUM_POST:
            return Forum.AnalyzeForumPost(domain_url)
        else:
            return Forum.AnalyzeForumUser(domain_url)
        
        return None

    def analyze(self, analyzer_type, domain_url: str, html: str, sha256: str, sitename: str):
        analyzer = self.create_analyzer(analyzer_type, domain_url)
        if not analyzer:
            return None
        try:
            argcount = analyzer.targetCheck.__code__.co_argcount
            if argcount == 3:
                is_target = analyzer.targetCheck(html, sha256)
            else:
                is_target = analyzer.targetCheck(html)
        except Exception as e:
            print(f"[ERROR][{sitename}] targetCheck 실패: {e}")
            return None
        return analyzer.parse(html, sha256, sitename) if is_target else None

