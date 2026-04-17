"use client";

import { useState } from "react";
import { Heart, Leaf, Moon } from "@phosphor-icons/react";
import { Button } from "@/components/Button";
import { Chip } from "@/components/Chip";
import { TabularPrice } from "@/components/TabularPrice";
import { ProductCard } from "@/components/ProductCard";
import { EditorialCard } from "@/components/EditorialCard";
import { ConsultationSlot } from "@/components/ConsultationSlot";
import { MembershipCard } from "@/components/MembershipCard";
import { GoalFilter } from "@/components/GoalFilter";
import { ContraindicationBanner } from "@/components/ContraindicationBanner";
import { ReviewBlock } from "@/components/ReviewBlock";
import { BottomSheet } from "@/components/BottomSheet";
import { ParallaxImage } from "@/components/ParallaxImage";
import { StoreCard } from "@/components/StoreCard";
import { ProtocolCard } from "@/components/ProtocolCard";
import { SectionHeader } from "@/components/SectionHeader";
import { SearchBar } from "@/components/SearchBar";
import { TabBar } from "@/components/TabBar";
import { IconButton } from "@/components/IconButton";
import { IngredientTable } from "@/components/IngredientTable";
import { ProtocolAssistantPrompt } from "@/components/ProtocolAssistantPrompt";
import type { Goal, TabKey } from "@/components/primitives";

// A single showcase page is the only way to keep visual coherence when
// the real screens arrive — every token and state visible together, so
// drift is caught by eye.

function TokenRow({ name, value, swatch }: { name: string; value: string; swatch?: string }) {
  return (
    <div className="flex items-center justify-between gap-4 border-b border-hairline py-3 last:border-b-0">
      <div className="flex items-center gap-4">
        {swatch && (
          <span
            aria-hidden
            className="h-10 w-10 rounded-card border border-hairline"
            style={{ background: swatch }}
          />
        )}
        <span className="font-sans text-sm text-ink">{name}</span>
      </div>
      <span data-num className="text-xs text-ink-muted">{value}</span>
    </div>
  );
}

function Group({ title, note, children }: { title: string; note?: string; children: React.ReactNode }) {
  return (
    <section className="space-y-6 border-t border-hairline pt-12 first:border-t-0 first:pt-0">
      <div>
        <p data-micro className="text-ink-muted">{title}</p>
        {note && <p className="mt-2 max-w-prose text-sm text-ink-muted">{note}</p>}
      </div>
      {children}
    </section>
  );
}

function Demo({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="space-y-2">
      <p data-micro>{label}</p>
      <div className="flex flex-wrap items-start gap-3 rounded-card bg-bone p-4">{children}</div>
    </div>
  );
}

export default function DesignShowcase() {
  const [goals, setGoals] = useState<Goal[]>(["sleep", "stress"]);
  const [tab, setTab] = useState<TabKey>("home");
  const [sheetOpen, setSheetOpen] = useState(false);
  const [search, setSearch] = useState("");

  return (
    <div className="mx-auto max-w-page px-page-x pb-32 pt-10">
      {/* Masthead ----------------------------------------------------- */}
      <header className="space-y-4 pb-12">
        <p data-micro>One Life Health · design system</p>
        <h1 className="font-display text-3xl tracking-tight">
          Apothecary Modern
        </h1>
        <p className="max-w-prose text-base text-ink-muted">
          A single surface to audit every token, primitive, and state. If a
          screen needs something that isn't here, we add it here first.
        </p>
      </header>

      {/* Palette ------------------------------------------------------ */}
      <Group title="Palette" note="Three accents do real work. Gold is reserved for membership. Signal / alert appear only on stock and errors.">
        <div className="grid gap-6 md:grid-cols-2">
          <div className="rounded-card border border-hairline bg-bone p-5">
            <TokenRow name="Ink" value="#1A1915" swatch="var(--ink)" />
            <TokenRow name="Ink · muted" value="#5C5A52" swatch="var(--ink-muted)" />
            <TokenRow name="Ink · subtle" value="#8A8578" swatch="var(--ink-subtle)" />
            <TokenRow name="Paper" value="#F4F1EA" swatch="var(--paper)" />
            <TokenRow name="Paper · deep" value="#EAE5DA" swatch="var(--paper-deep)" />
            <TokenRow name="Bone" value="#FFFCF5" swatch="var(--bone)" />
          </div>
          <div className="rounded-card border border-hairline bg-bone p-5">
            <TokenRow name="Sage" value="#6B7A5A" swatch="var(--sage)" />
            <TokenRow name="Sage · deep" value="#3E4A34" swatch="var(--sage-deep)" />
            <TokenRow name="Terracotta" value="#B5654A" swatch="var(--terracotta)" />
            <TokenRow name="Gold · rewards only" value="#B8934A" swatch="var(--gold)" />
            <TokenRow name="Signal · in-stock" value="#2C4A3A" swatch="var(--signal)" />
            <TokenRow name="Alert · out-of-stock" value="#8B3A2E" swatch="var(--alert)" />
          </div>
        </div>
      </Group>

      {/* Typography --------------------------------------------------- */}
      <Group title="Type" note="Fraunces (display), Inter Tight (UI), JetBrains Mono (numerics) — stand-ins for Canela / Söhne until licences land.">
        <div className="space-y-6 rounded-card bg-bone p-6">
          <div>
            <p data-micro>Display / 48</p>
            <p className="font-display text-3xl leading-display tracking-tight">A quieter way to live well.</p>
          </div>
          <div>
            <p data-micro>Display / 34</p>
            <p className="font-display text-2xl leading-display tracking-snug">Autumn in Pretoria — immunity season starts now.</p>
          </div>
          <div>
            <p data-micro>Display / 24</p>
            <p className="font-display text-xl leading-tight tracking-snug">Magnesium glycinate, citrate, orotate.</p>
          </div>
          <div>
            <p data-micro>Body / 18</p>
            <p className="text-lg text-ink-muted">Considered doses. Studied forms. Nothing that shouldn't be on your counter.</p>
          </div>
          <div>
            <p data-micro>Body / 16 · the floor for reading</p>
            <p className="max-w-prose text-base text-ink-muted">The smallest body text in the app. A 55-year-old should read this without reaching for glasses. If a designer proposes 14px body copy, politely decline.</p>
          </div>
          <div>
            <p data-micro>UI / 14 · metadata only</p>
            <p className="text-sm text-ink-subtle">Reviewer goal · in-stock line · timestamps.</p>
          </div>
          <div>
            <p data-micro>Mono · tabular</p>
            <p data-num className="text-lg">R 1 249.00 · 400 mg · 0800 012 345</p>
          </div>
          <hr />
          <p className="u-pullquote">
            Not clinical. Not bro-sciency. Not wellness influencer.
          </p>
        </div>
      </Group>

      {/* Spacing, radii, shadow --------------------------------------- */}
      <Group title="Space, radius, elevation">
        <div className="grid gap-6 md:grid-cols-3">
          <div className="rounded-card bg-bone p-5">
            <p data-micro className="mb-3">Spacing · 4pt</p>
            <div className="space-y-2">
              {[4, 8, 12, 16, 24, 32, 48, 64].map((v) => (
                <div key={v} className="flex items-center gap-3">
                  <div className="h-2 bg-sage-deep" style={{ width: v }} />
                  <span data-num className="text-xs text-ink-muted">{v}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="rounded-card bg-bone p-5">
            <p data-micro className="mb-3">Radius</p>
            <div className="space-y-3">
              <div className="h-10 rounded-card bg-paper-deep grid place-items-center text-xs text-ink-muted">card · 16</div>
              <div className="h-10 rounded-hero bg-paper-deep grid place-items-center text-xs text-ink-muted">hero · 24</div>
              <div className="h-10 rounded-pill bg-paper-deep grid place-items-center text-xs text-ink-muted">pill · 999</div>
            </div>
          </div>
          <div className="rounded-card bg-bone p-5">
            <p data-micro className="mb-3">Elevation · one token</p>
            <div className="h-24 rounded-card bg-bone shadow-card grid place-items-center text-xs text-ink-muted">
              card shadow
            </div>
          </div>
        </div>
      </Group>

      {/* Buttons ------------------------------------------------------ */}
      <Group title="Button">
        <Demo label="Variants">
          <Button variant="primary">Book a consultation</Button>
          <Button variant="secondary">Add to cart</Button>
          <Button variant="ghost">Skip for now</Button>
        </Demo>
        <Demo label="Sizes">
          <Button size="sm">Small</Button>
          <Button size="md">Medium</Button>
          <Button size="lg">Large</Button>
        </Demo>
        <Demo label="States">
          <Button loading>Booking</Button>
          <Button disabled>Out of stock</Button>
          <Button leadingIcon={<Leaf weight="regular" size={16} />}>Pharmacist pick</Button>
        </Demo>
      </Group>

      {/* Chips & GoalFilter ------------------------------------------- */}
      <Group title="Chip · Goal filter">
        <Demo label="Chip states">
          <Chip label="Sleep" selected={false} />
          <Chip label="Sleep" selected />
          <Chip label="Vegan" leadingIcon={<Leaf weight="regular" size={14} />} />
        </Demo>
        <Demo label="GoalFilter · max 3">
          <GoalFilter
            goals={["sleep", "energy", "stress", "gut", "immunity", "joints", "skin", "hormones", "focus", "recovery"]}
            selected={goals}
            onChange={setGoals}
            max={3}
          />
        </Demo>
      </Group>

      {/* TabularPrice ------------------------------------------------- */}
      <Group title="TabularPrice" note="Every ZAR amount in the app goes through this component.">
        <Demo label="Sizes">
          <TabularPrice cents={24900} size="sm" />
          <TabularPrice cents={24900} size="md" />
          <TabularPrice cents={24900} size="lg" />
          <TabularPrice cents={24900} size="display" />
        </Demo>
        <Demo label="Narrow / full / strike">
          <TabularPrice cents={24900} format="narrow" />
          <TabularPrice cents={24900} format="full" />
          <TabularPrice cents={29900} strike />
        </Demo>
      </Group>

      {/* ProductCard + EditorialCard ---------------------------------- */}
      <Group title="ProductCard · EditorialCard">
        <div className="grid gap-6 md:grid-cols-2">
          <div className="grid grid-cols-2 gap-4 rounded-card bg-bone p-4">
            <ProductCard
              id="1"
              slug="magnesium-glycinate"
              name="Magnesium Glycinate"
              brand="Vivid Health"
              imageUrl=""
              imageAlt="Magnesium Glycinate"
              price={24900}
              compareAtPrice={29900}
              tag={{ kind: "pharmacistPick" }}
            />
            <ProductCard
              id="2"
              slug="ashwagandha"
              name="Ashwagandha KSM-66"
              brand="Solgar"
              imageUrl=""
              imageAlt="Ashwagandha"
              price={38500}
              tag={{ kind: "saMade" }}
            />
            <ProductCard
              id="3"
              slug="probiotic"
              name="Daily Probiotic 50B"
              brand="Seed"
              imageUrl=""
              imageAlt="Probiotic"
              price={79900}
              tag={{ kind: "new" }}
              inStockAtUserStore={false}
            />
            <ProductCard
              id="4"
              slug="omega-3"
              name="Omega-3 1000mg"
              brand="Vivid Health"
              imageUrl=""
              imageAlt="Omega-3"
              price={21900}
              tag={{ kind: "subscribe", percentOff: 10 }}
            />
          </div>
          <EditorialCard
            eyebrow="Journal"
            title="Magnesium glycinate vs citrate vs orotate"
            excerpt="Same mineral, three different jobs. A buyer's note on when each one earns its place on your counter."
            imageUrl=""
            imageAlt="Still life of magnesium bottles on linen"
            href="/journal/magnesium"
            readingMinutes={4}
          />
        </div>
      </Group>

      {/* Consultation slots ------------------------------------------- */}
      <Group title="ConsultationSlot">
        <div className="space-y-3">
          <ConsultationSlot
            isoStart={new Date(Date.now() + 3600_000).toISOString()}
            durationMinutes={15}
            mode="in-store"
            storeName="Centurion"
            pharmacistName="Dr. Naledi Khumalo"
            onBook={() => {}}
          />
          <ConsultationSlot
            isoStart={new Date(Date.now() + 7200_000).toISOString()}
            durationMinutes={15}
            mode="video"
            pharmacistName="Ahmed Patel"
            onBook={() => {}}
          />
          <ConsultationSlot
            isoStart={new Date(Date.now() + 86_400_000).toISOString()}
            durationMinutes={30}
            mode="message"
            onBook={() => {}}
            disabled
          />
        </div>
      </Group>

      {/* MembershipCard ----------------------------------------------- */}
      <Group title="MembershipCard">
        <div className="grid gap-6 md:grid-cols-3">
          <MembershipCard memberName="Naadir" tier="seedling" points={120} pointsToNextTier={380} memberSince="2024-03-11" />
          <MembershipCard memberName="Lerato" tier="rooted" points={1540} pointsToNextTier={460} memberSince="2022-08-02" />
          <MembershipCard memberName="Sibusiso" tier="flourishing" points={5280} memberSince="2019-02-14" />
        </div>
      </Group>

      {/* Contraindication + Review + Ingredient ----------------------- */}
      <Group title="Contraindication · Review · Ingredient table">
        <ContraindicationBanner
          reasons={["pregnancy", "chronic-medication"]}
          productName="Ashwagandha KSM-66"
          onConsult={() => {}}
        />
        <div className="mt-6 rounded-card bg-bone p-6">
          <ReviewBlock rating={5} goal="sleep" body="Three weeks in and I'm asleep by 10:30, up by 6 without the alarm. Didn't expect something this quiet to move the needle." verifiedAt="2026-01-14" helpfulCount={18} />
          <ReviewBlock rating={4} goal="stress" body="Noticeable by week two. Less anxious on deadlines. Slight digestive issue the first few days, gone now." verifiedAt="2025-11-28" helpfulCount={6} />
        </div>
        <div className="mt-6">
          <IngredientTable
            servingSize="1 capsule"
            servingsPerContainer={60}
            rows={[
              { name: "Magnesium", form: "glycinate", amountPerServing: "200 mg", nrvPercent: 53 },
              { name: "Vitamin B6", form: "P-5-P", amountPerServing: "2 mg", nrvPercent: 143 },
              { name: "L-Theanine", amountPerServing: "100 mg" },
              { name: "Glycine", amountPerServing: "250 mg" },
            ]}
          />
        </div>
      </Group>

      {/* Search + Icon + Sheet + Parallax ----------------------------- */}
      <Group title="SearchBar · IconButton · BottomSheet · ParallaxImage">
        <Demo label="SearchBar with barcode scan">
          <SearchBar value={search} onChange={setSearch} onScan={() => {}} />
        </Demo>
        <Demo label="IconButton · with badge · tones">
          <IconButton icon={<Heart weight="regular" size={22} />} label="Save" onClick={() => {}} />
          <IconButton icon={<Heart weight="regular" size={22} />} label="Saved" onClick={() => {}} tone="sage" />
          <IconButton icon={<Moon weight="regular" size={22} />} label="Alerts" onClick={() => {}} badge={3} />
        </Demo>
        <Demo label="BottomSheet">
          <Button variant="secondary" onClick={() => setSheetOpen(true)}>Open sheet</Button>
        </Demo>
        <BottomSheet open={sheetOpen} onClose={() => setSheetOpen(false)} title="Secondary filters">
          <div className="space-y-4 pt-2">
            <p className="max-w-prose text-base text-ink-muted">Brand, dietary, price, in-stock at your store. The Shop tab opens this sheet for anything beyond a goal filter.</p>
            <div className="flex flex-wrap gap-2">
              <Chip label="Vegan" />
              <Chip label="Gluten-free" selected />
              <Chip label="SA made" />
              <Chip label="Under R300" />
            </div>
            <Button fullWidth onClick={() => setSheetOpen(false)}>Apply filters</Button>
          </div>
        </BottomSheet>
        <Demo label="ParallaxImage · scroll to see motion">
          <div className="h-80 w-full">
            <ParallaxImage src="" alt="Editorial still life" rounded="hero" aspectRatio="16/9" />
          </div>
        </Demo>
      </Group>

      {/* StoreCard + ProtocolCard + Assistant ------------------------- */}
      <Group title="StoreCard · ProtocolCard · Protocol Assistant">
        <div className="grid gap-6 md:grid-cols-2">
          <StoreCard
            storeId="centurion"
            name="Centurion"
            addressLine="Shop 6, The Grove Mall, Centurion"
            distanceKm={4.2}
            openUntil="18:30"
            phone="0800123456"
            mapImageUrl=""
            onDirections={() => {}}
            onCall={() => {}}
          />
          <ProtocolCard
            title="Your sleep stack"
            subtitle="Magnesium glycinate, L-theanine, ashwagandha"
            productIds={["1", "2", "3", "4"]}
            daysRemaining={11}
            source="consultation"
            onReorder={() => {}}
          />
        </div>
        <div className="mt-6">
          <ProtocolAssistantPrompt onSubmit={() => {}} />
        </div>
      </Group>

      {/* SectionHeader + TabBar --------------------------------------- */}
      <Group title="SectionHeader · TabBar">
        <SectionHeader
          eyebrow="This week"
          title="New at One Life"
          description="Three arrivals, curated by our buyers. No more, no fewer."
          action={{ label: "See all", href: "/shop" }}
        />
        <div className="relative mt-10 h-28 overflow-hidden rounded-hero border border-hairline bg-paper-deep/40">
          <div className="absolute inset-x-0 bottom-0">
            <TabBar active={tab} onNavigate={setTab} badges={{ shop: 2 }} />
          </div>
        </div>
      </Group>

      <footer className="mt-20 border-t border-hairline pt-8">
        <p data-micro>End of system</p>
        <p className="mt-2 max-w-prose text-sm text-ink-muted">
          Pass 3 brings Home and Product Detail. Hold off on celebrating until we
          see a product image on paper, a sticky add-to-cart bar in mono numerals,
          and a pharmacist's name on a consult card.
        </p>
      </footer>
    </div>
  );
}
