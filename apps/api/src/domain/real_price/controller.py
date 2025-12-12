"""Real Price 도메인 Controller"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from dependency_injector.wiring import inject, Provide
from typing import Optional

from .service import RealPriceService
from .dtos import PriceTrendResponse, PyeongListResponse, FloorPriceResponse


real_price_router = APIRouter(tags=["Real Price"], prefix="/real-price")


@real_price_router.get("/{complex_id}/trend", response_model=PriceTrendResponse)
@inject
async def get_price_trend(
    complex_id: str,
    months: int = Query(default=24, ge=1, le=120, description="조회 기간 (개월)"),
    pyeong_id: Optional[str] = Query(default=None, description="특정 평형 ID 필터"),
    service: RealPriceService = Depends(Provide["real_price_container.real_price_service"]),
):
    """
    평형별 실거래가 추이 조회

    - complex_id: 단지 ID
    - months: 조회 기간 (기본 24개월, 최대 120개월)
    - pyeong_id: 특정 평형만 조회 (선택)
    """
    result = await service.get_price_trend(
        complex_id=complex_id,
        months=months,
        pyeong_id=pyeong_id
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"단지를 찾을 수 없습니다: {complex_id}"
        )

    return result


@real_price_router.get("/{complex_id}/pyeongs", response_model=PyeongListResponse)
@inject
async def get_pyeong_list(
    complex_id: str,
    service: RealPriceService = Depends(Provide["real_price_container.real_price_service"]),
):
    """
    단지의 평형 목록 조회

    - 각 평형별 거래 건수, 최근 거래가, 최근 거래일 포함
    """
    result = await service.get_pyeong_list(complex_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"단지를 찾을 수 없습니다: {complex_id}"
        )

    return result


@real_price_router.get("/{complex_id}/floor-price", response_model=FloorPriceResponse)
@inject
async def get_floor_price(
    complex_id: str,
    months: int = Query(default=24, ge=1, le=120, description="조회 기간 (개월)"),
    pyeong_id: Optional[str] = Query(default=None, description="특정 평형 ID 필터"),
    service: RealPriceService = Depends(Provide["real_price_container.real_price_service"]),
):
    """
    층수별 가격 데이터 조회 (산점도용)

    - complex_id: 단지 ID
    - months: 조회 기간 (기본 24개월, 최대 120개월)
    - pyeong_id: 특정 평형만 조회 (선택)
    """
    result = await service.get_floor_price(
        complex_id=complex_id,
        months=months,
        pyeong_id=pyeong_id
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"단지를 찾을 수 없습니다: {complex_id}"
        )

    return result
