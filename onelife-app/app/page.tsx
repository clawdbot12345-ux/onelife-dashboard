import { redirect } from "next/navigation";

// Pass 2 only ships /design. Home, Shop, Consult, Rewards, Onboarding
// follow in Passes 3–4. Until then, root redirects to the showcase.
export default function Root() {
  redirect("/design");
}
