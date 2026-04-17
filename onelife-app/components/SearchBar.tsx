"use client";

import { MagnifyingGlass, Barcode, X } from "@phosphor-icons/react";
import type { SearchBarProps } from "./primitives";
import { cn } from "@/lib/utils";

export function SearchBar({
  value,
  onChange,
  onScan,
  placeholder = "Search products, brands, conditions",
  autoFocus,
  className,
}: SearchBarProps) {
  return (
    <div
      className={cn(
        "flex h-12 items-center gap-2 rounded-pill border border-hairline bg-bone px-4",
        "focus-within:border-ink/40",
        className,
      )}
    >
      <MagnifyingGlass weight="regular" size={18} className="text-ink-muted" aria-hidden />
      <input
        type="search"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        autoFocus={autoFocus}
        className="flex-1 bg-transparent text-base text-ink placeholder:text-ink-subtle focus:outline-none"
        aria-label="Search"
      />
      {value && (
        <button
          type="button"
          onClick={() => onChange("")}
          aria-label="Clear search"
          className="u-tap -mr-2 grid place-items-center text-ink-muted"
        >
          <X weight="regular" size={16} />
        </button>
      )}
      {onScan && (
        <button
          type="button"
          onClick={onScan}
          aria-label="Scan barcode"
          className="u-tap -mr-2 grid place-items-center text-ink"
        >
          <Barcode weight="regular" size={20} />
        </button>
      )}
    </div>
  );
}
