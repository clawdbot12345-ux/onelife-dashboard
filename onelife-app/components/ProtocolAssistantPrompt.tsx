"use client";

import { useState } from "react";
import { Sparkle, ArrowUp } from "@phosphor-icons/react";
import type { ProtocolAssistantPromptProps } from "./primitives";
import { cn } from "@/lib/utils";

const starters = [
  "I can't fall asleep before 1am",
  "Low energy, two coffees by 10am",
  "Stomach cramps after dairy",
];

export function ProtocolAssistantPrompt({
  onSubmit,
  loading,
  exampleCount = 3,
  className,
}: ProtocolAssistantPromptProps) {
  const [value, setValue] = useState("");
  const canSubmit = value.trim().length > 2 && !loading;

  return (
    <section className={cn("space-y-4 rounded-hero bg-bone p-6 shadow-card", className)}>
      <div className="flex items-center gap-2 text-ink-muted">
        <Sparkle weight="regular" size={16} />
        <span data-micro>AI · always reviewed by a human consultant</span>
      </div>

      <h3 className="font-display text-xl text-ink">
        Tell us, in your own words.
      </h3>
      <p className="max-w-prose text-sm text-ink-muted">
        Describe what's going on. We'll suggest a three-to-five product protocol
        with studies and timing, and offer a free consultant review before you
        buy anything.
      </p>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (canSubmit) onSubmit(value);
        }}
        className="relative"
      >
        <textarea
          value={value}
          onChange={(e) => setValue(e.target.value)}
          rows={3}
          placeholder="e.g. I wake up at 3am every night and can't get back to sleep."
          className="min-h-24 w-full resize-none rounded-card border border-hairline bg-paper p-4 pr-14 text-base text-ink placeholder:text-ink-subtle focus:border-ink/40 focus:outline-none"
        />
        <button
          type="submit"
          disabled={!canSubmit}
          aria-label="Submit"
          className={cn(
            "u-tap absolute bottom-3 right-3 grid place-items-center rounded-pill transition-colors",
            canSubmit
              ? "bg-sage-deep text-bone"
              : "bg-paper-deep text-ink-subtle",
          )}
        >
          <ArrowUp weight="bold" size={18} />
        </button>
      </form>

      <div className="flex flex-wrap gap-2 pt-1">
        {starters.slice(0, exampleCount).map((s) => (
          <button
            key={s}
            type="button"
            onClick={() => setValue(s)}
            className="rounded-pill border border-hairline px-3 py-1.5 text-sm text-ink-muted hover:border-ink/30 hover:text-ink"
          >
            {s}
          </button>
        ))}
      </div>
    </section>
  );
}
