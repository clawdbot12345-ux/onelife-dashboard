"use client";

import { useState } from "react";
import { MapPin, VideoCamera, ChatCircle } from "@phosphor-icons/react";
import { ConsultationSlot } from "@/components/ConsultationSlot";
import { ProtocolAssistantPrompt } from "@/components/ProtocolAssistantPrompt";
import { ProtocolCard } from "@/components/ProtocolCard";
import { SectionHeader } from "@/components/SectionHeader";
import { MOCK_CONSULT_SLOTS_FULL } from "@/lib/mock";
import type { ConsultMode } from "@/components/primitives";
import { cn } from "@/lib/utils";

type Mode = ConsultMode;

const modeMeta: Record<
  Mode,
  { Icon: typeof MapPin; title: string; copy: string; cta: string }
> = {
  "in-store": {
    Icon: MapPin,
    title: "In-store",
    copy: "Sit down with a health consultant at Centurion, Glen Village, Edenvale, or Woodlands.",
    cta: "Pick a store",
  },
  video: {
    Icon: VideoCamera,
    title: "Video call",
    copy: "Fifteen focused minutes over Zoom. Link arrives in your calendar.",
    cta: "Pick a time",
  },
  message: {
    Icon: ChatCircle,
    title: "Message",
    copy: "Ask anything. A health consultant replies within four business hours.",
    cta: "Start a thread",
  },
};

export default function ConsultPage() {
  const [mode, setMode] = useState<Mode | null>(null);
  const [generating, setGenerating] = useState(false);
  const [generated, setGenerated] = useState(false);

  const handleProtocol = () => {
    setGenerating(true);
    setGenerated(false);
    // Simulate an AI call. In production this hits the Claude API with
    // the user's goals/contraindications context and returns a typed
    // protocol that matches MockProduct ids.
    setTimeout(() => {
      setGenerating(false);
      setGenerated(true);
    }, 900);
  };

  return (
    <div className="space-y-section pb-8 pt-4">
      {/* Hero ------------------------------------------------------- */}
      <header className="px-page-x">
        <p data-micro>Consult</p>
        <h1 className="mt-3 font-display text-3xl leading-display tracking-tight text-ink">
          Talk to a health consultant.
        </h1>
        <p className="mt-3 max-w-prose text-lg text-ink-muted">
          Free. Fifteen minutes. No obligation. Fifteen years of experience on
          the other end.
        </p>
      </header>

      {/* Three modes ----------------------------------------------- */}
      <section className="space-y-5">
        <SectionHeader eyebrow="Book" title="Pick how you'd like to talk." />

        <div className="grid gap-4 px-page-x md:grid-cols-3">
          {(Object.keys(modeMeta) as Mode[]).map((m) => {
            const meta = modeMeta[m];
            const isActive = mode === m;
            return (
              <button
                key={m}
                type="button"
                onClick={() => setMode(isActive ? null : m)}
                aria-expanded={isActive}
                className={cn(
                  "flex min-h-36 flex-col items-start gap-3 rounded-hero border p-5 text-left transition-colors",
                  isActive
                    ? "border-ink bg-bone shadow-card"
                    : "border-hairline bg-bone hover:border-ink/40",
                )}
              >
                <span className="grid h-10 w-10 place-items-center rounded-pill bg-paper-deep">
                  <meta.Icon weight="regular" size={20} className="text-ink" />
                </span>
                <h3 className="font-display text-xl text-ink">{meta.title}</h3>
                <p className="text-sm text-ink-muted">{meta.copy}</p>
                <span className="mt-auto text-sm font-medium text-sage-deep">
                  {isActive ? "Showing slots below" : meta.cta}
                </span>
              </button>
            );
          })}
        </div>

        {mode && (
          <div className="space-y-3 px-page-x">
            <p data-micro className="pt-2">Earliest {modeMeta[mode].title.toLowerCase()} slots</p>
            {MOCK_CONSULT_SLOTS_FULL[mode].map((s) => (
              <ConsultationSlot
                key={s.isoStart}
                isoStart={s.isoStart}
                durationMinutes={s.durationMinutes}
                mode={s.mode}
                storeName={"storeName" in s ? s.storeName : undefined}
                consultantName={s.consultantName}
                onBook={() => {}}
              />
            ))}
          </div>
        )}
      </section>

      {/* Protocol Assistant --------------------------------------- */}
      <section className="space-y-5">
        <SectionHeader
          eyebrow="Protocol assistant"
          title="Or start with a description."
          description="An AI drafts a three-to-five product protocol. A health consultant reviews it before you buy."
        />
        <div className="px-page-x">
          <ProtocolAssistantPrompt onSubmit={handleProtocol} loading={generating} />
        </div>

        {generated && (
          <div className="px-page-x">
            <ProtocolCard
              title="A starting point for sleep"
              subtitle="Magnesium glycinate, L-theanine, ashwagandha — dosed to what you described."
              productIds={["p-mag-glycinate", "p-l-theanine", "p-ashwagandha"]}
              source="ai-assistant"
              onReview={() => setMode("message")}
              onReorder={() => {}}
            />
          </div>
        )}
      </section>
    </div>
  );
}
