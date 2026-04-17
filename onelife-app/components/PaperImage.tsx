/**
 * Placeholder image surface.
 *
 * We don't have commissioned photography yet (natural light, linen,
 * travertine — see brand brief). Until it arrives, anywhere the app
 * would use `next/image` renders a paper-deep tile with a subtle
 * botanical glyph. Honest placeholder, on-brand, zero CLS.
 */
import { cn } from "@/lib/utils";

type Aspect = "1/1" | "3/4" | "4/5" | "16/9";

const aspectClass: Record<Aspect, string> = {
  "1/1": "aspect-square",
  "3/4": "aspect-[3/4]",
  "4/5": "aspect-[4/5]",
  "16/9": "aspect-video",
};

export function PaperImage({
  aspect = "4/5",
  label,
  className,
  rounded = "card",
  glyph = "leaf",
}: {
  aspect?: Aspect;
  label?: string;
  className?: string;
  rounded?: "none" | "card" | "hero";
  glyph?: "leaf" | "bottle" | "mortar" | "none";
}) {
  const radius =
    rounded === "hero" ? "rounded-hero" : rounded === "card" ? "rounded-card" : "";

  return (
    <div
      role="img"
      aria-label={label ?? "Product imagery placeholder"}
      className={cn(
        "relative w-full overflow-hidden bg-paper-deep",
        aspectClass[aspect],
        radius,
        className,
      )}
    >
      {/* Hairline grid — evokes handmade apothecary paper */}
      <div
        aria-hidden
        className="absolute inset-0 opacity-[0.05]"
        style={{
          backgroundImage:
            "repeating-linear-gradient(0deg, var(--ink) 0 1px, transparent 1px 24px), repeating-linear-gradient(90deg, var(--ink) 0 1px, transparent 1px 24px)",
        }}
      />
      {glyph !== "none" && (
        <svg
          aria-hidden
          viewBox="0 0 60 60"
          className="absolute left-1/2 top-1/2 w-12 -translate-x-1/2 -translate-y-1/2 stroke-sage-deep"
          fill="none"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          {glyph === "leaf" && (
            <>
              <path d="M30 8c-10 8-16 18-16 28 0 8 6 16 16 16s16-8 16-16c0-10-6-20-16-28z" />
              <path d="M30 12v38" />
              <path d="M30 22c-4 2-8 4-10 6" />
              <path d="M30 30c-5 2-9 5-12 8" />
              <path d="M30 22c4 2 8 4 10 6" />
              <path d="M30 30c5 2 9 5 12 8" />
            </>
          )}
          {glyph === "bottle" && (
            <>
              <path d="M24 6h12" />
              <path d="M26 6v6c0 3-6 6-6 12v24a6 6 0 006 6h8a6 6 0 006-6V24c0-6-6-9-6-12V6" />
              <path d="M22 30h16" />
            </>
          )}
          {glyph === "mortar" && (
            <>
              <path d="M10 28h40l-4 18a4 4 0 01-4 4H18a4 4 0 01-4-4z" />
              <path d="M30 28V10" />
              <path d="M30 10l8-4" />
            </>
          )}
        </svg>
      )}
    </div>
  );
}
