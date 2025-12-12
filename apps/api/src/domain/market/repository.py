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

    async def get_region_price_overview(self, period: str = "3m") -> list[dict]:
        """
        지역별 가격 변동 개요 조회 (단지별 상승률의 평균)

        Args:
            period: 비교 기간 (1w: 1주일, 1m: 1개월, 3m: 3개월, 6m: 6개월, 1y: 1년)

        Returns:
            지역별 현재/이전 평균가, 변동률 (단지별 상승률 평균)
        """
        # 기간 파싱
        period_map = {
            "1w": relativedelta(weeks=1),
            "1m": relativedelta(months=1),
            "3m": relativedelta(months=3),
            "6m": relativedelta(months=6),
            "1y": relativedelta(years=1),
        }
        delta = period_map.get(period, relativedelta(months=3))

        current_start = date.today() - delta
        prev_start = current_start - delta
        prev_end = current_start - relativedelta(days=1)

        query = text("""
            WITH complex_prices AS (
                -- 단지별 현재/이전 기간 평균가 계산
                SELECT
                    reg.region_code,
                    reg.region_name,
                    rp.complex_id,
                    ROUND(AVG(CASE WHEN rp.trade_date >= :current_start THEN rp.deal_price END))::INTEGER as current_price,
                    ROUND(AVG(CASE WHEN rp.trade_date >= :prev_start AND rp.trade_date <= :prev_end THEN rp.deal_price END))::INTEGER as prev_price,
                    COUNT(CASE WHEN rp.trade_date >= :current_start THEN 1 END) as current_trade_count
                FROM staging.stg_real_prices rp
                JOIN staging.stg_complexes c ON rp.complex_id = c.complex_id
                JOIN staging.stg_regions reg ON LEFT(c.address_id, 5) || '00000' = reg.region_id
                WHERE rp.trade_date >= :prev_start
                GROUP BY reg.region_code, reg.region_name, rp.complex_id
                HAVING COUNT(CASE WHEN rp.trade_date >= :current_start THEN 1 END) > 0
            ),
            complex_change_rates AS (
                -- 단지별 상승률 계산
                SELECT
                    region_code,
                    region_name,
                    complex_id,
                    current_price,
                    prev_price,
                    current_trade_count,
                    CASE
                        WHEN prev_price > 0 AND current_price IS NOT NULL
                        THEN ((current_price - prev_price)::NUMERIC / prev_price * 100)
                        ELSE NULL
                    END as change_rate
                FROM complex_prices
            )
            SELECT
                region_code,
                region_name,
                ROUND(AVG(current_price))::INTEGER as current_avg_price,
                ROUND(AVG(prev_price))::INTEGER as prev_avg_price,
                SUM(current_trade_count)::INTEGER as trade_count,
                COUNT(DISTINCT complex_id)::INTEGER as complex_count,
                ROUND(AVG(change_rate), 2) as change_rate
            FROM complex_change_rates
            GROUP BY region_code, region_name
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
                "trade_count": row["trade_count"] or 0,
                "complex_count": row["complex_count"] or 0
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
