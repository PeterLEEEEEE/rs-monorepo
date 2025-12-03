from enum import Enum
from sqlalchemy import Integer, String, Boolean, VARCHAR, Float
from sqlalchemy.sql import expression
from sqlalchemy.orm import Mapped, mapped_column
from src.db.postgres.conn import Base
from src.db.mixins.mixin import Mixin

class TradeType(Enum):
    SALE = "SALE"      # 매매
    YEARLY = "YEARLY"  # 전세
    MONTHLY = "MONTHLY" # 월세

TRADE_TYPE_DISPLAY = {
    TradeType.SALE: "매매",
    TradeType.YEARLY: "전세",
    TradeType.MONTHLY: "월세"
}

class Article(Base, Mixin):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    trade_type: Mapped[TradeType] = mapped_column(
        Enum(TradeType, name="trade_type_enum"), nullable=False, default=TradeType.SALE
    )
    complex_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="APT"  # e.g., "APT", ""
    )
    content: Mapped[str] = mapped_column(String, nullable=False)
    author: Mapped[str] = mapped_column(String, nullable=False)  # 작성 부동산
    category: Mapped[str] = mapped_column(String(50), nullable=True)  # e.g., "news", "blog", "tutorial"
    floor_info: Mapped[str] = mapped_column(String(50), nullable=True)  # e.g., "3/14"
    area_info: Mapped[str] = mapped_column(String(50), nullable=True)  # e.g., "115/84"
    direction: Mapped[str] = mapped_column(String(10), nullable=True)  # e.g., "남향", "북향"
    price: Mapped[int] = mapped_column(Integer, nullable=False)  # 가격 e.g., 35억 , dealOrWarrantPrc
    move_in_date = mapped_column(String(50), nullable=True)  # 입주 가능일 e.g., "20250730"
    
    source_complex_id = mapped_column(Integer, nullable=False)  # 원천 Complex ID(단지 아이디)
    source_article_id: Mapped[str] = mapped_column(String, nullable=False)  # Source ID(원천 아이디) 이거로 업데이트 쳐야함
    source_updated_at: Mapped[str] = mapped_column(String(50), nullable=False)  # 20250729, articleConfirmYmd 이거로 정렬
    

