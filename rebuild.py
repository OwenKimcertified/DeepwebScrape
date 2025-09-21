import os ### 위치 변경 시 로그 파일 덮임
os.environ["LOG_MODE"] = "rebuild"

from Services.rebuildService import rebuild_analysis  
from log import logger
from datetime import datetime
import asyncio, argparse, sys

def read_sha_list_from_dir(directory: str) -> list[str]:
    if not os.path.isdir(directory):
        print(f"[ERROR] 디렉토리 없음: {directory}")
        sys.exit(1)
    sha_list = []
    for fname in os.listdir(directory):
        full_path = os.path.join(directory, fname)
        if os.path.isfile(full_path):
            sha_list.append(fname.strip())
    return sha_list


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="재분석을 위한 리빌드 파이프라인",
        epilog=(
            "\n사용 예시:\n" 
            "  디렉토리 기준:   python rebuild.py RebuildDir\n"
            "  날짜 기준:       python rebuild.py --start 2023-10-01\n"
            "  도메인 + 날짜:   python rebuild.py --domain akira --start 2023-11-01\n"
        ),
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument("sha_dir", nargs="?", metavar="sha_dir",
                        help="재분석할 sha256 디렉토리 (예: RebuildDir)")

    parser.add_argument("--domain", type=str, metavar="DOMAIN",
                        help="도메인 필터 (예: akira, cuba 등)")

    parser.add_argument("--start", type=str, metavar="START",
                        help="시작 날짜 (형식: YYYY-MM-DD)")

    parser.add_argument("--end", type=str, metavar="END",
                        help="종료 날짜 (형식: YYYY-MM-DD, 생략 가능)")

    args = parser.parse_args()

    async def main():
        if args.sha_dir:
            sha_list = read_sha_list_from_dir(args.sha_dir)
            await rebuild_analysis(sha_list=sha_list, domain_filter=args.domain)

        elif args.start:
            try:
                start_dt = datetime.fromisoformat(args.start)
                end_dt = datetime.fromisoformat(args.end) if args.end else None
            except ValueError:
                print("[ERROR] 날짜 형식은 YYYY-MM-DD여야 합니다.")
                sys.exit(1)

            await rebuild_analysis(start=start_dt, end=end_dt, domain_filter=args.domain)

        else:
            print("[ERROR] 디렉토리 인자 또는 --start 중 하나는 반드시 지정해야 합니다.")
            parser.print_help()
            sys.exit(1)

    logger.info("=== 리빌드 분석 시작 ===")
    asyncio.run(main())
    logger.info("=== 리빌드 분석 완료 ===")