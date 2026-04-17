"use client";

import { motion } from "framer-motion";
import { CircleNotch } from "@phosphor-icons/react";
import type { ButtonProps } from "./primitives";
import { cn } from "@/lib/utils";

const variantStyles: Record<NonNullable<ButtonProps["variant"]>, string> = {
  primary:
    "bg-sage-deep text-bone hover:bg-ink disabled:bg-ink-muted disabled:text-bone",
  secondary:
    "bg-paper text-ink border border-ink/30 hover:border-ink disabled:border-hairline disabled:text-ink-subtle",
  ghost:
    "bg-transparent text-ink hover:bg-paper-deep disabled:text-ink-subtle",
};

const sizeStyles: Record<NonNullable<ButtonProps["size"]>, string> = {
  sm: "h-10 px-4 text-sm",
  md: "h-11 px-6 text-base",
  lg: "h-14 px-8 text-base",
};

export function Button({
  variant = "primary",
  size = "md",
  fullWidth,
  loading,
  disabled,
  leadingIcon,
  trailingIcon,
  onClick,
  type = "button",
  className,
  children,
}: ButtonProps) {
  return (
    <motion.button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      whileTap={disabled || loading ? undefined : { scale: 0.98 }}
      transition={{ type: "spring", stiffness: 420, damping: 38 }}
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-pill font-sans font-medium",
        "transition-colors duration-fast ease-quiet",
        "disabled:cursor-not-allowed",
        variantStyles[variant],
        sizeStyles[size],
        fullWidth && "w-full",
        className,
      )}
    >
      {loading ? (
        <CircleNotch weight="regular" className="animate-spin" size={18} />
      ) : (
        leadingIcon
      )}
      <span>{children}</span>
      {!loading && trailingIcon}
    </motion.button>
  );
}
