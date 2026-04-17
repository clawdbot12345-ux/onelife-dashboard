/**
 * Seed data for the Pass-3 prototype.
 *
 * Shape mirrors what the Shopify Storefront API + Omni Accounts ERP
 * adapters will return in Pass 4. Prices are VAT-exclusive integer
 * cents in ZAR. Any number rendered in the UI should pass through
 * TabularPrice or a tabular-nums class.
 */

import type { Goal, MembershipTier } from "@/components/primitives";

export type MockProduct = {
  id: string;
  slug: string;
  name: string;
  brand: string;
  benefit: string;         // one-line promise, sentence case, no exclamations
  price: number;           // cents
  compareAtPrice?: number;
  dosagePerDay: string;    // "1 capsule"
  daysSupplyPerBottle: number;
  goals: Goal[];
  saMade: boolean;
  consultantPick: boolean;
  vegan: boolean;
  inStockAtUserStore: boolean;
  glyph: "bottle" | "mortar" | "leaf";
  buyersNote: string;
  howToTake: {
    timing: "morning" | "with-food" | "evening";
    text: string;
  }[];
  ingredients: {
    name: string;
    form?: string;
    amountPerServing: string;
    nrvPercent?: number;
  }[];
  evidence: {
    title: string;
    journal: string;
    year: number;
    url: string;
  }[];
  pairsWith: string[];     // product ids
};

export type MockReview = {
  productId: string;
  rating: 1 | 2 | 3 | 4 | 5;
  goal: Goal;
  body: string;
  verifiedAt: string;
  helpfulCount?: number;
};

export type MockConsultSlot = {
  isoStart: string;
  durationMinutes: number;
  mode: "in-store" | "video" | "message";
  storeName?: string;
  consultantName: string;
};

export type MockStore = {
  id: "centurion" | "glen-village" | "edenvale" | "woodlands";
  name: string;
  addressLine: string;
  phone: string;
  distanceKm: number;
  openUntil: string;
};

/* ---------------------------------------------------------------- */

export const MOCK_PRODUCTS: MockProduct[] = [
  {
    id: "p-mag-glycinate",
    slug: "magnesium-glycinate",
    name: "Magnesium Glycinate",
    brand: "Vivid Health",
    benefit: "The gentle form. For sleep, muscles, and a quieter mind.",
    price: 24900,
    compareAtPrice: 29900,
    dosagePerDay: "1 capsule",
    daysSupplyPerBottle: 60,
    goals: ["sleep", "stress", "recovery"],
    saMade: true,
    consultantPick: true,
    vegan: true,
    inStockAtUserStore: true,
    glyph: "bottle",
    buyersNote:
      "We stock three forms of magnesium. Glycinate is the one we reach for when a customer mentions sleep, racing thoughts, or muscle twitches. Citrate is for constipation; orotate is niche. This is where most people should start.",
    howToTake: [
      { timing: "evening", text: "One capsule, 30–60 minutes before bed." },
      { timing: "with-food", text: "Take with a small meal if you have a sensitive stomach." },
    ],
    ingredients: [
      { name: "Magnesium", form: "bisglycinate", amountPerServing: "200 mg", nrvPercent: 53 },
      { name: "Vitamin B6", form: "P-5-P", amountPerServing: "2 mg", nrvPercent: 143 },
      { name: "L-Glycine", amountPerServing: "250 mg" },
    ],
    evidence: [
      {
        title: "Oral magnesium supplementation and subjective sleep quality",
        journal: "Journal of Research in Medical Sciences",
        year: 2022,
        url: "https://pubmed.ncbi.nlm.nih.gov/",
      },
      {
        title: "Magnesium bisglycinate bioavailability vs. oxide in healthy adults",
        journal: "Nutrients",
        year: 2021,
        url: "https://pubmed.ncbi.nlm.nih.gov/",
      },
      {
        title: "Magnesium, stress, and HPA-axis regulation",
        journal: "Neuropsychobiology",
        year: 2020,
        url: "https://pubmed.ncbi.nlm.nih.gov/",
      },
    ],
    pairsWith: ["p-l-theanine", "p-ashwagandha", "p-omega-3"],
  },
  {
    id: "p-ashwagandha",
    slug: "ashwagandha-ksm-66",
    name: "Ashwagandha KSM-66",
    brand: "Solgar",
    benefit: "Standardised adaptogen for the long, loud months.",
    price: 38500,
    dosagePerDay: "1 capsule",
    daysSupplyPerBottle: 60,
    goals: ["stress", "energy", "recovery"],
    saMade: false,
    consultantPick: true,
    vegan: false,
    inStockAtUserStore: true,
    glyph: "bottle",
    buyersNote:
      "KSM-66 is the extract with the most human data behind it. We won't stock generic ashwagandha — it's cheap for a reason, and the active withanolides vary wildly.",
    howToTake: [
      { timing: "morning", text: "One capsule with breakfast, consistently." },
      { timing: "with-food", text: "Not on an empty stomach." },
    ],
    ingredients: [
      { name: "Ashwagandha root", form: "KSM-66", amountPerServing: "600 mg" },
      { name: "Withanolides", amountPerServing: "30 mg" },
    ],
    evidence: [
      {
        title: "Chronic stress and sleep with ashwagandha KSM-66",
        journal: "Cureus",
        year: 2020,
        url: "https://pubmed.ncbi.nlm.nih.gov/",
      },
    ],
    pairsWith: ["p-mag-glycinate", "p-l-theanine"],
  },
  {
    id: "p-l-theanine",
    slug: "l-theanine",
    name: "L-Theanine",
    brand: "Vivid Health",
    benefit: "The calm inside green tea, without the caffeine.",
    price: 18900,
    dosagePerDay: "1–2 capsules",
    daysSupplyPerBottle: 60,
    goals: ["stress", "focus", "sleep"],
    saMade: true,
    consultantPick: false,
    vegan: true,
    inStockAtUserStore: true,
    glyph: "bottle",
    buyersNote:
      "A quiet workhorse. Stack it with magnesium at night, or pair it with coffee in the morning to blunt the jitters.",
    howToTake: [
      { timing: "morning", text: "One with your morning coffee." },
      { timing: "evening", text: "One before bed if sleep is the target." },
    ],
    ingredients: [
      { name: "L-Theanine", amountPerServing: "200 mg" },
    ],
    evidence: [
      {
        title: "L-theanine and alpha-wave activity in adults under stress",
        journal: "Nutrients",
        year: 2019,
        url: "https://pubmed.ncbi.nlm.nih.gov/",
      },
    ],
    pairsWith: ["p-mag-glycinate", "p-ashwagandha"],
  },
  {
    id: "p-omega-3",
    slug: "omega-3-1000",
    name: "Omega-3 1000 mg",
    brand: "Vivid Health",
    benefit: "Wild-caught, molecularly distilled. For the heart and the head.",
    price: 21900,
    dosagePerDay: "2 softgels",
    daysSupplyPerBottle: 45,
    goals: ["focus", "joints", "immunity"],
    saMade: true,
    consultantPick: false,
    vegan: false,
    inStockAtUserStore: true,
    glyph: "bottle",
    buyersNote:
      "Third-party tested for heavy metals and oxidation. Most cheap omega-3s fail on oxidation — you'd smell it if you cracked the capsule.",
    howToTake: [
      { timing: "with-food", text: "Two softgels with a fat-containing meal." },
    ],
    ingredients: [
      { name: "EPA", amountPerServing: "600 mg" },
      { name: "DHA", amountPerServing: "400 mg" },
      { name: "Vitamin E", amountPerServing: "10 mg" },
    ],
    evidence: [
      {
        title: "Omega-3 intake and cardiovascular outcomes",
        journal: "JAMA Cardiology",
        year: 2021,
        url: "https://pubmed.ncbi.nlm.nih.gov/",
      },
    ],
    pairsWith: ["p-vitamin-d"],
  },
  {
    id: "p-vitamin-d",
    slug: "vitamin-d3-k2",
    name: "Vitamin D3 + K2",
    brand: "Solal",
    benefit: "For the long winters, when the sun forgets us.",
    price: 19900,
    dosagePerDay: "1 drop",
    daysSupplyPerBottle: 90,
    goals: ["immunity", "joints"],
    saMade: true,
    consultantPick: false,
    vegan: false,
    inStockAtUserStore: true,
    glyph: "bottle",
    buyersNote:
      "D3 needs K2 to deposit calcium in the bones, not the arteries. Buying them separately is needlessly complicated.",
    howToTake: [
      { timing: "with-food", text: "One drop with your largest meal." },
    ],
    ingredients: [
      { name: "Vitamin D3", form: "cholecalciferol", amountPerServing: "2000 IU", nrvPercent: 1000 },
      { name: "Vitamin K2", form: "MK-7", amountPerServing: "100 mcg", nrvPercent: 133 },
    ],
    evidence: [
      {
        title: "Vitamin D status and immune function",
        journal: "BMJ",
        year: 2017,
        url: "https://pubmed.ncbi.nlm.nih.gov/",
      },
    ],
    pairsWith: ["p-omega-3"],
  },
  {
    id: "p-probiotic",
    slug: "daily-probiotic-50b",
    name: "Daily Probiotic · 50B",
    brand: "Seed",
    benefit: "24 strains, refrigeration-free, actually makes it past the stomach.",
    price: 79900,
    dosagePerDay: "2 capsules",
    daysSupplyPerBottle: 30,
    goals: ["gut", "immunity"],
    saMade: false,
    consultantPick: true,
    vegan: true,
    inStockAtUserStore: false,
    glyph: "mortar",
    buyersNote:
      "Nested-capsule technology that survives stomach acid. Expensive, but the only probiotic we recommend for stubborn bloating.",
    howToTake: [
      { timing: "morning", text: "Two capsules first thing, empty stomach." },
    ],
    ingredients: [
      { name: "24 probiotic strains", amountPerServing: "53.6 billion AFU" },
      { name: "Polyphenol blend", amountPerServing: "185 mg" },
    ],
    evidence: [
      {
        title: "Multi-strain synbiotic and GI symptoms in adults",
        journal: "Gut Microbes",
        year: 2023,
        url: "https://pubmed.ncbi.nlm.nih.gov/",
      },
    ],
    pairsWith: ["p-omega-3", "p-vitamin-d"],
  },
];

export const MOCK_REVIEWS: MockReview[] = [
  {
    productId: "p-mag-glycinate",
    rating: 5,
    goal: "sleep",
    body: "Three weeks in and I'm asleep by 10:30, up by 6 without the alarm. Didn't expect something this quiet to move the needle.",
    verifiedAt: "2026-01-14",
    helpfulCount: 18,
  },
  {
    productId: "p-mag-glycinate",
    rating: 4,
    goal: "stress",
    body: "Noticeable by week two. Less anxious on deadlines. Slight digestive issue the first few days, gone now.",
    verifiedAt: "2025-11-28",
    helpfulCount: 6,
  },
  {
    productId: "p-mag-glycinate",
    rating: 5,
    goal: "recovery",
    body: "Leg cramps after long runs are gone. Tried three other brands first.",
    verifiedAt: "2025-10-02",
    helpfulCount: 3,
  },
];

export const MOCK_CONSULT_SLOTS: MockConsultSlot[] = [
  {
    isoStart: new Date(Date.now() + 90 * 60_000).toISOString(),
    durationMinutes: 15,
    mode: "video",
    consultantName: "Dr. Naledi Khumalo",
  },
  {
    isoStart: new Date(Date.now() + 3.5 * 3600_000).toISOString(),
    durationMinutes: 15,
    mode: "in-store",
    storeName: "Centurion",
    consultantName: "Ahmed Patel",
  },
  {
    isoStart: new Date(Date.now() + 23 * 3600_000).toISOString(),
    durationMinutes: 30,
    mode: "in-store",
    storeName: "Glen Village",
    consultantName: "Thandi Maseko",
  },
];

export const MOCK_STORES: MockStore[] = [
  {
    id: "centurion",
    name: "Centurion",
    addressLine: "Shop 6, The Grove Mall, Centurion",
    phone: "0800123456",
    distanceKm: 4.2,
    openUntil: "18:30",
  },
  {
    id: "glen-village",
    name: "Glen Village",
    addressLine: "Glen Village Centre, Pretoria",
    phone: "0800123457",
    distanceKm: 11.8,
    openUntil: "18:00",
  },
  {
    id: "edenvale",
    name: "Edenvale",
    addressLine: "Eastgate Boulevard, Edenvale",
    phone: "0800123458",
    distanceKm: 28.4,
    openUntil: "17:30",
  },
];

export const MOCK_EDITORIAL = {
  eyebrow: "Journal",
  title: "Magnesium glycinate vs citrate vs orotate",
  excerpt:
    "Same mineral, three different jobs. A buyer's note on when each one earns its place on your counter.",
  href: "/journal/magnesium-forms",
  readingMinutes: 4,
};

export const MOCK_THIS_WEEK = [
  {
    id: "tw-1",
    eyebrow: "New arrival",
    title: "Seed DS-01 daily synbiotic",
    href: "/product/daily-probiotic-50b",
  },
  {
    id: "tw-2",
    eyebrow: "Restock",
    title: "Vivid Health Magnesium back in at Centurion",
    href: "/product/magnesium-glycinate",
  },
  {
    id: "tw-3",
    eyebrow: "Community",
    title: "Free talk: sleep, without the supplements (Apr 23, Edenvale)",
    href: "/events/sleep-talk",
  },
];

export const MOCK_USER = {
  firstName: "Naadir",
  memberName: "Naadir Dawjee",
  tier: "rooted" as MembershipTier,
  points: 1540,
  pointsToNextTier: 460,
  memberSince: "2022-08-02",
};

export const MOCK_BRANDS = [
  "Vivid Health",
  "Solgar",
  "Solal",
  "Seed",
  "Thorne",
  "Garden of Life",
  "NOW Foods",
  "Vital Proteins",
];

export const MOCK_EARN_WAYS = [
  { title: "Every R10 spent", reward: "1 point" },
  { title: "Complete a consultation", reward: "50 points" },
  { title: "Leave a verified review", reward: "25 points" },
  { title: "Refer a friend", reward: "200 points" },
];

export const MOCK_REDEMPTIONS = [
  {
    id: "r-1",
    title: "R50 off your next order",
    cost: 500,
    glyph: "bottle" as const,
  },
  {
    id: "r-2",
    title: "Free 30-minute consultation",
    cost: 750,
    glyph: "mortar" as const,
  },
  {
    id: "r-3",
    title: "Vivid Health tote bag",
    cost: 1200,
    glyph: "leaf" as const,
  },
  {
    id: "r-4",
    title: "R200 off any Seed product",
    cost: 2000,
    glyph: "bottle" as const,
  },
];

export const MOCK_MEMBER_PERKS = [
  "Free delivery on orders under R400",
  "Early access to new arrivals and restocks",
  "Birthday gift from the buyer's desk",
  "One free quarterly in-depth consultation",
  "Members-only events in-store",
];

// Fuller consult roster so Consult page's three modes feel real.
export const MOCK_CONSULT_SLOTS_FULL = {
  "in-store": [
    {
      isoStart: new Date(Date.now() + 3.5 * 3600_000).toISOString(),
      durationMinutes: 15,
      mode: "in-store" as const,
      storeName: "Centurion",
      consultantName: "Ahmed Patel",
    },
    {
      isoStart: new Date(Date.now() + 5 * 3600_000).toISOString(),
      durationMinutes: 15,
      mode: "in-store" as const,
      storeName: "Centurion",
      consultantName: "Ahmed Patel",
    },
    {
      isoStart: new Date(Date.now() + 23 * 3600_000).toISOString(),
      durationMinutes: 30,
      mode: "in-store" as const,
      storeName: "Glen Village",
      consultantName: "Thandi Maseko",
    },
  ],
  video: [
    {
      isoStart: new Date(Date.now() + 90 * 60_000).toISOString(),
      durationMinutes: 15,
      mode: "video" as const,
      consultantName: "Dr. Naledi Khumalo",
    },
    {
      isoStart: new Date(Date.now() + 4 * 3600_000).toISOString(),
      durationMinutes: 30,
      mode: "video" as const,
      consultantName: "Dr. Naledi Khumalo",
    },
  ],
  message: [
    {
      isoStart: new Date(Date.now() + 2 * 3600_000).toISOString(),
      durationMinutes: 240,
      mode: "message" as const,
      consultantName: "First available consultant",
    },
  ],
};

/* ---------------------------------------------------------------- */

export function findProduct(slug: string) {
  return MOCK_PRODUCTS.find((p) => p.slug === slug);
}

export function findProductById(id: string) {
  return MOCK_PRODUCTS.find((p) => p.id === id);
}

export function reviewsFor(productId: string) {
  return MOCK_REVIEWS.filter((r) => r.productId === productId);
}
