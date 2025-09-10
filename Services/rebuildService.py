import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from collections import defaultdict

from Repository.metaStore import MongoMetaStore
from Router.domain import RawReader
from Services.analyzeService import AnalyzeService
from Services.domain import DomainAnalyzeService
from log import logger

MAX_CONCURRENCY = 4
executor = ThreadPoolExecutor(max_workers=5)


async def rebuild_analyze(sha256, domain_filter, meta_store: ..., analyze_service:AnalyzeService, 
                          domain_service:DomainAnalyzeService, stats, semaphore):
    try:
        async with semaphore:
            html = await RawReader.read_file(sha256)

        candidates = domain_service.get_target_data(sha256, html)
        has_result = False
        saved = 0

        for analyzer_type, sitename, domain_url in candidates:
            if domain_filter and domain_filter not in domain_url:
                continue

            results = await asyncio.get_event_loop().run_in_executor(
                executor,
                lambda: analyze_service.analyze(analyzer_type, domain_url, html, sha256, sitename)
            )

            if results:
                has_result = True
                saved += len(results)
                stats[analyzer_type][sitename] += len(results)
                domain_service.store_results(analyzer_type, results)
                logger.info(f"[REBUILD][{sha256}] {sitename}:{analyzer_type} → {len(results)}건")

        return 1 if has_result else 0, saved, 0

    except FileNotFoundError:
        logger.warning(f"[REBUILD][WARN] 파일 없음: {sha256}")
        return 0, 0, 0
    except Exception as e:
        logger.error(f"[REBUILD][ERROR] {sha256} 처리 실패: {e}")
        return 0, 0, 1


async def rebuild_analysis(
    sha_list: list[str] = None,
    domain_filter: str = None,
    start: datetime = None,
    end: datetime = None,
):
    meta_store = MongoMetaStore.get_instance()
    analyze_service = AnalyzeService()
    domain_service = DomainAnalyzeService(rebuild=True)

    if sha_list is None:
        assert start is not None, "[ERROR] start 날짜는 필수입니다."
        if end is None:
            end = datetime.utcnow()
        sha_list = meta_store.meta.distinct("sha256", {
            "timestamp_store": {"$gte": start, "$lt": end}
        })

    logger.info(f"[REBUILD] 재분석 대상 SHA 수: {len(sha_list)}")

    stats = defaultdict(lambda: defaultdict(int))
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)

    tasks = [
        rebuild_analyze(
            sha256, domain_filter, meta_store,
            analyze_service, domain_service,
            stats, semaphore
        ) for sha256 in sha_list
    ]

    results = await asyncio.gather(*tasks)
    count_valid = sum(x[0] for x in results)
    count_saved = sum(x[1] for x in results)
    count_error = sum(x[2] for x in results)

    logger.info("=" * 40)
    logger.info("리빌드 분석 통계 요약")
    logger.info("-" * 40)
    logger.info(f" - 전체 SHA 수               : {len(sha_list)}")
    logger.info(f" - 분석 결과 있는 SHA 수     : {count_valid}")
    logger.info(f" - 저장된 총 결과 건수       : {count_saved}")
    logger.info(f" - 예외 발생 SHA 수          : {count_error}")
    logger.info("-" * 40)
    for analyzer_type, sitename_counts in stats.items():
        for sitename, count in sitename_counts.items():
            logger.info(f" - {analyzer_type}:{sitename} → {count}건")
    logger.info("=" * 40)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=str, help="시작 날짜 예: 2023-10-01")
    parser.add_argument("--end", type=str, help="종료 날짜 예: 2023-10-02")
    parser.add_argument("--domain", type=str, default=None, help="도메인 필터링")
    args = parser.parse_args()

    start = datetime.strptime(args.start, "%Y-%m-%d") if args.start else None
    end = datetime.strptime(args.end, "%Y-%m-%d") if args.end else None

    logger.info("=== 리빌드 분석 시작 ===")
    asyncio.run(rebuild_analysis(start=start, end=end, domain_filter=args.domain))
    logger.info("=== 리빌드 분석 완료 ===")
