from typing import Optional
from datetime import date, timedelta
from langchain_core.tools import tool
from sqlalchemy import text


class ComparisonTools:
    """Comparison Agent tools for comparing complexes."""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    def get_tools(self) -> list:
        """Return list of tools with session factory bound."""

        @tool
        async def compare_complexes(complex_ids: list[str]) -> list[dict]:
            """여러 단지의 기본 정보 비교

            Args:
                complex_ids: 비교할 단지 ID 목록

            Returns:
                단지별 비교 정보
            """
            if not complex_ids or len(complex_ids) < 2:
                return {"error": "비교를 위해 최소 2개 이상의 단지 ID가 필요합니다."}

            placeholders = ", ".join([f":id_{i}" for i in range(len(complex_ids))])
            params = {f"id_{i}": cid for i, cid in enumerate(complex_ids)}

            query = text(f"""
                SELECT
                    complex_no,
                    payload->>'complexName' as complex_name,
                    payload->>'totalDongCount' as dong_count,
                    payload->>'totalHouseHoldCount' as household_count,
                    payload->>'useApproveYmd' as approve_date,
                    payload->>'minPrice' as min_price,
                    payload->>'maxPrice' as max_price,
                    payload->>'minPriceByLetter' as min_price_letter,
                    payload->>'maxPriceByLetter' as max_price_letter,
                    payload->>'minLeasePrice' as min_lease_price,
                    payload->>'maxLeasePrice' as max_lease_price,
                    payload->>'minLeasePriceByLetter' as min_lease_letter,
                    payload->>'maxLeasePriceByLetter' as max_lease_letter,
                    payload->>'minArea' as min_area,
                    payload->>'maxArea' as max_area,
                    payload->'realPrice' as recent_real_price,
                    payload->>'latitude' as latitude,
                    payload->>'longitude' as longitude
                FROM raw.complex_details
                WHERE complex_no IN ({placeholders})
            """)

            async with self.session_factory() as session:
                result = await session.execute(query, params)
                rows = result.fetchall()
                return [dict(row._mapping) for row in rows]

        @tool
        async def compare_prices(
            complex_ids: list[str],
            min_area: Optional[float] = None,
            max_area: Optional[float] = None,
            months: int = 12,
        ) -> list[dict]:
            """여러 단지의 실거래가 비교 (동일 평형대 기준)

            Args:
                complex_ids: 비교할 단지 ID 목록
                min_area: 최소 전용면적 (㎡)
                max_area: 최대 전용면적 (㎡)
                months: 조회 기간 (개월, 기본 12개월)

            Returns:
                단지별 가격 통계 비교
            """
            if not complex_ids or len(complex_ids) < 2:
                return {"error": "비교를 위해 최소 2개 이상의 단지 ID가 필요합니다."}

            placeholders = ", ".join([f":id_{i}" for i in range(len(complex_ids))])
            params = {f"id_{i}": cid for i, cid in enumerate(complex_ids)}
            params["start_date"] = date.today() - timedelta(days=months * 30)

            conditions = [
                f"complex_id IN ({placeholders})",
                "trade_date >= :start_date"
            ]

            if min_area:
                conditions.append("exclusive_area_sqm >= :min_area")
                params["min_area"] = min_area

            if max_area:
                conditions.append("exclusive_area_sqm <= :max_area")
                params["max_area"] = max_area

            where_clause = " AND ".join(conditions)
            query = text(f"""
                SELECT
                    complex_id,
                    COUNT(*) as trade_count,
                    AVG(deal_price) as avg_price,
                    MAX(deal_price) as max_price,
                    MIN(deal_price) as min_price,
                    AVG(exclusive_area_sqm) as avg_area,
                    MIN(trade_date) as period_start,
                    MAX(trade_date) as period_end
                FROM staging.stg_real_prices
                WHERE {where_clause}
                GROUP BY complex_id
                ORDER BY avg_price DESC
            """)

            async with self.session_factory() as session:
                result = await session.execute(query, params)
                rows = result.fetchall()
                return [dict(row._mapping) for row in rows]

        return [compare_complexes, compare_prices]
