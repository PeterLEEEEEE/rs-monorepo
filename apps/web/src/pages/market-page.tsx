import { useParams, Link } from "react-router-dom";

// 서울시 구 목록 (추후 API로 대체)
const SEOUL_REGIONS = [
  { code: "gangnam", name: "강남구" },
  { code: "seocho", name: "서초구" },
  { code: "songpa", name: "송파구" },
  { code: "yongsan", name: "용산구" },
  { code: "seongdong", name: "성동구" },
  { code: "mapo", name: "마포구" },
  { code: "dongjak", name: "동작구" },
  { code: "yeongdeungpo", name: "영등포구" },
  { code: "gwangjin", name: "광진구" },
  { code: "gangdong", name: "강동구" },
  { code: "nowon", name: "노원구" },
  { code: "gangseo", name: "강서구" },
  { code: "gangbuk", name: "강북구" },
  { code: "seongbuk", name: "성북구" },
  { code: "jongno", name: "종로구" },
  { code: "jung", name: "중구" },
];

export default function MarketPage() {
  const { regionCode } = useParams<{ regionCode: string }>();

  // 지역 상세 페이지
  if (regionCode) {
    const region = SEOUL_REGIONS.find((r) => r.code === regionCode);

    return (
      <div className="mx-auto max-w-4xl p-6">
        <nav className="mb-6">
          <Link to="/market" className="text-blue-600 hover:underline">
            &larr; 지역 목록으로
          </Link>
        </nav>

        <h1 className="mb-6 text-2xl font-bold text-gray-900">
          {region?.name || regionCode} 시세 분석
        </h1>

        {/* Placeholder - 추후 차트 구현 */}
        <div className="space-y-6">
          <div className="rounded-lg border border-dashed border-gray-300 bg-gray-50 p-12">
            <p className="text-center text-gray-500">
              지역 데이터 매핑 후 구현 예정
            </p>
            <p className="mt-2 text-center text-sm text-gray-400">
              평균 시세 추이, 거래량 차트 등
            </p>
          </div>
        </div>
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

      <h1 className="mb-6 text-2xl font-bold text-gray-900">지역별 시세</h1>

      <div className="mb-4 rounded-lg border border-amber-200 bg-amber-50 p-4">
        <p className="text-sm text-amber-800">
          지역 데이터 매핑 작업 진행 후 기능이 활성화됩니다.
        </p>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
        {SEOUL_REGIONS.map((region) => (
          <Link
            key={region.code}
            to={`/market/${region.code}`}
            className="rounded-lg border border-gray-200 bg-white p-4 transition-all hover:border-emerald-300 hover:shadow-sm"
          >
            <h3 className="font-medium text-gray-900">{region.name}</h3>
            <p className="mt-1 text-sm text-gray-400">준비 중</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
