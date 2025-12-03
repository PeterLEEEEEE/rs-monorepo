from enum import Enum, StrEnum


class RealEstateType(Enum):
    APT = "아파트"
    ABVG = "아파트분양권"
    OPST = "오피스텔"
    JGC = "재건축"


class TradeType(Enum):
    A1 = "매매"
    B1 = "전세"

class DatabaseType(StrEnum):
    REDIS = "redis"
    POSTGRES = "postgres"
    MONGO = "mongo"
