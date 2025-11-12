from __future__ import annotations
import time
import structlog
from tenacity import Retrying, stop_after_attempt, wait_random_exponential, retry_if_exception_type, RetryCallState
from typing import Optional, List
from .types import StylistTone, StylistResult
from .settings import Settings
from .safety import analyze_topic, clamp_length, strip_excess_emojis
from .prompts import build_system_prompt, build_user_prompt
from .agents import create_stylist_agent, create_stylist_task, run_crew
from .cache import cache_get, cache_set, make_cache_key

log = structlog.get_logger(__name__)

class StylistError(RuntimeError):
    pass

class ResponseStyleEnhancer:
    def __init__(self, cfg: Optional[Settings] = None) -> None:
        self.cfg = cfg or Settings()
        log.info(
            "stylist.init",
            provider=self.cfg.provider,
            openai_model=self.cfg.openai_model,
            ollama_model=self.cfg.ollama_model,
            temperature=self.cfg.temperature,
            max_tokens=self.cfg.max_tokens,
        )

    def _provider_chain(self) -> List[str]:
        chain = [self.cfg.provider]
        fallback = None
        if self.cfg.provider == "openai":
            fallback = "ollama"
        elif self.cfg.provider == "ollama" and self.cfg.get_openai_api_key():
            fallback = "openai"
        if fallback and fallback not in chain:
            chain.append(fallback)
        return chain

    def _invoke(self, question: str, answer: str, tone: StylistTone, serious: bool) -> str:
        def _log_retry(retry_state: RetryCallState) -> None:
            err = None
            if retry_state.outcome:
                try:
                    err = retry_state.outcome.exception()
                except Exception:
                    err = retry_state.outcome
            log.warning(
                "stylist.retry",
                try_num=retry_state.attempt_number,
                err=str(err) if err else "unknown"
            )

        retryer = Retrying(
            reraise=True,
            stop=stop_after_attempt(self.cfg.retry_attempts),
            wait=wait_random_exponential(
                multiplier=self.cfg.retry_min_wait_s,
                max=self.cfg.retry_max_wait_s
            ),
            retry=retry_if_exception_type((StylistError, RuntimeError)),
            before_sleep=_log_retry
        )

        def _call_with_provider(provider_choice: str) -> str:
            provider_override = None if provider_choice == self.cfg.provider else provider_choice
            system_prompt = build_system_prompt(
                tone=tone,
                max_emojis=self.cfg.max_emojis,
                max_length_chars=self.cfg.max_length_chars,
                serious=serious
            )
            user_prompt = build_user_prompt(question, answer)
            agent = create_stylist_agent(system_prompt, self.cfg, provider_override)
            task = create_stylist_task(agent, user_prompt)

            out = run_crew(agent, task)
            if not isinstance(out, str) or not out.strip():
                raise StylistError("Empty LLM output")
            return out.strip()

        def execute_call() -> str:
            last_error: Optional[Exception] = None
            for provider_choice in self._provider_chain():
                try:
                    return _call_with_provider(provider_choice)
                except Exception as e:
                    last_error = e
                    log.warning(
                        "stylist.provider_attempt_failed",
                        provider=provider_choice,
                        err=str(e),
                    )
            if last_error:
                log.exception("stylist.llm_error", exc=str(last_error))
                raise StylistError(str(last_error)) from last_error
            raise StylistError("Unknown LLM failure")

        return retryer(execute_call)

    def enhance(self, *, question: str, plain_answer: str, tone: StylistTone = StylistTone.WITTY) -> StylistResult:
        t0 = time.perf_counter()
        reduce, note = analyze_topic(question, plain_answer, self.cfg)
        used_tone = StylistTone.PROFESSIONAL if reduce else tone
        cache_key = make_cache_key(
            question.strip(),
            plain_answer.strip(),
            used_tone.value,
            f"{self.cfg.provider}:{self.cfg.active_model()}",
        )
        cached = cache_get(cache_key)
        if cached:
            log.info("stylist.cache_hit", key=cache_key)
            elapsed = int((time.perf_counter() - t0) * 1000)
            return {
                "styled_text": cached,
                "used_tone": used_tone,
                "safety_notes": note,
                "elapsed_ms": elapsed,
                "cache_hit": True,
            }

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
                "elapsed_ms": elapsed,
                "cache_hit": False,
            }

        # Post-process: clamp and emoji-limit
        rewritten = clamp_length(rewritten, self.cfg.max_length_chars)
        rewritten = strip_excess_emojis(rewritten, self.cfg.max_emojis)
        cache_set(cache_key, rewritten, self.cfg.cache_ttl_s, self.cfg.cache_max_items)

        elapsed = int((time.perf_counter() - t0)*1000)
        return {
            "styled_text": rewritten,
            "used_tone": used_tone,
            "safety_notes": note,
            "elapsed_ms": elapsed,
            "cache_hit": False,
        }
