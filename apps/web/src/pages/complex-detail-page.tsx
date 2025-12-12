import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { getPriceTrend, getFloorPrice } from "@/api/real-price";
import { getComplexDetail } from "@/api/complex";
import { ComplexSearch } from "@/components/complex/ComplexSearch";
import { PyeongSelector } from "@/components/complex/PyeongSelector";
import { PriceTrendChart } from "@/components/complex/PriceTrendChart";
import { FloorPriceChart } from "@/components/complex/FloorPriceChart";
import { PeriodSelector } from "@/components/complex/PeriodSelector";
import { cn } from "@/lib/utils";
import type { ComplexSearchItem } from "@/types/complex";

type ChartTab = "trend" | "floor";

export default function ComplexDetailPage() {
  const { complexId } = useParams<{ complexId: string }>();
  const navigate = useNavigate();

  const [selectedPyeongIds, setSelectedPyeongIds] = useState<string[]>([]);
  const [compareMode, setCompareMode] = useState(false);
  const [selectedMonths, setSelectedMonths] = useState(24);
  const [activeTab, setActiveTab] = useState<ChartTab>("trend");
  const [groupByPyeong, setGroupByPyeong] = useState(false);

  // 단지 상세 정보
  const { data: complexDetail, isLoading: isLoadingComplex } = useQuery({
    queryKey: ["complexDetail", complexId],
    queryFn: () => getComplexDetail(complexId!),
    enabled: !!complexId,
  });

  // 실거래가 추이
  const { data: priceTrend, isLoading: isLoadingTrend } = useQuery({
    queryKey: ["priceTrend", complexId, selectedMonths],
    queryFn: () => getPriceTrend(complexId!, selectedMonths),
    enabled: !!complexId,
  });

  // 층수별 가격 데이터
  const { data: floorPrice, isLoading: isLoadingFloor } = useQuery({
    queryKey: ["floorPrice", complexId, selectedMonths],
    queryFn: () => getFloorPrice(complexId!, selectedMonths),
    enabled: !!complexId && activeTab === "floor",
  });

  // 첫 번째 평형 자동 선택
  useEffect(() => {
    if (priceTrend?.pyeongs.length && selectedPyeongIds.length === 0) {
      const firstWithTrend = priceTrend.pyeongs.find((p) => p.trend.length > 0);
      if (firstWithTrend) {
        setSelectedPyeongIds([firstWithTrend.pyeongId]);
      }
    }
  }, [priceTrend, selectedPyeongIds.length]);

  // 단지 선택 시 해당 페이지로 이동
  const handleComplexSelect = (complex: ComplexSearchItem) => {
    setSelectedPyeongIds([]);
    setCompareMode(false);
    setActiveTab("trend");
    setGroupByPyeong(false);
    navigate(`/complex/${complex.complexId}`);
  };

  // 가격 포맷팅
  const formatPrice = (price?: number) => {
    if (!price) return "-";
    if (price >= 10000) {
      const eok = Math.floor(price / 10000);
      const man = price % 10000;
      if (man === 0) return `${eok}억`;
      return `${eok}억 ${man.toLocaleString()}만`;
    }
    return `${price.toLocaleString()}만`;
  };

  return (
    <div className="mx-auto max-w-4xl space-y-6 p-4">
      {/* 검색 */}
      <div>
        <h1 className="mb-4 text-2xl font-bold text-gray-900">
          아파트 실거래가 조회
        </h1>
        <ComplexSearch onSelect={handleComplexSelect} />
      </div>

      {/* 단지 정보 */}
      {complexId && (
        <>
          {isLoadingComplex ? (
            <div className="animate-pulse rounded-lg bg-gray-100 p-6">
              <div className="h-6 w-48 rounded bg-gray-300" />
              <div className="mt-2 h-4 w-32 rounded bg-gray-300" />
            </div>
          ) : complexDetail ? (
            <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="text-xl font-bold text-gray-900">
                    {complexDetail.complexName}
                  </h2>
                  <p className="mt-1 text-sm text-gray-600">
                    {complexDetail.complexTypeName}
                    {complexDetail.totalHouseholdCount &&
                      ` · ${complexDetail.totalHouseholdCount.toLocaleString()}세대`}
                    {complexDetail.totalDongCount &&
                      ` · ${complexDetail.totalDongCount}개동`}
                    {complexDetail.useApproveYmd &&
                      ` · ${complexDetail.useApproveYmd.slice(0, 4)}년 준공`}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-600">매매가</p>
                  <p className="text-lg font-bold text-blue-600">
                    {formatPrice(complexDetail.minPrice)} ~{" "}
                    {formatPrice(complexDetail.maxPrice)}
                  </p>
                  {complexDetail.minLeasePrice && (
                    <>
                      <p className="mt-2 text-sm font-medium text-gray-600">
                        전세가
                      </p>
                      <p className="font-semibold text-gray-800">
                        {formatPrice(complexDetail.minLeasePrice)} ~{" "}
                        {formatPrice(complexDetail.maxLeasePrice)}
                      </p>
                    </>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className="rounded-lg border border-red-200 bg-red-50 p-6">
              <p className="font-medium text-red-700">
                단지 정보를 찾을 수 없습니다
              </p>
            </div>
          )}

          {/* 평형 선택 & 차트 */}
          {isLoadingTrend ? (
            <div className="space-y-4">
              <div className="animate-pulse">
                <div className="flex gap-2">
                  {[1, 2, 3, 4].map((i) => (
                    <div
                      key={i}
                      className="h-8 w-16 rounded-full bg-gray-300"
                    />
                  ))}
                </div>
              </div>
              <div className="h-80 animate-pulse rounded-lg bg-gray-200" />
            </div>
          ) : priceTrend && priceTrend.pyeongs.length > 0 ? (
            <div className="space-y-5 rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
              {/* 탭 선택 */}
              <div className="flex border-b border-gray-200">
                <button
                  onClick={() => setActiveTab("trend")}
                  className={cn(
                    "px-4 py-2 text-sm font-medium transition-colors",
                    activeTab === "trend"
                      ? "border-b-2 border-blue-600 text-blue-600"
                      : "text-gray-600 hover:text-gray-900"
                  )}
                >
                  가격 추이
                </button>
                <button
                  onClick={() => setActiveTab("floor")}
                  className={cn(
                    "px-4 py-2 text-sm font-medium transition-colors",
                    activeTab === "floor"
                      ? "border-b-2 border-blue-600 text-blue-600"
                      : "text-gray-600 hover:text-gray-900"
                  )}
                >
                  층수별 분석
                </button>
              </div>

              {/* 기간 선택 */}
              <PeriodSelector
                selectedMonths={selectedMonths}
                onSelect={setSelectedMonths}
              />

              {/* 가격 추이 탭 */}
              {activeTab === "trend" && (
                <>
                  {/* 평형 선택 */}
                  <PyeongSelector
                    pyeongs={priceTrend.pyeongs}
                    selectedIds={selectedPyeongIds}
                    onSelect={setSelectedPyeongIds}
                    compareMode={compareMode}
                    onCompareModeChange={setCompareMode}
                    groupByPyeong={groupByPyeong}
                    onGroupByPyeongChange={setGroupByPyeong}
                  />

                  {/* 차트 */}
                  <PriceTrendChart
                    pyeongs={priceTrend.pyeongs}
                    selectedIds={selectedPyeongIds}
                    compareMode={compareMode}
                  />
                </>
              )}

              {/* 층수별 분석 탭 */}
              {activeTab === "floor" && (
                <>
                  {/* 평형 선택 (비교 모드 없음) */}
                  <PyeongSelector
                    pyeongs={priceTrend.pyeongs}
                    selectedIds={selectedPyeongIds}
                    onSelect={setSelectedPyeongIds}
                    compareMode={false}
                    onCompareModeChange={() => {}}
                    hideCompareToggle
                    groupByPyeong={groupByPyeong}
                    onGroupByPyeongChange={setGroupByPyeong}
                  />

                  {/* 산점도 차트 */}
                  {isLoadingFloor ? (
                    <div className="h-80 animate-pulse rounded-lg bg-gray-200" />
                  ) : floorPrice ? (
                    <FloorPriceChart
                      trades={floorPrice.trades}
                      selectedPyeongIds={selectedPyeongIds}
                    />
                  ) : (
                    <div className="flex h-80 items-center justify-center rounded-lg border border-dashed border-gray-300 bg-gray-50">
                      <p className="font-medium text-gray-600">
                        데이터를 불러오는 중...
                      </p>
                    </div>
                  )}
                </>
              )}
            </div>
          ) : (
            <div className="rounded-lg border border-gray-200 bg-gray-50 p-6">
              <p className="text-center font-medium text-gray-600">
                실거래 데이터가 없습니다
              </p>
            </div>
          )}
        </>
      )}

      {/* 초기 상태 */}
      {!complexId && (
        <div className="rounded-lg border border-dashed border-gray-300 bg-gray-50 p-12">
          <p className="text-center font-medium text-gray-600">
            아파트 단지를 검색하여 실거래가 추이를 확인하세요
          </p>
        </div>
      )}
    </div>
  );
}
