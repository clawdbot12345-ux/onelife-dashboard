"use client";

import { MagnifyingGlass, Handbag } from "@phosphor-icons/react";
import type { AppShellProps } from "./primitives";
import { PageHeader } from "./PageHeader";
import { TabBar } from "./TabBar";
import { IconButton } from "./IconButton";

export function AppShell({
  activeTab,
  onNavigate,
  cartCount,
  children,
}: AppShellProps) {
  return (
    <div className="mx-auto flex min-h-[100dvh] max-w-page flex-col bg-paper">
      <PageHeader
        trailing={
          <>
            <IconButton
              icon={<MagnifyingGlass weight="regular" size={22} />}
              label="Search"
              onClick={() => onNavigate("shop")}
            />
            <IconButton
              icon={<Handbag weight="regular" size={22} />}
              label="Cart"
              badge={cartCount}
              onClick={() => onNavigate("shop")}
            />
          </>
        }
      />
      <main className="flex-1 pb-24">{children}</main>
      <TabBar
        active={activeTab}
        onNavigate={onNavigate}
        badges={cartCount ? { shop: cartCount } : undefined}
      />
    </div>
  );
}
