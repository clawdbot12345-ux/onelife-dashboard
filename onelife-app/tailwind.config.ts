/**
 * One Life Health — Apothecary Modern design system
 *
 * Tokens only. No component styling, no hardcoded hex or spacing in
 * consumers. If a value isn't here (or in globals.css), it doesn't
 * belong in the app.
 *
 * Rule of three: any screen uses at most 3 of these palette colours
 * plus ink/paper. Enforced by code review, not by config.
 */
import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx,mdx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  // Paper bg / ink fg defaults live in globals.css; darkMode stays off.
  // The palette *is* the mood — there is no alt theme.
  darkMode: "class",
  theme: {
    // Override, don't extend. Default Tailwind palette is banned.
    colors: {
      transparent: "transparent",
      current: "currentColor",
      inherit: "inherit",

      ink: {
        DEFAULT: "var(--ink)",          // #1A1915 warm near-black
        muted: "var(--ink-muted)",      // #5C5A52
        subtle: "var(--ink-subtle)",    // #8A8578 for captions / metadata
      },
      paper: {
        DEFAULT: "var(--paper)",        // #F4F1EA Aesop-bag off-white
        deep: "var(--paper-deep)",      // #EAE5DA
      },
      bone: "var(--bone)",              // #FFFCF5 elevated surface
      sage: {
        DEFAULT: "var(--sage)",         // #6B7A5A muted eucalyptus
        deep: "var(--sage-deep)",       // #3E4A34 CTA / hover
      },
      terracotta: "var(--terracotta)",  // #B5654A urgency / sale
      gold: "var(--gold)",              // #B8934A rewards tier ONLY
      signal: "var(--signal)",          // #2C4A3A success / in-stock
      alert: "var(--alert)",            // #8B3A2E error / out-of-stock

      // Hairline dividers — sampled against paper, not neutral greys.
      hairline: "var(--hairline)",      // rgba(26,25,21,0.08)
    },

    fontFamily: {
      // Commercial primaries with open-source fallbacks that ship today.
      // Swap to Canela / Söhne via next/font once licences are in place.
      display: [
        "Canela",
        "PP Editorial New",
        "Fraunces",
        "ui-serif",
        "Georgia",
        "serif",
      ],
      sans: [
        "Söhne",
        "Inter Tight",
        "Inter",
        "ui-sans-serif",
        "system-ui",
        "sans-serif",
      ],
      mono: [
        "Söhne Mono",
        "JetBrains Mono",
        "ui-monospace",
        "SFMono-Regular",
        "monospace",
      ],
    },

    // Scale: 48 / 34 / 24 / 18 / 16 / 14 / 12
    // Pairs (size, { lineHeight, letterSpacing }) so consumers can't
    // compose bad combos. Display is tight, body is airy.
    fontSize: {
      "micro": ["0.6875rem", { lineHeight: "1.2", letterSpacing: "0.08em" }], // 11px, small caps
      "xs":    ["0.75rem",   { lineHeight: "1.4" }],   // 12
      "sm":    ["0.875rem",  { lineHeight: "1.5" }],   // 14
      "base":  ["1rem",      { lineHeight: "1.5" }],   // 16
      "lg":    ["1.125rem",  { lineHeight: "1.5" }],   // 18
      "xl":    ["1.5rem",    { lineHeight: "1.25", letterSpacing: "-0.01em" }],   // 24
      "2xl":   ["2.125rem",  { lineHeight: "1.15", letterSpacing: "-0.015em" }],  // 34
      "3xl":   ["3rem",      { lineHeight: "1.1",  letterSpacing: "-0.02em" }],   // 48
    },

    // 4pt grid. Named aliases so intent is readable.
    spacing: {
      "0":   "0",
      "px":  "1px",
      "0.5": "2px",
      "1":   "4px",
      "2":   "8px",
      "3":   "12px",
      "4":   "16px",
      "5":   "20px",
      "6":   "24px",
      "8":   "32px",
      "10":  "40px",
      "12":  "48px",
      "14":  "56px",
      "16":  "64px",
      "20":  "80px",
      "24":  "96px",
      "32":  "128px",
      // Semantic — prefer these in layout code.
      "gutter":  "24px",
      "section": "64px",
      "page-x":  "24px",  // mobile; desktop uses container
      "tap":     "44px",  // min tap target
    },

    borderRadius: {
      none: "0",
      card: "16px",       // product tiles, default cards
      hero: "24px",       // editorial / feature cards
      pill: "999px",      // chips, filter rails, membership
      // Deliberate omission: no 4px / 8px radius. Either sharp or soft.
    },

    boxShadow: {
      // Single shadow token. Depth comes from type + space, not glow.
      card: "0 1px 2px rgba(26,25,21,0.04), 0 8px 24px rgba(26,25,21,0.06)",
      none: "none",
    },

    letterSpacing: {
      tight: "-0.02em",
      snug:  "-0.01em",
      normal: "0",
      caps:  "0.08em",    // only use with .font-micro
    },

    lineHeight: {
      display: "1.15",
      tight:   "1.25",
      body:    "1.5",
    },

    extend: {
      fontFeatureSettings: {
        tabular: '"tnum" 1, "lnum" 1',
      },

      // Motion tokens. If a consumer reaches past these, push back.
      transitionDuration: {
        fast:   "160ms",
        base:   "280ms",
        slow:   "480ms",
        parallax: "8000ms",
      },
      transitionTimingFunction: {
        // Close to a spring settle; springs proper come from framer-motion.
        quiet: "cubic-bezier(0.22, 1, 0.36, 1)",
      },

      screens: {
        // Mobile-first. These are the only breakpoints we design for.
        sm: "480px",
        md: "768px",
        lg: "1024px",
        xl: "1280px",
      },

      maxWidth: {
        prose: "62ch",      // editorial reading measure
        page:  "1200px",
      },

      zIndex: {
        base:     "0",
        sticky:   "20",
        tabbar:   "40",
        sheet:    "60",
        toast:    "80",
        modal:    "100",
      },

      backgroundImage: {
        // For membership card only — paper → bone vertical wash.
        "tier-wash": "linear-gradient(180deg, var(--paper) 0%, var(--bone) 100%)",
      },
    },
  },
  // Only what we actually use. Typography plugin for the Health Hub
  // article view arrives in Pass 4.
  plugins: [],
};

export default config;
