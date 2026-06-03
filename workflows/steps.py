import json
from typing import AsyncIterator

from agents.sql_generator.agent import sql_generator_agent, Deps
from app.dependecies.logger import logger
from workflows.context import WorkflowContext


async def step_generate_sql(ctx: WorkflowContext) -> AsyncIterator[str]:
    """Generate SQL from sanitized intent"""
    yield f"data: {json.dumps({'step': 'generating', 'message': 'Thinking...'})}\n\n"

    deps = Deps(semantic_layer=ctx.config.semantic_layer)
    generation_result = await sql_generator_agent.run(ctx.sanitized_query, deps=deps)

    # Clean the SQL: strip whitespace and trailing punctuation
    raw_sql = generation_result.output.sql
    ctx.generated_sql = raw_sql.strip().rstrip(".")

    logger.info("generated sql", generated_sql=ctx.generated_sql)

    yield f"data: {json.dumps({'step': 'generated_sql', 'sql': ctx.generated_sql})}\n\n"
