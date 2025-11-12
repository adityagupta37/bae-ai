from __future__ import annotations
import os
import structlog
from typing import Any, Optional
from crewai import Agent, Task, Crew, LLM
from crewai.crews.crew_output import CrewOutput
from crewai.llms.providers.openai.completion import OpenAICompletion as OpenAIChat
from .settings import Settings

log = structlog.get_logger(__name__)

def build_llm(cfg: Settings, provider_override: Optional[str] = None):
    provider = (provider_override or cfg.provider).lower()

    if provider == "openai":
        api_key = cfg.get_openai_api_key()
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is required for OpenAI provider usage.")
        log.debug(
            "llm.openai",
            model=cfg.openai_model,
            temperature=cfg.temperature,
            max_tokens=cfg.max_tokens,
        )
        return OpenAIChat(
            model=cfg.openai_model,
            api_key=api_key,
            temperature=cfg.temperature,
            top_p=1.0,
            presence_penalty=0.0,
            frequency_penalty=0.0,
            max_tokens=cfg.max_tokens,
        )

    if provider == "ollama":
        raw_base_url = cfg.ollama_base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
        base_url = raw_base_url.rstrip("/")
        if base_url.endswith("/v1"):
            base_url = base_url[: -len("/v1")]
        api_key = os.getenv("OLLAMA_API_KEY", "ollama")
        log.debug(
            "llm.ollama",
            model=cfg.ollama_model,
            base_url=base_url,
            temperature=cfg.temperature,
            max_tokens=cfg.max_tokens,
        )
        return LLM(
            model=f"ollama/{cfg.ollama_model}",
            api_base=base_url,
            api_key=api_key,
            temperature=cfg.temperature,
            top_p=1.0,
            presence_penalty=0.0,
            frequency_penalty=0.0,
            max_tokens=cfg.max_tokens,
            extra_body={
                "temperature": cfg.temperature,
                "num_predict": cfg.max_tokens,
            },
        )

    raise ValueError(f"Unsupported provider '{provider}'")

def create_stylist_agent(system_prompt: str, cfg: Settings, provider_override: Optional[str] = None) -> Agent:
    llm = build_llm(cfg, provider_override)

    return Agent(
        role="Response Humor Stylist",
        goal="Rewrite plain responses to be lively and witty while preserving accuracy.",
        backstory=system_prompt,
        verbose=False,
        allow_delegation=False,
        llm=llm,
    )


def create_stylist_task(agent: Agent, user_prompt: str) -> Task:
    return Task(
        description="Rewrite the provided answer per the stylist rules.",
        expected_output="One rewritten answer only.",
        agent=agent,
        input=user_prompt,
    )


def run_crew(agent: Agent, task: Task) -> str:
    crew = Crew(agents=[agent], tasks=[task], verbose=False)
    result: Any = crew.kickoff()

    if isinstance(result, CrewOutput):
        if result.raw:
            return result.raw
        if result.tasks_output:
            for task_output in result.tasks_output:
                text = None
                if isinstance(task_output, dict):
                    text = task_output.get("raw") or task_output.get("summary")
                elif hasattr(task_output, "raw"):
                    text = getattr(task_output, "raw")
                if text:
                    return text
        return ""

    return result
