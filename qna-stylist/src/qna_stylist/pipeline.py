from __future__ import annotations
import time
import structlog
from tenacity import retry, stop_after_attempt, wait_random_exponential, retry_if_exception_type
from typing import Optional
from .types import StylistTone, StylistResult
from .settings import Settings
from .safety import analyze_topic, clamp_length, strip_excess_emojis
from .prompts import build_system_prompt, build_user_prompt
from .agents import create_stylist_agent, create_stylist_task, run_crew

log = structlog.get_logger(__name__)

class StylistError(RuntimeError):
    pass

class ResponseStyleEnhancer:
    def __init__(self, cfg: Optional[Settings] = None) -> None:
        self.cfg = cfg or Settings()
        log.info("stylist.init", model=self.cfg.llm_model, max_emojis=self.cfg.max_emojis)

    @retry(
        reraise=True,
        stop=stop_after_attempt(lambda self: self.cfg.retry_attempts),
        wait=wait_random_exponential(multiplier=lambda self: self.cfg.retry_min_wait_s,
                                     max=lambda self: self.cfg.retry_max_wait_s),
        retry=retry_if_exception_type((StylistError, RuntimeError)),
        before_sleep=lambda retry_state: log.warning("stylist.retry", try_num=retry_state.attempt_number, err=str(retry_state.outcome.exception()) if retry_state.outcome else "unknown")
    )
    def _invoke(self, question: str, answer: str, tone: StylistTone, serious: bool) -> str:
        system_prompt = build_system_prompt(
            tone=tone,
            max_emojis=self.cfg.max_emojis,
            max_length_chars=self.cfg.max_length_chars,
            serious=serious
        )
        user_prompt = build_user_prompt(question, answer)
        agent = create_stylist_agent(system_prompt)
        task = create_stylist_task(agent, user_prompt)

        try:
            out = run_crew(agent, task)
        except Exception as e:
            log.exception("stylist.llm_error", exc=str(e))
            raise StylistError(str(e)) from e

        if not isinstance(out, str) or not out.strip():
            raise StylistError("Empty LLM output")
        return out.strip()

    def enhance(self, *, question: str, plain_answer: str, tone: StylistTone = StylistTone.WITTY) -> StylistResult:
        t0 = time.perf_counter()
        reduce, note = analyze_topic(question, plain_answer, self.cfg)
        used_tone = StylistTone.PROFESSIONAL if reduce else tone

        try:
            rewritten = self._invoke(question, plain_answer, used_tone, serious=reduce)
        except Exception as e:
            # Fail-safe: return original text with a gentle fallback
            log.error("stylist.fallback", reason=str(e))
            elapsed = int((time.perf_counter() - t0)*1000)
            return {
                "styled_text": plain_answer,
                "used_tone": StylistTone.PROFESSIONAL if reduce else tone,
                "safety_notes": (note or "") + (" | Fallback to original due to error." if note else "Fallback to original due to error."),
                "elapsed_ms": elapsed
            }

        # Post-process: clamp and emoji-limit
        rewritten = clamp_length(rewritten, self.cfg.max_length_chars)
        rewritten = strip_excess_emojis(rewritten, self.cfg.max_emojis)

        elapsed = int((time.perf_counter() - t0)*1000)
        return {
            "styled_text": rewritten,
            "used_tone": used_tone,
            "safety_notes": note,
            "elapsed_ms": elapsed
        }
