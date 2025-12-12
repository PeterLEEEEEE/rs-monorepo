"""Market 도메인 Controller"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from dependency_injector.wiring import inject, Provide

from .service import MarketService
from .dtos import RegionListResponse, RegionPriceOverviewResponse, RegionDetailResponse


market_router = APIRouter(tags=["Market"], prefix="/market")


@market_router.get("/regions", response_model=RegionListResponse)
@inject
async def get_region_list(
    service: MarketService = Depends(Provide["market_container.market_service"]),
):
    """
    지역 목록 조회

    - 현재 데이터가 있는 모든 지역(구) 목록 반환
    - 각 지역별 단지 수 포함
    """
    return await service.get_region_list()


@market_router.get("/overview", response_model=RegionPriceOverviewResponse)
@inject
async def get_region_price_overview(
    months: int = Query(default=3, ge=1, le=12, description="비교 기간 (개월)"),
    service: MarketService = Depends(Provide["market_container.market_service"]),
):
    """
    지역별 가격 변동 개요 조회

    - months: 비교 기간 (기본 3개월)
    - 각 지역별 현재/이전 평균가, 변동률 반환
    - 변동률 기준 내림차순 정렬
    """
    return await service.get_region_price_overview(months=months)


@market_router.get("/{region_code}", response_model=RegionDetailResponse)
@inject
async def get_region_detail(
    region_code: str,
    months: int = Query(default=12, ge=1, le=60, description="조회 기간 (개월)"),
    service: MarketService = Depends(Provide["market_container.market_service"]),
):
    """
    특정 지역 상세 정보 조회

    - region_code: 지역 코드 (예: gangnam, seocho)
    - months: 조회 기간 (기본 12개월, 최대 60개월)
    - 월별 가격 추이, 단지 수, 거래 건수 등 포함
    """
    result = await service.get_region_detail(
        region_code=region_code,
        months=months
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"지역을 찾을 수 없습니다: {region_code}"
        )

    return result
