import { Link } from "react-router-dom";

export default function IndexPage() {
  return (
    <div className="mx-auto max-w-6xl p-6">
      <h1 className="mb-8 text-3xl font-bold text-gray-900">
        부동산 시세 대시보드
      </h1>

      <div className="grid gap-6 md:grid-cols-2">
        {/* 단지별 실거래가 */}
        <Link
          to="/complex"
          className="group rounded-xl border border-gray-200 bg-white p-6 shadow-sm transition-all hover:border-blue-300 hover:shadow-md"
        >
          <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-blue-100 text-blue-600 group-hover:bg-blue-600 group-hover:text-white">
            <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
          </div>
          <h2 className="mb-2 text-xl font-semibold text-gray-900">
            단지별 실거래가
          </h2>
          <p className="text-gray-600">
            아파트 단지를 검색하여 평형별 실거래가 추이와 층수별 가격을 확인하세요.
          </p>
        </Link>

        {/* 지역별 시세 */}
        <Link
          to="/market"
          className="group rounded-xl border border-gray-200 bg-white p-6 shadow-sm transition-all hover:border-emerald-300 hover:shadow-md"
        >
          <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-emerald-100 text-emerald-600 group-hover:bg-emerald-600 group-hover:text-white">
            <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <h2 className="mb-2 text-xl font-semibold text-gray-900">
            지역별 시세
          </h2>
          <p className="text-gray-600">
            서울시 구별 아파트 시세 추이와 거래량을 분석하세요.
          </p>
          <span className="mt-3 inline-block rounded-full bg-gray-100 px-2 py-1 text-xs text-gray-500">
            준비 중
          </span>
        </Link>
      </div>

      {/* 빠른 통계 (placeholder) */}
      <div className="mt-8 grid gap-4 md:grid-cols-4">
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <p className="text-sm text-gray-500">수집 단지 수</p>
          <p className="text-2xl font-bold text-gray-900">258</p>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <p className="text-sm text-gray-500">총 거래 건수</p>
          <p className="text-2xl font-bold text-gray-900">-</p>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <p className="text-sm text-gray-500">평균 거래가</p>
          <p className="text-2xl font-bold text-gray-900">-</p>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <p className="text-sm text-gray-500">최근 업데이트</p>
          <p className="text-2xl font-bold text-gray-900">-</p>
        </div>
      </div>
    </div>
  );
}
