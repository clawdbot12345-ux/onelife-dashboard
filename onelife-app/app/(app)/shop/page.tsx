"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { Sliders } from "@phosphor-icons/react";
import { SearchBar } from "@/components/SearchBar";
import { GoalFilter } from "@/components/GoalFilter";
import { ProductCard } from "@/components/ProductCard";
import { Chip } from "@/components/Chip";
import { Button } from "@/components/Button";
import { BottomSheet } from "@/components/BottomSheet";
import { MOCK_BRANDS, MOCK_PRODUCTS } from "@/lib/mock";
import type { Goal } from "@/components/primitives";

const ALL_GOALS: Goal[] = [
  "sleep", "energy", "stress", "gut", "immunity",
  "joints", "skin", "hormones", "focus", "recovery",
];

export default function ShopPage() {
  const router = useRouter();
  const [search, setSearch] = useState("");
  const [goals, setGoals] = useState<Goal[]>([]);
  const [brands, setBrands] = useState<string[]>([]);
  const [onlyVegan, setOnlyVegan] = useState(false);
  const [onlySaMade, setOnlySaMade] = useState(false);
  const [onlyInStock, setOnlyInStock] = useState(false);
  const [sheetOpen, setSheetOpen] = useState(false);

  const secondaryCount =
    brands.length + (onlyVegan ? 1 : 0) + (onlySaMade ? 1 : 0) + (onlyInStock ? 1 : 0);

  const products = useMemo(() => {
    const q = search.trim().toLowerCase();
    return MOCK_PRODUCTS.filter((p) => {
      if (q && !`${p.name} ${p.brand} ${p.benefit}`.toLowerCase().includes(q)) return false;
      if (goals.length && !p.goals.some((g) => goals.includes(g))) return false;
      if (brands.length && !brands.includes(p.brand)) return false;
      if (onlyVegan && !p.vegan) return false;
      if (onlySaMade && !p.saMade) return false;
      if (onlyInStock && !p.inStockAtUserStore) return false;
      return true;
    });
  }, [search, goals, brands, onlyVegan, onlySaMade, onlyInStock]);

  const clearAll = () => {
    setGoals([]);
    setBrands([]);
    setOnlyVegan(false);
    setOnlySaMade(false);
    setOnlyInStock(false);
  };

  return (
    <div className="pb-8 pt-4">
      {/* Top controls ---------------------------------------------- */}
      <div className="space-y-4 px-page-x">
        <SearchBar
          value={search}
          onChange={setSearch}
          onScan={() => {}}
          placeholder="Magnesium, Seed, sleep…"
        />
      </div>

      {/* Goal filter rail — the primary lens ---------------------- */}
      <div className="mt-5">
        <div className="mb-2 flex items-center justify-between px-page-x">
          <p data-micro>Filter by goal</p>
          <button
            type="button"
            onClick={() => setSheetOpen(true)}
            className="inline-flex items-center gap-1.5 text-sm font-medium text-ink"
          >
            <Sliders weight="regular" size={16} />
            More filters
            {secondaryCount > 0 && (
              <span
                data-num
                className="grid h-5 min-w-5 place-items-center rounded-pill bg-ink px-1 text-[10px] text-bone"
              >
                {secondaryCount}
              </span>
            )}
          </button>
        </div>
        <div className="px-page-x">
          <GoalFilter goals={ALL_GOALS} selected={goals} onChange={setGoals} />
        </div>
      </div>

      {/* Results count -------------------------------------------- */}
      <div className="mt-6 flex items-baseline justify-between px-page-x">
        <p className="text-sm text-ink-muted">
          <span data-num className="text-ink">{products.length}</span>{" "}
          {products.length === 1 ? "product" : "products"}
        </p>
        {(goals.length > 0 || secondaryCount > 0 || search) && (
          <button
            type="button"
            onClick={() => {
              setSearch("");
              clearAll();
            }}
            className="text-sm font-medium text-ink underline underline-offset-4"
          >
            Clear all
          </button>
        )}
      </div>

      {/* Grid ------------------------------------------------------ */}
      {products.length > 0 ? (
        <div className="mt-6 grid grid-cols-2 gap-x-4 gap-y-8 px-page-x md:grid-cols-3 lg:grid-cols-4">
          {products.map((p) => (
            <ProductCard
              key={p.id}
              id={p.id}
              slug={p.slug}
              name={p.name}
              brand={p.brand}
              imageUrl=""
              imageAlt={p.name}
              price={p.price}
              compareAtPrice={p.compareAtPrice}
              tag={
                p.pharmacistPick
                  ? { kind: "pharmacistPick" }
                  : p.saMade
                    ? { kind: "saMade" }
                    : undefined
              }
              inStockAtUserStore={p.inStockAtUserStore}
              onPress={(id) => {
                const prod = MOCK_PRODUCTS.find((x) => x.id === id);
                if (prod) router.push(`/product/${prod.slug}`);
              }}
            />
          ))}
        </div>
      ) : (
        <div className="mt-16 space-y-4 px-page-x text-center">
          <p data-micro>Nothing matches</p>
          <p className="mx-auto max-w-prose text-lg text-ink-muted">
            Widen your filters, or ask a pharmacist — they know the catalogue
            better than any search bar.
          </p>
          <div className="pt-2">
            <Button variant="secondary" onClick={() => router.push("/consult")}>
              Message a pharmacist
            </Button>
          </div>
        </div>
      )}

      {/* Secondary filter sheet ----------------------------------- */}
      <BottomSheet open={sheetOpen} onClose={() => setSheetOpen(false)} title="More filters">
        <div className="space-y-8 pb-4">
          <FilterGroup label="Brand">
            <div className="flex flex-wrap gap-2">
              {MOCK_BRANDS.map((brand) => (
                <Chip
                  key={brand}
                  label={brand}
                  selected={brands.includes(brand)}
                  onToggle={(next) =>
                    setBrands(next ? [...brands, brand] : brands.filter((b) => b !== brand))
                  }
                />
              ))}
            </div>
          </FilterGroup>

          <FilterGroup label="Dietary">
            <div className="flex flex-wrap gap-2">
              <Chip label="Vegan" selected={onlyVegan} onToggle={setOnlyVegan} />
              <Chip label="SA made" selected={onlySaMade} onToggle={setOnlySaMade} />
            </div>
          </FilterGroup>

          <FilterGroup label="Availability">
            <div className="flex flex-wrap gap-2">
              <Chip
                label="In stock at my store"
                selected={onlyInStock}
                onToggle={setOnlyInStock}
              />
            </div>
          </FilterGroup>

          <div className="flex gap-3 pt-2">
            <Button variant="ghost" onClick={clearAll}>Clear</Button>
            <Button fullWidth onClick={() => setSheetOpen(false)}>
              Show {products.length} {products.length === 1 ? "product" : "products"}
            </Button>
          </div>
        </div>
      </BottomSheet>
    </div>
  );
}

function FilterGroup({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <section className="space-y-3">
      <p data-micro>{label}</p>
      {children}
    </section>
  );
}
