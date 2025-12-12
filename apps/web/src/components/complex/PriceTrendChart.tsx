import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  ComposedChart,
} from "recharts";
import type { PyeongTrendItem } from "@/types/real-price";

// 차트 색상 팔레트 (더 진한 색상으로 변경)
const COLORS = [
  "#2563EB", // blue-600
  "#059669", // emerald-600
  "#D97706", // amber-600
  "#DC2626", // red-600
  "#7C3AED", // violet-600
  "#DB2777", // pink-600
  "#0891B2", // cyan-600
  "#EA580C", // orange-600
];

interface PriceTrendChartProps {
  pyeongs: PyeongTrendItem[];
  selectedIds: string[];
  compareMode: boolean;
}

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

// X축 날짜 포맷 (연도 포함)
function formatXAxis(month: string, index: number, data: unknown[]): string {
  const [year, mon] = month.split("-");
  // 1월이거나 첫 번째 데이터면 연도 표시
  if (mon === "01" || index === 0) {
    return `${year}.${mon}`;
  }
  return mon;
}

export function PriceTrendChart({
  pyeongs,
  selectedIds,
  compareMode,
}: PriceTrendChartProps) {
  const selectedPyeongs = pyeongs.filter((p) =>
    selectedIds.includes(p.pyeongId)
  );

  if (selectedPyeongs.length === 0) {
    return (
      <div className="flex h-80 items-center justify-center rounded-lg border border-dashed border-gray-300 bg-gray-50">
        <p className="text-gray-600 font-medium">평형을 선택하면 차트가 표시됩니다</p>
      </div>
    );
  }

  // 단일 평형: 영역 차트 (min-max 범위 표시)
  if (!compareMode && selectedPyeongs.length === 1) {
    const pyeong = selectedPyeongs[0];
    const data = pyeong.trend.map((item) => ({
      month: item.month,
      avgPrice: item.avgPrice,
      minPrice: item.minPrice,
      maxPrice: item.maxPrice,
      tradeCount: item.tradeCount,
    }));

    const pyeongLabel = pyeong.pyeongName2
      ? `${pyeong.pyeongName2}평`
      : `${pyeong.exclusiveAreaPyeong?.toFixed(0)}평`;

    return (
      <div className="space-y-3">
        <h3 className="text-base font-semibold text-gray-900">
          {pyeongLabel} 실거래가 추이
        </h3>
        <ResponsiveContainer width="100%" height={350}>
          <ComposedChart data={data} margin={{ top: 10, right: 10, left: 10, bottom: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#D1D5DB" />
            <XAxis
              dataKey="month"
              tick={{ fontSize: 12, fill: "#374151", fontWeight: 500 }}
              tickFormatter={(value, index) => formatXAxis(value, index, data)}
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
              formatter={(value: number, name: string) => {
                const labels: Record<string, string> = {
                  avgPrice: "평균가",
                  minPrice: "최저가",
                  maxPrice: "최고가",
                };
                return [formatPrice(value), labels[name] || name];
              }}
              labelFormatter={(label) => {
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
              labelStyle={{ color: "#111827", fontWeight: 600, marginBottom: "4px" }}
            />
            <Legend
              wrapperStyle={{ fontSize: "14px", fontWeight: 500 }}
              formatter={(value) => {
                const labels: Record<string, string> = {
                  avgPrice: "평균가",
                  minPrice: "최저가",
                  maxPrice: "최고가",
                };
                return <span style={{ color: "#374151" }}>{labels[value] || value}</span>;
              }}
            />
            {/* min-max 영역 */}
            <Area
              type="monotone"
              dataKey="maxPrice"
              stroke="none"
              fill="#BFDBFE"
              fillOpacity={0.6}
              name="maxPrice"
            />
            <Area
              type="monotone"
              dataKey="minPrice"
              stroke="none"
              fill="white"
              name="minPrice"
            />
            {/* 평균가 라인 */}
            <Line
              type="monotone"
              dataKey="avgPrice"
              stroke="#2563EB"
              strokeWidth={3}
              dot={{ fill: "#2563EB", r: 4, strokeWidth: 2, stroke: "white" }}
              activeDot={{ r: 6, stroke: "white", strokeWidth: 2 }}
              name="avgPrice"
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    );
  }

  // 비교 모드: 멀티 라인 차트
  const allMonths = new Set<string>();
  selectedPyeongs.forEach((p) => {
    p.trend.forEach((t) => allMonths.add(t.month));
  });

  const sortedMonths = Array.from(allMonths).sort();

  const data = sortedMonths.map((month) => {
    const row: Record<string, string | number> = { month };
    selectedPyeongs.forEach((pyeong) => {
      const trendItem = pyeong.trend.find((t) => t.month === month);
      const key = pyeong.pyeongName2 || pyeong.pyeongId;
      row[key] = trendItem?.avgPrice ?? 0;
    });
    return row;
  });

  return (
    <div className="space-y-3">
      <h3 className="text-base font-semibold text-gray-900">평형별 실거래가 비교</h3>
      <ResponsiveContainer width="100%" height={350}>
        <LineChart data={data} margin={{ top: 10, right: 10, left: 10, bottom: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#D1D5DB" />
          <XAxis
            dataKey="month"
            tick={{ fontSize: 12, fill: "#374151", fontWeight: 500 }}
            tickFormatter={(value, index) => formatXAxis(value, index, data)}
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
            labelFormatter={(label) => {
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
            labelStyle={{ color: "#111827", fontWeight: 600, marginBottom: "4px" }}
          />
          <Legend
            wrapperStyle={{ fontSize: "14px", fontWeight: 500 }}
            formatter={(value) => <span style={{ color: "#374151" }}>{value}평</span>}
          />
          {selectedPyeongs.map((pyeong, index) => {
            const key = pyeong.pyeongName2 || pyeong.pyeongId;
            return (
              <Line
                key={pyeong.pyeongId}
                type="monotone"
                dataKey={key}
                stroke={COLORS[index % COLORS.length]}
                strokeWidth={3}
                dot={{ fill: COLORS[index % COLORS.length], r: 4, strokeWidth: 2, stroke: "white" }}
                activeDot={{ r: 6, stroke: "white", strokeWidth: 2 }}
                name={key}
              />
            );
          })}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
