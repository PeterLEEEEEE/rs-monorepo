from airflow.sdk import dag
from pendulum import datetime, duration

from common_tasks import get_target_complex_ids_task, chunk_complex_ids
from operators.api_to_postgres_ops import ComplexDetailPostgresOperator


@dag(
    dag_id="dags_complex_price_weekly",
    start_date=datetime(2025, 1, 1, tz="Asia/Seoul"),
    schedule="0 3 * * 0",  # 매주 일요일 새벽 3시
    catchup=False,
    tags=["realestate", "price", "weekly"],
    description="단지 가격 정보 주간 업데이트 (세대수 500 이상)",
)
def complex_price_weekly_dag():
    """
    단지 가격 정보 주간 업데이트 DAG

    - totalHouseholdCount >= 500인 단지 대상
    - minPrice, maxPrice, minLeasePrice, maxLeasePrice 등 업데이트
    - 매주 일요일 새벽 3시 실행
    """

    # 1. 세대수 500 이상인 단지 ID 조회
    complex_ids = get_target_complex_ids_task(household_count=500)

    # 2. 10개씩 청크로 나눔
    id_chunks = chunk_complex_ids(complex_ids, chunk_size=10)

    # 3. 단지 상세정보 수집 (동적 Task Mapping)
    fetch_details = ComplexDetailPostgresOperator.partial(
        task_id="fetch_complex_details",
        postgres_conn_id="postgres_default",
        sleep_min_sec=2,
        sleep_max_sec=5,
        retries=3,
        retry_delay=duration(minutes=5),
    ).expand(complex_nos=id_chunks)

    # 순차 실행
    complex_ids >> id_chunks >> fetch_details


complex_price_weekly_dag()
