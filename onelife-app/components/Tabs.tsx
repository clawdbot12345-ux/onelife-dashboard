"use client";

import { motion } from "framer-motion";
import type { TabsProps } from "./primitives";
import { cn } from "@/lib/utils";

export function Tabs<T extends string>({
  items,
  active,
  onChange,
  sticky,
  className,
}: TabsProps<T>) {
  return (
    <div
      role="tablist"
      className={cn(
        "flex gap-1 overflow-x-auto border-b border-hairline bg-paper/90 px-page-x backdrop-blur-md",
        "[scrollbar-width:none] [&::-webkit-scrollbar]:hidden",
        sticky && "sticky top-14 z-sticky",
        className,
      )}
    >
      {items.map((item) => {
        const isActive = item.key === active;
        return (
          <button
            key={item.key}
            role="tab"
            aria-selected={isActive}
            onClick={() => onChange(item.key)}
            className={cn(
              "relative whitespace-nowrap px-3 py-3.5 font-sans text-sm transition-colors",
              isActive ? "text-ink" : "text-ink-muted hover:text-ink",
            )}
          >
            {item.label}
            {isActive && (
              <motion.span
                layoutId="tabs-underline"
                className="absolute inset-x-3 -bottom-px h-px bg-ink"
                transition={{ type: "spring", stiffness: 420, damping: 38 }}
              />
            )}
          </button>
        );
      })}
    </div>
  );
}
