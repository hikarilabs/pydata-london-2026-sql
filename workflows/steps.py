import json
from typing import AsyncIterator

from agents.intent_validator.agent import intent_classifier_agent
from agents.shared import QueryType, Deps
from agents.sql_generator.agent import sql_generator_agent
from app.dependencies.logger import logger
from workflows.context import WorkflowContext


async def step_classify_query(ctx: WorkflowContext) -> AsyncIterator[str]:
    """Classify user intent for security and relevance"""
    yield f"data: {json.dumps({'step': 'classifying', 'message': 'Analyzing user request...'})}\n\n"

    logger.info("user query", user_id=ctx.user_id, query=ctx.user_query)

    deps = Deps(semantic_layer=ctx.config.semantics, cust_id=ctx.user_id)
    query_type_result = await intent_classifier_agent.run(ctx.user_query, deps=deps)

    # TODO: track token usage per workflow step
    tkns_usage = query_type_result.usage()
    tkns_usage_input = tkns_usage.input_tokens
    tkns_usage_output = tkns_usage.output_tokens

    query_type = query_type_result.output.query_type.value

    # persist query type classification result to the context
    ctx.query_type = query_type
    ctx.query_type_reason = query_type_result.output.reason

    logger.info(
        "intent classification",
        user_id=ctx.user_id,
        query_type=query_type,
        query_type_reason=query_type_result.output.reason,
    )

    # Handle non-valid intents will return a 400x error
    if query_type == QueryType.MALICIOUS or query_type == QueryType.OFF_TOPIC:
        summary = "I can only help with questions about your own banking data. Please ask about your accounts, balances, transactions, or spending."
        ctx.workflow_summary = summary
        ctx.sanitized_query = (
            ctx.user_query
        )  # Set to the original query since we're not processing it
        ctx.is_sql_valid = False  # No SQL was generated, so it's not valid
        ctx.is_valid_sql_reason = (
            "Query rejected during intent classification - no SQL generated."
        )

        yield f"data: {json.dumps({'step': 'complete', 'summary': summary})}\n\n"
        ctx.should_continue = False
        return

    if query_type == QueryType.AMBIGUOUS:
        summary = "I'm not sure what banking information you're looking for. Could you clarify — for example, are you asking about your balance, a specific transaction, or your spending in a category?"
        ctx.workflow_summary = summary
        ctx.sanitized_query = (
            ctx.user_query
        )  # Set to the original query since we're not processing it
        ctx.is_sql_valid = False  # No SQL was generated, so it's not valid
        ctx.is_valid_sql_reason = "Query was ambiguous - no SQL generated."

        yield f"data: {json.dumps({'step': 'complete', 'summary': summary})}\n\n"
        ctx.should_continue = False
        return

    # Store sanitized intent for next steps
    logger.info(
        "sanitised user query for sql generation",
        user_id=ctx.user_id,
        user_query=ctx.user_query,
        sanitized_query=query_type_result.output.sanitized_query,
    )

    ctx.sanitized_query = query_type_result.output.sanitized_query


async def step_generate_sql(ctx: WorkflowContext) -> AsyncIterator[str]:
    """Generate SQL from sanitized intent"""
    yield f"data: {json.dumps({'step': 'generating', 'message': 'Thinking...'})}\n\n"

    deps = Deps(semantic_layer=ctx.config.semantics, cust_id=ctx.user_id)
    generation_result = await sql_generator_agent.run(ctx.sanitized_query, deps=deps)

    # Clean the SQL: strip whitespace and trailing punctuation
    raw_sql = generation_result.output.sql
    ctx.generated_sql = raw_sql.strip().rstrip(".")

    logger.info("generated sql", generated_sql=ctx.generated_sql)

    yield f"data: {json.dumps({'step': 'generated_sql', 'sql': ctx.generated_sql})}\n\n"
