import { SectionHeader } from "@/components/SectionHeader";

// Pass 4 builds Shop proper — goal-first filter rail, barcode scan,
// secondary-filter bottom sheet. This stub keeps the tab bar honest
// so the other screens don't dead-end here.
export default function ShopPage() {
  return (
    <div className="space-y-10 pt-8">
      <SectionHeader
        eyebrow="Pass 4 · in progress"
        title="Shop arrives next."
        description="Goal-first filter rail, barcode scan, secondary-filter sheet, and the full catalogue. Home and a sample Product Detail are live — visit the magnesium glycinate page from Home's curated rail."
      />
    </div>
  );
}
