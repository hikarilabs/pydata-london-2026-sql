from dataclasses import dataclass
from typing import Any, Optional, Literal

from pydantic_ai import Agent, RunContext, ModelSettings
from pydantic import BaseModel, Field

from agents.shared import Deps
from agents.sql_generator.prompts import sql_generator_user, sql_generator_analyst


class SqlResponse(BaseModel):
    sql: str = Field(description="The raw SQL query without any markdown formatting")
    intent_status: Literal["valid", "rejected"] = Field(
        description="Whether the intent was valid or rejected", default="valid"
    )
    rejection_reason: Optional[str] = Field(
        description="Reason for rejection if intent_status is 'rejected'", default=None
    )


PromptMode = Literal["user", "analyst"]

_PROMPT_MAP = {
    "user": sql_generator_user,
    "analyst": sql_generator_analyst,
}


def build_sql_generator(mode: PromptMode = "user") -> Agent:
    """Create a SQL generator agent with the specified system prompt mode."""
    prompt_fn = _PROMPT_MAP[mode]

    agent = Agent(
        "openai:gpt-4o",
        output_type=SqlResponse,
        deps_type=Deps,
        model_settings=ModelSettings(temperature=0.0),
    )

    agent.system_prompt(prompt_fn)
    return agent


# Pre-built agent instances
sql_generator_user_agent = build_sql_generator("user")
sql_generator_analyst_agent = build_sql_generator("analyst")
