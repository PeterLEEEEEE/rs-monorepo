import { useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { getRegionPriceOverview, getRegionDetail } from "@/api/market";

// 기간 옵션
const PERIOD_OPTIONS = [
  { value: "1w", label: "1주일" },
  { value: "1m", label: "1개월" },
  { value: "3m", label: "3개월" },
  { value: "6m", label: "6개월" },
  { value: "1y", label: "1년" },
];

// 가격 포맷팅 (만원 -> 억)
function formatPrice(price: number): string {
  if (price >= 10000) {
    const eok = Math.floor(price / 10000);
    const man = price % 10000;
    if (man === 0) {
      return `${eok}억`;
    }
    return `${eok}억 ${man.toLocaleString()}만`;
  }
  return `${price.toLocaleString()}만`;
}

// 단축 가격 포맷 (Y축용)
function formatPriceShort(price: number): string {
  if (price >= 10000) {
    return `${(price / 10000).toFixed(1)}억`;
  }
  return `${(price / 1000).toFixed(0)}천`;
}

// X축 날짜 포맷
function formatXAxis(month: string, index: number): string {
  const [year, mon] = month.split("-");
  if (mon === "01" || index === 0) {
    return `${year}.${mon}`;
  }
  return mon;
}

export default function MarketPage() {
  const { regionCode } = useParams<{ regionCode: string }>();
  const [selectedPeriod, setSelectedPeriod] = useState("3m");

  // 지역별 가격 변동 개요 조회
  const { data: overviewData, isLoading: isOverviewLoading } = useQuery({
    queryKey: ["regionPriceOverview", selectedPeriod],
    queryFn: () => getRegionPriceOverview(selectedPeriod),
    enabled: !regionCode,
  });

  // 지역 상세 정보 조회
  const { data: detailData, isLoading: isDetailLoading } = useQuery({
    queryKey: ["regionDetail", regionCode, 12],
    queryFn: () => getRegionDetail(regionCode!, 12),
    enabled: !!regionCode,
  });

  // 지역 상세 페이지
  if (regionCode) {
    return (
      <div className="mx-auto max-w-4xl p-6">
        <nav className="mb-6">
          <Link to="/market" className="text-blue-600 hover:underline">
            &larr; 지역 목록으로
          </Link>
        </nav>

        {isDetailLoading ? (
          <div className="animate-pulse space-y-4">
            <div className="h-8 w-48 rounded bg-gray-200" />
            <div className="h-64 rounded bg-gray-200" />
          </div>
        ) : detailData ? (
          <>
            <h1 className="mb-2 text-2xl font-bold text-gray-900">
              {detailData.regionName} 시세 분석
            </h1>
            <p className="mb-6 text-sm text-gray-500">
              단지 {detailData.complexCount}개 | 거래 {detailData.tradeCount.toLocaleString()}건
              {detailData.avgPrice && ` | 평균 ${formatPrice(detailData.avgPrice)}`}
            </p>

            <div className="space-y-6">
              {/* 가격 추이 차트 */}
              <div className="rounded-lg border bg-white p-6">
                <h3 className="mb-4 text-base font-semibold text-gray-900">
                  월별 평균 실거래가 추이
                </h3>
                {detailData.priceTrend.length > 0 ? (
                  <ResponsiveContainer width="100%" height={350}>
                    <LineChart
                      data={detailData.priceTrend}
                      margin={{ top: 10, right: 10, left: 10, bottom: 10 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="#D1D5DB" />
                      <XAxis
                        dataKey="month"
                        tick={{ fontSize: 12, fill: "#374151", fontWeight: 500 }}
                        tickFormatter={formatXAxis}
                        axisLine={{ stroke: "#9CA3AF" }}
                        tickLine={{ stroke: "#9CA3AF" }}
                      />
                      <YAxis
                        tick={{ fontSize: 12, fill: "#374151", fontWeight: 500 }}
                        tickFormatter={formatPriceShort}
                        domain={["dataMin - 5000", "dataMax + 5000"]}
                        axisLine={{ stroke: "#9CA3AF" }}
                        tickLine={{ stroke: "#9CA3AF" }}
                        width={60}
                      />
                      <Tooltip
                        formatter={(value: number) => [formatPrice(value), "평균가"]}
                        labelFormatter={(label: string) => {
                          const [year, month] = label.split("-");
                          return `${year}년 ${month}월`;
                        }}
                        contentStyle={{
                          backgroundColor: "white",
                          border: "1px solid #E5E7EB",
                          borderRadius: "8px",
                          boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
                          fontSize: "14px",
                          fontWeight: 500,
                        }}
                      />
                      <Line
                        type="monotone"
                        dataKey="avgPrice"
                        stroke="#2563EB"
                        strokeWidth={3}
                        dot={{ fill: "#2563EB", r: 4, strokeWidth: 2, stroke: "white" }}
                        activeDot={{ r: 6, stroke: "white", strokeWidth: 2 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex h-64 items-center justify-center rounded-lg border border-dashed border-gray-300 bg-gray-50">
                    <p className="text-gray-500">거래 데이터가 없습니다</p>
                  </div>
                )}
              </div>

              {/* 거래량 차트 */}
              {detailData.priceTrend.length > 0 && (
                <div className="rounded-lg border bg-white p-6">
                  <h3 className="mb-4 text-base font-semibold text-gray-900">
                    월별 거래량
                  </h3>
                  <ResponsiveContainer width="100%" height={200}>
                    <LineChart
                      data={detailData.priceTrend}
                      margin={{ top: 10, right: 10, left: 10, bottom: 10 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="#D1D5DB" />
                      <XAxis
                        dataKey="month"
                        tick={{ fontSize: 12, fill: "#374151" }}
                        tickFormatter={formatXAxis}
                        axisLine={{ stroke: "#9CA3AF" }}
                        tickLine={{ stroke: "#9CA3AF" }}
                      />
                      <YAxis
                        tick={{ fontSize: 12, fill: "#374151" }}
                        axisLine={{ stroke: "#9CA3AF" }}
                        tickLine={{ stroke: "#9CA3AF" }}
                        width={40}
                      />
                      <Tooltip
                        formatter={(value: number) => [`${value}건`, "거래량"]}
                        labelFormatter={(label: string) => {
                          const [year, month] = label.split("-");
                          return `${year}년 ${month}월`;
                        }}
                        contentStyle={{
                          backgroundColor: "white",
                          border: "1px solid #E5E7EB",
                          borderRadius: "8px",
                          fontSize: "14px",
                        }}
                      />
                      <Line
                        type="monotone"
                        dataKey="tradeCount"
                        stroke="#059669"
                        strokeWidth={2}
                        dot={{ fill: "#059669", r: 3, strokeWidth: 2, stroke: "white" }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>
          </>
        ) : (
          <div className="rounded-lg border border-red-200 bg-red-50 p-6">
            <p className="text-red-700">지역 정보를 찾을 수 없습니다.</p>
          </div>
        )}
      </div>
    );
  }

  // 지역 목록 페이지
  return (
    <div className="mx-auto max-w-4xl p-6">
      <nav className="mb-6">
        <Link to="/" className="text-blue-600 hover:underline">
          &larr; 대시보드로
        </Link>
      </nav>

      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">지역별 시세</h1>

        {/* 기간 선택기 */}
        <div className="flex gap-1 rounded-lg border bg-gray-100 p-1">
          {PERIOD_OPTIONS.map((option) => (
            <button
              key={option.value}
              onClick={() => setSelectedPeriod(option.value)}
              className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                selectedPeriod === option.value
                  ? "bg-white text-gray-900 shadow-sm"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      {overviewData && (
        <p className="mb-4 text-sm text-gray-500">
          {overviewData.period} 전 대비 변동률 (단지별 상승률 평균)
        </p>
      )}

      {isOverviewLoading ? (
        <div className="grid gap-3 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
          {[...Array(16)].map((_, i) => (
            <div key={i} className="animate-pulse rounded-lg border bg-gray-100 p-4">
              <div className="h-5 w-16 rounded bg-gray-200" />
              <div className="mt-2 h-4 w-24 rounded bg-gray-200" />
            </div>
          ))}
        </div>
      ) : overviewData ? (
        <div className="grid gap-3 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
          {overviewData.regions.map((region) => (
            <Link
              key={region.regionCode}
              to={`/market/${region.regionCode}`}
              className="rounded-lg border border-gray-200 bg-white p-4 transition-all hover:border-emerald-300 hover:shadow-sm"
            >
              <div className="flex items-center justify-between">
                <h3 className="font-medium text-gray-900">{region.regionName}</h3>
                {region.changeRate !== null && (
                  <span
                    className={`text-sm font-semibold ${
                      region.changeRate > 0
                        ? "text-red-600"
                        : region.changeRate < 0
                          ? "text-blue-600"
                          : "text-gray-500"
                    }`}
                  >
                    {region.changeRate > 0 ? "+" : ""}
                    {region.changeRate.toFixed(1)}%
                  </span>
                )}
              </div>
              <p className="mt-1 text-sm text-gray-500">
                {region.currentAvgPrice
                  ? formatPrice(region.currentAvgPrice)
                  : "데이터 없음"}
              </p>
              <p className="mt-0.5 text-xs text-gray-400">
                {region.complexCount}개 단지 | 거래 {region.tradeCount.toLocaleString()}건
              </p>
            </Link>
          ))}
        </div>
      ) : (
        <div className="rounded-lg border border-red-200 bg-red-50 p-6">
          <p className="text-red-700">데이터를 불러오는데 실패했습니다.</p>
        </div>
      )}
    </div>
  );
}
