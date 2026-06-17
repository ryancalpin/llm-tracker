#!/usr/bin/env python3
"""
Merge OpenRouter raw data + curated specialties + hosting services into one
data/models.json file the frontend loads. Also extract a list of "free" models
on OpenRouter for the promo section.
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"


def load(name: str) -> dict:
    return json.loads((DATA / name).read_text())


def find_specialty(model_id: str, specialties: dict) -> dict | None:
    """Match model_id against curated specialty entries (exact, then prefix)."""
    if model_id in specialties:
        return specialties[model_id]
    # try matching the canonical id form (sometimes OpenRouter uses a versioned slug)
    for k, v in specialties.items():
        if model_id == k or model_id.startswith(k + ":"):
            return v
    return None


def find_hosting(model_id: str, hosting: dict) -> list:
    if model_id in hosting:
        return hosting[model_id]
    for k, v in hosting.items():
        if model_id == k or model_id.startswith(k + ":"):
            return v
    return []


def find_free_promos(model: dict, promos: list) -> list:
    """Check if model matches a free promo pattern (by id)."""
    out = []
    mid = model.get("id", "")
    for p in promos:
        pat = p["model_pattern"]
        # Treat pattern as prefix/substring; the curated patterns are real model ids or prefixes
        if mid == pat or mid.startswith(pat):
            out.append(p)
    return out


def main() -> int:
    raw = load("openrouter_raw.json")
    curated = load("curated.json")
    specs_data = load("specialties.json")
    hosting = load("hosting.json")

    specs = specs_data.get("specialties", {})
    promos = curated.get("free_promos", [])
    subs = curated.get("subscriptions", [])

    enriched = []
    free_models_section = []
    for m in raw.get("models", []):
        mid = m.get("id", "")
        spec = find_specialty(mid, specs) or {}
        hosts = find_hosting(mid, hosting)
        promo_matches = find_free_promos(m, promos)

        # If pricing-in is 0 (free on OpenRouter), surface as a free model
        is_free_on_or = (m.get("pricing_in_per_m") == 0 and m.get("pricing_out_per_m") == 0)
        if is_free_on_or or promo_matches:
            free_models_section.append({
                "id": mid,
                "name": m.get("name"),
                "provider": m.get("provider"),
                "context_length": m.get("context_length"),
                "modality_in": m.get("modality_in"),
                "supports_tools": m.get("supports_tools"),
                "promo": "Free on OpenRouter" if is_free_on_or else None,
                "promos": [
                    {"start": p.get("start"), "end": p.get("end"), "provider": p.get("provider"), "notes": p.get("notes"), "promo": p.get("promo")}
                    for p in promo_matches
                ],
            })

        enriched.append({
            **m,
            "specialties": spec.get("specialties", []),
            "scores": spec.get("scores", {}),
            "blurb": spec.get("blurb"),
            "hosting": hosts,
            "promos": [
                {"start": p.get("start"), "end": p.get("end"), "provider": p.get("provider"), "notes": p.get("notes"), "promo": p.get("promo")}
                for p in promo_matches
            ],
        })

    # Sort by provider then name for stable display
    enriched.sort(key=lambda x: ((x.get("provider") or ""), (x.get("name") or "")))

    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "openrouter_fetched_at": raw.get("fetched_at"),
        "model_count": len(enriched),
        "provider_count": len({m.get("provider") for m in enriched if m.get("provider")}),
        "free_model_count": len(free_models_section),
        "models": enriched,
        "free_promos_section": sorted(free_models_section, key=lambda x: (x.get("provider") or "", x.get("name") or "")),
        "subscriptions": subs,
    }
    (DATA / "models.json").write_text(json.dumps(out, indent=None))  # compact for size
    print(f"OK: merged {len(enriched)} models, {len(free_models_section)} free, {len(subs)} subscription tiers -> {DATA/'models.json'}")
    print(f"   file size: {(DATA / 'models.json').stat().st_size / 1024:.1f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
