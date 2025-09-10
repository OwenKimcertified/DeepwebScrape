from loguru import logger
import sys, os

logger.remove()

                                     # 로그 종류 구분
mode = os.getenv("LOG_MODE", "app")  # 기본은 app 리빌드는 rebuild

logger.add(
    f"logs/{{time:YYYY-MM-DD}}_{mode}.log",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}:{function}:{line}</cyan> - <level>{message}</level>",
    level="DEBUG",
    rotation="00:00"
)

logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="DEBUG",
    colorize=True
)