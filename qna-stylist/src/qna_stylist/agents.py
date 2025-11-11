from __future__ import annotations
from crewai import Agent, Task, Crew

def create_stylist_agent(system_prompt: str) -> Agent:
    
    return Agent(
        role="Response Humor Stylist",
        goal="Rewrite plain responses to be lively and witty while preserving accuracy.",
        backstory=system_prompt,
        verbose=False,
        allow_delegation=False,
    )

def create_stylist_task(agent: Agent, user_prompt: str) -> Task:
    return Task(
        description="Rewrite the provided answer per the stylist rules.",
        expected_output="One rewritten answer only.",
        agent=agent,
        input=user_prompt
    )

def run_crew(agent: Agent, task: Task) -> str:
    crew = Crew(agents=[agent], tasks=[task], verbose=False)
    return crew.kickoff()
