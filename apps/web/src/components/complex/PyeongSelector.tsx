import { useMemo } from "react";
import { cn } from "@/lib/utils";
import type { PyeongTrendItem } from "@/types/real-price";

interface PyeongSelectorProps {
  pyeongs: PyeongTrendItem[];
  selectedIds: string[];
  onSelect: (ids: string[]) => void;
  compareMode: boolean;
  onCompareModeChange: (enabled: boolean) => void;
  hideCompareToggle?: boolean;
  groupByPyeong?: boolean;
  onGroupByPyeongChange?: (enabled: boolean) => void;
}

// 평수 추출 (25A -> 25, 34B -> 34)
function extractPyeongNumber(pyeongName2?: string): string {
  if (!pyeongName2) return "";
  const match = pyeongName2.match(/^(\d+)/);
  return match ? match[1] : pyeongName2;
}

interface PyeongGroup {
  pyeongNumber: string;
  label: string;
  pyeongIds: string[];
  pyeongs: PyeongTrendItem[];
}

export function PyeongSelector({
  pyeongs,
  selectedIds,
  onSelect,
  compareMode,
  onCompareModeChange,
  hideCompareToggle = false,
  groupByPyeong = false,
  onGroupByPyeongChange,
}: PyeongSelectorProps) {
  // 평수별 그룹핑
  const pyeongGroups = useMemo(() => {
    const groups = new Map<string, PyeongGroup>();

    pyeongs.forEach((pyeong) => {
      const pyeongNumber = extractPyeongNumber(pyeong.pyeongName2);
      const key = pyeongNumber || pyeong.pyeongId;

      if (!groups.has(key)) {
        groups.set(key, {
          pyeongNumber: key,
          label: `${key}평`,
          pyeongIds: [],
          pyeongs: [],
        });
      }

      const group = groups.get(key)!;
      group.pyeongIds.push(pyeong.pyeongId);
      group.pyeongs.push(pyeong);
    });

    // 평수 기준 정렬
    return Array.from(groups.values()).sort(
      (a, b) => parseInt(a.pyeongNumber) - parseInt(b.pyeongNumber)
    );
  }, [pyeongs]);

  // 그룹에 하나라도 선택된 평형이 있는지 확인
  const isGroupSelected = (group: PyeongGroup) => {
    return group.pyeongIds.some((id) => selectedIds.includes(id));
  };

  // 그룹의 모든 평형이 선택되었는지 확인
  const isGroupFullySelected = (group: PyeongGroup) => {
    return group.pyeongIds.every((id) => selectedIds.includes(id));
  };

  const handleClick = (pyeongId: string) => {
    if (compareMode) {
      // 비교 모드: 토글 선택
      if (selectedIds.includes(pyeongId)) {
        onSelect(selectedIds.filter((id) => id !== pyeongId));
      } else {
        onSelect([...selectedIds, pyeongId]);
      }
    } else {
      // 단일 선택 모드
      onSelect([pyeongId]);
    }
  };

  const handleGroupClick = (group: PyeongGroup) => {
    if (compareMode) {
      // 비교 모드: 그룹 전체 토글
      if (isGroupFullySelected(group)) {
        // 모두 선택됨 -> 모두 해제
        onSelect(selectedIds.filter((id) => !group.pyeongIds.includes(id)));
      } else {
        // 일부/미선택 -> 모두 선택
        const newIds = new Set([...selectedIds, ...group.pyeongIds]);
        onSelect(Array.from(newIds));
      }
    } else {
      // 단일 선택 모드: 그룹의 모든 평형 선택
      onSelect(group.pyeongIds);
    }
  };

  // 묶기 가능 여부 (같은 평수가 여러 개 있는 경우만)
  const canGroup = pyeongGroups.some((g) => g.pyeongIds.length > 1);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-gray-700">평형 선택</h3>
        <div className="flex items-center gap-4">
          {canGroup && onGroupByPyeongChange && (
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={groupByPyeong}
                onChange={(e) => onGroupByPyeongChange(e.target.checked)}
                className="rounded border-gray-300"
              />
              <span className="text-gray-600">평수 묶기</span>
            </label>
          )}
          {!hideCompareToggle && (
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={compareMode}
                onChange={(e) => onCompareModeChange(e.target.checked)}
                className="rounded border-gray-300"
              />
              <span className="text-gray-600">비교 모드</span>
            </label>
          )}
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {groupByPyeong ? (
          // 평수별 그룹 표시
          pyeongGroups.map((group) => {
            const isSelected = isGroupSelected(group);
            const isFullySelected = isGroupFullySelected(group);
            const hasMultiple = group.pyeongIds.length > 1;

            return (
              <button
                key={group.pyeongNumber}
                onClick={() => handleGroupClick(group)}
                className={cn(
                  "rounded-full px-3 py-1.5 text-sm font-medium transition-colors",
                  isFullySelected
                    ? "bg-blue-600 text-white"
                    : isSelected
                      ? "bg-blue-200 text-blue-800"
                      : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                )}
                title={
                  hasMultiple
                    ? `${group.pyeongs.map((p) => p.pyeongName2 || p.pyeongId).join(", ")}`
                    : undefined
                }
              >
                {group.label}
                {hasMultiple && (
                  <span className="ml-1 text-xs opacity-70">
                    ({group.pyeongIds.length})
                  </span>
                )}
              </button>
            );
          })
        ) : (
          // 개별 평형 표시
          pyeongs.map((pyeong) => {
            const isSelected = selectedIds.includes(pyeong.pyeongId);
            const label = pyeong.pyeongName2
              ? `${pyeong.pyeongName2}평`
              : `${pyeong.exclusiveAreaPyeong?.toFixed(0)}평`;

            return (
              <button
                key={pyeong.pyeongId}
                onClick={() => handleClick(pyeong.pyeongId)}
                className={cn(
                  "rounded-full px-3 py-1.5 text-sm font-medium transition-colors",
                  isSelected
                    ? "bg-blue-600 text-white"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                )}
              >
                {label}
              </button>
            );
          })
        )}
      </div>

      {compareMode && selectedIds.length === 0 && (
        <p className="text-sm text-gray-500">
          비교할 평형을 선택하세요 (여러 개 선택 가능)
        </p>
      )}
    </div>
  );
}
