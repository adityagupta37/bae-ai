import time
from qna_stylist import ResponseStyleEnhancer, StylistTone
from qna_stylist.settings import Settings
from qna_stylist.cache import cache_clear
from qna_stylist import agents


def setup_function(_function):
    cache_clear()


def test_cache_hit_skips_llm(monkeypatch):
    cfg = Settings(provider="openai", openai_api_key="test-key")
    enhancer = ResponseStyleEnhancer(cfg=cfg)
    call_counter = {"count": 0}

    def fake_invoke(self, question, answer, tone, serious):
        call_counter["count"] += 1
        time.sleep(0.05)
        return "Styled!"

    monkeypatch.setattr(ResponseStyleEnhancer, "_invoke", fake_invoke)

    first = enhancer.enhance(
        question="How do I reset?",
        plain_answer="Follow the reset steps.",
        tone=StylistTone.WITTY,
    )
    second = enhancer.enhance(
        question="How do I reset?",
        plain_answer="Follow the reset steps.",
        tone=StylistTone.WITTY,
    )

    assert call_counter["count"] == 1
    assert first["styled_text"] == second["styled_text"] == "Styled!"
    assert second["elapsed_ms"] <= first["elapsed_ms"]
    assert first["cache_hit"] is False
    assert second["cache_hit"] is True


def test_build_llm_applies_generation_params(monkeypatch):
    captured = {}

    class DummyLLM:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr(agents, "OpenAIChat", DummyLLM)
    cfg = Settings(
        provider="openai",
        openai_api_key="test-key",
        temperature=0.42,
        max_tokens=321,
        openai_model="gpt-test",
    )

    agents.build_llm(cfg)

    assert captured["model"] == "gpt-test"
    assert captured["temperature"] == 0.42
    assert captured["max_tokens"] == 321
    assert captured["top_p"] == 1.0
