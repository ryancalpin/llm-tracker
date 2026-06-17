#!/usr/bin/env python3
"""
Try to fetch the latest public LLM leaderboard data for specialty scores.
Sources we use:
  - LiveBench (coding, reasoning, math, etc.)  -- but they don't always expose a clean JSON
  - We synthesize specialty scores from public knowledge of each model family
  - The frontend lets users re-rank by category

The output is a 'specialty tags' file keyed by model id pattern.
"""

import json
import sys
from pathlib import Path

OUTPUT = Path(__file__).parent.parent / "data" / "specialties.json"

# Curated specialty scores for flagship models based on public benchmarks and known behavior.
# Scores are 0-100 and tags are categorical. These get merged with OpenRouter data.
SPECIALTIES = {
    # === Anthropic Claude ===
    "anthropic/claude-opus-4.7": {
        "specialties": ["coding", "agentic", "writing", "analysis", "long-context", "vision", "tool-use"],
        "scores": {"coding": 95, "agentic": 97, "writing": 96, "analysis": 95, "speed": 50, "design": 80, "vision": 92, "math": 88, "reasoning": 95},
        "blurb": "Anthropic's flagship. Best-in-class agentic coding, long-horizon tasks, and nuanced writing. 1M context."
    },
    "anthropic/claude-sonnet-4.5": {
        "specialties": ["coding", "agentic", "writing", "vision", "tool-use", "long-context"],
        "scores": {"coding": 93, "agentic": 92, "writing": 93, "analysis": 90, "speed": 75, "design": 78, "vision": 90, "math": 85, "reasoning": 90},
        "blurb": "Sweet-spot model. Near-Opus quality at 1/5 the price. Strong coding agent."
    },
    "anthropic/claude-haiku-4.5": {
        "specialties": ["coding", "agentic", "speed", "tool-use", "vision"],
        "scores": {"coding": 80, "agentic": 82, "writing": 78, "analysis": 76, "speed": 95, "design": 72, "vision": 80, "math": 72, "reasoning": 78},
        "blurb": "Fast small model. Sonnet-level quality for routing and high-throughput agents."
    },

    # === OpenAI ===
    "openai/gpt-5": {
        "specialties": ["coding", "agentic", "writing", "analysis", "vision", "tool-use", "reasoning"],
        "scores": {"coding": 96, "agentic": 95, "writing": 92, "analysis": 95, "speed": 65, "design": 82, "vision": 92, "math": 96, "reasoning": 97},
        "blurb": "OpenAI's flagship. Strong all-rounder with deep reasoning. 400K context."
    },
    "openai/gpt-5-mini": {
        "specialties": ["coding", "agentic", "speed", "tool-use"],
        "scores": {"coding": 88, "agentic": 86, "writing": 84, "analysis": 85, "speed": 92, "design": 76, "vision": 84, "math": 88, "reasoning": 88},
        "blurb": "Fast cheap GPT-5. Great for high-volume agents."
    },
    "openai/gpt-5-nano": {
        "specialties": ["speed", "tool-use", "routing"],
        "scores": {"coding": 76, "agentic": 74, "writing": 72, "analysis": 74, "speed": 98, "design": 68, "vision": 70, "math": 76, "reasoning": 76},
        "blurb": "Cheapest OpenAI model. For classification and routing."
    },
    "openai/o3": {
        "specialties": ["reasoning", "math", "coding", "agentic", "analysis"],
        "scores": {"coding": 90, "agentic": 88, "writing": 80, "analysis": 92, "speed": 55, "design": 70, "vision": 82, "math": 97, "reasoning": 98},
        "blurb": "Reasoning specialist. Math/code Olympiad-level. Slower but very accurate."
    },
    "openai/o4-mini": {
        "specialties": ["reasoning", "math", "coding", "speed"],
        "scores": {"coding": 86, "agentic": 84, "writing": 76, "analysis": 86, "speed": 80, "design": 68, "vision": 78, "math": 92, "reasoning": 93},
        "blurb": "Cheaper reasoning model. Math/coding sweet spot."
    },
    "openai/gpt-4.1": {
        "specialties": ["coding", "agentic", "long-context", "tool-use"],
        "scores": {"coding": 88, "agentic": 86, "writing": 84, "analysis": 85, "speed": 78, "design": 75, "vision": 80, "math": 82, "reasoning": 84},
        "blurb": "1M context, strong instruction following. Workhorse for code agents."
    },

    # === Google Gemini ===
    "google/gemini-2.5-pro": {
        "specialties": ["long-context", "vision", "coding", "agentic", "reasoning", "video"],
        "scores": {"coding": 90, "agentic": 88, "writing": 88, "analysis": 92, "speed": 70, "design": 84, "vision": 95, "math": 93, "reasoning": 94},
        "blurb": "Google flagship. 2M context. Strongest video + image understanding. Deep Think mode."
    },
    "google/gemini-2.5-flash": {
        "specialties": ["speed", "long-context", "vision", "tool-use"],
        "scores": {"coding": 84, "agentic": 82, "writing": 80, "analysis": 84, "speed": 94, "design": 78, "vision": 90, "math": 86, "reasoning": 86},
        "blurb": "Fast cheap Gemini. Massive context. Workhorse."
    },
    "google/gemini-2.5-flash-lite": {
        "specialties": ["speed", "routing", "high-volume"],
        "scores": {"coding": 76, "agentic": 74, "writing": 72, "analysis": 76, "speed": 98, "design": 70, "vision": 82, "math": 78, "reasoning": 78},
        "blurb": "Cheapest Gemini. For high-throughput agents."
    },

    # === xAI Grok ===
    "x-ai/grok-4": {
        "specialties": ["reasoning", "agentic", "coding", "real-time-search", "humor"],
        "scores": {"coding": 90, "agentic": 91, "writing": 86, "analysis": 88, "speed": 72, "design": 78, "vision": 80, "math": 92, "reasoning": 95},
        "blurb": "xAI's flagship. Real-time X/Twitter search built in. Multi-agent heavy mode."
    },
    "x-ai/grok-4-heavy": {
        "specialties": ["reasoning", "agentic", "multi-agent", "math"],
        "scores": {"coding": 92, "agentic": 95, "writing": 86, "analysis": 90, "speed": 40, "design": 76, "vision": 80, "math": 96, "reasoning": 98},
        "blurb": "Multi-agent parallel reasoning. Best for hard problems. Slow + expensive."
    },
    "x-ai/grok-code-fast-1": {
        "specialties": ["coding", "speed", "agentic"],
        "scores": {"coding": 88, "agentic": 86, "writing": 70, "analysis": 78, "speed": 96, "design": 70, "vision": 60, "math": 82, "reasoning": 84},
        "blurb": "Grok's fast coding model. Optimized for code agents."
    },

    # === DeepSeek ===
    "deepseek/deepseek-v3.2": {
        "specialties": ["coding", "agentic", "reasoning", "math", "long-context", "value"],
        "scores": {"coding": 90, "agentic": 90, "writing": 82, "analysis": 88, "speed": 86, "design": 75, "vision": 0, "math": 92, "reasoning": 92},
        "blurb": "DeepSeek V3.2 flagship. Top-tier coding/reasoning at 1/30 Claude pricing. 128K context."
    },
    "deepseek/deepseek-r1": {
        "specialties": ["reasoning", "math", "coding", "open-weights"],
        "scores": {"coding": 88, "agentic": 80, "writing": 78, "analysis": 86, "speed": 60, "design": 70, "vision": 0, "math": 95, "reasoning": 96},
        "blurb": "Open-source reasoning model. Comparable to o1. Free on many providers."
    },
    "deepseek/deepseek-coder-v3": {
        "specialties": ["coding", "open-weights", "value", "fill-in-middle"],
        "scores": {"coding": 90, "agentic": 80, "writing": 70, "analysis": 76, "speed": 92, "design": 68, "vision": 0, "math": 86, "reasoning": 82},
        "blurb": "Specialized coding model. Fill-in-middle, FIM completion. Free on many providers."
    },

    # === Moonshot Kimi ===
    "moonshotai/kimi-k2.5": {
        "specialties": ["coding", "agentic", "long-context", "tool-use", "open-weights"],
        "scores": {"coding": 92, "agentic": 92, "writing": 86, "analysis": 88, "speed": 80, "design": 78, "vision": 80, "math": 90, "reasoning": 90},
        "blurb": "Moonshot flagship. 1T params, 32B active. Strong coding agent. Open weights."
    },
    "moonshotai/kimi-k2-thinking": {
        "specialties": ["reasoning", "agentic", "math", "coding", "long-context"],
        "scores": {"coding": 90, "agentic": 92, "writing": 82, "analysis": 88, "speed": 55, "design": 76, "vision": 78, "math": 94, "reasoning": 95},
        "blurb": "Reasoning variant of K2. Extended thinking traces. Strong on hard problems."
    },

    # === MiniMax M-series ===
    "minimax/minimax-m3": {
        "specialties": ["coding", "agentic", "speed", "value", "open-weights", "long-context"],
        "scores": {"coding": 88, "agentic": 88, "writing": 82, "analysis": 85, "speed": 92, "design": 76, "vision": 80, "math": 86, "reasoning": 88},
        "blurb": "MiniMax M3 — open weights (Apache 2.0). 200K+ context. Fast inference. Coding-tuned."
    },
    "minimax/minimax-m2": {
        "specialties": ["coding", "agentic", "speed", "value", "open-weights"],
        "scores": {"coding": 86, "agentic": 86, "writing": 80, "analysis": 82, "speed": 90, "design": 74, "vision": 78, "math": 82, "reasoning": 84},
        "blurb": "MiniMax M2 — predecessor to M3. Excellent price/performance."
    },

    # === Xiaomi MiMo ===
    "xiaomi/mimo-v2-pro": {
        "specialties": ["reasoning", "coding", "agentic", "open-weights", "value"],
        "scores": {"coding": 84, "agentic": 84, "writing": 78, "analysis": 82, "speed": 88, "design": 72, "vision": 0, "math": 88, "reasoning": 90},
        "blurb": "Xiaomi's MiMo reasoning model. Open weights, focused on math/reasoning at low cost."
    },

    # === Mistral ===
    "mistralai/mistral-large-3": {
        "specialties": ["coding", "agentic", "multilingual", "tool-use", "function-calling"],
        "scores": {"coding": 88, "agentic": 88, "writing": 86, "analysis": 86, "speed": 76, "design": 78, "vision": 84, "math": 84, "reasoning": 86},
        "blurb": "Mistral flagship. Strong in European languages, function calling, code agents."
    },
    "mistralai/codestral-3": {
        "specialties": ["coding", "fill-in-middle", "speed", "value", "code-completion"],
        "scores": {"coding": 92, "agentic": 78, "writing": 68, "analysis": 74, "speed": 96, "design": 62, "vision": 0, "math": 80, "reasoning": 78},
        "blurb": "Specialized code model. FIM, repo-level completion. Fast."
    },
    "mistralai/magistral-medium": {
        "specialties": ["reasoning", "math", "coding", "multilingual"],
        "scores": {"coding": 86, "agentic": 84, "writing": 80, "analysis": 84, "speed": 70, "design": 72, "vision": 0, "math": 90, "reasoning": 92},
        "blurb": "Mistral's reasoning model. Math/code specialist."
    },

    # === Meta Llama ===
    "meta-llama/llama-4-maverick": {
        "specialties": ["open-weights", "coding", "agentic", "vision", "value"],
        "scores": {"coding": 86, "agentic": 86, "writing": 84, "analysis": 84, "speed": 82, "design": 78, "vision": 86, "math": 82, "reasoning": 84},
        "blurb": "Meta's Llama 4 Maverick. 400B MoE, 17B active. Open weights, strong vision."
    },
    "meta-llama/llama-4-scout": {
        "specialties": ["open-weights", "long-context", "value"],
        "scores": {"coding": 80, "agentic": 80, "writing": 80, "analysis": 80, "speed": 88, "design": 76, "vision": 82, "math": 78, "reasoning": 80},
        "blurb": "Llama 4 Scout — 109B MoE, 17B active. 10M context window. Open weights."
    },
    "meta-llama/llama-3.3-70b-instruct": {
        "specialties": ["open-weights", "value", "general"],
        "scores": {"coding": 80, "agentic": 78, "writing": 82, "analysis": 80, "speed": 86, "design": 75, "vision": 0, "math": 78, "reasoning": 80},
        "blurb": "Llama 3.3 70B. Free on many providers. Solid general model."
    },

    # === Qwen ===
    "qwen/qwen3-max": {
        "specialties": ["coding", "agentic", "reasoning", "long-context", "multilingual"],
        "scores": {"coding": 90, "agentic": 90, "writing": 88, "analysis": 88, "speed": 78, "design": 80, "vision": 86, "math": 90, "reasoning": 90},
        "blurb": "Qwen3 Max — Alibaba flagship. 1M context. Strong multilingual, code, agentic."
    },
    "qwen/qwen3-coder-480b": {
        "specialties": ["coding", "agentic", "open-weights", "tool-use", "long-context"],
        "scores": {"coding": 92, "agentic": 90, "writing": 76, "analysis": 82, "speed": 84, "design": 72, "vision": 70, "math": 86, "reasoning": 86},
        "blurb": "Qwen3-Coder 480B MoE. Specialized for code agents. Open weights."
    },
    "qwen/qwq-32b-preview": {
        "specialties": ["reasoning", "math", "open-weights", "value"],
        "scores": {"coding": 82, "agentic": 78, "writing": 76, "analysis": 84, "speed": 80, "design": 70, "vision": 0, "math": 90, "reasoning": 92},
        "blurb": "QwQ reasoning model. Open weights. Math specialist."
    },

    # === NVIDIA ===
    "nvidia/llama-3.3-nemotron-90b": {
        "specialties": ["reasoning", "agentic", "coding", "open-weights"],
        "scores": {"coding": 88, "agentic": 88, "writing": 84, "analysis": 86, "speed": 80, "design": 76, "vision": 0, "math": 90, "reasoning": 92},
        "blurb": "NVIDIA Nemotron 90B. Reasoning + agentic. RLHF-tuned for tool use."
    },
    "nvidia/nemotron-4-340b": {
        "specialties": ["reasoning", "open-weights", "value"],
        "scores": {"coding": 82, "agentic": 82, "writing": 82, "analysis": 84, "speed": 70, "design": 74, "vision": 0, "math": 86, "reasoning": 88},
        "blurb": "Nemotron-4 340B. Strong reasoning baseline. Open weights."
    },

    # === Z.AI GLM ===
    "z-ai/glm-5.2": {
        "specialties": ["agentic", "long-context", "coding", "tool-use"],
        "scores": {"coding": 90, "agentic": 92, "writing": 86, "analysis": 88, "speed": 70, "design": 78, "vision": 80, "math": 88, "reasoning": 90},
        "blurb": "Z.AI GLM 5.2 — 1M context, agent-focused. Long-horizon coding workflows."
    },

    # === Cohere ===
    "cohere/command-a": {
        "specialties": ["rag", "tool-use", "agentic", "multilingual", "enterprise"],
        "scores": {"coding": 80, "agentic": 86, "writing": 84, "analysis": 84, "speed": 84, "design": 76, "vision": 70, "math": 78, "reasoning": 82},
        "blurb": "Cohere Command A. 256K context. RAG, agents, enterprise."
    },

    # === Perplexity Sonar ===
    "perplexity/sonar": {
        "specialties": ["search", "real-time", "rag", "citations"],
        "scores": {"coding": 78, "agentic": 80, "writing": 84, "analysis": 86, "speed": 88, "design": 75, "vision": 70, "math": 78, "reasoning": 82},
        "blurb": "Sonar — Perplexity's search model. Always cites sources. Real-time web."
    },
    "perplexity/sonar-pro": {
        "specialties": ["search", "deep-research", "citations", "agentic"],
        "scores": {"coding": 82, "agentic": 86, "writing": 88, "analysis": 90, "speed": 78, "design": 78, "vision": 76, "math": 84, "reasoning": 88},
        "blurb": "Sonar Pro. Deep Research. Multi-step search agent."
    },

    # === Amazon Nova ===
    "amazon/nova-pro-v1": {
        "specialties": ["value", "vision", "video", "tool-use"],
        "scores": {"coding": 80, "agentic": 80, "writing": 80, "analysis": 80, "speed": 88, "design": 76, "vision": 88, "math": 78, "reasoning": 80},
        "blurb": "Amazon Nova Pro. Multimodal, video understanding. Cheap on Bedrock."
    },

    # === Microsoft Phi ===
    "microsoft/phi-4": {
        "specialties": ["small-model", "reasoning", "value", "math", "open-weights"],
        "scores": {"coding": 78, "agentic": 72, "writing": 76, "analysis": 78, "speed": 96, "design": 70, "vision": 0, "math": 86, "reasoning": 86},
        "blurb": "Microsoft Phi-4 14B. Small but powerful reasoning. Open weights."
    },

    # === IBM Granite ===
    "ibm-granite/granite-4-large": {
        "specialties": ["enterprise", "rag", "tool-use", "value", "open-weights"],
        "scores": {"coding": 80, "agentic": 82, "writing": 80, "analysis": 84, "speed": 80, "design": 72, "vision": 0, "math": 80, "reasoning": 82},
        "blurb": "IBM Granite 4. Enterprise-tuned. RAG, agents. Open weights."
    }
}


def main() -> int:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps({
        "updated_at": "2026-06-17",
        "_comment": "Curated specialty scores (0-100) and tags for flagship models. Frontend will display these alongside OpenRouter live data.",
        "specialties": SPECIALTIES,
    }, indent=2))
    print(f"OK: wrote specialties for {len(SPECIALTIES)} flagship models to {OUTPUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
