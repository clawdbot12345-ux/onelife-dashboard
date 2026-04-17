"use client";

import { NavigationArrow, Phone } from "@phosphor-icons/react";
import type { StoreCardProps } from "./primitives";
import { cn } from "@/lib/utils";

export function StoreCard({
  name,
  addressLine,
  distanceKm,
  openUntil,
  phone,
  onDirections,
  onCall,
  className,
}: StoreCardProps) {
  return (
    <article
      className={cn(
        "overflow-hidden rounded-hero border border-hairline bg-bone shadow-card",
        className,
      )}
    >
      {/* Static map placeholder — production ships a rendered PNG from
          Mapbox static API, cached at the edge. Real map is never
          interactive in a card — one tap opens the native Maps app. */}
      <div
        aria-hidden
        className="relative h-36 w-full bg-paper-deep"
        style={{
          backgroundImage:
            "repeating-linear-gradient(45deg, transparent 0 14px, var(--hairline) 14px 15px)",
        }}
      >
        <div className="absolute inset-0 grid place-items-center">
          <div className="h-4 w-4 rounded-pill bg-sage-deep ring-4 ring-paper" />
        </div>
      </div>

      <div className="space-y-4 p-5">
        <div>
          <h3 className="font-display text-xl text-ink">{name}</h3>
          <p className="text-sm text-ink-muted">{addressLine}</p>
          <div className="mt-2 flex items-center gap-3 text-sm text-ink">
            {distanceKm !== undefined && (
              <span data-num>{distanceKm.toFixed(1)} km</span>
            )}
            {openUntil && distanceKm !== undefined && (
              <span className="h-1 w-1 rounded-pill bg-hairline" aria-hidden />
            )}
            {openUntil && (
              <span className="text-signal">Open until {openUntil}</span>
            )}
          </div>
        </div>

        <div className="flex gap-3">
          <button
            type="button"
            onClick={onDirections}
            className="u-tap inline-flex flex-1 items-center justify-center gap-2 rounded-pill bg-ink px-4 py-2.5 text-sm font-medium text-bone"
          >
            <NavigationArrow weight="regular" size={16} />
            Directions
          </button>
          <button
            type="button"
            onClick={onCall}
            aria-label={`Call ${name} on ${phone}`}
            className="u-tap inline-flex items-center justify-center gap-2 rounded-pill border border-ink/30 px-4 py-2.5 text-sm font-medium text-ink"
          >
            <Phone weight="regular" size={16} />
            Call
          </button>
        </div>
      </div>
    </article>
  );
}
