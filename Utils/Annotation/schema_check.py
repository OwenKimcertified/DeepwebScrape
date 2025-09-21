from contextlib import contextmanager
from functools import wraps
import pymysql
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# DB 연결
db = pymysql.connect(host="", user="", password="", db="")
cursor = db.cursor(pymysql.cursors.DictCursor)  # DictCursor로 row를 딕셔너리 형태로 받음

# 배치 제너레이터
def batch(cursor: pymysql.cursors.Cursor, batchsize: int):
    while True:
        rows = cursor.fetchmany(batchsize)
        if not rows:
            break
        yield rows

# 유효성 검사 데코레이터
def validate(schema: dict):
    def decorated(func):
        @wraps(func)
        def innermain(batched):
            valid_rows = []
            invalid_rows = []
            for row in batched:
                # 스키마 기반으로 유효성 검사
                if all(isinstance(row.get(k), v) for k, v in schema.items()):
                    valid_rows.append(row)
                else:
                    invalid_rows.append(row)
            return func(valid_rows), invalid_rows
        return innermain
    return decorated

# 삽입 컨텍스트 매니저
@contextmanager
def insert_context(db):
    try:
        yield
        db.commit()
    except Exception as e:
        db.rollback()
        raise e

# 메인 처리 함수
@validate(schema={"id": int, "name": str})  # 예시 스키마
def process_batch(rows):
    if not rows:
        return [], []
    insert_sql = "INSERT INTO test_table (id, name) VALUES (%(id)s, %(name)s)"
    failed_rows = []
    try:
        with insert_context(db):
            cursor.executemany(insert_sql, rows)
            return rows, []
    except Exception as e:
        logger.error(f"삽입 실패: {e}")
        failed_rows.extend(rows)
        return [], failed_rows

# 전체 처리 로직
def main(sql: str, batchsize: int):
    invalid_rows_all = []
    failed_rows_all = []
    try:
        cursor.execute(sql)
        for batched_rows in batch(cursor, batchsize):
            (processed_rows, failed_rows), invalid_rows = process_batch(batched_rows)
            invalid_rows_all.extend(invalid_rows)
            failed_rows_all.extend(failed_rows)
            logger.info(f"배치 처리 - 성공: {len(processed_rows)}건, 유효성 검사 실패: {len(invalid_rows)}건, 삽입 실패: {len(failed_rows)}건")
    except Exception as e:
        logger.error(f"쿼리 실행 실패: {e}")
    finally:
        logger.info(f"총 성공: {cursor.rowcount - len(invalid_rows_all) - len(failed_rows_all)}건")
        logger.info(f"총 유효성 검사 실패: {len(invalid_rows_all)}건, 데이터: {invalid_rows_all}")
        logger.info(f"총 삽입 실패: {len(failed_rows_all)}건, 데이터: {failed_rows_all}")
        cursor.close()
        db.close()





# 실행 테스트
sql = "SELECT id, name FROM source_table"  # 예시 쿼리
main(sql, batchsize=100)

    

def batch_yield_data(cursor:pymysql.cursors.Cursor, batchsize):
    while True:
        rows = cursor.fetchmany(batchsize)
        if not rows:
            break
        yield rows

def validation(schema:dict):
    def decorated(func):
        @wraps(func)
        def warppedfunc(batched_rows, *arg, **kwargs):
            valid, err = [], []
            for row in batched_rows:
                ok = True
                for col, expected in schema.items():
                    if col not in row:
                        err.append({"reason":"missing", "col":col, "row":row})
                        ok = False
                        break
                    v = row[col]
                    # None 허용 여부: expected를 튜플로 받아 처리
                    if v is not None and not isinstance(v, expected if isinstance(expected, tuple) else (expected,)):
                        err.append({"reason":"type", "col":col, "value":v, "row":row})
                        ok = False
                        break
                if ok:
                    valid.append(row)
            return func(batched_rows, *arg, **kwargs), err
        return warppedfunc
    return decorated

@contextmanager
def process():
    valid_rows = []
    err_rows = []
    yield valid_rows, err_rows 

@validation(schema = {"schema..."})
def datacheck(batched_rows):
    return batched_rows
    
conn = pymysql.connect(...)
cursor = conn.cursor()

### insert
sql = """insert into ..."""

# 조회 sql
cursor.execute("sql")
a = []
b = []
with process() as (val_rows, err_rows):
    for rows in batch_yield_data(cursor, 30000):
        valid, err = datacheck(rows)
        a.extend(valid)
        b.extend(err)
        
    try:
        if a:
            cursor.executemany(sql, [tuple(row) for row in a])
        else:
            pass
        
    except:
        raise ValueError
        # cursor.rollback()
        
    finally:
        conn.commit()
        cursor.close()
        conn.close()
        logger.info(b)