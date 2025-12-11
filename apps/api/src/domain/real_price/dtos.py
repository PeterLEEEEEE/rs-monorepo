"""Real Price 도메인 DTO"""
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field
from src.core.utils import snake2camel


# ============== Request Schemas ==============

class PriceTrendRequest(BaseModel):
    """실거래가 추이 조회 요청"""
    months: int = Field(default=24, ge=1, le=120, description="조회 기간 (개월)")
    pyeong_id: Optional[str] = Field(default=None, description="특정 평형 ID 필터")


# ============== Response Schemas ==============

class MonthlyTrendItem(BaseModel):
    """월별 거래 추이"""
    month: str = Field(description="월 (YYYY-MM)")
    avg_price: int = Field(description="평균 거래가 (만원)")
    min_price: int = Field(description="최저 거래가 (만원)")
    max_price: int = Field(description="최고 거래가 (만원)")
    trade_count: int = Field(description="거래 건수")

    class Config:
        alias_generator = snake2camel
        populate_by_name = True


class PyeongTrendItem(BaseModel):
    """평형별 거래 추이"""
    pyeong_id: str = Field(description="평형 ID")
    pyeong_name: Optional[str] = Field(default=None, description="평형명 (㎡)")
    pyeong_name2: Optional[str] = Field(default=None, description="평형명 (평)")
    exclusive_area_sqm: Optional[float] = Field(default=None, description="전용면적 (㎡)")
    exclusive_area_pyeong: Optional[float] = Field(default=None, description="전용면적 (평)")
    trend: list[MonthlyTrendItem] = Field(description="월별 추이")

    class Config:
        alias_generator = snake2camel
        populate_by_name = True


class PriceTrendResponse(BaseModel):
    """실거래가 추이 응답"""
    complex_id: str = Field(description="단지 ID")
    complex_name: str = Field(description="단지명")
    pyeongs: list[PyeongTrendItem] = Field(description="평형별 추이")

    class Config:
        alias_generator = snake2camel
        populate_by_name = True


class PyeongSummaryItem(BaseModel):
    """평형 요약 정보"""
    pyeong_id: str = Field(description="평형 ID")
    pyeong_name: Optional[str] = Field(default=None, description="평형명 (㎡)")
    pyeong_name2: Optional[str] = Field(default=None, description="평형명 (평)")
    exclusive_area_sqm: Optional[float] = Field(default=None, description="전용면적 (㎡)")
    exclusive_area_pyeong: Optional[float] = Field(default=None, description="전용면적 (평)")
    trade_count: int = Field(description="총 거래 건수")
    latest_price: Optional[int] = Field(default=None, description="최근 거래가 (만원)")
    latest_trade_date: Optional[date] = Field(default=None, description="최근 거래일")

    class Config:
        alias_generator = snake2camel
        populate_by_name = True


class PyeongListResponse(BaseModel):
    """평형 목록 응답"""
    complex_id: str = Field(description="단지 ID")
    complex_name: str = Field(description="단지명")
    pyeongs: list[PyeongSummaryItem] = Field(description="평형 목록")

    class Config:
        alias_generator = snake2camel
        populate_by_name = True
