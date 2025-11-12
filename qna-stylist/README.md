## QnA Stylist

Small helper that rewrites factual QnA answers with a witty tone while respecting topic safety filters. The stylist now prefers OpenAI `gpt-4o-mini` for maximum accuracy and will fall back to a local [Ollama](https://ollama.com/) `phi3:medium` model when cloud access fails.

### Prerequisites

- Python 3.11+
- [Ollama](https://ollama.com/) (only if you want to run Phi-3 locally)
- An OpenAI-style API key if you plan to use the OpenAI backend

### Setup

```bash
cd qna-stylist
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Running with OpenAI (default)

```bash
export OPENAI_API_KEY=sk-...
# optional overrides:
# export STYLIST_PROVIDER=openai
# export STYLIST_OPENAI_MODEL=gpt-4o-mini
```

Then run the quick check shown below.

### Running with Ollama fallback/local-only

1. Install Ollama (macOS example): `brew install ollama`
2. Start the Ollama service (brew does this automatically once installed) and download the model:
   ```bash
   ollama pull phi3:medium
   ```
3. Ensure the following environment variables are present (defaults shown):
   ```bash
   export STYLIST_PROVIDER=ollama
   export STYLIST_OLLAMA_MODEL=phi3:medium
   export OLLAMA_BASE_URL=http://localhost:11434/v1
   export OLLAMA_API_KEY=ollama
   ```

Now run a quick check:

```bash
python - <<'PY'
import json
from qna_stylist import ResponseStyleEnhancer, StylistTone

stylist = ResponseStyleEnhancer()
result = stylist.enhance(
    question="How can I reset my account password if I lost access to email?",
    plain_answer="Go to settings, click forgot password, follow instructions sent to your phone.",
    tone=StylistTone.WITTY
)
print(json.dumps(result, indent=2, default=str))
PY
```

### Advanced configuration

See `docs/CONFIG.md` for details on switching providers, tuning temperature / max tokens, and adjusting cache lifetimes.
