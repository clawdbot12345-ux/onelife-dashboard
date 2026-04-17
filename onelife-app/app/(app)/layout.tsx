"use client";

import { usePathname, useRouter } from "next/navigation";
import { AppShell } from "@/components/AppShell";
import type { TabKey } from "@/components/primitives";
import { useUser } from "@/lib/user";

const tabPath: Record<TabKey, string> = {
  home: "/home",
  shop: "/shop",
  consult: "/consult",
  rewards: "/rewards",
  account: "/account",
};

function activeFromPath(pathname: string): TabKey {
  if (pathname.startsWith("/shop") || pathname.startsWith("/product")) return "shop";
  if (pathname.startsWith("/consult")) return "consult";
  if (pathname.startsWith("/rewards")) return "rewards";
  if (pathname.startsWith("/account")) return "account";
  return "home";
}

export default function ShellLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const cartCount = useUser((s) => s.cartCount);

  return (
    <AppShell
      activeTab={activeFromPath(pathname)}
      onNavigate={(key) => router.push(tabPath[key])}
      cartCount={cartCount}
    >
      {children}
    </AppShell>
  );
}
