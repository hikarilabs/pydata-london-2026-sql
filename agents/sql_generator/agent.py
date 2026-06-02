from dataclasses import dataclass
from typing import Any, Optional, Literal

from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field

from agents.sql_generator.prompts import sql_generator_p1


@dataclass
class Deps:
    """Dependencies for the agent, holding the semantic layer data."""

    semantic_layer: str | dict[str, Any] | None


class SqlResponse(BaseModel):
    sql: str = Field(description="The raw SQL query without any markdown formatting")
    intent_status: Literal["valid", "rejected"] = Field(
        description="Whether the intent was valid or rejected", default="valid"
    )
    rejection_reason: Optional[str] = Field(
        description="Reason for rejection if intent_status is 'rejected'", default=None
    )


# Define the Generator Agent
sql_generator_agent = Agent("openai:gpt-4o", output_type=SqlResponse, deps_type=Deps)


@sql_generator_agent.system_prompt
def inject_semantic_layer(ctx: RunContext[Deps]) -> str:
    return sql_generator_p1(ctx)
