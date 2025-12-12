import { API_URL } from "@/lib/constants";
import type {
  PriceTrendResponse,
  PyeongListResponse,
  FloorPriceResponse,
} from "@/types/real-price";

export async function getPriceTrend(
  complexId: string,
  months: number = 24,
  pyeongId?: string
): Promise<PriceTrendResponse> {
  const params = new URLSearchParams({
    months: months.toString(),
  });

  if (pyeongId) {
    params.append("pyeong_id", pyeongId);
  }

  const response = await fetch(
    `${API_URL}/real-price/${complexId}/trend?${params}`
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "실거래가 정보를 가져오는데 실패했습니다.");
  }

  return response.json();
}

export async function getPyeongList(
  complexId: string
): Promise<PyeongListResponse> {
  const response = await fetch(`${API_URL}/real-price/${complexId}/pyeongs`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "평형 정보를 가져오는데 실패했습니다.");
  }

  return response.json();
}

export async function getFloorPrice(
  complexId: string,
  months: number = 24,
  pyeongId?: string
): Promise<FloorPriceResponse> {
  const params = new URLSearchParams({
    months: months.toString(),
  });

  if (pyeongId) {
    params.append("pyeong_id", pyeongId);
  }

  const response = await fetch(
    `${API_URL}/real-price/${complexId}/floor-price?${params}`
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "층수별 가격 정보를 가져오는데 실패했습니다.");
  }

  return response.json();
}
