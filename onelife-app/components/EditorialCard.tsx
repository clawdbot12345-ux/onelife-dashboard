"use client";

import Link from "next/link";
import type { EditorialCardProps } from "./primitives";
import { PaperImage } from "./PaperImage";
import { cn } from "@/lib/utils";

export function EditorialCard({
  eyebrow,
  title,
  excerpt,
  imageAlt,
  href,
  readingMinutes,
  className,
}: EditorialCardProps) {
  return (
    <Link
      href={href}
      className={cn(
        "group block overflow-hidden rounded-hero bg-bone shadow-card",
        className,
      )}
    >
      <PaperImage aspect="16/9" label={imageAlt} glyph="leaf" rounded="none" />
      <div className="space-y-3 p-6">
        {eyebrow && <p data-micro>{eyebrow}</p>}
        <h3 className="font-display text-xl leading-tight">{title}</h3>
        {excerpt && (
          <p className="max-w-prose text-base text-ink-muted">{excerpt}</p>
        )}
        {readingMinutes && (
          <p data-micro className="text-ink-subtle">
            {readingMinutes} min read
          </p>
        )}
      </div>
    </Link>
  );
}
