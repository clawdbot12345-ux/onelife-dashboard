"use client";

import { motion } from "framer-motion";
import type { SubscriptionToggleProps } from "./primitives";
import { cn } from "@/lib/utils";

export function SubscriptionToggle({
  value,
  onChange,
  percentOff,
  cadenceLabel = "every 30 days",
  className,
}: SubscriptionToggleProps) {
  return (
    <div
      role="radiogroup"
      aria-label="Purchase type"
      className={cn("overflow-hidden rounded-card border border-hairline", className)}
    >
      {(["one-time", "subscribe"] as const).map((opt) => {
        const isActive = value === opt;
        return (
          <button
            key={opt}
            type="button"
            role="radio"
            aria-checked={isActive}
            onClick={() => onChange(opt)}
            className={cn(
              "relative flex w-full items-start justify-between gap-4 px-5 py-4 text-left transition-colors",
              isActive ? "bg-bone" : "bg-paper hover:bg-paper-deep/50",
              opt === "subscribe" && "border-t border-hairline",
            )}
          >
            <div>
              <div className="flex items-center gap-2">
                <span
                  aria-hidden
                  className={cn(
                    "grid h-4 w-4 place-items-center rounded-pill border",
                    isActive ? "border-ink" : "border-hairline",
                  )}
                >
                  {isActive && (
                    <motion.span
                      layoutId="sub-dot"
                      className="h-2 w-2 rounded-pill bg-ink"
                      transition={{ type: "spring", stiffness: 420, damping: 38 }}
                    />
                  )}
                </span>
                <span className="font-sans text-base text-ink">
                  {opt === "one-time" ? "One-time" : `Subscribe · save ${percentOff}%`}
                </span>
              </div>
              <p className="mt-1 pl-6 text-sm text-ink-muted">
                {opt === "one-time"
                  ? "Pay today. No commitment."
                  : `${cadenceLabel}. Free delivery. Cancel anytime.`}
              </p>
            </div>
          </button>
        );
      })}
    </div>
  );
}
