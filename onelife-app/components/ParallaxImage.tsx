"use client";

import { useRef } from "react";
import { motion, useScroll, useTransform, useReducedMotion } from "framer-motion";
import type { ParallaxImageProps } from "./primitives";
import { PaperImage } from "./PaperImage";
import { cn } from "@/lib/utils";

export function ParallaxImage({
  alt,
  aspectRatio = "4/5",
  rounded = "card",
  strength = 0.15,
  className,
}: ParallaxImageProps) {
  const ref = useRef<HTMLDivElement>(null);
  const prefersReduced = useReducedMotion();
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"],
  });
  const translateY = useTransform(
    scrollYProgress,
    [0, 1],
    prefersReduced ? ["0%", "0%"] : [`-${strength * 100}%`, `${strength * 100}%`],
  );

  return (
    <div
      ref={ref}
      className={cn("overflow-hidden", rounded === "hero" ? "rounded-hero" : rounded === "card" ? "rounded-card" : "", className)}
    >
      <motion.div style={{ y: translateY }} className="h-[115%] w-full">
        <PaperImage aspect={aspectRatio} label={alt} rounded="none" glyph="leaf" />
      </motion.div>
    </div>
  );
}
