import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ZAxis,
} from "recharts";
import type { FloorPriceItem } from "@/types/real-price";

// 차트 색상 팔레트
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

interface FloorPriceChartProps {
  trades: FloorPriceItem[];
  selectedPyeongIds: string[];
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

export function FloorPriceChart({
  trades,
  selectedPyeongIds,
}: FloorPriceChartProps) {
  // 선택된 평형 필터링
  const filteredTrades = selectedPyeongIds.length > 0
    ? trades.filter((t) => selectedPyeongIds.includes(t.pyeongId))
    : trades;

  if (filteredTrades.length === 0) {
    return (
      <div className="flex h-80 items-center justify-center rounded-lg border border-dashed border-gray-300 bg-gray-50">
        <p className="font-medium text-gray-600">층수별 거래 데이터가 없습니다</p>
      </div>
    );
  }

  // 평형별로 데이터 그룹핑
  const pyeongGroups = new Map<string, FloorPriceItem[]>();
  filteredTrades.forEach((trade) => {
    const key = trade.pyeongName2 || trade.pyeongId;
    if (!pyeongGroups.has(key)) {
      pyeongGroups.set(key, []);
    }
    pyeongGroups.get(key)!.push(trade);
  });

  const pyeongKeys = Array.from(pyeongGroups.keys());

  return (
    <div className="space-y-3">
      <h3 className="text-base font-semibold text-gray-900">
        층수별 거래가 분포
      </h3>
      <ResponsiveContainer width="100%" height={350}>
        <ScatterChart margin={{ top: 10, right: 10, left: 10, bottom: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#D1D5DB" />
          <XAxis
            type="number"
            dataKey="floor"
            name="층수"
            tick={{ fontSize: 12, fill: "#374151", fontWeight: 500 }}
            axisLine={{ stroke: "#9CA3AF" }}
            tickLine={{ stroke: "#9CA3AF" }}
            label={{
              value: "층수",
              position: "insideBottomRight",
              offset: -5,
              style: { fontSize: 12, fill: "#6B7280", fontWeight: 500 },
            }}
          />
          <YAxis
            type="number"
            dataKey="dealPrice"
            name="거래가"
            tick={{ fontSize: 12, fill: "#374151", fontWeight: 500 }}
            tickFormatter={formatPriceShort}
            axisLine={{ stroke: "#9CA3AF" }}
            tickLine={{ stroke: "#9CA3AF" }}
            width={60}
            label={{
              value: "거래가",
              angle: -90,
              position: "insideLeft",
              style: { fontSize: 12, fill: "#6B7280", fontWeight: 500 },
            }}
          />
          <ZAxis range={[60, 60]} />
          <Tooltip
            cursor={{ strokeDasharray: "3 3" }}
            content={({ active, payload }) => {
              if (!active || !payload || payload.length === 0) return null;
              const data = payload[0].payload as FloorPriceItem;
              return (
                <div className="rounded-lg border border-gray-200 bg-white p-3 shadow-lg">
                  <p className="mb-1 font-semibold text-gray-900">
                    {data.pyeongName2 ? `${data.pyeongName2}평` : data.pyeongId}
                  </p>
                  <p className="text-sm text-gray-700">
                    <span className="font-medium">층수:</span> {data.floor}층
                  </p>
                  <p className="text-sm text-gray-700">
                    <span className="font-medium">거래가:</span>{" "}
                    {formatPrice(data.dealPrice)}
                  </p>
                  <p className="text-sm text-gray-700">
                    <span className="font-medium">거래일:</span> {data.tradeDate}
                  </p>
                </div>
              );
            }}
          />
          <Legend
            wrapperStyle={{ fontSize: "14px", fontWeight: 500 }}
            formatter={(value) => (
              <span style={{ color: "#374151" }}>{value}평</span>
            )}
          />
          {pyeongKeys.map((pyeongKey, index) => (
            <Scatter
              key={pyeongKey}
              name={pyeongKey}
              data={pyeongGroups.get(pyeongKey)}
              fill={COLORS[index % COLORS.length]}
            />
          ))}
        </ScatterChart>
      </ResponsiveContainer>
      <p className="text-center text-sm text-gray-500">
        총 {filteredTrades.length}건의 거래
      </p>
    </div>
  );
}
