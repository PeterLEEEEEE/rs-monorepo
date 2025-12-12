import { API_URL } from "@/lib/constants";
import type {
  RegionListResponse,
  RegionPriceOverviewResponse,
  RegionDetailResponse,
} from "@/types/market";

export async function getRegionList(): Promise<RegionListResponse> {
  const response = await fetch(`${API_URL}/market/regions`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "지역 목록을 가져오는데 실패했습니다.");
  }

  return response.json();
}

export async function getRegionPriceOverview(
  period: string = "3m"
): Promise<RegionPriceOverviewResponse> {
  const params = new URLSearchParams({
    period,
  });

  const response = await fetch(`${API_URL}/market/overview?${params}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "지역별 가격 정보를 가져오는데 실패했습니다.");
  }

  return response.json();
}

export async function getRegionDetail(
  regionCode: string,
  months: number = 12
): Promise<RegionDetailResponse> {
  const params = new URLSearchParams({
    months: months.toString(),
  });

  const response = await fetch(`${API_URL}/market/${regionCode}?${params}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "지역 정보를 가져오는데 실패했습니다.");
  }

  return response.json();
}
