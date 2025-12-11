"""Real Price 도메인 Repository"""
from typing import Optional
from datetime import date
from dateutil.relativedelta import relativedelta
from sqlalchemy import text

from src.db.base_repository import BaseRepository


class RealPriceRepository(BaseRepository):
    """실거래가 Repository - staging 스키마의 테이블 조회"""

    async def get_complex_info(self, complex_id: str) -> Optional[dict]:
        """단지 기본 정보 조회"""
        query = text("""
            SELECT
                complex_id,
                complex_name
            FROM staging.stg_complexes
            WHERE complex_id = :complex_id
        """)
        result = await self.session.execute(query, {"complex_id": complex_id})
        row = result.mappings().first()
        return dict(row) if row else None

    async def get_pyeong_list(self, complex_id: str) -> list[dict]:
        """단지의 평형 목록 조회"""
        query = text("""
            SELECT
                p.pyeong_id,
                p.pyeong_name,
                p.pyeong_name2,
                p.exclusive_area_sqm,
                p.exclusive_area_pyeong,
                COALESCE(stats.trade_count, 0) as trade_count,
                stats.latest_price,
                stats.latest_trade_date
            FROM staging.stg_pyeongs p
            LEFT JOIN (
                SELECT
                    pyeong_id,
                    COUNT(*) as trade_count,
                    (ARRAY_AGG(deal_price ORDER BY trade_date DESC))[1] as latest_price,
                    MAX(trade_date) as latest_trade_date
                FROM staging.stg_real_prices
                WHERE complex_id = :complex_id
                GROUP BY pyeong_id
            ) stats ON p.pyeong_id = stats.pyeong_id
            WHERE p.complex_id = :complex_id
            ORDER BY p.exclusive_area_pyeong
        """)
        result = await self.session.execute(query, {"complex_id": complex_id})
        return [dict(row) for row in result.mappings().all()]

    async def get_monthly_price_trend(
        self,
        complex_id: str,
        months: int = 24,
        pyeong_id: Optional[str] = None
    ) -> list[dict]:
        """
        평형별 월별 실거래가 추이 조회

        Args:
            complex_id: 단지 ID
            months: 조회 기간 (개월)
            pyeong_id: 특정 평형 필터 (선택)

        Returns:
            평형별 월별 집계 데이터
        """
        start_date = date.today() - relativedelta(months=months)

        if pyeong_id:
            query = text("""
                SELECT
                    pyeong_id,
                    TO_CHAR(trade_date, 'YYYY-MM') as month,
                    ROUND(AVG(deal_price))::INTEGER as avg_price,
                    MIN(deal_price)::INTEGER as min_price,
                    MAX(deal_price)::INTEGER as max_price,
                    COUNT(*)::INTEGER as trade_count
                FROM staging.stg_real_prices
                WHERE complex_id = :complex_id
                  AND pyeong_id = :pyeong_id
                  AND trade_date >= :start_date
                GROUP BY pyeong_id, TO_CHAR(trade_date, 'YYYY-MM')
                ORDER BY pyeong_id, month
            """)
            params = {
                "complex_id": complex_id,
                "pyeong_id": pyeong_id,
                "start_date": start_date
            }
        else:
            query = text("""
                SELECT
                    pyeong_id,
                    TO_CHAR(trade_date, 'YYYY-MM') as month,
                    ROUND(AVG(deal_price))::INTEGER as avg_price,
                    MIN(deal_price)::INTEGER as min_price,
                    MAX(deal_price)::INTEGER as max_price,
                    COUNT(*)::INTEGER as trade_count
                FROM staging.stg_real_prices
                WHERE complex_id = :complex_id
                  AND trade_date >= :start_date
                GROUP BY pyeong_id, TO_CHAR(trade_date, 'YYYY-MM')
                ORDER BY pyeong_id, month
            """)
            params = {"complex_id": complex_id, "start_date": start_date}

        result = await self.session.execute(query, params)
        return [dict(row) for row in result.mappings().all()]

    async def get_pyeong_info(self, complex_id: str, pyeong_ids: list[str]) -> dict[str, dict]:
        """
        평형 정보 조회 (벌크)

        Returns:
            {pyeong_id: {pyeong_name, pyeong_name2, ...}, ...}
        """
        if not pyeong_ids:
            return {}

        query = text("""
            SELECT
                pyeong_id,
                pyeong_name,
                pyeong_name2,
                exclusive_area_sqm,
                exclusive_area_pyeong
            FROM staging.stg_pyeongs
            WHERE complex_id = :complex_id
              AND pyeong_id = ANY(:pyeong_ids)
        """)
        result = await self.session.execute(
            query,
            {"complex_id": complex_id, "pyeong_ids": pyeong_ids}
        )
        return {row["pyeong_id"]: dict(row) for row in result.mappings().all()}
