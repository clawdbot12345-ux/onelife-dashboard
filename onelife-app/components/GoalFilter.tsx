"use client";

import type { GoalFilterProps, Goal } from "./primitives";
import { Chip } from "./Chip";
import { cn } from "@/lib/utils";

const goalLabel: Record<Goal, string> = {
  sleep: "Sleep",
  energy: "Energy",
  stress: "Stress",
  gut: "Gut",
  immunity: "Immunity",
  joints: "Joints",
  skin: "Skin",
  hormones: "Hormones",
  focus: "Focus",
  recovery: "Recovery",
};

export function GoalFilter({
  goals,
  selected,
  onChange,
  max,
  className,
}: GoalFilterProps) {
  const toggle = (goal: Goal) => {
    const isSelected = selected.includes(goal);
    if (isSelected) {
      onChange(selected.filter((g) => g !== goal));
    } else {
      if (max !== undefined && selected.length >= max) return;
      onChange([...selected, goal]);
    }
  };

  return (
    <div
      className={cn(
        "flex gap-2 overflow-x-auto pb-1",
        // Hide scrollbar while preserving scroll — feels native.
        "[scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden",
        className,
      )}
      role="group"
      aria-label="Filter by health goal"
    >
      {goals.map((goal) => (
        <Chip
          key={goal}
          label={goalLabel[goal]}
          selected={selected.includes(goal)}
          onToggle={() => toggle(goal)}
        />
      ))}
    </div>
  );
}
