"use client";

import { motion } from "framer-motion";
import type { IconButtonProps } from "./primitives";
import { cn } from "@/lib/utils";

export function IconButton({
  icon,
  label,
  onClick,
  badge,
  tone = "neutral",
  className,
}: IconButtonProps) {
  const toneClass =
    tone === "alert"
      ? "text-alert"
      : tone === "signal"
        ? "text-signal"
        : tone === "sage"
          ? "text-sage-deep"
          : "text-ink";

  return (
    <motion.button
      type="button"
      onClick={onClick}
      aria-label={label}
      whileTap={{ scale: 0.92 }}
      transition={{ type: "spring", stiffness: 420, damping: 38 }}
      className={cn(
        "u-tap relative grid place-items-center rounded-pill",
        "hover:bg-paper-deep transition-colors duration-fast",
        toneClass,
        className,
      )}
    >
      {icon}
      {badge !== undefined && badge > 0 && (
        <span
          data-num
          className="absolute right-1 top-1 grid min-h-4 min-w-4 place-items-center rounded-pill bg-terracotta px-1 text-[10px] font-medium text-bone"
        >
          {badge > 99 ? "99+" : badge}
        </span>
      )}
    </motion.button>
  );
}
