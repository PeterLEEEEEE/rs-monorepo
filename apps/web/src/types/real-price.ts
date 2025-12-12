// 월별 거래 추이
export interface MonthlyTrendItem {
  month: string; // YYYY-MM
  avgPrice: number;
  minPrice: number;
  maxPrice: number;
  tradeCount: number;
}

// 평형별 거래 추이
export interface PyeongTrendItem {
  pyeongId: string;
  pyeongName?: string;
  pyeongName2?: string;
  exclusiveAreaSqm?: number;
  exclusiveAreaPyeong?: number;
  trend: MonthlyTrendItem[];
}

// 실거래가 추이 응답
export interface PriceTrendResponse {
  complexId: string;
  complexName: string;
  pyeongs: PyeongTrendItem[];
}

// 평형 요약 정보
export interface PyeongSummaryItem {
  pyeongId: string;
  pyeongName?: string;
  pyeongName2?: string;
  exclusiveAreaSqm?: number;
  exclusiveAreaPyeong?: number;
  tradeCount: number;
  latestPrice?: number;
  latestTradeDate?: string;
}

// 평형 목록 응답
export interface PyeongListResponse {
  complexId: string;
  complexName: string;
  pyeongs: PyeongSummaryItem[];
}

// 층수별 가격 아이템
export interface FloorPriceItem {
  floor: number;
  dealPrice: number;
  tradeDate: string;
  pyeongId: string;
  pyeongName2?: string;
}

// 층수별 가격 응답
export interface FloorPriceResponse {
  complexId: string;
  complexName: string;
  trades: FloorPriceItem[];
}
