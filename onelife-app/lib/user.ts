"use client";

import { create } from "zustand";
import type { ContraindicationReason, Goal } from "@/components/primitives";
import { MOCK_USER } from "./mock";

// Minimal user profile. Source of truth for onboarding answers that
// drive cross-screen behaviour (contraindication banner on PDP,
// curated rail on Home).
type UserState = {
  firstName: string;
  selectedGoals: Goal[];
  contraindications: ContraindicationReason[];
  dietaryVegan: boolean;
  cartCount: number;

  setGoals: (goals: Goal[]) => void;
  setContraindications: (reasons: ContraindicationReason[]) => void;
  addToCart: () => void;
};

export const useUser = create<UserState>((set) => ({
  firstName: MOCK_USER.firstName,
  // Seed with the onboarding state a repeat customer would have.
  selectedGoals: ["sleep", "stress"],
  // Demonstrates the contraindication banner. Pass 4 will set these
  // from real onboarding answers.
  contraindications: ["chronic-medication"],
  dietaryVegan: false,
  cartCount: 0,

  setGoals: (goals) => set({ selectedGoals: goals }),
  setContraindications: (reasons) => set({ contraindications: reasons }),
  addToCart: () => set((s) => ({ cartCount: s.cartCount + 1 })),
}));
