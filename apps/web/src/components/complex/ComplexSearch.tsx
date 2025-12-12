import { useState, useEffect, useRef } from "react";
import { searchComplexes } from "@/api/complex";
import type { ComplexSearchItem } from "@/types/complex";

interface ComplexSearchProps {
  onSelect: (complex: ComplexSearchItem) => void;
}

export function ComplexSearch({ onSelect }: ComplexSearchProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<ComplexSearchItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // 검색 debounce
  useEffect(() => {
    if (query.length < 2) {
      setResults([]);
      setIsOpen(false);
      return;
    }

    const timer = setTimeout(async () => {
      setIsLoading(true);
      try {
        const response = await searchComplexes(query);
        setResults(response.items);
        setIsOpen(true);
      } catch (error) {
        console.error("검색 실패:", error);
        setResults([]);
      } finally {
        setIsLoading(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [query]);

  // 외부 클릭 시 닫기
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSelect = (complex: ComplexSearchItem) => {
    setQuery(complex.complexName);
    setIsOpen(false);
    onSelect(complex);
  };

  // 가격 포맷팅
  const formatPrice = (price?: number) => {
    if (!price) return "-";
    if (price >= 10000) {
      return `${(price / 10000).toFixed(1)}억`;
    }
    return `${price}만`;
  };

  return (
    <div ref={containerRef} className="relative">
      <div className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="아파트 단지명을 검색하세요"
          className="w-full rounded-lg border border-gray-300 px-4 py-3 pr-10 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
        />
        {isLoading && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2">
            <div className="h-5 w-5 animate-spin rounded-full border-2 border-gray-300 border-t-blue-600" />
          </div>
        )}
      </div>

      {isOpen && results.length > 0 && (
        <div className="absolute z-50 mt-1 max-h-80 w-full overflow-auto rounded-lg border border-gray-200 bg-white shadow-lg">
          {results.map((complex) => (
            <button
              key={complex.complexId}
              onClick={() => handleSelect(complex)}
              className="w-full px-4 py-3 text-left hover:bg-gray-50 focus:bg-gray-50 focus:outline-none"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-900">
                    {complex.complexName}
                  </p>
                  <p className="text-sm text-gray-500">
                    {complex.complexTypeName} · {complex.totalHouseholdCount}세대
                    {complex.useApproveYmd &&
                      ` · ${complex.useApproveYmd.slice(0, 4)}년`}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-blue-600">
                    {formatPrice(complex.minPrice)} ~ {formatPrice(complex.maxPrice)}
                  </p>
                </div>
              </div>
            </button>
          ))}
        </div>
      )}

      {isOpen && query.length >= 2 && results.length === 0 && !isLoading && (
        <div className="absolute z-50 mt-1 w-full rounded-lg border border-gray-200 bg-white p-4 shadow-lg">
          <p className="text-center text-gray-500">검색 결과가 없습니다</p>
        </div>
      )}
    </div>
  );
}
