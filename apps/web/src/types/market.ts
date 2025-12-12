export interface RegionItem {
  regionCode: string;
  regionName: string;
  complexCount: number;
}

export interface RegionListResponse {
  regions: RegionItem[];
}

export interface MonthlyPriceItem {
  month: string;
  avgPrice: number;
  tradeCount: number;
}

export interface RegionPriceChange {
  regionCode: string;
  regionName: string;
  currentAvgPrice: number | null;
  prevAvgPrice: number | null;
  changeRate: number | null;
  tradeCount: number;
}

export interface RegionPriceOverviewResponse {
  period: string;
  regions: RegionPriceChange[];
}

export interface RegionDetailResponse {
  regionCode: string;
  regionName: string;
  complexCount: number;
  avgPrice: number | null;
  tradeCount: number;
  priceTrend: MonthlyPriceItem[];
}
