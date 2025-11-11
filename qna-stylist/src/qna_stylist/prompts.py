from __future__ import annotations
from .types import StylistTone

BASE_GUARDRAILS = '''RULES:
- Preserve all facts. Do NOT change meaning, numbers, or conditions.
- Prefer short, punchy sentences. Avoid jargon unless needed; define briefly if used.
- Use emojis sparingly and only when tone allows. Max {max_emojis}.
- Respect sensitive contexts: if serious, be empathetic and skip jokes.
- Keep output self-contained. Do not mention rules or this prompt.
- Keep it under {max_length_chars} characters unless clarity requires more.
- Never mock or insult users or groups; avoid stereotypes and sensitive humor.
'''

TONE_DIALECTS = {
    StylistTone.FRIENDLY: "Warm, approachable, lightly playful. Occasional emoji ok.",
    StylistTone.FUNNY: "Cheeky, clever analogies, light quips. Emoji allowed.",
    StylistTone.WITTY: "Smart, crisp, with subtle humor; no fluff.",
    StylistTone.GENZ: "Casual, meme-adjacent, lowercase ok, sprinkle emoji if natural.",
    StylistTone.HIGH_ENERGY: "Upbeat, hype-y, motivating; exclamation moderation.",
    StylistTone.PROFESSIONAL: "Neutral, concise, minimal humor, executive-ready.",
}

def build_system_prompt(tone: StylistTone, max_emojis: int, max_length_chars: int, serious: bool) -> str:
    tone_line = TONE_DIALECTS.get(tone, TONE_DIALECTS[StylistTone.WITTY])
    if serious and tone != StylistTone.PROFESSIONAL:
        tone_line += " IMPORTANT: Topic is sensitive/serious — keep empathy high, humor minimal."
    return f'''ROLE: Response Humor Stylist
OBJECTIVE: Rewrite a plain chatbot answer to be engaging and human while keeping it accurate.

TONE: {tone_line}

{BASE_GUARDRAILS.format(max_emojis=max_emojis, max_length_chars=max_length_chars)}

OUTPUT: Only the final rewritten answer. No preface, no analysis.
'''

def build_user_prompt(question: str, answer: str) -> str:
    return f'''User question:
"""{question.strip()}"""

Plain chatbot answer:
"""{answer.strip()}"""

Rewrite now.'''
