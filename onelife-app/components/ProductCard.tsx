"use client";

import { motion } from "framer-motion";
import type { ProductCardProps, ProductTag } from "./primitives";
import { TabularPrice } from "./TabularPrice";
import { PaperImage } from "./PaperImage";
import { cn } from "@/lib/utils";

// Tag precedence encoded in the type already; this just maps to copy + tone.
const tagCopy = (tag: ProductTag) => {
  switch (tag.kind) {
    case "pharmacistPick":
      return { label: "Pharmacist pick", tone: "sage" as const };
    case "saMade":
      return { label: "SA made", tone: "ink" as const };
    case "new":
      return { label: "New", tone: "ink" as const };
    case "subscribe":
      return { label: `Subscribe · ${tag.percentOff}%`, tone: "terracotta" as const };
  }
};

export function ProductCard({
  id,
  name,
  brand,
  imageAlt,
  price,
  compareAtPrice,
  tag,
  inStockAtUserStore,
  onPress,
  className,
}: ProductCardProps) {
  const t = tag ? tagCopy(tag) : null;

  return (
    <motion.button
      type="button"
      onClick={() => onPress?.(id)}
      whileTap={{ scale: 0.98 }}
      transition={{ type: "spring", stiffness: 420, damping: 38 }}
      className={cn(
        "group flex w-full flex-col items-start gap-3 text-left",
        className,
      )}
    >
      <div className="relative w-full">
        <PaperImage aspect="4/5" label={imageAlt} glyph="bottle" />
        {t && (
          <span
            data-micro
            className={cn(
              "absolute left-3 top-3 rounded-pill bg-bone/90 px-2 py-1 backdrop-blur-sm",
              t.tone === "sage" && "text-sage-deep",
              t.tone === "terracotta" && "text-terracotta",
              t.tone === "ink" && "text-ink",
            )}
          >
            {t.label}
          </span>
        )}
      </div>

      <div className="w-full px-1">
        <p data-micro className="mb-1 text-ink-subtle">
          {brand}
        </p>
        <h3 className="font-display text-lg leading-tight text-ink">
          {name}
        </h3>
        <div className="mt-2 flex items-baseline gap-2">
          <TabularPrice cents={price} format="full" />
          {compareAtPrice && compareAtPrice > price && (
            <TabularPrice cents={compareAtPrice} format="full" size="sm" strike />
          )}
        </div>
        {inStockAtUserStore === false && (
          <p data-micro className="mt-2 text-alert">
            Out of stock at your store
          </p>
        )}
      </div>
    </motion.button>
  );
}
