#!/usr/bin/env python3
"""
Fetch live model data from OpenRouter's free public API.
Output: data/openrouter_raw.json

OpenRouter aggregates 300+ models from 50+ providers with:
- Real-time pricing (per token, converted to per-million)
- Context length
- Modality (text/image/audio/video in/out)
- Supported parameters (tools, structured output, reasoning, etc.)
- Creation date
"""

import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

OUTPUT = Path(__file__).parent.parent / "data" / "openrouter_raw.json"
URL = "https://openrouter.ai/api/v1/models"


def fetch() -> dict:
    req = urllib.request.Request(URL, headers={"User-Agent": "llm-tracker/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def normalize(m: dict) -> dict:
    """Pull out only the fields we need and normalize them."""
    pricing = m.get("pricing", {}) or {}
    arch = m.get("architecture", {}) or {}
    top = m.get("top_provider", {}) or {}
    params = m.get("supported_parameters", []) or []

    # Pricing comes as USD per token. Convert to per-million-tokens.
    prompt_per_m = None
    completion_per_m = None
    try:
        if pricing.get("prompt") is not None:
            prompt_per_m = float(pricing["prompt"]) * 1_000_000
    except (ValueError, TypeError):
        pass
    try:
        if pricing.get("completion") is not None:
            completion_per_m = float(pricing["completion"]) * 1_000_000
    except (ValueError, TypeError):
        pass

    return {
        "id": m.get("id"),
        "canonical_slug": m.get("canonical_slug"),
        "name": m.get("name"),
        "provider": m.get("id", "").split("/")[0] if m.get("id") else None,
        "description": m.get("description"),
        "context_length": m.get("context_length"),
        "max_completion_tokens": top.get("max_completion_tokens"),
        "modality_in": arch.get("input_modalities", []) or [],
        "modality_out": arch.get("output_modalities", []) or [],
        "tokenizer": arch.get("tokenizer"),
        "pricing_in_per_m": prompt_per_m,
        "pricing_out_per_m": completion_per_m,
        "supports_tools": "tools" in params,
        "supports_structured_output": "structured_outputs" in params,
        "supports_reasoning": "reasoning" in params,
        "supports_vision": "image" in (arch.get("input_modalities") or []),
        "moderated": top.get("is_moderated", False),
        "created": m.get("created"),
        "knowledge_cutoff": m.get("knowledge_cutoff"),
    }


def main() -> int:
    try:
        raw = fetch()
    except Exception as e:
        print(f"ERROR fetching OpenRouter: {e}", file=sys.stderr)
        return 1

    models = [normalize(m) for m in raw.get("data", [])]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps({
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "source": "openrouter.ai",
        "count": len(models),
        "models": models,
    }, indent=2))

    providers = sorted({m["provider"] for m in models if m["provider"]})
    print(f"OK: wrote {len(models)} models from {len(providers)} providers to {OUTPUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
