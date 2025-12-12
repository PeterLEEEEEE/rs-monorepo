"""Complex 도메인 DTO"""
from typing import Optional
from pydantic import BaseModel, Field
from src.core.utils import snake2camel


class ComplexSearchItem(BaseModel):
    """단지 검색 결과 아이템"""
    complex_id: str = Field(description="단지 ID")
    complex_name: str = Field(description="단지명")
    complex_type_name: Optional[str] = Field(default=None, description="단지 유형명")
    total_household_count: Optional[int] = Field(default=None, description="총 세대수")
    use_approve_ymd: Optional[str] = Field(default=None, description="사용승인일")
    min_price: Optional[int] = Field(default=None, description="최저 매매가 (만원)")
    max_price: Optional[int] = Field(default=None, description="최고 매매가 (만원)")

    class Config:
        alias_generator = snake2camel
        populate_by_name = True


class ComplexSearchResponse(BaseModel):
    """단지 검색 응답"""
    query: str = Field(description="검색어")
    total: int = Field(description="검색 결과 수")
    items: list[ComplexSearchItem] = Field(description="검색 결과")

    class Config:
        alias_generator = snake2camel
        populate_by_name = True


class ComplexDetailResponse(BaseModel):
    """단지 상세 정보 응답"""
    complex_id: str = Field(description="단지 ID")
    complex_name: str = Field(description="단지명")
    complex_type: Optional[str] = Field(default=None, description="단지 유형 코드")
    complex_type_name: Optional[str] = Field(default=None, description="단지 유형명")
    total_dong_count: Optional[int] = Field(default=None, description="총 동 수")
    total_household_count: Optional[int] = Field(default=None, description="총 세대수")
    use_approve_ymd: Optional[str] = Field(default=None, description="사용승인일")
    latitude: Optional[float] = Field(default=None, description="위도")
    longitude: Optional[float] = Field(default=None, description="경도")
    min_price: Optional[int] = Field(default=None, description="최저 매매가 (만원)")
    max_price: Optional[int] = Field(default=None, description="최고 매매가 (만원)")
    min_price_text: Optional[str] = Field(default=None, description="최저 매매가 텍스트")
    max_price_text: Optional[str] = Field(default=None, description="최고 매매가 텍스트")
    min_lease_price: Optional[int] = Field(default=None, description="최저 전세가 (만원)")
    max_lease_price: Optional[int] = Field(default=None, description="최고 전세가 (만원)")

    class Config:
        alias_generator = snake2camel
        populate_by_name = True
