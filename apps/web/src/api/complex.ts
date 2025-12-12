import { API_URL } from "@/lib/constants";
import type {
  ComplexSearchResponse,
  ComplexDetail,
} from "@/types/complex";

export async function searchComplexes(
  query: string,
  limit: number = 20
): Promise<ComplexSearchResponse> {
  const params = new URLSearchParams({
    q: query,
    limit: limit.toString(),
  });

  const response = await fetch(`${API_URL}/complex/search?${params}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "단지 검색에 실패했습니다.");
  }

  return response.json();
}

export async function getComplexDetail(
  complexId: string
): Promise<ComplexDetail> {
  const response = await fetch(`${API_URL}/complex/${complexId}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "단지 정보를 가져오는데 실패했습니다.");
  }

  return response.json();
}
