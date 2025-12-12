"""Complex 도메인 Service"""
from typing import Optional
from logger import logger

from .repository import ComplexRepository
from .dtos import (
    ComplexSearchResponse,
    ComplexSearchItem,
    ComplexDetailResponse,
)


class ComplexService:
    """단지 서비스"""

    def __init__(self, repository: ComplexRepository):
        self.repository = repository

    async def search_complexes(self, query: str, limit: int = 20) -> ComplexSearchResponse:
        """
        단지명으로 검색

        Args:
            query: 검색어
            limit: 최대 결과 수

        Returns:
            ComplexSearchResponse
        """
        results = await self.repository.search_complexes(query, limit)

        items = [
            ComplexSearchItem(
                complex_id=row["complex_id"],
                complex_name=row["complex_name"],
                complex_type_name=row.get("complex_type_name"),
                total_household_count=row.get("total_household_count"),
                use_approve_ymd=row.get("use_approve_ymd"),
                min_price=row.get("min_price"),
                max_price=row.get("max_price"),
            )
            for row in results
        ]

        return ComplexSearchResponse(
            query=query,
            total=len(items),
            items=items
        )

    async def get_complex_detail(self, complex_id: str) -> Optional[ComplexDetailResponse]:
        """
        단지 상세 정보 조회

        Args:
            complex_id: 단지 ID

        Returns:
            ComplexDetailResponse or None
        """
        result = await self.repository.get_complex_detail(complex_id)

        if not result:
            logger.warning(f"Complex not found: {complex_id}")
            return None

        return ComplexDetailResponse(
            complex_id=result["complex_id"],
            complex_name=result["complex_name"],
            complex_type=result.get("complex_type"),
            complex_type_name=result.get("complex_type_name"),
            total_dong_count=result.get("total_dong_count"),
            total_household_count=result.get("total_household_count"),
            use_approve_ymd=result.get("use_approve_ymd"),
            latitude=float(result["latitude"]) if result.get("latitude") else None,
            longitude=float(result["longitude"]) if result.get("longitude") else None,
            min_price=result.get("min_price"),
            max_price=result.get("max_price"),
            min_price_text=result.get("min_price_text"),
            max_price_text=result.get("max_price_text"),
            min_lease_price=result.get("min_lease_price"),
            max_lease_price=result.get("max_lease_price"),
        )
