"use client";

import { motion } from "framer-motion";
import { MapPin, VideoCamera, ChatCircle } from "@phosphor-icons/react";
import type { ConsultationSlotProps, ConsultMode } from "./primitives";
import { formatTimeSA } from "@/lib/fmt";
import { cn } from "@/lib/utils";

const modeMeta: Record<ConsultMode, { Icon: typeof MapPin; label: string }> = {
  "in-store": { Icon: MapPin, label: "In-store" },
  video: { Icon: VideoCamera, label: "Video" },
  message: { Icon: ChatCircle, label: "Message" },
};

export function ConsultationSlot({
  isoStart,
  durationMinutes,
  mode,
  storeName,
  consultantName,
  onBook,
  disabled,
  className,
}: ConsultationSlotProps) {
  const { Icon, label } = modeMeta[mode];

  return (
    <motion.button
      type="button"
      onClick={() => !disabled && onBook(isoStart)}
      disabled={disabled}
      whileTap={disabled ? undefined : { scale: 0.99 }}
      transition={{ type: "spring", stiffness: 420, damping: 38 }}
      className={cn(
        "flex w-full items-center justify-between gap-4 rounded-card border border-hairline bg-bone p-4 text-left",
        "transition-colors duration-fast ease-quiet",
        disabled
          ? "cursor-not-allowed opacity-50"
          : "hover:border-ink/40 hover:bg-paper",
        className,
      )}
    >
      <div className="flex items-center gap-4">
        <div className="flex h-12 w-12 items-center justify-center rounded-pill bg-paper-deep">
          <Icon weight="regular" size={20} className="text-ink" />
        </div>
        <div>
          <p data-num className="text-lg text-ink">
            {formatTimeSA(isoStart)}
          </p>
          <p className="text-sm text-ink-muted">
            {label}
            {storeName && ` · ${storeName}`}
            {` · ${durationMinutes} min`}
          </p>
          {consultantName && (
            <p data-micro className="mt-1">
              With {consultantName}
            </p>
          )}
        </div>
      </div>
      <span className="font-sans text-sm font-medium text-sage-deep">Book</span>
    </motion.button>
  );
}
