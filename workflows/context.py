from dataclasses import dataclass, field
from typing import Optional, Any, Callable, AsyncIterator
from uuid import UUID

from db.client import PostgresClient


@dataclass
class AgentConfig:
    """
    The agent config can either have one or more databases and 'tools' to
    complete a SQL Query
    """

    db_client: PostgresClient  # Access to a database
    semantics: Optional[dict[str, Any] | str] = None


@dataclass
class WorkflowContext:
    workflow_id: UUID
    user_id: int
    workflow_type: str
    user_query: str
    config: AgentConfig

    # Derived state -> mutated by workflow steps
    query_type: Optional[str] = None
    query_type_reason: str = None
    sanitized_query: Optional[str] = None
    generated_sql: Optional[str] = None
    is_sql_valid: bool = True
    is_sql_valid_reason: str = None
    db_results: Optional[list] = None
    summary: str = None

    # Flags for flow control
    should_continue: bool = True
    error_sent: bool = False

    # Conversation history
    conversation_history: list[dict] = field(default_factory=list[dict])

    # Pipeline steps
    _steps: list[Callable] = field(default_factory=list, repr=False)

    def register(self, *steps: Callable) -> "WorkflowContext":
        self._steps.extend(steps)
        return self

    async def run(self) -> AsyncIterator[str]:
        for step in self._steps:
            async for event in step(self):
                yield event
            if not self.should_continue:
                return
