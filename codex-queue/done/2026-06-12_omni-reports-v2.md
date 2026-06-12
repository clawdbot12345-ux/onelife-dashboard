# Codex task: Omni reports v2 — get per-store / per-item data flowing

Date: 2026-06-12 · Follow-up to the successful probe (thank you — pipeline confirmed working).
Unblocks: T2–T4 store baselines, Vivid GP verification, product matrix v1.0.

## Context
`/Report/Sales Analysis Johann Custom` works but only returns sales-by-discount-band with no date/store/item dimensions (see `data/omni/ANALYSIS.md`). The Omni Web Server (v7.21.68) serves any saved report by name: `/Report/{Name}?UserName=..&Password=..&CompanyName=Onelife`.

## Steps (in order of likely payoff)
1. **Probe for existing report names** — same auth, try names like: `Sales Analysis`, `Sales by Branch`, `Branch Sales`, `Daily Sales`, `Sales by Item`, `Stock on Hand`, `Stock Analysis`, `GP Analysis`, `Sales Analysis Custom`, and any variants Johann may have saved. A 200 with JSON = exists; 500 = doesn't. Log every hit to `data/omni/probe/SUMMARY.md` (append, credential-redacted) and commit samples.
2. **Test URL parameters** on the working report — append candidates like `&DateFrom=2026-06-01&DateTo=2026-06-12`, `&FromDate=`, `&ToDate=`, `&Branch=`, `&Period=`. If any changes the payload, document the working parameter names.
3. **If neither yields per-store data**: in the Omni Accounts desktop client (report designer / web reports config — or ask Johann/Naadir's accountant who built the existing one), define and expose these three reports:
   - `Engine Daily Branch Sales` — date, branch, sales excl VAT, cost of sales (last 90 days minimum; trailing 12 months once for baselines)
   - `Engine Sales by Item` — period, item code, description, supplier/brand, qty, sales excl, cost (per branch if possible)
   - `Engine Stock on Hand` — item, branch, qty on hand
4. Run `OMNI_REPORT_URL='<base report url>' python3 scripts/omni_probe.py` against anything new, commit results to `claude/end-to-end-goal-tdcj0f`, push.

## Definition of done
At least one report responding with per-branch (or per-item) rows, samples committed. The cloud engine then builds the parser, the scheduled sync, and the stores dashboard without further local work.
