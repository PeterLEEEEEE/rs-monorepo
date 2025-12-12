"""Market 도메인 DTO"""
from typing import Optional
from pydantic import BaseModel, Field
from src.core.utils import snake2camel


class RegionItem(BaseModel):
    """지역 정보"""
    region_code: str = Field(description="지역 코드 (예: gangnam)")
    region_name: str = Field(description="지역명 (예: 강남구)")
    complex_count: int = Field(description="단지 수")

    class Config:
        alias_generator = snake2camel
        populate_by_name = True


class RegionListResponse(BaseModel):
    """지역 목록 응답"""
    regions: list[RegionItem] = Field(description="지역 목록")

    class Config:
        alias_generator = snake2camel
        populate_by_name = True


class MonthlyPriceItem(BaseModel):
    """월별 가격 정보"""
    month: str = Field(description="월 (YYYY-MM)")
    avg_price: int = Field(description="평균 거래가 (만원)")
    trade_count: int = Field(description="거래 건수")

    class Config:
        alias_generator = snake2camel
        populate_by_name = True


class RegionPriceChange(BaseModel):
    """지역별 가격 변동"""
    region_code: str = Field(description="지역 코드")
    region_name: str = Field(description="지역명")
    current_avg_price: Optional[int] = Field(default=None, description="현재 평균가 (만원)")
    prev_avg_price: Optional[int] = Field(default=None, description="이전 평균가 (만원)")
    change_rate: Optional[float] = Field(default=None, description="변동률 (%)")
    trade_count: int = Field(default=0, description="거래 건수")

    class Config:
        alias_generator = snake2camel
        populate_by_name = True


class RegionPriceOverviewResponse(BaseModel):
    """지역별 가격 변동 개요 응답"""
    period: str = Field(description="비교 기간 (예: 3개월)")
    regions: list[RegionPriceChange] = Field(description="지역별 변동 정보")

    class Config:
        alias_generator = snake2camel
        populate_by_name = True


class RegionDetailResponse(BaseModel):
    """지역 상세 정보 응답"""
    region_code: str = Field(description="지역 코드")
    region_name: str = Field(description="지역명")
    complex_count: int = Field(description="단지 수")
    avg_price: Optional[int] = Field(default=None, description="평균 거래가 (만원)")
    trade_count: int = Field(default=0, description="총 거래 건수")
    price_trend: list[MonthlyPriceItem] = Field(description="월별 가격 추이")

    class Config:
        alias_generator = snake2camel
        populate_by_name = True
