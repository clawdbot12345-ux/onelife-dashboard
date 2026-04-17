"use client";

import {
  House,
  Storefront,
  Stethoscope,
  Gift,
  UserCircle,
  type IconProps,
} from "@phosphor-icons/react";
import { motion } from "framer-motion";
import type { TabBarProps, TabKey } from "./primitives";
import { cn } from "@/lib/utils";

type Entry = {
  key: TabKey;
  label: string;
  Icon: React.ComponentType<IconProps>;
};

const entries: Entry[] = [
  { key: "home", label: "Home", Icon: House },
  { key: "shop", label: "Shop", Icon: Storefront },
  { key: "consult", label: "Consult", Icon: Stethoscope },
  { key: "rewards", label: "Rewards", Icon: Gift },
  { key: "account", label: "Account", Icon: UserCircle },
];

export function TabBar({ active, onNavigate, badges, className }: TabBarProps) {
  return (
    <nav
      aria-label="Primary"
      className={cn(
        "fixed inset-x-0 bottom-0 z-tabbar",
        "pb-[calc(env(safe-area-inset-bottom)+8px)] pt-2",
        "border-t border-hairline bg-paper/95 backdrop-blur-md",
        className,
      )}
    >
      <ul className="mx-auto flex max-w-page items-end justify-around px-2">
        {entries.map(({ key, label, Icon }) => {
          const isActive = key === active;
          const isCentre = key === "consult";
          const badge = badges?.[key];
          return (
            <li key={key} className="flex-1">
              <button
                type="button"
                onClick={() => onNavigate(key)}
                aria-current={isActive ? "page" : undefined}
                aria-label={label}
                className={cn(
                  "u-tap relative mx-auto flex w-full flex-col items-center gap-1 py-1",
                )}
              >
                <span
                  className={cn(
                    "grid place-items-center rounded-pill transition-colors duration-fast",
                    isCentre
                      ? "-mt-5 h-14 w-14 bg-sage-deep text-bone shadow-card"
                      : "h-8 w-8",
                    !isCentre && isActive && "text-ink",
                    !isCentre && !isActive && "text-ink-muted",
                  )}
                >
                  <Icon weight={isActive && !isCentre ? "fill" : "regular"} size={isCentre ? 24 : 22} />
                  {badge ? (
                    <span
                      data-num
                      className="absolute right-[calc(50%-18px)] top-0 min-w-4 rounded-pill bg-terracotta px-1 text-[10px] font-medium text-bone"
                    >
                      {badge > 99 ? "99+" : badge}
                    </span>
                  ) : null}
                </span>
                <span
                  data-micro
                  className={cn(
                    "leading-none",
                    isActive ? "text-ink" : "text-ink-subtle",
                  )}
                >
                  {label}
                </span>
                {isActive && !isCentre && (
                  <motion.span
                    layoutId="tabbar-dot"
                    className="absolute -bottom-1 h-[3px] w-6 rounded-pill bg-ink"
                    transition={{ type: "spring", stiffness: 420, damping: 38 }}
                  />
                )}
              </button>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
