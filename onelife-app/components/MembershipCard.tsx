import type { MembershipCardProps, MembershipTier } from "./primitives";
import { cn } from "@/lib/utils";

const tierCopy: Record<MembershipTier, { label: string; next?: MembershipTier }> = {
  seedling: { label: "Seedling", next: "rooted" },
  rooted: { label: "Rooted", next: "flourishing" },
  flourishing: { label: "Flourishing" },
};

export function MembershipCard({
  memberName,
  tier,
  points,
  pointsToNextTier,
  memberSince,
  className,
}: MembershipCardProps) {
  const meta = tierCopy[tier];
  // Progress is informational — show fullness to next tier or full bar at top.
  const progress = meta.next && pointsToNextTier
    ? Math.max(0.08, 1 - pointsToNextTier / (pointsToNextTier + points))
    : 1;

  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-hero border border-hairline bg-tier-wash p-8 shadow-card",
        className,
      )}
    >
      <div className="flex items-start justify-between">
        <div>
          <p data-micro className="text-gold">One Life Community</p>
          <p className="mt-1 font-display text-xl text-ink">{memberName}</p>
        </div>
        <span
          data-micro
          className="rounded-pill border border-gold/40 px-3 py-1.5 text-gold"
        >
          {meta.label}
        </span>
      </div>

      <div className="mt-10">
        <p data-micro className="text-ink-muted">Points</p>
        <p data-num className="mt-1 font-mono text-3xl tracking-tight text-ink">
          {points.toLocaleString("en-ZA")}
        </p>
      </div>

      {meta.next && pointsToNextTier !== undefined && (
        <div className="mt-6">
          <div className="relative h-[2px] w-full bg-hairline">
            <div
              className="absolute inset-y-0 left-0 bg-sage-deep"
              style={{ width: `${progress * 100}%` }}
            />
          </div>
          <p data-micro className="mt-2 text-ink-muted">
            {pointsToNextTier.toLocaleString("en-ZA")} points to {tierCopy[meta.next].label}
          </p>
        </div>
      )}

      <p data-micro className="mt-6 text-ink-subtle">
        Member since {new Date(memberSince).getFullYear()}
      </p>
    </div>
  );
}
