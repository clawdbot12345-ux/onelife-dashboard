#!/usr/bin/env python3
"""Build the Vivid product-rename migration from vivid/backend/products.json.

New naming grammar (blueprint §3):  Vivid <Product> — <benefit> · <size>
Range moves to a structured tag (range:immune …) — old brand_ tags are KEPT
so existing smart collections keep working. Handles are never touched (SEO).

Outputs:
  vivid/backend/apply/product-updates.json  (title + tags updates)
  vivid/backend/rename-backup.json          (rollback map: id -> old title/tags)
  vivid/backend/rename-table.md             (review table for the PR)
Copy fixes (CoQ10/MSM body_html) are staged separately.
"""
import json
import os
import re

SRC = "vivid/backend/products.json"

# handle -> (new title, range tag)
# benefit lines follow SAHPRA low-risk wording (supports/assists/maintains)
NAMES = {
    "vivid-health-immune-mullein-60-capsules": ("Vivid Mullein — traditional respiratory support · 60 capsules", "immune"),
    "vivid-health-gut-health-clove-60-capsules": ("Vivid Clove — traditional gut & digestive support · 60 capsules", "gut"),
    "vivid-health-gut-health-colon-flush-120-capsules": ("Vivid Colon Flush — gentle colon cleanse support · 120 capsules", "gut"),
    "vivid-health-vivid-nourishment-turmeric-300-capsules": ("Vivid Turmeric — antioxidant & joint comfort support · 300 capsules", "gut"),
    "vivid-health-vivid-nourishment-cayenne-300-capsules": ("Vivid Cayenne — circulation & metabolism support · 300 capsules", "gut"),
    "vivid-health-immune-liver-kidney-formula-90-capsules": ("Vivid Liver & Kidney Formula — organ support blend · 90 capsules", "immune"),
    "vivid-health-gut-health-black-walnut-60-capsules": ("Vivid Black Walnut — traditional digestive balance · 60 capsules", "gut"),
    "vivid-health-gut-health-immune-wormwood-60-capsules": ("Vivid Wormwood — traditional gut balance support · 60 capsules", "gut"),
    "vivid-health-woman-maca-60-capsules": ("Vivid Maca — energy & hormonal balance support · 60 capsules", "woman"),
    "vivid-health-vivid-body-flexijoint-advanced-120-capsules": ("Vivid Flexijoint Advanced — complete joint support · 120 capsules", "body"),
    "vivid-health-stay-vivid-d-ribose-150g": ("Vivid D-Ribose — cellular energy support · 150g powder", "mind"),
    "vivid-health-vivid-body-bone-supreme-120-capsules": ("Vivid Bone Supreme — bone & skeletal support · 120 capsules", "body"),
    "vivid-health-physical-health-omega-oil-90-capsules": ("Vivid Omega Oil — heart, brain & eye support · 90 capsules", "body"),
    "vivid-health-men-prosta-care-60-capsules": ("Vivid Prosta Care — prostate & urinary support · 60 capsules", "man"),
    "vivid-health-immune-allergy-control-60-capsules": ("Vivid Allergy Control — seasonal comfort support · 60 capsules", "immune"),
    "vivid-health-gut-health-colon-flush-powder-135g": ("Vivid Colon Flush — gentle colon cleanse support · 135g powder", "gut"),
    "vivid-health-vivid-body-colest-control-60-capsules": ("Vivid Cholesterol Support — heart health maintenance · 60 capsules", "body"),
    "vivid-health-immune-astragalus-60-capsules": ("Vivid Astragalus — immune & vitality support · 60 capsules", "immune"),
    "vivid-health-physical-health-l-glutamine-500g": ("Vivid L-Glutamine — gut lining & recovery support · 500g powder", "body"),
    "vivid-health-immune-l-lysine-60-capsules": ("Vivid L-Lysine — immune & skin support · 60 capsules", "immune"),
    "vivid-health-immune-buffered-c-300-capsules": ("Vivid Buffered C — gentle everyday vitamin C · 300 capsules", "immune"),
    "vivid-health-stay-vivid-tranquil-60-capsules": ("Vivid Tranquil — calm & relaxation support · 60 capsules", "mind"),
    "vivid-health-woman-sage-60-capsules": ("Vivid Sage — menopause comfort support · 60 capsules", "woman"),
    "vivid-health-vivid-body-msm-90-capsules": ("Vivid MSM — joint, skin & hair support · 90 capsules", "body"),
    "vivid-health-vivid-body-msm-500g": ("Vivid MSM — joint, skin & hair support · 500g powder", "body"),
    "vivid-health-vivid-body-msm-300-capsules": ("Vivid MSM — joint, skin & hair support · 300 capsules", "body"),
    "vivid-health-stay-vivid-liquorice-root-60-capsules": ("Vivid Liquorice Root — digestive & adrenal support · 60 capsules", "mind"),
    "vivid-health-vivid-body-joint-relief-60-capsules": ("Vivid Joint Relief — everyday joint comfort · 60 capsules", "body"),
    "vivid-health-vivid-body-garcinia-cambogia-60-capsules": ("Vivid Garcinia Cambogia — appetite & weight management support · 60 capsules", "body"),
    "vivid-health-vivid-nourishment-cayenne-90-capsules": ("Vivid Cayenne — circulation & metabolism support · 90 capsules", "gut"),
    "vivid-health-vivid-nourishment-cayenne-250g": ("Vivid Cayenne — circulation & metabolism support · 250g powder", "gut"),
    "vivid-health-immune-buffered-c-90-capsules": ("Vivid Buffered C — gentle everyday vitamin C · 90 capsules", "immune"),
    "vivid-health-immune-buffered-c-150g": ("Vivid Buffered C — gentle everyday vitamin C · 150g powder", "immune"),
    "vivid-health-vivid-nourishment-apple-cider-90-capsules": ("Vivid Apple Cider — digestion & blood sugar support · 90 capsules", "gut"),
    "vivid-health-nutrient-health-turmeric-plus-60-capsules": ("Vivid Turmeric Plus — enhanced anti-inflammatory support · 60 capsules", "gut"),
    "vivid-health-immune-advanced-buffered-c-300-capsules": ("Vivid Advanced Buffered C — high-strength gentle vitamin C · 300 capsules", "immune"),
    "vivid-health-vivid-nourishment-spirulina-250g": ("Vivid Spirulina — green superfood nourishment · 250g powder", "gut"),
    "vivid-health-immune-quercetin-complex-60-capsules": ("Vivid Quercetin Complex — immune & seasonal support · 60 capsules", "immune"),
    "vivid-health-stay-vivid-omega-oil-300-capsules": ("Vivid Omega Oil — heart, brain & eye support · 300 capsules", "body"),
    "vivid-health-vivid-body-msm-150g": ("Vivid MSM — joint, skin & hair support · 150g powder", "body"),
    "vivid-health-vivid-nourishment-moringa-powder-300-capsules": ("Vivid Moringa — daily green nourishment · 300 capsules", "gut"),
    "vivid-health-immune-immune-plus-60-capsules": ("Vivid Immune Plus — daily immune defence blend · 60 capsules", "immune"),
    "vivid-health-stay-vivid-griffonia-5-htp-60-capsules": ("Vivid Griffonia 5-HTP — mood & sleep support · 60 capsules", "mind"),
    "vivid-health-stay-vivid-gaba-150g": ("Vivid GABA — calm & restful sleep support · 150g powder", "mind"),
    "vivid-health-vivid-body-flexijoint-300-capsules": ("Vivid Flexijoint — everyday joint support · 300 capsules", "body"),
    "vivid-health-vivid-nourishment-epsom-salt-1kg": ("Vivid Epsom Salt — bath soak for tired muscles · 1kg", "body"),
    "vivid-health-stay-vivid-dmae-150g": ("Vivid DMAE — focus & mental clarity support · 150g powder", "mind"),
    "vivid-health-vivid-body-coenzyme-q10-60-capsules": ("Vivid Coenzyme Q10 — cellular energy & heart support · 60 capsules", "body"),
    "vivid-health-vivid-body-bone-supreme-500-capsules": ("Vivid Bone Supreme — bone & skeletal support · 500 capsules", "body"),
    "vivid-health-nutritent-health-barley-grass-300-capsules": ("Vivid Barley Grass — alkalising green nourishment · 300 capsules", "gut"),
    "vivid-health-nutritent-health-barley-grass-200g": ("Vivid Barley Grass — alkalising green nourishment · 200g powder", "gut"),
    "vivid-health-woman-angus-castus-60-capsules": ("Vivid Agnus Castus — hormonal balance support · 60 capsules", "woman"),
}

RANGE_LABEL = {"immune": "Vivid Immune", "gut": "Vivid Gut", "mind": "Vivid Mind",
               "body": "Vivid Body", "woman": "Vivid Woman", "man": "Vivid Man"}


def main():
    products = json.load(open(SRC))
    by_handle = {p["handle"]: p for p in products}
    updates, backup, rows, missing = [], [], [], []

    for handle, (new_title, rng) in NAMES.items():
        p = by_handle.get(handle)
        if not p:
            missing.append(handle)
            continue
        old_tags = p.get("tags", "")
        tags = [t.strip() for t in old_tags.split(",") if t.strip()]
        new_tags = [t for t in tags if not t.startswith("range:")]
        new_tags.append(f"range:{rng}")
        if "sa made" not in [t.lower() for t in new_tags]:
            new_tags.append("SA Made")
        upd = {"id": p["id"]}
        if p["title"] != new_title:
            upd["title"] = new_title
        joined = ", ".join(new_tags)
        if joined != old_tags:
            upd["tags"] = joined
        if len(upd) > 1:
            updates.append(upd)
            backup.append({"id": p["id"], "handle": handle,
                           "old_title": p["title"], "old_tags": old_tags})
            rows.append(f"| `{handle}` | {p['title']} | **{new_title}** | {RANGE_LABEL[rng]} |")

    unmapped = [p for p in products if p["handle"] not in NAMES
                and not re.match(r"^Vivid .+ (Stack|Pack)", p["title"])]

    os.makedirs("vivid/backend/apply", exist_ok=True)
    json.dump(updates, open("vivid/backend/apply/product-updates.json", "w"), indent=1)
    json.dump(backup, open("vivid/backend/rename-backup.json", "w"), indent=1)
    with open("vivid/backend/rename-table.md", "w") as f:
        f.write("# Vivid rename migration (handles unchanged — SEO safe)\n\n")
        f.write("| Handle | Old title | New title | Range |\n|---|---|---|---|\n")
        f.write("\n".join(rows) + "\n")
        if missing:
            f.write(f"\nMissing handles (not found in pull): {missing}\n")
        if unmapped:
            f.write("\nUnmapped products (left untouched): " +
                    ", ".join(f"`{p['handle']}`" for p in unmapped) + "\n")
    print(f"{len(updates)} updates staged, {len(missing)} missing, {len(unmapped)} unmapped")


if __name__ == "__main__":
    main()
