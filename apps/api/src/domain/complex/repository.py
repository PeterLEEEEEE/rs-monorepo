"""Complex 도메인 Repository"""
from typing import Optional
from sqlalchemy import text

from src.db.base_repository import BaseRepository


class ComplexRepository(BaseRepository):
    """단지 Repository - staging 스키마의 stg_complexes 테이블 조회"""

    async def search_complexes(self, query: str, limit: int = 20) -> list[dict]:
        """
        단지명으로 검색

        Args:
            query: 검색어 (단지명)
            limit: 최대 결과 수

        Returns:
            검색된 단지 목록
        """
        sql = text("""
            SELECT
                complex_id,
                complex_name,
                complex_type_name,
                total_household_count,
                use_approve_ymd,
                min_price,
                max_price
            FROM staging.stg_complexes
            WHERE complex_name ILIKE :query
            ORDER BY total_household_count DESC NULLS LAST
            LIMIT :limit
        """)
        result = await self.session.execute(
            sql,
            {"query": f"%{query}%", "limit": limit}
        )
        return [dict(row) for row in result.mappings().all()]

    async def get_complex_detail(self, complex_id: str) -> Optional[dict]:
        """
        단지 상세 정보 조회

        Args:
            complex_id: 단지 ID

        Returns:
            단지 상세 정보 또는 None
        """
        sql = text("""
            SELECT
                complex_id,
                complex_name,
                complex_type,
                complex_type_name,
                total_dong_count,
                total_household_count,
                use_approve_ymd,
                latitude,
                longitude,
                min_price,
                max_price,
                min_price_text,
                max_price_text,
                min_lease_price,
                max_lease_price
            FROM staging.stg_complexes
            WHERE complex_id = :complex_id
        """)
        result = await self.session.execute(sql, {"complex_id": complex_id})
        row = result.mappings().first()
        return dict(row) if row else None
