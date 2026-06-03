"""
Workflow orchestrators that compose reusable steps into complete pipelines.
Each workflow defines a specific execution path through the available steps.
"""

import json
from typing import AsyncIterator
from uuid import UUID

from workflows.context import WorkflowContext, AgentConfig
from workflows.steps import (
    step_classify_query,
    step_generate_sql,
    # step_validate_sql,
    # step_execute_sql,
    # step_summarize_and_render,
)

# ==================== MAIN TEXT-TO-SQL WORKFLOW ====================


async def chat_workflow_processor(
    customer_id: int,
    workflow_id: UUID,
    workflow_type: str,
    customer_query: str,
    config: AgentConfig,
) -> AsyncIterator[str]:
    """
    Full text-to-SQL workflow with intent classification, generation, validation, and execution.

    Pipeline:
        Fetch Semantic Layer → Classify Intent → Generate SQL →
        Validate SQL → Execute SQL → Summarize & Render

    Args:
        customer_id: Authenticated user's ID
        customer_query: Natural language query from the user
        workflow_type: Type of workflow (e.g., 'chat', 'report')
        workflow_id: unique identifier for a workflow
        config

    Yields:
        SSE events as JSON strings
    """
    try:
        # Initialize shared context
        ctx = WorkflowContext(
            user_id=customer_id,
            workflow_id=workflow_id,
            workflow_type=workflow_type,
            user_query=customer_query,
            config=config,
        ).register(
            step_classify_query,
            step_generate_sql,
            # step_validate_sql,
            # step_execute_sql,
            # step_summarize_and_render,
        )

        async for event in ctx.run():
            yield event

    except Exception as e:
        print(f"\n[ERROR] Workflow failed: {str(e)}\n")
        yield f"data: {json.dumps({'error': f'Workflow failed: {str(e)}'})}\n\n"
