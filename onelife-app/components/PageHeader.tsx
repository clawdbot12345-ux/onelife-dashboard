"use client";

import { CaretLeft } from "@phosphor-icons/react";
import type { PageHeaderProps } from "./primitives";
import { IconButton } from "./IconButton";
import { cn } from "@/lib/utils";

export function PageHeader({
  title,
  showBack,
  onBack,
  trailing,
  className,
}: PageHeaderProps) {
  return (
    <header
      className={cn(
        "sticky top-0 z-sticky flex h-14 items-center justify-between gap-3 bg-paper/90 px-2 backdrop-blur-md",
        className,
      )}
    >
      <div className="flex items-center gap-1">
        {showBack ? (
          <IconButton
            icon={<CaretLeft weight="regular" size={22} />}
            label="Back"
            onClick={() => onBack?.()}
          />
        ) : (
          <span
            data-micro
            className="pl-3 font-display text-base tracking-normal text-ink"
            style={{ fontVariant: "normal", textTransform: "none", letterSpacing: 0 }}
          >
            One Life
          </span>
        )}
      </div>
      {title && (
        <h1 className="font-display text-lg text-ink">{title}</h1>
      )}
      <div className="flex items-center gap-1">{trailing}</div>
    </header>
  );
}
