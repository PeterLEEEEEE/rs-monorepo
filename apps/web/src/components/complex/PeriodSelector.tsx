import { cn } from "@/lib/utils";

export interface PeriodOption {
  label: string;
  months: number;
}

export const PERIOD_OPTIONS: PeriodOption[] = [
  { label: "3개월", months: 3 },
  { label: "6개월", months: 6 },
  { label: "1년", months: 12 },
  { label: "2년", months: 24 },
  { label: "5년", months: 60 },
  { label: "10년", months: 120 },
];

interface PeriodSelectorProps {
  selectedMonths: number;
  onSelect: (months: number) => void;
}

export function PeriodSelector({
  selectedMonths,
  onSelect,
}: PeriodSelectorProps) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-sm font-medium text-gray-700">조회 기간:</span>
      <div className="flex gap-1">
        {PERIOD_OPTIONS.map((option) => (
          <button
            key={option.months}
            onClick={() => onSelect(option.months)}
            className={cn(
              "rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
              selectedMonths === option.months
                ? "bg-blue-600 text-white"
                : "bg-gray-100 text-gray-700 hover:bg-gray-200"
            )}
          >
            {option.label}
          </button>
        ))}
      </div>
    </div>
  );
}
