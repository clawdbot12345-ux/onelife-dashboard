"use client";

import { Leaf } from "@phosphor-icons/react";
import type {
  ContraindicationBannerProps,
  ContraindicationReason,
} from "./primitives";
import { cn } from "@/lib/utils";

const reasonCopy: Record<ContraindicationReason, string> = {
  pregnancy: "pregnancy",
  breastfeeding: "breastfeeding",
  "chronic-medication": "chronic medication",
  "age-under-18": "age under 18",
};

function joinWithOxford(items: string[]) {
  if (items.length <= 1) return items.join("");
  if (items.length === 2) return items.join(" and ");
  return `${items.slice(0, -1).join(", ")}, and ${items[items.length - 1]}`;
}

export function ContraindicationBanner({
  reasons,
  productName,
  onConsult,
  className,
}: ContraindicationBannerProps) {
  const phrase = joinWithOxford(reasons.map((r) => reasonCopy[r]));

  return (
    <aside
      className={cn(
        "flex gap-4 rounded-hero border border-sage/20 bg-sage/10 p-5",
        className,
      )}
      role="note"
    >
      <Leaf
        weight="regular"
        size={24}
        className="shrink-0 text-sage-deep"
        aria-hidden
      />
      <div>
        <p className="font-sans text-base text-ink">
          A quick word, before you add this.
        </p>
        <p className="mt-1 max-w-prose text-sm text-ink-muted">
          You told us about {phrase}. A health consultant should see {productName} first —
          some ingredients interact with common medicines, and we'd rather be
          certain than sorry.
        </p>
        <button
          type="button"
          onClick={onConsult}
          className="mt-3 inline-flex items-center gap-1 text-sm font-medium text-sage-deep underline underline-offset-4"
        >
          Message a health consultant
        </button>
      </div>
    </aside>
  );
}
