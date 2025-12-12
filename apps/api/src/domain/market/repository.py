"""Market 도메인 Repository"""
from typing import Optional
from datetime import date
from dateutil.relativedelta import relativedelta
from sqlalchemy import text

from src.db.base_repository import BaseRepository


class MarketRepository(BaseRepository):
    """시장 분석 Repository - staging 스키마의 테이블 조회"""

    async def get_region_list(self) -> list[dict]:
        """지역 목록 및 단지 수 조회"""
        query = text("""
            SELECT
                r.region_id,
                r.region_code,
                r.region_name,
                COUNT(DISTINCT c.complex_id) as complex_count
            FROM staging.stg_regions r
            LEFT JOIN staging.stg_complexes c
                ON LEFT(c.address_id, 5) || '00000' = r.region_id
            GROUP BY r.region_id, r.region_code, r.region_name
            ORDER BY r.region_name
        """)
        result = await self.session.execute(query)
        rows = result.mappings().all()

        return [dict(row) for row in rows]

    async def get_region_price_overview(self, months: int = 3) -> list[dict]:
        """
        지역별 가격 변동 개요 조회

        Args:
            months: 비교 기간 (기본 3개월)

        Returns:
            지역별 현재/이전 평균가, 변동률
        """
        current_start = date.today() - relativedelta(months=months)
        prev_start = current_start - relativedelta(months=months)
        prev_end = current_start - relativedelta(days=1)

        query = text("""
            WITH region_prices AS (
                SELECT
                    reg.region_code,
                    reg.region_name,
                    rp.deal_price,
                    rp.trade_date
                FROM staging.stg_real_prices rp
                JOIN staging.stg_complexes c ON rp.complex_id = c.complex_id
                JOIN staging.stg_regions reg ON LEFT(c.address_id, 5) || '00000' = reg.region_id
                WHERE rp.trade_date >= :prev_start
            ),
            current_period AS (
                SELECT
                    region_code,
                    region_name,
                    ROUND(AVG(deal_price))::INTEGER as avg_price,
                    COUNT(*) as trade_count
                FROM region_prices
                WHERE trade_date >= :current_start
                GROUP BY region_code, region_name
            ),
            prev_period AS (
                SELECT
                    region_code,
                    ROUND(AVG(deal_price))::INTEGER as avg_price
                FROM region_prices
                WHERE trade_date >= :prev_start AND trade_date <= :prev_end
                GROUP BY region_code
            )
            SELECT
                c.region_code,
                c.region_name,
                c.avg_price as current_avg_price,
                p.avg_price as prev_avg_price,
                c.trade_count,
                CASE
                    WHEN p.avg_price > 0 AND c.avg_price IS NOT NULL
                    THEN ROUND(((c.avg_price - p.avg_price)::NUMERIC / p.avg_price * 100), 2)
                    ELSE NULL
                END as change_rate
            FROM current_period c
            LEFT JOIN prev_period p ON c.region_code = p.region_code
            ORDER BY change_rate DESC NULLS LAST
        """)

        result = await self.session.execute(query, {
            "current_start": current_start,
            "prev_start": prev_start,
            "prev_end": prev_end
        })
        rows = result.mappings().all()

        return [
            {
                "region_code": row["region_code"],
                "region_name": row["region_name"],
                "current_avg_price": row["current_avg_price"],
                "prev_avg_price": row["prev_avg_price"],
                "change_rate": float(row["change_rate"]) if row["change_rate"] is not None else None,
                "trade_count": row["trade_count"] or 0
            }
            for row in rows
        ]

    async def get_region_detail(
        self,
        region_code: str,
        months: int = 12
    ) -> Optional[dict]:
        """
        특정 지역 상세 정보 조회

        Args:
            region_code: 지역 코드 (예: gangnam)
            months: 조회 기간 (기본 12개월)

        Returns:
            지역 상세 정보 (단지 수, 평균가, 월별 추이 등)
        """
        start_date = date.today() - relativedelta(months=months)

        # 지역 정보 및 단지 수 조회
        region_query = text("""
            SELECT
                r.region_id,
                r.region_code,
                r.region_name,
                COUNT(DISTINCT c.complex_id) as complex_count
            FROM staging.stg_regions r
            LEFT JOIN staging.stg_complexes c
                ON LEFT(c.address_id, 5) || '00000' = r.region_id
            WHERE r.region_code = :region_code
            GROUP BY r.region_id, r.region_code, r.region_name
        """)
        region_result = await self.session.execute(
            region_query,
            {"region_code": region_code}
        )
        region_row = region_result.mappings().first()

        if not region_row:
            return None

        region_id = region_row["region_id"]
        region_name = region_row["region_name"]
        complex_count = region_row["complex_count"]

        # 월별 가격 추이 조회
        trend_query = text("""
            SELECT
                TO_CHAR(rp.trade_date, 'YYYY-MM') as month,
                ROUND(AVG(rp.deal_price))::INTEGER as avg_price,
                COUNT(*) as trade_count
            FROM staging.stg_real_prices rp
            JOIN staging.stg_complexes c ON rp.complex_id = c.complex_id
            WHERE LEFT(c.address_id, 5) || '00000' = :region_id
              AND rp.trade_date >= :start_date
            GROUP BY TO_CHAR(rp.trade_date, 'YYYY-MM')
            ORDER BY month
        """)
        trend_result = await self.session.execute(
            trend_query,
            {"region_id": region_id, "start_date": start_date}
        )
        trend_rows = trend_result.mappings().all()

        price_trend = [
            {
                "month": row["month"],
                "avg_price": row["avg_price"],
                "trade_count": row["trade_count"]
            }
            for row in trend_rows
        ]

        # 전체 평균가 및 거래 건수
        total_avg_price = None
        total_trade_count = 0
        if price_trend:
            total_trade_count = sum(item["trade_count"] for item in price_trend)
            weighted_sum = sum(
                item["avg_price"] * item["trade_count"]
                for item in price_trend
            )
            total_avg_price = weighted_sum // total_trade_count if total_trade_count > 0 else None

        return {
            "region_code": region_code,
            "region_name": region_name,
            "complex_count": complex_count,
            "avg_price": total_avg_price,
            "trade_count": total_trade_count,
            "price_trend": price_trend
        }
