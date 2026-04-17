"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { AnimatePresence, motion } from "framer-motion";
import { X, CaretLeft } from "@phosphor-icons/react";
import { Button } from "@/components/Button";
import { Chip } from "@/components/Chip";
import { PaperImage } from "@/components/PaperImage";
import { useUser } from "@/lib/user";
import type { ContraindicationReason, Goal } from "@/components/primitives";
import { cn } from "@/lib/utils";

const ALL_GOALS: Goal[] = [
  "sleep", "energy", "stress", "gut", "immunity",
  "joints", "skin", "hormones", "focus", "recovery",
];

type DietLabel = "Vegan" | "Gluten-free" | "Keto";

export default function OnboardingFlow() {
  const router = useRouter();
  const { setGoals, setContraindications } = useUser();

  const [step, setStep] = useState(0);
  const [direction, setDirection] = useState(1);
  const [goalState, setGoalState] = useState<Goal[]>([]);
  const [dietState, setDietState] = useState<DietLabel[]>([]);
  const [contraState, setContraState] = useState<ContraindicationReason[]>([]);

  const next = () => {
    setDirection(1);
    setStep((s) => Math.min(3, s + 1));
  };
  const back = () => {
    setDirection(-1);
    setStep((s) => Math.max(0, s - 1));
  };

  const finish = (to: "/consult" | "/home") => {
    setGoals(goalState);
    setContraindications(contraState);
    router.push(to);
  };

  return (
    <div className="relative mx-auto flex min-h-[100dvh] max-w-page flex-col bg-paper">
      {/* Chrome ---------------------------------------------------- */}
      <header className="flex h-14 items-center justify-between px-3">
        <button
          type="button"
          onClick={step === 0 ? () => router.push("/home") : back}
          aria-label={step === 0 ? "Close" : "Back"}
          className="u-tap grid place-items-center text-ink"
        >
          {step === 0 ? <X weight="regular" size={20} /> : <CaretLeft weight="regular" size={22} />}
        </button>
        <div className="flex items-center gap-1.5">
          {[0, 1, 2, 3].map((i) => (
            <span
              key={i}
              aria-hidden
              className={cn(
                "h-1 w-6 rounded-pill transition-colors",
                i <= step ? "bg-ink" : "bg-hairline",
              )}
            />
          ))}
        </div>
        <span className="w-11" aria-hidden />
      </header>

      {/* Steps ---------------------------------------------------- */}
      <main className="flex flex-1 flex-col overflow-hidden">
        <AnimatePresence mode="wait" custom={direction}>
          <motion.div
            key={step}
            custom={direction}
            initial={{ opacity: 0, x: direction * 16 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: direction * -16 }}
            transition={{ type: "spring", stiffness: 280, damping: 32 }}
            className="flex flex-1 flex-col"
          >
            {step === 0 && <StepBrand onBegin={next} />}
            {step === 1 && (
              <StepGoals value={goalState} onChange={setGoalState} onContinue={next} />
            )}
            {step === 2 && (
              <StepLifestyle
                diet={dietState}
                onDiet={setDietState}
                contra={contraState}
                onContra={setContraState}
                onContinue={next}
              />
            )}
            {step === 3 && (
              <StepConsult
                onBook={() => finish("/consult")}
                onSkip={() => finish("/home")}
              />
            )}
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  );
}

/* Step 1 ---------------------------------------------------------- */

function StepBrand({ onBegin }: { onBegin: () => void }) {
  return (
    <div className="flex flex-1 flex-col">
      <div className="flex-1 px-page-x pt-4">
        <PaperImage aspect="3/4" rounded="hero" glyph="leaf" />
      </div>
      <div className="space-y-4 px-page-x py-8">
        <p data-micro>A quieter way to live well.</p>
        <h1 className="font-display text-3xl leading-display tracking-tight text-ink">
          Twenty-five years of considered health, now in your pocket.
        </h1>
        <p className="max-w-prose text-base text-ink-muted">
          Before we recommend anything, we ask three things. It takes under a
          minute.
        </p>
        <div className="pt-4">
          <Button fullWidth size="lg" onClick={onBegin}>
            Begin
          </Button>
        </div>
      </div>
    </div>
  );
}

/* Step 2 ---------------------------------------------------------- */

function StepGoals({
  value,
  onChange,
  onContinue,
}: {
  value: Goal[];
  onChange: (v: Goal[]) => void;
  onContinue: () => void;
}) {
  const canContinue = value.length >= 1;
  return (
    <div className="flex flex-1 flex-col">
      <div className="space-y-3 px-page-x pt-4">
        <p data-micro>Step 2 of 4</p>
        <h1 className="font-display text-2xl leading-display tracking-snug text-ink">
          What are you focused on?
        </h1>
        <p className="max-w-prose text-base text-ink-muted">
          Pick up to three. You can change these later.
        </p>
      </div>

      <div className="flex-1 px-page-x pt-8">
        <div className="flex flex-wrap gap-2">
          {ALL_GOALS.map((g) => {
            const isSelected = value.includes(g);
            const atLimit = value.length >= 3 && !isSelected;
            return (
              <Chip
                key={g}
                label={g[0]!.toUpperCase() + g.slice(1)}
                selected={isSelected}
                size="md"
                onToggle={(sel) => {
                  if (atLimit) return;
                  onChange(sel ? [...value, g] : value.filter((x) => x !== g));
                }}
              />
            );
          })}
        </div>
        {value.length >= 3 && (
          <p data-micro className="mt-4 text-ink-subtle">
            Three selected. Deselect one to swap.
          </p>
        )}
      </div>

      <div className="px-page-x py-6">
        <Button fullWidth size="lg" disabled={!canContinue} onClick={onContinue}>
          {canContinue ? "Continue" : "Pick at least one"}
        </Button>
      </div>
    </div>
  );
}

/* Step 3 ---------------------------------------------------------- */

const DIET_OPTIONS: DietLabel[] = ["Vegan", "Gluten-free", "Keto"];
const CONTRA_OPTIONS: { value: ContraindicationReason; label: string }[] = [
  { value: "pregnancy", label: "Pregnant" },
  { value: "breastfeeding", label: "Breastfeeding" },
  { value: "chronic-medication", label: "On chronic medication" },
];

function StepLifestyle({
  diet,
  onDiet,
  contra,
  onContra,
  onContinue,
}: {
  diet: DietLabel[];
  onDiet: (v: DietLabel[]) => void;
  contra: ContraindicationReason[];
  onContra: (v: ContraindicationReason[]) => void;
  onContinue: () => void;
}) {
  return (
    <div className="flex flex-1 flex-col">
      <div className="space-y-3 px-page-x pt-4">
        <p data-micro>Step 3 of 4</p>
        <h1 className="font-display text-2xl leading-display tracking-snug text-ink">
          Anything we should know about?
        </h1>
        <p className="max-w-prose text-base text-ink-muted">
          Some supplements aren't right for everyone. This stays private and
          only surfaces on products where it matters.
        </p>
      </div>

      <div className="flex-1 space-y-8 px-page-x pt-8">
        <section className="space-y-3">
          <p data-micro>Dietary</p>
          <div className="flex flex-wrap gap-2">
            {DIET_OPTIONS.map((d) => (
              <Chip
                key={d}
                label={d}
                selected={diet.includes(d)}
                onToggle={(sel) =>
                  onDiet(sel ? [...diet, d] : diet.filter((x) => x !== d))
                }
              />
            ))}
          </div>
        </section>

        <section className="space-y-3">
          <p data-micro>Health</p>
          <div className="flex flex-wrap gap-2">
            {CONTRA_OPTIONS.map((c) => (
              <Chip
                key={c.value}
                label={c.label}
                selected={contra.includes(c.value)}
                onToggle={(sel) =>
                  onContra(
                    sel ? [...contra, c.value] : contra.filter((x) => x !== c.value),
                  )
                }
              />
            ))}
          </div>
        </section>
      </div>

      <div className="px-page-x py-6">
        <Button fullWidth size="lg" onClick={onContinue}>
          Continue
        </Button>
      </div>
    </div>
  );
}

/* Step 4 ---------------------------------------------------------- */

function StepConsult({
  onBook,
  onSkip,
}: {
  onBook: () => void;
  onSkip: () => void;
}) {
  return (
    <div className="flex flex-1 flex-col">
      <div className="flex-1 px-page-x pt-4">
        <PaperImage aspect="3/4" rounded="hero" glyph="mortar" />
      </div>
      <div className="space-y-4 px-page-x py-8">
        <p data-micro>Before we recommend anything</p>
        <h1 className="font-display text-2xl leading-display tracking-snug text-ink">
          Book fifteen minutes with a pharmacist. It's free, forever.
        </h1>
        <p className="max-w-prose text-base text-ink-muted">
          Fifteen years of experience, a quiet conversation, no upsell. It's
          what makes a One Life recommendation worth more than a search result.
        </p>
        <div className="flex flex-col gap-3 pt-4">
          <Button fullWidth size="lg" onClick={onBook}>
            Book a consultation
          </Button>
          <Button variant="ghost" fullWidth size="md" onClick={onSkip}>
            Skip for now
          </Button>
        </div>
      </div>
    </div>
  );
}
