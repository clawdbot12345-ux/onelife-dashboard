"use client";

import { Check } from "@phosphor-icons/react";
import { MembershipCard } from "@/components/MembershipCard";
import { SectionHeader } from "@/components/SectionHeader";
import { PaperImage } from "@/components/PaperImage";
import { MOCK_EARN_WAYS, MOCK_MEMBER_PERKS, MOCK_REDEMPTIONS, MOCK_USER } from "@/lib/mock";
import { useUser } from "@/lib/user";

export default function RewardsPage() {
  const firstName = useUser((s) => s.firstName);
  const memberName = firstName === MOCK_USER.firstName ? MOCK_USER.memberName : firstName;

  return (
    <div className="space-y-section pb-8 pt-4">
      {/* Hero card ------------------------------------------------- */}
      <section className="px-page-x">
        <p data-micro className="mb-4">One Life Community</p>
        <MembershipCard
          memberName={memberName}
          tier={MOCK_USER.tier}
          points={MOCK_USER.points}
          pointsToNextTier={MOCK_USER.pointsToNextTier}
          memberSince={MOCK_USER.memberSince}
        />
      </section>

      {/* Earn ------------------------------------------------------ */}
      <section className="space-y-5">
        <SectionHeader eyebrow="Earn" title="How points arrive." />
        <ul className="divide-y divide-hairline overflow-hidden rounded-card border border-hairline bg-bone">
          {MOCK_EARN_WAYS.map((w) => (
            <li key={w.title} className="flex items-center justify-between gap-4 px-5 py-4">
              <span className="font-sans text-base text-ink">{w.title}</span>
              <span data-num className="text-ink-muted">{w.reward}</span>
            </li>
          ))}
        </ul>
      </section>

      {/* Redeem ---------------------------------------------------- */}
      <section className="space-y-5">
        <SectionHeader eyebrow="Redeem" title="Spend them on something considered." />
        <div className="grid grid-cols-2 gap-4 px-page-x md:grid-cols-4">
          {MOCK_REDEMPTIONS.map((r) => {
            const affordable = MOCK_USER.points >= r.cost;
            return (
              <article
                key={r.id}
                className="space-y-3 rounded-card border border-hairline bg-bone p-4"
              >
                <PaperImage aspect="1/1" rounded="card" glyph={r.glyph} />
                <div>
                  <p className="font-sans text-sm text-ink">{r.title}</p>
                  <div className="mt-2 flex items-center justify-between">
                    <span data-num className="text-sm text-ink">
                      {r.cost.toLocaleString("en-ZA")} pts
                    </span>
                    <button
                      type="button"
                      disabled={!affordable}
                      className="rounded-pill px-3 py-1 text-xs font-medium text-ink disabled:text-ink-subtle"
                    >
                      {affordable ? "Redeem" : "Locked"}
                    </button>
                  </div>
                </div>
              </article>
            );
          })}
        </div>
      </section>

      {/* Perks ----------------------------------------------------- */}
      <section className="space-y-5">
        <SectionHeader eyebrow="Perks" title="What membership actually does." />
        <ul className="space-y-3 px-page-x">
          {MOCK_MEMBER_PERKS.map((perk) => (
            <li key={perk} className="flex items-start gap-3">
              <span className="mt-1 grid h-5 w-5 shrink-0 place-items-center rounded-pill border border-sage-deep text-sage-deep">
                <Check weight="regular" size={12} />
              </span>
              <span className="font-sans text-base text-ink">{perk}</span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
