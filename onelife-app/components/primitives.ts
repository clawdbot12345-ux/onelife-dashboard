/**
 * One Life Health — component API sketches
 *
 * Pass 1 deliverable: typed contracts only, no implementations.
 * Every component in the app comes from this file. If a screen needs
 * something that isn't here, we add it here first, then build it.
 *
 * Design rules encoded as types:
 *   - Colours are enums of palette tokens, never arbitrary strings.
 *   - ProductCard shows at most ONE tag. The union enforces it.
 *   - MembershipTier is closed. No "platinum" surprises.
 *   - Motion is always opt-out via `prefers-reduced-motion`, not opt-in.
 */

import type { ReactNode } from "react";

/* ------------------------------------------------------------------ */
/* Shared primitives                                                   */
/* ------------------------------------------------------------------ */

export type PaletteAccent = "sage" | "terracotta" | "gold";
export type Tone = "neutral" | "signal" | "alert" | "sage";
export type Size = "sm" | "md" | "lg";

export interface WithChildren { children: ReactNode; }
export interface WithClassName { className?: string; }

export type ZARCents = number; // store prices as integer cents, render with TabularPrice

/* ------------------------------------------------------------------ */
/* 01. Button                                                          */
/* Primary = sage-deep fill, Secondary = ink outline on paper,         */
/* Ghost = ink text only. No tertiary.                                 */
/* ------------------------------------------------------------------ */
export interface ButtonProps extends WithClassName {
  variant?: "primary" | "secondary" | "ghost";
  size?: Size;
  fullWidth?: boolean;
  loading?: boolean;
  disabled?: boolean;
  leadingIcon?: ReactNode;
  trailingIcon?: ReactNode;
  onClick?: () => void;
  type?: "button" | "submit";
  children: ReactNode;
  /** For analytics — required on any commerce CTA. */
  eventName?: string;
}

/* ------------------------------------------------------------------ */
/* 02. Chip                                                            */
/* Filter rail, onboarding goals, dietary tags. Pill radius, 36px tap. */
/* ------------------------------------------------------------------ */
export interface ChipProps extends WithClassName {
  label: string;
  selected?: boolean;
  onToggle?: (next: boolean) => void;
  leadingIcon?: ReactNode;
  /** Capped at 8 per rail; keep copy to ≤2 words. */
  size?: "sm" | "md";
}

/* ------------------------------------------------------------------ */
/* 03. TabularPrice                                                    */
/* The only way to render a ZAR amount. VAT-exclusive by default,      */
/* match the storefront. Never use it for non-money numbers.           */
/* ------------------------------------------------------------------ */
export interface TabularPriceProps extends WithClassName {
  cents: ZARCents;
  /** "R 249.00" vs "R249". Most surfaces use "narrow". */
  format?: "narrow" | "full";
  strike?: boolean;
  size?: "sm" | "md" | "lg" | "display";
}

/* ------------------------------------------------------------------ */
/* 04. ProductCard                                                     */
/* Shop grid + Curated-for-you rails. ONE tag max — the union enforces */
/* precedence: consultantPick > saMade > new > subscribe.              */
/* Label: "Consultant pick" — credentialed in-house role, brand rule.  */
/* ------------------------------------------------------------------ */
export type ProductTag =
  | { kind: "consultantPick" }
  | { kind: "saMade" }
  | { kind: "new" }
  | { kind: "subscribe"; percentOff: number };

export interface ProductCardProps extends WithClassName {
  id: string;
  slug: string;
  name: string;
  brand: string;
  imageUrl: string;
  imageAlt: string;
  price: ZARCents;
  compareAtPrice?: ZARCents;
  tag?: ProductTag;
  inStockAtUserStore?: boolean;
  onPress?: (id: string) => void;
  priority?: boolean; // next/image LCP hint
}

/* ------------------------------------------------------------------ */
/* 05. EditorialCard                                                   */
/* Full-bleed Health Hub hero. Parallax on scroll, 8s duration.        */
/* ------------------------------------------------------------------ */
export interface EditorialCardProps extends WithClassName {
  eyebrow?: string;          // "Journal" / "Buyer's note"
  title: string;
  excerpt?: string;
  imageUrl: string;
  imageAlt: string;
  href: string;
  readingMinutes?: number;
  parallax?: boolean;
}

/* ------------------------------------------------------------------ */
/* 06. ConsultationSlot                                                */
/* Single bookable slot. Grouped into a day by the caller.             */
/* ------------------------------------------------------------------ */
export type ConsultMode = "in-store" | "video" | "message";

export interface ConsultationSlotProps extends WithClassName {
  isoStart: string;          // "2026-04-18T09:30:00+02:00"
  durationMinutes: number;
  mode: ConsultMode;
  storeName?: string;        // required if mode === "in-store"
  consultantName?: string;
  consultantImageUrl?: string;
  onBook: (isoStart: string) => void;
  disabled?: boolean;
}

/* ------------------------------------------------------------------ */
/* 07. MembershipCard                                                  */
/* Rewards hero. Gradient tier-wash, tabular points, 2px progress line.*/
/* ------------------------------------------------------------------ */
export type MembershipTier = "seedling" | "rooted" | "flourishing";

export interface MembershipCardProps extends WithClassName {
  memberName: string;
  tier: MembershipTier;
  points: number;
  pointsToNextTier?: number; // omit when at top tier
  memberSince: string;       // ISO date
}

/* ------------------------------------------------------------------ */
/* 08. GoalFilter                                                      */
/* Primary filter rail on Shop. Horizontal scroll on mobile.           */
/* ------------------------------------------------------------------ */
export type Goal =
  | "sleep" | "energy" | "stress" | "gut" | "immunity"
  | "joints" | "skin" | "hormones" | "focus" | "recovery";

export interface GoalFilterProps extends WithClassName {
  goals: Goal[];
  selected: Goal[];
  onChange: (next: Goal[]) => void;
  /** Max selectable. Onboarding = 3, Shop = unlimited. */
  max?: number;
}

/* ------------------------------------------------------------------ */
/* 09. ContraindicationBanner                                          */
/* Sage background, never red — warmth over alarm. Shown on PDP when   */
/* user flagged pregnancy / breastfeeding / chronic meds.              */
/* ------------------------------------------------------------------ */
export type ContraindicationReason =
  | "pregnancy" | "breastfeeding" | "chronic-medication" | "age-under-18";

export interface ContraindicationBannerProps extends WithClassName {
  reasons: ContraindicationReason[];
  productName: string;
  onConsult: () => void;     // routes to Consult tab pre-filled
}

/* ------------------------------------------------------------------ */
/* 10. ReviewBlock                                                     */
/* Verified purchase only. Shows reviewer goal, not name.              */
/* ------------------------------------------------------------------ */
export interface ReviewBlockProps extends WithClassName {
  rating: 1 | 2 | 3 | 4 | 5;
  goal: Goal;
  body: string;
  verifiedAt: string;        // ISO
  helpfulCount?: number;
}

/* ------------------------------------------------------------------ */
/* 11. BottomSheet                                                     */
/* Native-feel modal sheet. Drag to dismiss. Used for secondary        */
/* filters, size-picker, consult confirmation.                         */
/* ------------------------------------------------------------------ */
export interface BottomSheetProps extends WithChildren, WithClassName {
  open: boolean;
  onClose: () => void;
  title?: string;
  /** If true, sheet snaps to 50% before 100%. Default false. */
  snap?: boolean;
  dismissible?: boolean;     // false = force user to choose
}

/* ------------------------------------------------------------------ */
/* 12. ParallaxImage                                                   */
/* Hero imagery wrapper. Respects reduced-motion.                      */
/* ------------------------------------------------------------------ */
export interface ParallaxImageProps extends WithClassName {
  src: string;
  alt: string;
  aspectRatio?: "4/5" | "1/1" | "3/4" | "16/9";
  rounded?: "none" | "card" | "hero";
  strength?: number;         // 0–1, default 0.15
  priority?: boolean;
}

/* ------------------------------------------------------------------ */
/* 13. StoreCard                                                       */
/* Home + Account. Map tile, opening hours, call/directions actions.   */
/* ------------------------------------------------------------------ */
export interface StoreCardProps extends WithClassName {
  storeId: "centurion" | "glen-village" | "edenvale" | "woodlands";
  name: string;
  addressLine: string;
  distanceKm?: number;
  openUntil?: string;        // "18:30" — caller computes from hours
  phone: string;
  mapImageUrl: string;       // static map, not interactive (perf)
  onDirections: () => void;
  onCall: () => void;
}

/* ------------------------------------------------------------------ */
/* 14. ProtocolCard                                                    */
/* Home + Protocol Assistant result. Horizontal rail of 3–5 products   */
/* grouped with a title, days-left meter, reorder CTA.                 */
/* ------------------------------------------------------------------ */
export interface ProtocolCardProps extends WithClassName {
  title: string;             // "Your sleep stack"
  subtitle?: string;
  productIds: string[];      // hydrated by caller
  daysRemaining?: number;    // null for AI-suggested (not yet on subscription)
  source: "consultation" | "ai-assistant" | "repeat-purchase";
  onReorder?: () => void;
  onReview?: () => void;     // "Have a health consultant review this"
}

/* ------------------------------------------------------------------ */
/* 15. SectionHeader                                                   */
/* Serif title + optional sans eyebrow + optional link-right.          */
/* ------------------------------------------------------------------ */
export interface SectionHeaderProps extends WithClassName {
  eyebrow?: string;          // micro-caps
  title: string;
  description?: string;
  action?: { label: string; href: string };
}

/* ------------------------------------------------------------------ */
/* 16. SearchBar                                                       */
/* Persistent on Shop. Includes barcode-scan affordance.               */
/* ------------------------------------------------------------------ */
export interface SearchBarProps extends WithClassName {
  value: string;
  onChange: (v: string) => void;
  onScan?: () => void;       // opens camera sheet
  placeholder?: string;
  autoFocus?: boolean;
}

/* ------------------------------------------------------------------ */
/* 17. TabBar (bottom nav)                                             */
/* 5 slots, centre slot (Consult) slightly elevated.                   */
/* ------------------------------------------------------------------ */
export type TabKey = "home" | "shop" | "consult" | "rewards" | "account";

export interface TabBarProps extends WithClassName {
  active: TabKey;
  onNavigate: (key: TabKey) => void;
  /** Show numeric badge on shop (cart) or account (orders). */
  badges?: Partial<Record<TabKey, number>>;
}

/* ------------------------------------------------------------------ */
/* 18. IconButton                                                      */
/* 44×44 minimum. Used in header for search, cart, back.               */
/* ------------------------------------------------------------------ */
export interface IconButtonProps extends WithClassName {
  icon: ReactNode;
  label: string;             // always required for a11y
  onClick: () => void;
  badge?: number;
  tone?: Tone;
}

/* ------------------------------------------------------------------ */
/* 19. IngredientTable                                                 */
/* Full ingredient list on PDP. Tabular mono, alternating paper-deep.  */
/* ------------------------------------------------------------------ */
export interface IngredientRow {
  name: string;
  amountPerServing: string;  // "400 mg", "2 billion CFU"
  nrvPercent?: number;       // Nutrient Reference Value
  form?: string;             // "glycinate", "citrate"
}

export interface IngredientTableProps extends WithClassName {
  rows: IngredientRow[];
  servingSize: string;       // "1 capsule"
  servingsPerContainer: number;
}

/* ------------------------------------------------------------------ */
/* 20. ProtocolAssistantPrompt                                         */
/* Free-text intake on Consult tab. Returns a ProtocolCard result.     */
/* Clearly labelled AI. "Have a health consultant review this" required.*/
/* ------------------------------------------------------------------ */
export interface ProtocolAssistantPromptProps extends WithClassName {
  onSubmit: (prompt: string) => void;
  loading?: boolean;
  exampleCount?: 2 | 3;      // prompt-starters shown below input
}

/* ------------------------------------------------------------------ */
/* 21. Tabs                                                            */
/* Sticky tab strip for PDP info panels. Controlled by parent so       */
/* deep links can open on a specific tab.                              */
/* ------------------------------------------------------------------ */
export interface TabsItem<T extends string = string> {
  key: T;
  label: string;
}

export interface TabsProps<T extends string = string> extends WithClassName {
  items: readonly TabsItem<T>[];
  active: T;
  onChange: (key: T) => void;
  /** Sticks to top of scroll container when scrolled past. */
  sticky?: boolean;
}

/* ------------------------------------------------------------------ */
/* 22. SubscriptionToggle                                              */
/* PDP + cart. Two-state pill: one-time vs subscription (10% off,      */
/* free delivery). Intentionally not a checkbox — this is a decision.  */
/* ------------------------------------------------------------------ */
export interface SubscriptionToggleProps extends WithClassName {
  value: "one-time" | "subscribe";
  onChange: (v: "one-time" | "subscribe") => void;
  percentOff: number;
  cadenceLabel?: string;     // "every 30 days"
}

/* ------------------------------------------------------------------ */
/* Layout shells — not counted in the primitive set, but needed.       */
/* ------------------------------------------------------------------ */

export interface AppShellProps extends WithChildren {
  activeTab: TabKey;
  onNavigate: (key: TabKey) => void;
  cartCount?: number;
}

export interface PageHeaderProps extends WithClassName {
  title?: string;            // omit on Home; brand mark stands in
  showBack?: boolean;
  onBack?: () => void;
  trailing?: ReactNode;      // slot for IconButton cluster
}
