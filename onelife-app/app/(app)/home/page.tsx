"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowRight } from "@phosphor-icons/react";
import { SectionHeader } from "@/components/SectionHeader";
import { ProtocolCard } from "@/components/ProtocolCard";
import { ConsultationSlot } from "@/components/ConsultationSlot";
import { EditorialCard } from "@/components/EditorialCard";
import { ProductCard } from "@/components/ProductCard";
import { StoreCard } from "@/components/StoreCard";
import { PaperImage } from "@/components/PaperImage";
import {
  MOCK_CONSULT_SLOTS,
  MOCK_EDITORIAL,
  MOCK_PRODUCTS,
  MOCK_STORES,
  MOCK_THIS_WEEK,
} from "@/lib/mock";
import { useUser } from "@/lib/user";

function greeting(): string {
  const h = new Date().getHours();
  if (h < 12) return "Good morning";
  if (h < 17) return "Good afternoon";
  return "Good evening";
}

export default function HomePage() {
  const router = useRouter();
  const { firstName, selectedGoals } = useUser();

  // Curated rail: products that share at least one goal with the user.
  const curated = MOCK_PRODUCTS.filter((p) =>
    p.goals.some((g) => selectedGoals.includes(g)),
  ).slice(0, 4);

  const nearestStore = MOCK_STORES[0]!;

  const goToProduct = (id: string) => {
    const p = MOCK_PRODUCTS.find((x) => x.id === id);
    if (p) router.push(`/product/${p.slug}`);
  };

  return (
    <div className="space-y-section pt-4">
      {/* Greeting --------------------------------------------------- */}
      <section className="px-page-x">
        <p data-micro className="text-ink-muted">
          Autumn in Pretoria · immunity season starts now
        </p>
        <h1 className="mt-3 font-display text-3xl leading-display tracking-tight text-ink">
          {greeting()}, {firstName}.
        </h1>
      </section>

      {/* Your protocol --------------------------------------------- */}
      <section className="space-y-5">
        <SectionHeader
          eyebrow="Your protocol"
          title="Still on track."
          action={{ label: "All protocols", href: "/account" }}
        />
        <div className="px-page-x">
          <ProtocolCard
            title="Sleep stack"
            subtitle="Magnesium glycinate · L-theanine · Ashwagandha"
            productIds={["p-mag-glycinate", "p-l-theanine", "p-ashwagandha"]}
            daysRemaining={11}
            source="consultation"
            onReorder={() => router.push("/shop")}
          />
        </div>
      </section>

      {/* Book a consultation --------------------------------------- */}
      <section className="space-y-5">
        <SectionHeader
          eyebrow="Consult"
          title="Talk to a health consultant."
          description="Free, fifteen minutes, no obligation. Today's earliest below."
          action={{ label: "All slots", href: "/consult" }}
        />
        <div className="space-y-3 px-page-x">
          {MOCK_CONSULT_SLOTS.slice(0, 2).map((slot) => (
            <ConsultationSlot
              key={slot.isoStart}
              isoStart={slot.isoStart}
              durationMinutes={slot.durationMinutes}
              mode={slot.mode}
              storeName={slot.storeName}
              consultantName={slot.consultantName}
              onBook={() => router.push("/consult")}
            />
          ))}
        </div>
      </section>

      {/* Editorial hero -------------------------------------------- */}
      <section className="px-page-x">
        <EditorialCard
          eyebrow={MOCK_EDITORIAL.eyebrow}
          title={MOCK_EDITORIAL.title}
          excerpt={MOCK_EDITORIAL.excerpt}
          imageUrl=""
          imageAlt="Three magnesium bottles on linen, morning light"
          href={MOCK_EDITORIAL.href}
          readingMinutes={MOCK_EDITORIAL.readingMinutes}
        />
      </section>

      {/* Curated for you ------------------------------------------ */}
      <section className="space-y-5">
        <SectionHeader
          eyebrow="Curated for you"
          title="Chosen around your goals."
          description={`Based on ${selectedGoals.join(", ")}.`}
          action={{ label: "Shop all", href: "/shop" }}
        />
        <div
          className="flex gap-4 overflow-x-auto px-page-x pb-2 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
          role="region"
          aria-label="Curated products"
        >
          {curated.map((p) => (
            <div key={p.id} className="w-[58%] shrink-0 md:w-56">
              <ProductCard
                id={p.id}
                slug={p.slug}
                name={p.name}
                brand={p.brand}
                imageUrl=""
                imageAlt={p.name}
                price={p.price}
                compareAtPrice={p.compareAtPrice}
                tag={
                  p.consultantPick
                    ? { kind: "consultantPick" }
                    : p.saMade
                      ? { kind: "saMade" }
                      : undefined
                }
                inStockAtUserStore={p.inStockAtUserStore}
                onPress={goToProduct}
              />
            </div>
          ))}
        </div>
      </section>

      {/* This week ------------------------------------------------- */}
      <section className="space-y-5">
        <SectionHeader
          eyebrow="This week"
          title="At One Life."
        />
        <ul className="space-y-px">
          {MOCK_THIS_WEEK.map((item) => (
            <li key={item.id}>
              <Link
                href={item.href}
                className="flex items-center gap-4 border-t border-hairline bg-bone px-page-x py-4 transition-colors hover:bg-paper-deep/40 last:border-b last:border-b-hairline"
              >
                <div className="h-14 w-14 shrink-0 overflow-hidden rounded-card">
                  <PaperImage aspect="1/1" rounded="none" glyph="leaf" />
                </div>
                <div className="min-w-0 flex-1">
                  <p data-micro>{item.eyebrow}</p>
                  <p className="mt-1 truncate font-sans text-base text-ink">{item.title}</p>
                </div>
                <ArrowRight weight="regular" size={18} className="text-ink-muted" />
              </Link>
            </li>
          ))}
        </ul>
      </section>

      {/* Visit a store -------------------------------------------- */}
      <section className="space-y-5">
        <SectionHeader
          eyebrow="Visit"
          title="Your nearest store."
          action={{ label: "All stores", href: "/account" }}
        />
        <div className="px-page-x">
          <StoreCard
            storeId={nearestStore.id}
            name={nearestStore.name}
            addressLine={nearestStore.addressLine}
            distanceKm={nearestStore.distanceKm}
            openUntil={nearestStore.openUntil}
            phone={nearestStore.phone}
            mapImageUrl=""
            onDirections={() => {}}
            onCall={() => {
              if (typeof window !== "undefined") {
                window.location.href = `tel:${nearestStore.phone}`;
              }
            }}
          />
        </div>
      </section>
    </div>
  );
}
