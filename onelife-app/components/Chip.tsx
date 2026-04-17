"use client";

import { motion } from "framer-motion";
import type { ChipProps } from "./primitives";
import { cn } from "@/lib/utils";

export function Chip({
  label,
  selected = false,
  onToggle,
  leadingIcon,
  size = "md",
  className,
}: ChipProps) {
  const height = size === "sm" ? "h-9 text-sm px-3" : "h-10 text-sm px-4";

  return (
    <motion.button
      type="button"
      role="checkbox"
      aria-checked={selected}
      onClick={() => onToggle?.(!selected)}
      whileTap={{ scale: 0.97 }}
      transition={{ type: "spring", stiffness: 420, damping: 38 }}
      className={cn(
        "inline-flex items-center gap-2 rounded-pill border font-sans",
        "transition-colors duration-fast ease-quiet",
        height,
        selected
          ? "bg-ink text-bone border-ink"
          : "bg-paper text-ink border-hairline hover:border-ink/40",
        className,
      )}
    >
      {leadingIcon && <span className="shrink-0">{leadingIcon}</span>}
      <span className="whitespace-nowrap">{label}</span>
    </motion.button>
  );
}
