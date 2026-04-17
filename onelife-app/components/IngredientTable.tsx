import type { IngredientTableProps } from "./primitives";
import { cn } from "@/lib/utils";

export function IngredientTable({
  rows,
  servingSize,
  servingsPerContainer,
  className,
}: IngredientTableProps) {
  return (
    <div className={cn("overflow-hidden rounded-card border border-hairline bg-bone", className)}>
      <div className="flex items-center justify-between px-4 py-3 text-sm text-ink-muted">
        <span>
          Serving size <span data-num className="text-ink">{servingSize}</span>
        </span>
        <span>
          <span data-num className="text-ink">{servingsPerContainer}</span> servings
        </span>
      </div>
      <table className="w-full border-collapse text-left font-mono text-sm">
        <thead>
          <tr className="border-y border-hairline text-ink-muted">
            <th className="px-4 py-2 font-normal uppercase tracking-caps text-[11px]">
              Ingredient
            </th>
            <th className="px-4 py-2 text-right font-normal uppercase tracking-caps text-[11px]">
              Per serving
            </th>
            <th className="px-4 py-2 text-right font-normal uppercase tracking-caps text-[11px]">
              NRV
            </th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr
              key={row.name}
              className={cn(
                "border-b border-hairline last:border-b-0",
                i % 2 === 1 && "bg-paper-deep/40",
              )}
            >
              <td className="px-4 py-3 font-sans text-ink">
                {row.name}
                {row.form && (
                  <span className="ml-2 text-ink-subtle">({row.form})</span>
                )}
              </td>
              <td className="px-4 py-3 text-right tabular-nums text-ink">
                {row.amountPerServing}
              </td>
              <td className="px-4 py-3 text-right tabular-nums text-ink-muted">
                {row.nrvPercent !== undefined ? `${row.nrvPercent}%` : "—"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
