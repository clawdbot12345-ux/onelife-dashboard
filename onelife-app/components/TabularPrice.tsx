import type { TabularPriceProps } from "./primitives";
import { formatZar } from "@/lib/fmt";
import { cn } from "@/lib/utils";

const sizeStyles: Record<NonNullable<TabularPriceProps["size"]>, string> = {
  sm: "text-sm",
  md: "text-base",
  lg: "text-lg",
  display: "text-2xl",
};

export function TabularPrice({
  cents,
  format = "full",
  strike,
  size = "md",
  className,
}: TabularPriceProps) {
  return (
    <span
      data-num
      className={cn(
        "font-mono tabular-nums tracking-snug",
        strike && "line-through text-ink-subtle",
        sizeStyles[size],
        className,
      )}
    >
      {formatZar(cents, format)}
    </span>
  );
}
