"use client";

import { useEffect } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { X } from "@phosphor-icons/react";
import type { BottomSheetProps } from "./primitives";
import { cn } from "@/lib/utils";

export function BottomSheet({
  open,
  onClose,
  title,
  dismissible = true,
  children,
  className,
}: BottomSheetProps) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape" && dismissible) onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, dismissible, onClose]);

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={dismissible ? onClose : undefined}
            className="fixed inset-0 z-sheet bg-ink/30 backdrop-blur-[2px]"
            aria-hidden
          />
          <motion.div
            role="dialog"
            aria-modal="true"
            aria-label={title}
            initial={{ y: "100%" }}
            animate={{ y: 0 }}
            exit={{ y: "100%" }}
            drag={dismissible ? "y" : false}
            dragConstraints={{ top: 0, bottom: 0 }}
            dragElastic={{ top: 0, bottom: 0.4 }}
            onDragEnd={(_, info) => {
              if (info.offset.y > 80 || info.velocity.y > 500) onClose();
            }}
            transition={{ type: "spring", stiffness: 280, damping: 32 }}
            className={cn(
              "fixed inset-x-0 bottom-0 z-sheet max-h-[90vh] overflow-hidden rounded-t-hero bg-paper pb-[env(safe-area-inset-bottom)] shadow-card",
              className,
            )}
          >
            <div className="flex items-center justify-between px-6 pt-4">
              <div className="mx-auto h-1 w-10 rounded-pill bg-hairline" />
            </div>
            {(title || dismissible) && (
              <div className="flex items-center justify-between px-6 pb-2 pt-4">
                {title && (
                  <h2 className="font-display text-xl text-ink">{title}</h2>
                )}
                {dismissible && (
                  <button
                    type="button"
                    onClick={onClose}
                    aria-label="Close"
                    className="u-tap -mr-3 grid place-items-center text-ink"
                  >
                    <X weight="regular" size={20} />
                  </button>
                )}
              </div>
            )}
            <div className="overflow-y-auto px-6 pb-8">{children}</div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
