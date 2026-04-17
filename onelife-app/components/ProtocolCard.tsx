"use client";

import { ArrowClockwise, Sparkle, UserCircle, Package } from "@phosphor-icons/react";
import type { ProtocolCardProps } from "./primitives";
import { PaperImage } from "./PaperImage";
import { cn } from "@/lib/utils";

const sourceMeta: Record<
  ProtocolCardProps["source"],
  { Icon: typeof Sparkle; label: string }
> = {
  consultation: { Icon: UserCircle, label: "From your consultation" },
  "ai-assistant": { Icon: Sparkle, label: "AI suggestion · consultant review recommended" },
  "repeat-purchase": { Icon: Package, label: "Reorder soon" },
};

export function ProtocolCard({
  title,
  subtitle,
  productIds,
  daysRemaining,
  source,
  onReorder,
  onReview,
  className,
}: ProtocolCardProps) {
  const { Icon, label } = sourceMeta[source];

  return (
    <section
      className={cn(
        "overflow-hidden rounded-hero border border-hairline bg-bone shadow-card",
        className,
      )}
    >
      <div className="flex items-start justify-between gap-4 p-5">
        <div>
          <div className="flex items-center gap-2 text-ink-muted">
            <Icon weight="regular" size={16} />
            <span data-micro>{label}</span>
          </div>
          <h3 className="mt-2 font-display text-xl text-ink">{title}</h3>
          {subtitle && (
            <p className="mt-1 text-sm text-ink-muted">{subtitle}</p>
          )}
        </div>
        {daysRemaining !== undefined && (
          <div className="text-right">
            <p data-num className="font-mono text-xl text-ink">
              {daysRemaining}
            </p>
            <p data-micro className="text-ink-subtle">days left</p>
          </div>
        )}
      </div>

      <div className="flex gap-3 overflow-x-auto px-5 pb-5 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
        {productIds.map((id) => (
          <div key={id} className="w-24 shrink-0 space-y-2">
            <PaperImage aspect="1/1" rounded="card" glyph="bottle" />
          </div>
        ))}
      </div>

      <div className="flex gap-2 border-t border-hairline p-3">
        {onReorder && (
          <button
            type="button"
            onClick={onReorder}
            className="u-tap inline-flex flex-1 items-center justify-center gap-2 rounded-pill bg-sage-deep px-4 py-2 text-sm font-medium text-bone"
          >
            <ArrowClockwise weight="regular" size={16} />
            Reorder stack
          </button>
        )}
        {onReview && source === "ai-assistant" && (
          <button
            type="button"
            onClick={onReview}
            className="u-tap inline-flex items-center justify-center rounded-pill border border-ink/30 px-4 py-2 text-sm font-medium text-ink"
          >
            Have a consultant review
          </button>
        )}
      </div>
    </section>
  );
}
