import type { ReviewBlockProps } from "./primitives";
import { cn } from "@/lib/utils";

const goalLabel: Record<ReviewBlockProps["goal"], string> = {
  sleep: "Sleep",
  energy: "Energy",
  stress: "Stress",
  gut: "Gut",
  immunity: "Immunity",
  joints: "Joints",
  skin: "Skin",
  hormones: "Hormones",
  focus: "Focus",
  recovery: "Recovery",
};

// 1.5px-stroke rating glyph — intentionally not stars; a single vertical
// tick rising up to the rating, left aligned. Quieter than 5 stars.
function RatingMark({ rating }: { rating: 1 | 2 | 3 | 4 | 5 }) {
  return (
    <svg
      aria-label={`${rating} out of 5`}
      viewBox="0 0 50 10"
      className="h-2.5 w-[50px]"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
    >
      {[0, 1, 2, 3, 4].map((i) => (
        <line
          key={i}
          x1={2 + i * 12}
          y1={i < rating ? 2 : 6}
          x2={2 + i * 12}
          y2={8}
          className={i < rating ? "text-ink" : "text-hairline"}
        />
      ))}
    </svg>
  );
}

export function ReviewBlock({
  rating,
  goal,
  body,
  verifiedAt,
  helpfulCount,
  className,
}: ReviewBlockProps) {
  return (
    <article
      className={cn(
        "space-y-3 border-t border-hairline pt-5",
        className,
      )}
    >
      <div className="flex items-center justify-between text-ink">
        <RatingMark rating={rating} />
        <span data-micro>Bought for {goalLabel[goal]}</span>
      </div>
      <p className="max-w-prose text-base leading-[1.55] text-ink">
        {body}
      </p>
      <div className="flex items-center justify-between">
        <p data-micro className="text-ink-subtle">
          Verified {new Date(verifiedAt).toLocaleDateString("en-ZA", {
            month: "short",
            year: "numeric",
          })}
        </p>
        {helpfulCount !== undefined && (
          <p data-micro className="text-ink-subtle">
            {helpfulCount} found this helpful
          </p>
        )}
      </div>
    </article>
  );
}
