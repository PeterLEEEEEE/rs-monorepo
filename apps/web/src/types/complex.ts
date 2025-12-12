// 단지 검색 결과 아이템
export interface ComplexSearchItem {
  complexId: string;
  complexName: string;
  complexTypeName?: string;
  totalHouseholdCount?: number;
  useApproveYmd?: string;
  minPrice?: number;
  maxPrice?: number;
}

// 단지 검색 응답
export interface ComplexSearchResponse {
  query: string;
  total: number;
  items: ComplexSearchItem[];
}

// 단지 상세 정보
export interface ComplexDetail {
  complexId: string;
  complexName: string;
  complexType?: string;
  complexTypeName?: string;
  totalDongCount?: number;
  totalHouseholdCount?: number;
  useApproveYmd?: string;
  latitude?: number;
  longitude?: number;
  minPrice?: number;
  maxPrice?: number;
  minPriceText?: string;
  maxPriceText?: string;
  minLeasePrice?: number;
  maxLeasePrice?: number;
}
