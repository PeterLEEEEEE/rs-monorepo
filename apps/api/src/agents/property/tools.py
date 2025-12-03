from typing import Optional
from langchain_core.tools import tool
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class PropertyTools:
    """Property Agent tools for searching articles and complex info."""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    def get_tools(self) -> list:
        """Return list of tools with session factory bound."""

        @tool
        async def search_articles(
            complex_name: Optional[str] = None,
            min_area: Optional[int] = None,
            max_area: Optional[int] = None,
            trade_type: Optional[str] = None,
            direction: Optional[str] = None,
            min_price: Optional[int] = None,
            max_price: Optional[int] = None,
            limit: int = 10,
        ) -> list[dict]:
            """매물 검색

            Args:
                complex_name: 단지명 (예: 헬리오시티, 서초힐스)
                min_area: 최소 전용면적 (㎡)
                max_area: 최대 전용면적 (㎡)
                trade_type: 거래유형 (매매, 전세, 월세)
                direction: 향 (남향, 동향 등)
                min_price: 최소 가격 (만원 단위)
                max_price: 최대 가격 (만원 단위)
                limit: 결과 수 제한

            Returns:
                매물 목록
            """
            conditions = ["expire_at > NOW()"]
            params = {}

            if complex_name:
                conditions.append("payload->>'articleName' ILIKE :complex_name")
                params["complex_name"] = f"%{complex_name}%"

            if min_area:
                conditions.append("(payload->>'area2')::int >= :min_area")
                params["min_area"] = min_area

            if max_area:
                conditions.append("(payload->>'area2')::int <= :max_area")
                params["max_area"] = max_area

            if trade_type:
                conditions.append("payload->>'tradeTypeName' = :trade_type")
                params["trade_type"] = trade_type

            if direction:
                conditions.append("payload->>'direction' ILIKE :direction")
                params["direction"] = f"%{direction}%"

            where_clause = " AND ".join(conditions)
            query = text(f"""
                SELECT
                    complex_no,
                    article_no,
                    payload->>'articleName' as complex_name,
                    payload->>'area2' as exclusive_area,
                    payload->>'floorInfo' as floor_info,
                    payload->>'direction' as direction,
                    payload->>'tradeTypeName' as trade_type,
                    payload->>'dealOrWarrantPrc' as price,
                    payload->>'articleFeatureDesc' as description,
                    payload->>'tagList' as tags,
                    article_confirm_date
                FROM raw.articles
                WHERE {where_clause}
                ORDER BY article_confirm_date DESC
                LIMIT :limit
            """)
            params["limit"] = limit

            async with self.session_factory() as session:
                result = await session.execute(query, params)
                rows = result.fetchall()
                return [dict(row._mapping) for row in rows]

        @tool
        async def get_article_detail(
            complex_no: str,
            article_no: str,
        ) -> dict:
            """특정 매물의 상세 정보 조회

            Args:
                complex_no: 단지 번호
                article_no: 매물 번호

            Returns:
                매물 상세 정보
            """
            query = text("""
                SELECT
                    complex_no,
                    article_no,
                    payload,
                    article_confirm_date,
                    expire_at
                FROM raw.articles
                WHERE complex_no = :complex_no AND article_no = :article_no
            """)

            async with self.session_factory() as session:
                result = await session.execute(
                    query, {"complex_no": complex_no, "article_no": article_no}
                )
                row = result.fetchone()
                if row:
                    return dict(row._mapping)
                return {"error": "매물을 찾을 수 없습니다."}

        @tool
        async def get_complex_info(complex_no: str) -> dict:
            """단지 정보 조회 (평형, 동 정보, 세대수 등)

            Args:
                complex_no: 단지 번호

            Returns:
                단지 상세 정보
            """
            query = text("""
                SELECT
                    complex_no,
                    payload->>'complexName' as complex_name,
                    payload->>'totalDongCount' as dong_count,
                    payload->>'totalHouseHoldCount' as household_count,
                    payload->>'useApproveYmd' as approve_date,
                    payload->>'minPrice' as min_price,
                    payload->>'maxPrice' as max_price,
                    payload->>'minLeasePrice' as min_lease_price,
                    payload->>'maxLeasePrice' as max_lease_price,
                    payload->'pyeongs' as pyeongs,
                    payload->'dongs' as dongs,
                    payload->'realPrice' as recent_real_price
                FROM raw.complex_details
                WHERE complex_no = :complex_no
            """)

            async with self.session_factory() as session:
                result = await session.execute(query, {"complex_no": complex_no})
                row = result.fetchone()
                if row:
                    return dict(row._mapping)
                return {"error": "단지를 찾을 수 없습니다."}

        return [search_articles, get_article_detail, get_complex_info]
