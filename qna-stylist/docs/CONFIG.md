## Stylist configuration quick reference

### Providers and models

```bash
# Prefer OpenAI (default)
export STYLIST_PROVIDER=openai
export STYLIST_OPENAI_MODEL=gpt-4o-mini
export OPENAI_API_KEY=sk-...

# Prefer Ollama / local fallback
export STYLIST_PROVIDER=ollama
export STYLIST_OLLAMA_MODEL=phi3:medium
export OLLAMA_BASE_URL=http://localhost:11434/v1
```

The engine automatically fails over between OpenAI and Ollama: OpenAI → Ollama if the API call fails, and Ollama → OpenAI (when an API key is present) for a secondary attempt.

### Generation controls

```bash
export STYLIST_TEMPERATURE=0.6
export STYLIST_MAX_TOKENS=512
```

These values are forwarded directly to the CrewAI LLM adapter (temperature, top_p, penalties, and max tokens/`num_predict`).

### Cache knobs

```bash
export STYLIST_CACHE_TTL_S=600
export STYLIST_CACHE_MAX_ITEMS=1024
```

The cache stores fully processed stylist outputs keyed by question, answer, tone, and provider/model. Lower the TTL for fresher responses, or raise `CACHE_MAX_ITEMS` to keep more rewrites in memory.
