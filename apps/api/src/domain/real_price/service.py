"""Real Price 도메인 Service"""
from typing import Optional
from collections import defaultdict
from logger import logger

from .repository import RealPriceRepository
from .dtos import (
    PriceTrendResponse,
    PyeongTrendItem,
    MonthlyTrendItem,
    PyeongListResponse,
    PyeongSummaryItem,
    FloorPriceResponse,
    FloorPriceItem,
)


class RealPriceService:
    """실거래가 서비스"""

    def __init__(self, repository: RealPriceRepository):
        self.repository = repository

    async def get_price_trend(
        self,
        complex_id: str,
        months: int = 24,
        pyeong_id: Optional[str] = None
    ) -> Optional[PriceTrendResponse]:
        """
        평형별 실거래가 추이 조회

        Args:
            complex_id: 단지 ID
            months: 조회 기간 (개월)
            pyeong_id: 특정 평형 필터 (선택)

        Returns:
            PriceTrendResponse or None (단지 없을 시)
        """
        # 1. 단지 정보 조회
        complex_info = await self.repository.get_complex_info(complex_id)
        if not complex_info:
            logger.warning(f"Complex not found: {complex_id}")
            return None

        # 2. 월별 추이 데이터 조회
        trend_data = await self.repository.get_monthly_price_trend(
            complex_id=complex_id,
            months=months,
            pyeong_id=pyeong_id
        )

        if not trend_data:
            # 거래 데이터가 없어도 단지 정보는 반환
            return PriceTrendResponse(
                complex_id=complex_id,
                complex_name=complex_info["complex_name"],
                pyeongs=[]
            )

        # 3. 평형 정보 조회
        pyeong_ids = list(set(row["pyeong_id"] for row in trend_data))
        pyeong_info_map = await self.repository.get_pyeong_info(complex_id, pyeong_ids)

        # 4. 평형별로 데이터 그룹핑
        pyeong_trends: dict[str, list[dict]] = defaultdict(list)
        for row in trend_data:
            pyeong_trends[row["pyeong_id"]].append(row)

        # 5. 응답 구성
        pyeongs = []
        for pid, monthly_data in pyeong_trends.items():
            pyeong_info = pyeong_info_map.get(pid, {})

            trend_items = [
                MonthlyTrendItem(
                    month=item["month"],
                    avg_price=item["avg_price"],
                    min_price=item["min_price"],
                    max_price=item["max_price"],
                    trade_count=item["trade_count"]
                )
                for item in monthly_data
            ]

            pyeongs.append(PyeongTrendItem(
                pyeong_id=pid,
                pyeong_name=pyeong_info.get("pyeong_name"),
                pyeong_name2=pyeong_info.get("pyeong_name2"),
                exclusive_area_sqm=pyeong_info.get("exclusive_area_sqm"),
                exclusive_area_pyeong=pyeong_info.get("exclusive_area_pyeong"),
                trend=trend_items
            ))

        # 전용면적 기준 정렬
        pyeongs.sort(key=lambda x: x.exclusive_area_pyeong or 0)

        return PriceTrendResponse(
            complex_id=complex_id,
            complex_name=complex_info["complex_name"],
            pyeongs=pyeongs
        )

    async def get_pyeong_list(self, complex_id: str) -> Optional[PyeongListResponse]:
        """
        단지의 평형 목록 조회

        Args:
            complex_id: 단지 ID

        Returns:
            PyeongListResponse or None (단지 없을 시)
        """
        # 1. 단지 정보 조회
        complex_info = await self.repository.get_complex_info(complex_id)
        if not complex_info:
            logger.warning(f"Complex not found: {complex_id}")
            return None

        # 2. 평형 목록 조회
        pyeong_list = await self.repository.get_pyeong_list(complex_id)

        pyeongs = [
            PyeongSummaryItem(
                pyeong_id=row["pyeong_id"],
                pyeong_name=row.get("pyeong_name"),
                pyeong_name2=row.get("pyeong_name2"),
                exclusive_area_sqm=row.get("exclusive_area_sqm"),
                exclusive_area_pyeong=row.get("exclusive_area_pyeong"),
                trade_count=row["trade_count"],
                latest_price=row.get("latest_price"),
                latest_trade_date=row.get("latest_trade_date")
            )
            for row in pyeong_list
        ]

        return PyeongListResponse(
            complex_id=complex_id,
            complex_name=complex_info["complex_name"],
            pyeongs=pyeongs
        )

    async def get_floor_price(
        self,
        complex_id: str,
        months: int = 24,
        pyeong_id: Optional[str] = None
    ) -> Optional[FloorPriceResponse]:
        """
        층수별 가격 데이터 조회 (산점도용)

        Args:
            complex_id: 단지 ID
            months: 조회 기간 (개월)
            pyeong_id: 특정 평형 필터 (선택)

        Returns:
            FloorPriceResponse or None (단지 없을 시)
        """
        # 1. 단지 정보 조회
        complex_info = await self.repository.get_complex_info(complex_id)
        if not complex_info:
            logger.warning(f"Complex not found: {complex_id}")
            return None

        # 2. 층수별 가격 데이터 조회
        floor_data = await self.repository.get_floor_price_data(
            complex_id=complex_id,
            months=months,
            pyeong_id=pyeong_id
        )

        trades = [
            FloorPriceItem(
                floor=row["floor"],
                deal_price=row["deal_price"],
                trade_date=row["trade_date"],
                pyeong_id=row["pyeong_id"],
                pyeong_name2=row.get("pyeong_name2")
            )
            for row in floor_data
        ]

        return FloorPriceResponse(
            complex_id=complex_id,
            complex_name=complex_info["complex_name"],
            trades=trades
        )
