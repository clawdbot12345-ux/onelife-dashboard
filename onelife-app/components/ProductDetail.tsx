"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Sun, ForkKnife, MoonStars, ArrowRight, Leaf } from "@phosphor-icons/react";
import type { MockProduct, MockReview } from "@/lib/mock";
import { useUser } from "@/lib/user";
import { Button } from "./Button";
import { Tabs } from "./Tabs";
import { TabularPrice } from "./TabularPrice";
import { ParallaxImage } from "./ParallaxImage";
import { IngredientTable } from "./IngredientTable";
import { ReviewBlock } from "./ReviewBlock";
import { ProductCard } from "./ProductCard";
import { ContraindicationBanner } from "./ContraindicationBanner";
import { SectionHeader } from "./SectionHeader";
import { SubscriptionToggle } from "./SubscriptionToggle";
import { cn } from "@/lib/utils";

type TabKey = "why" | "how" | "inside" | "evidence" | "pairs";

const TAB_ITEMS: { key: TabKey; label: string }[] = [
  { key: "why", label: "Why we stock it" },
  { key: "how", label: "How to take it" },
  { key: "inside", label: "What's inside" },
  { key: "evidence", label: "Evidence" },
  { key: "pairs", label: "Pairs well with" },
];

const timingMeta: Record<
  MockProduct["howToTake"][number]["timing"],
  { Icon: typeof Sun; label: string }
> = {
  morning: { Icon: Sun, label: "Morning" },
  "with-food": { Icon: ForkKnife, label: "With food" },
  evening: { Icon: MoonStars, label: "Evening" },
};

const SUB_PERCENT = 10;

export function ProductDetail({
  product,
  reviews,
  pairsWith,
}: {
  product: MockProduct;
  reviews: MockReview[];
  pairsWith: MockProduct[];
}) {
  const router = useRouter();
  const addToCart = useUser((s) => s.addToCart);
  const contraindications = useUser((s) => s.contraindications);

  const [tab, setTab] = useState<TabKey>("why");
  const [purchase, setPurchase] = useState<"one-time" | "subscribe">("one-time");

  const livePrice =
    purchase === "subscribe"
      ? Math.round(product.price * (1 - SUB_PERCENT / 100))
      : product.price;

  const avgRating = reviews.length
    ? Math.round(reviews.reduce((s, r) => s + r.rating, 0) / reviews.length)
    : undefined;

  return (
    <article className="pb-32">
      {/* Hero ------------------------------------------------------- */}
      <div className="bg-paper-deep/40">
        <div className="mx-auto max-w-[520px] px-page-x pb-6 pt-2">
          <ParallaxImage
            src=""
            alt={`${product.name} on linen, morning light`}
            aspectRatio="3/4"
            rounded="hero"
          />
        </div>
      </div>

      {/* Above the fold -------------------------------------------- */}
      <header className="space-y-5 px-page-x pt-8">
        <div>
          <p data-micro>{product.brand}</p>
          <h1 className="mt-2 font-display text-2xl leading-display tracking-tight text-ink">
            {product.name}
          </h1>
          <p className="mt-2 max-w-prose text-base text-ink-muted">
            {product.benefit}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-sm text-ink-muted">
          {avgRating && (
            <span className="flex items-center gap-2">
              <span data-num className="text-ink">{avgRating}.0</span>
              <span>· {reviews.length} verified reviews</span>
            </span>
          )}
          <span>
            <span data-num className="text-ink">{product.dosagePerDay}</span> per day
          </span>
          <span>
            <span data-num className="text-ink">{product.daysSupplyPerBottle}</span>-day supply
          </span>
        </div>

        <div className="flex items-baseline gap-3 pt-1">
          <TabularPrice cents={livePrice} size="display" />
          {purchase === "subscribe" && (
            <TabularPrice cents={product.price} strike size="md" />
          )}
        </div>

        <SubscriptionToggle
          value={purchase}
          onChange={setPurchase}
          percentOff={SUB_PERCENT}
          cadenceLabel={`every ${product.daysSupplyPerBottle} days`}
        />

        {contraindications.length > 0 && (
          <ContraindicationBanner
            reasons={contraindications}
            productName={product.name}
            onConsult={() => router.push("/consult")}
          />
        )}

        <div className="flex flex-wrap gap-2 pt-1">
          {product.pharmacistPick && (
            <span className="inline-flex items-center gap-1.5 rounded-pill bg-sage/10 px-3 py-1.5 text-sm text-sage-deep">
              <Leaf weight="regular" size={14} /> Pharmacist pick
            </span>
          )}
          {product.saMade && (
            <span className="rounded-pill border border-hairline px-3 py-1.5 text-sm text-ink">
              SA made
            </span>
          )}
          {product.vegan && (
            <span className="rounded-pill border border-hairline px-3 py-1.5 text-sm text-ink">
              Vegan
            </span>
          )}
        </div>
      </header>

      {/* Tabs ------------------------------------------------------- */}
      <div className="mt-10">
        <Tabs items={TAB_ITEMS} active={tab} onChange={setTab} sticky />
        <div className="px-page-x py-8">
          {tab === "why" && (
            <div className="max-w-prose space-y-5">
              <p data-micro>A note from the buyer</p>
              <p className="text-lg leading-[1.55] text-ink">
                {product.buyersNote}
              </p>
            </div>
          )}

          {tab === "how" && (
            <div className="grid gap-4 sm:grid-cols-3">
              {product.howToTake.map((s) => {
                const { Icon, label } = timingMeta[s.timing];
                return (
                  <div
                    key={s.timing}
                    className="rounded-card border border-hairline bg-bone p-5"
                  >
                    <div className="flex items-center gap-2 text-ink">
                      <Icon weight="regular" size={18} />
                      <span data-micro className="text-ink">{label}</span>
                    </div>
                    <p className="mt-3 text-base leading-[1.55] text-ink-muted">
                      {s.text}
                    </p>
                  </div>
                );
              })}
            </div>
          )}

          {tab === "inside" && (
            <IngredientTable
              rows={product.ingredients}
              servingSize={product.dosagePerDay}
              servingsPerContainer={product.daysSupplyPerBottle}
            />
          )}

          {tab === "evidence" && (
            <ul className="divide-y divide-hairline overflow-hidden rounded-card border border-hairline bg-bone">
              {product.evidence.map((e) => (
                <li key={e.url}>
                  <a
                    href={e.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center justify-between gap-4 p-5 transition-colors hover:bg-paper-deep/40"
                  >
                    <div className="min-w-0">
                      <p className="font-sans text-base text-ink">{e.title}</p>
                      <p data-micro className="mt-1 text-ink-subtle">
                        {e.journal} · {e.year}
                      </p>
                    </div>
                    <ArrowRight weight="regular" size={18} className="shrink-0 text-ink-muted" />
                  </a>
                </li>
              ))}
            </ul>
          )}

          {tab === "pairs" && (
            <div className="grid grid-cols-2 gap-4 md:grid-cols-3">
              {pairsWith.map((p) => (
                <ProductCard
                  key={p.id}
                  id={p.id}
                  slug={p.slug}
                  name={p.name}
                  brand={p.brand}
                  imageUrl=""
                  imageAlt={p.name}
                  price={p.price}
                  tag={
                    p.pharmacistPick
                      ? { kind: "pharmacistPick" }
                      : p.saMade
                        ? { kind: "saMade" }
                        : undefined
                  }
                  onPress={(id) => router.push(`/product/${pairsWith.find((x) => x.id === id)!.slug}`)}
                />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Reviews ---------------------------------------------------- */}
      {reviews.length > 0 && (
        <section className="space-y-6 pt-4">
          <SectionHeader
            eyebrow="Verified reviews"
            title={`What ${reviews.length} customers said.`}
            description="Verified purchase only. Reviewers name their goal, not themselves."
          />
          <div className="space-y-5 px-page-x">
            {reviews.map((r, i) => (
              <ReviewBlock
                key={i}
                rating={r.rating}
                goal={r.goal}
                body={r.body}
                verifiedAt={r.verifiedAt}
                helpfulCount={r.helpfulCount}
              />
            ))}
          </div>
        </section>
      )}

      {/* Sticky add-to-cart --------------------------------------- */}
      <StickyBar
        price={livePrice}
        subscribe={purchase === "subscribe"}
        inStock={product.inStockAtUserStore}
        onAdd={() => addToCart()}
      />
    </article>
  );
}

function StickyBar({
  price,
  subscribe,
  inStock,
  onAdd,
}: {
  price: number;
  subscribe: boolean;
  inStock: boolean;
  onAdd: () => void;
}) {
  return (
    <motion.div
      initial={{ y: 80, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ type: "spring", stiffness: 280, damping: 32, delay: 0.2 }}
      className={cn(
        "fixed inset-x-0 bottom-[calc(env(safe-area-inset-bottom)+76px)] z-sticky",
        "mx-auto flex max-w-page items-center justify-between gap-4 border-t border-hairline bg-paper/95 px-page-x py-3 backdrop-blur-md",
      )}
    >
      <div className="min-w-0">
        <TabularPrice cents={price} size="lg" />
        <p data-micro className="mt-0.5 text-ink-muted">
          {subscribe ? "Subscription · free delivery" : "Excl. VAT"}
        </p>
      </div>
      <Button
        variant="primary"
        size="md"
        onClick={onAdd}
        disabled={!inStock}
      >
        {inStock ? "Add to cart" : "Out of stock"}
      </Button>
    </motion.div>
  );
}
