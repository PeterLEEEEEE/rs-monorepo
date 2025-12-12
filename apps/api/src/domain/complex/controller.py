"""Complex 도메인 Controller"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from dependency_injector.wiring import inject, Provide

from .service import ComplexService
from .dtos import ComplexSearchResponse, ComplexDetailResponse


complex_router = APIRouter(tags=["Complex"], prefix="/complex")


@complex_router.get("/search", response_model=ComplexSearchResponse)
@inject
async def search_complexes(
    q: str = Query(..., min_length=1, description="검색어 (단지명)"),
    limit: int = Query(default=20, ge=1, le=100, description="최대 결과 수"),
    service: ComplexService = Depends(Provide["complex_container.complex_service"]),
):
    """
    단지 검색

    - q: 검색어 (단지명, 부분 일치)
    - limit: 최대 결과 수 (기본 20, 최대 100)
    """
    return await service.search_complexes(query=q, limit=limit)


@complex_router.get("/{complex_id}", response_model=ComplexDetailResponse)
@inject
async def get_complex_detail(
    complex_id: str,
    service: ComplexService = Depends(Provide["complex_container.complex_service"]),
):
    """
    단지 상세 정보 조회

    - complex_id: 단지 ID
    """
    result = await service.get_complex_detail(complex_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"단지를 찾을 수 없습니다: {complex_id}"
        )

    return result
