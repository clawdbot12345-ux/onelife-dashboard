import Link from "next/link";
import { ArrowUpRight } from "@phosphor-icons/react";
import type { SectionHeaderProps } from "./primitives";
import { cn } from "@/lib/utils";

export function SectionHeader({
  eyebrow,
  title,
  description,
  action,
  className,
}: SectionHeaderProps) {
  return (
    <header
      className={cn(
        "flex items-end justify-between gap-6 px-page-x",
        className,
      )}
    >
      <div className="space-y-2">
        {eyebrow && <p data-micro>{eyebrow}</p>}
        <h2 className="font-display text-2xl leading-display tracking-snug text-ink">
          {title}
        </h2>
        {description && (
          <p className="max-w-prose text-sm text-ink-muted">{description}</p>
        )}
      </div>
      {action && (
        <Link
          href={action.href}
          className="inline-flex shrink-0 items-center gap-1 text-sm font-medium text-ink"
        >
          {action.label}
          <ArrowUpRight weight="regular" size={14} />
        </Link>
      )}
    </header>
  );
}
