from typing import Optional
from datetime import date, timedelta
from langchain_core.tools import tool
from sqlalchemy import text


class MarketTools:
    """Market Agent tools for real price analysis."""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    def get_tools(self) -> list:
        """Return list of tools with session factory bound."""

        @tool
        async def get_real_prices(
            complex_id: str,
            pyeong_id: Optional[str] = None,
            trade_type: Optional[str] = None,
            start_date: Optional[str] = None,
            end_date: Optional[str] = None,
            limit: int = 20,
        ) -> list[dict]:
            """실거래가 내역 조회

            Args:
                complex_id: 단지 ID
                pyeong_id: 평형 ID (선택)
                trade_type: 거래유형 - 매매, 전세 (선택)
                start_date: 조회 시작일 YYYY-MM-DD (선택)
                end_date: 조회 종료일 YYYY-MM-DD (선택)
                limit: 결과 수 제한

            Returns:
                실거래 내역 목록
            """
            conditions = ["complex_id = :complex_id"]
            params = {"complex_id": complex_id}

            if pyeong_id:
                conditions.append("pyeong_id = :pyeong_id")
                params["pyeong_id"] = pyeong_id

            if trade_type:
                conditions.append("trade_type = :trade_type")
                params["trade_type"] = trade_type

            if start_date:
                conditions.append("trade_date >= :start_date")
                params["start_date"] = start_date

            if end_date:
                conditions.append("trade_date <= :end_date")
                params["end_date"] = end_date

            where_clause = " AND ".join(conditions)
            query = text(f"""
                SELECT
                    complex_id,
                    pyeong_id,
                    floor,
                    trade_date,
                    deal_price,
                    trade_type,
                    area_m,
                    area_p,
                    exclusive_area_sqm,
                    exclusive_area_pyeong
                FROM staging.stg_real_prices
                WHERE {where_clause}
                ORDER BY trade_date DESC
                LIMIT :limit
            """)
            params["limit"] = limit

            async with self.session_factory() as session:
                result = await session.execute(query, params)
                rows = result.fetchall()
                return [dict(row._mapping) for row in rows]

        @tool
        async def get_price_stats(
            complex_id: str,
            pyeong_id: Optional[str] = None,
            months: int = 12,
        ) -> dict:
            """가격 통계 조회 (평균가, 최고가, 최저가, 거래건수)

            Args:
                complex_id: 단지 ID
                pyeong_id: 평형 ID (선택)
                months: 조회 기간 (개월, 기본 12개월)

            Returns:
                가격 통계 정보
            """
            conditions = [
                "complex_id = :complex_id",
                "trade_date >= :start_date"
            ]
            params = {
                "complex_id": complex_id,
                "start_date": date.today() - timedelta(days=months * 30),
            }

            if pyeong_id:
                conditions.append("pyeong_id = :pyeong_id")
                params["pyeong_id"] = pyeong_id

            where_clause = " AND ".join(conditions)
            query = text(f"""
                SELECT
                    COUNT(*) as trade_count,
                    AVG(deal_price) as avg_price,
                    MAX(deal_price) as max_price,
                    MIN(deal_price) as min_price,
                    MIN(trade_date) as period_start,
                    MAX(trade_date) as period_end
                FROM staging.stg_real_prices
                WHERE {where_clause}
            """)

            async with self.session_factory() as session:
                result = await session.execute(query, params)
                row = result.fetchone()
                if row:
                    return dict(row._mapping)
                return {"error": "통계 데이터를 찾을 수 없습니다."}

        @tool
        async def get_price_trend(
            complex_id: str,
            pyeong_id: Optional[str] = None,
            months: int = 24,
        ) -> list[dict]:
            """시세 추이 분석 (월별 평균가 추이)

            Args:
                complex_id: 단지 ID
                pyeong_id: 평형 ID (선택)
                months: 조회 기간 (개월, 기본 24개월)

            Returns:
                월별 시세 추이
            """
            conditions = [
                "complex_id = :complex_id",
                "trade_date >= :start_date"
            ]
            params = {
                "complex_id": complex_id,
                "start_date": date.today() - timedelta(days=months * 30),
            }

            if pyeong_id:
                conditions.append("pyeong_id = :pyeong_id")
                params["pyeong_id"] = pyeong_id

            where_clause = " AND ".join(conditions)
            query = text(f"""
                SELECT
                    DATE_TRUNC('month', trade_date) as month,
                    COUNT(*) as trade_count,
                    AVG(deal_price) as avg_price,
                    MAX(deal_price) as max_price,
                    MIN(deal_price) as min_price
                FROM staging.stg_real_prices
                WHERE {where_clause}
                GROUP BY DATE_TRUNC('month', trade_date)
                ORDER BY month DESC
            """)

            async with self.session_factory() as session:
                result = await session.execute(query, params)
                rows = result.fetchall()
                return [dict(row._mapping) for row in rows]

        return [get_real_prices, get_price_stats, get_price_trend]
