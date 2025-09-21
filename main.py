import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

from Repository.metaStore import MongoMetaStore
from Router.domain import RawReader
from Services.analyzeService import AnalyzeService
from Services.domain import DomainAnalyzeService
from Interface.domain import AnalyzerType
from log import logger

MAX_CONCURRENCY = 4
executor = ThreadPoolExecutor(max_workers = 4)

async def analyze_one_sha256(
    sha256: str,
    meta_store: MongoMetaStore,
    analyze_service: AnalyzeService,
    domain_router: DomainAnalyzeService,
    stat_counter: dict,
    batch_storage: dict,
    semaphore: asyncio.Semaphore
) -> tuple[int, int]:
    """
    단일 SHA256 HTML 파일을 분석하고 결과를 저장소에 누적합니다.

    Returns:
        tuple[int, int]: (성공 여부, 예외 발생 여부)
            - (1, 0): 분석 성공
            - (0, 1): 처리 실패 (예외 발생)
            - (0, 0): 파일 없음 or 분석 대상 아님
    """

    try:
        async with semaphore:
            html = await RawReader.read_file(sha256)

        # 도메인 정보 후보군 분류
        which_analyzers = domain_router.get_target_data(sha256, html)

        analysis_success = False

        for analyzer_type, sitename, domain_url in which_analyzers:
            # 코루틴이 실행한 이벤트 루프 get, 쓰레드 풀에 delegate, 중단점으로 동시성 처리
            results = await asyncio.get_event_loop().run_in_executor(
                executor,
                lambda: analyze_service.analyze(analyzer_type, domain_url, html, sha256, sitename)
            )

            if not results:
                continue

            analysis_success = True
            logger.info(f"[+] {sha256} 분석 성공 → {sitename}:{analyzer_type} → {len(results)}건")

            # 메타 정보에서 연관 문서 존재 확인
            meta_doc = meta_store.meta.find_one({"sha256": sha256}, {"tag.related": 1})
            if meta_doc and meta_doc.get("tag", {}).get("related"):
                logger.warning(f"[!] 연관 문서 존재: {sha256} → {len(meta_doc['tag']['related'])}건")

            # 통계 및 결과 저장소 누적
            stat_counter[analyzer_type][sitename] += len(results)
            batch_storage[analyzer_type].extend(results)

        return (1, 0) if analysis_success else (0, 0)

    except FileNotFoundError:
        logger.warning(f"[WARN] 파일 없음: {sha256}")
        return (0, 0)

    except Exception as e:
        logger.error(f"[ERROR] 처리 실패: {sha256} → {str(e)}")
        return (0, 1)

async def batch_analysis(start: datetime, end: datetime):
    logger.info(f"[BATCH] 분석 시간대: {start} ~ {end}")
    meta_store = MongoMetaStore.get_instance()
    analyze_service = AnalyzeService()
    domain_service = DomainAnalyzeService()

    sha_list = meta_store.meta.distinct("sha256", {
        "timestamp_store": {"$gte": start, "$lt": end}
    })
    logger.info(f"[INFO] 대상 파일 수: {len(sha_list)}")

    result_stats = {
        AnalyzerType.RANSOMWARE: {"AKIRA": 0, "Cuba": 0, "PLAY": 0},
        AnalyzerType.FORUM_USER: {"Breached": 0},
        AnalyzerType.FORUM_POST: {"Breached": 0},
    }

    batch_results = {
        AnalyzerType.RANSOMWARE: [],
        AnalyzerType.FORUM_USER: [],
        AnalyzerType.FORUM_POST: [],
    }

    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
    tasks = [
        analyze_one_sha256(
            sha, meta_store, analyze_service, domain_service,
            result_stats, batch_results, semaphore
        ) for sha in sha_list
    ]

    results = await asyncio.gather(*tasks)
    count_valid = sum(r[0] for r in results)
    count_errors = sum(r[1] for r in results)

    count_saved = 0
    for analyzer_type, results in batch_results.items():
        count_saved += len(results)
        domain_service.store_results(analyzer_type, results)

    logger.info("=" * 40)
    logger.info("배치 단위 분석 집계")
    logger.info("-" * 40)
    logger.info(f" - 전체 처리한 파일 수             : {len(sha_list)}")
    logger.info(f" - 유효 분석 파일 수               : {count_valid}")
    logger.info(f" - 분석 후 저장된 총 rows          : {count_saved}")
    logger.info(f" - 분석 중 예외 발생한 파일 수     : {count_errors}")
    logger.info("-" * 40)
    for analyzer_type, site_stats in result_stats.items():
        for sitename, count in site_stats.items():
            logger.info(f" - {analyzer_type}:{sitename} -> {count}건")
    logger.info("=" * 40)


def run_main():
    meta = MongoMetaStore.get_instance().meta
    first_doc = meta.find_one(sort=[("timestamp_store", 1)])
    last_doc = meta.find_one(sort=[("timestamp_store", -1)])

    if not first_doc or not last_doc:
        logger.warning("메타데이터에 분석할 타임스탬프 없음")
        return

    start_time = first_doc["timestamp_store"].replace(minute=0, second=0, microsecond=0)
    end_time = last_doc["timestamp_store"].replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)

    async def run():
        current = start_time
        while current < end_time:
            await batch_analysis(current, current + timedelta(hours=1))
            current += timedelta(hours=1)

    asyncio.run(run())


if __name__ == "__main__":
    logger.info("=== 1시간 단위 전체 분석 시작 ===")
    run_main()
    logger.info("=== 전체 배치 완료 ===")