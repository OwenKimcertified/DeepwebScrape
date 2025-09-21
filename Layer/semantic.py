from abc import ABC, abstractmethod

class MartInterface(ABC):
    @abstractmethod
    def accept(self, transformedData):
        """마트가 통합된 관점의 데이터를 받아서 자체 처리"""
        pass

class BI_MART(MartInterface):
    pass


class ANALYZER_MART(MartInterface):
    pass


class MLDL_MART(MartInterface):
    pass


class integrate:
    """통합 데이터에서 각 마트로 뻗는 중앙 분배자
       데이터들의 출처 및 계층 확인
    """
    def __init__(self):
        self.marts = [
            BI_MART(),
            ANALYZER_MART(),
            MLDL_MART(),
            # etc ...
        ]
    
    ...

