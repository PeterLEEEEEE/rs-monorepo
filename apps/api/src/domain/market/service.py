"""Market 도메인 Service"""
from typing import Optional
from logger import logger

from .repository import MarketRepository
from .dtos import (
    RegionListResponse,
    RegionItem,
    RegionPriceOverviewResponse,
    RegionPriceChange,
    RegionDetailResponse,
    MonthlyPriceItem,
)


class MarketService:
    """시장 분석 서비스"""

    def __init__(self, repository: MarketRepository):
        self.repository = repository

    async def get_region_list(self) -> RegionListResponse:
        """지역 목록 조회"""
        regions_data = await self.repository.get_region_list()

        regions = [
            RegionItem(
                region_code=r["region_code"],
                region_name=r["region_name"],
                complex_count=r["complex_count"]
            )
            for r in regions_data
        ]

        return RegionListResponse(regions=regions)

    async def get_region_price_overview(self, period: str = "3m") -> RegionPriceOverviewResponse:
        """지역별 가격 변동 개요 조회"""
        overview_data = await self.repository.get_region_price_overview(period=period)

        # 기간 라벨 변환
        period_labels = {
            "1w": "1주일",
            "1m": "1개월",
            "3m": "3개월",
            "6m": "6개월",
            "1y": "1년",
        }
        period_label = period_labels.get(period, period)

        regions = [
            RegionPriceChange(
                region_code=r["region_code"],
                region_name=r["region_name"],
                current_avg_price=r["current_avg_price"],
                prev_avg_price=r["prev_avg_price"],
                change_rate=r["change_rate"],
                trade_count=r["trade_count"],
                complex_count=r["complex_count"]
            )
            for r in overview_data
        ]

        return RegionPriceOverviewResponse(
            period=period_label,
            regions=regions
        )

    async def get_region_detail(
        self,
        region_code: str,
        months: int = 12
    ) -> Optional[RegionDetailResponse]:
        """특정 지역 상세 정보 조회"""
        detail_data = await self.repository.get_region_detail(
            region_code=region_code,
            months=months
        )

        if not detail_data:
            logger.warning(f"Region not found: {region_code}")
            return None

        price_trend = [
            MonthlyPriceItem(
                month=item["month"],
                avg_price=item["avg_price"],
                trade_count=item["trade_count"]
            )
            for item in detail_data["price_trend"]
        ]

        return RegionDetailResponse(
            region_code=detail_data["region_code"],
            region_name=detail_data["region_name"],
            complex_count=detail_data["complex_count"],
            avg_price=detail_data["avg_price"],
            trade_count=detail_data["trade_count"],
            price_trend=price_trend
        )
