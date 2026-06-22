import { cn } from "@/lib/utils";

/**
 * The Lead Score ring — the recurring visual signature of LeadForge AI.
 * Used in Lead Finder, CRM, and Reports so a lead's score is always
 * recognizable as the same motif across the product, instead of a flat
 * number that blends into surrounding text.
 *
 * Score bands map to color:
 *   80-100  hot     success (green)
 *   60-79   good    accent (indigo)
 *   40-59   medium  warning (amber)
 *   0-39    cold    danger (red)
 */
function bandFor(score: number) {
  if (score >= 80) return { color: "#22C55E", label: "Hot" };
  if (score >= 60) return { color: "#6366F1", label: "Good" };
  if (score >= 40) return { color: "#F59E0B", label: "Medium" };
  return { color: "#EF4444", label: "Cold" };
}

export function ScoreRing({
  score,
  size = 44,
  showLabel = false,
  className,
}: {
  score: number;
  size?: number;
  showLabel?: boolean;
  className?: string;
}) {
  const { color, label } = bandFor(score);
  const stroke = size * 0.09;
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className={cn("flex items-center gap-2", className)}>
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="#262629"
            strokeWidth={stroke}
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={stroke}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            className="transition-all duration-500 ease-out"
          />
        </svg>
        <span
          className="absolute inset-0 flex items-center justify-center font-mono font-semibold text-ink"
          style={{ fontSize: size * 0.32 }}
        >
          {score}
        </span>
      </div>
      {showLabel && (
        <span className="text-sm font-medium" style={{ color }}>
          {label}
        </span>
      )}
    </div>
  );
}
