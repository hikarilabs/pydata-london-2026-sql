import json
from typing import AsyncIterator

from agents.analyst.agent import summary_agent
from agents.intent_validator.agent import intent_classifier_agent, intent_analyst_classifier_agent
from agents.shared import QueryType, Deps
from agents.sql_generator.agent import (
    sql_generator_user_agent,
    sql_generator_analyst_agent,
)
from agents.sql_validator.agent import sql_validator_agent
from app.dependencies.logger import logger
from workflows.context import WorkflowContext
from workflows.query.execute import execute_query
from workflows.query.serialiser import json_serializer


async def step_classify_user_query(ctx: WorkflowContext) -> AsyncIterator[str]:
    """Classify user intent for security and relevance"""
    yield f"data: {json.dumps({'step': 'classifying', 'message': 'Analyzing user request...'})}\n\n"

    logger.info("user query", user_id=ctx.user_id, query=ctx.user_query)

    deps = Deps(semantic_layer=ctx.config.semantics, cust_id=ctx.user_id)
    query_type_result = await intent_classifier_agent.run(ctx.user_query, deps=deps)

    # TODO: track token usage per workflow step
    tkns_usage = query_type_result.usage
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

async def step_classify_analyst_query(ctx: WorkflowContext) -> AsyncIterator[str]:
    """Classify analyst intent — allows portfolio-wide queries"""
    yield f"data: {json.dumps({'step': 'classifying', 'message': 'Analyzing analyst request...'})}\n\n"

    logger.info("analyst query", user_id=ctx.user_id, query=ctx.user_query)

    deps = Deps(semantic_layer=ctx.config.semantics, cust_id=ctx.user_id)
    query_type_result = await intent_analyst_classifier_agent.run(ctx.user_query, deps=deps)

    tkns_usage = query_type_result.usage
    tkns_usage_input = tkns_usage.input_tokens
    tkns_usage_output = tkns_usage.output_tokens

    query_type = query_type_result.output.query_type.value

    ctx.query_type = query_type
    ctx.query_type_reason = query_type_result.output.reason

    logger.info(
        "intent classification",
        user_id=ctx.user_id,
        query_type=query_type,
        query_type_reason=query_type_result.output.reason,
    )

    if query_type == QueryType.MALICIOUS or query_type == QueryType.OFF_TOPIC:
        summary = "I can only help with analytical questions about banking portfolio data. Please ask about accounts, balances, transactions, or customer segments."
        ctx.workflow_summary = summary
        ctx.sanitized_query = ctx.user_query
        ctx.is_sql_valid = False
        ctx.is_valid_sql_reason = "Query rejected during intent classification - no SQL generated."

        yield f"data: {json.dumps({'step': 'complete', 'summary': summary})}\n\n"
        ctx.should_continue = False
        return

    if query_type == QueryType.AMBIGUOUS:
        summary = "I'm not sure what you're looking for. Could you clarify — for example, are you asking about total balances, spend by segment, or transaction volumes?"
        ctx.workflow_summary = summary
        ctx.sanitized_query = ctx.user_query
        ctx.is_sql_valid = False
        ctx.is_valid_sql_reason = "Query was ambiguous - no SQL generated."

        yield f"data: {json.dumps({'step': 'complete', 'summary': summary})}\n\n"
        ctx.should_continue = False
        return

    logger.info(
        "sanitised analyst query for sql generation",
        user_id=ctx.user_id,
        user_query=ctx.user_query,
        sanitized_query=query_type_result.output.sanitized_query,
    )

    ctx.sanitized_query = query_type_result.output.sanitized_query

async def step_generate_user_sql(ctx: WorkflowContext) -> AsyncIterator[str]:
    """Generate SQL from sanitized intent"""
    yield f"data: {json.dumps({'step': 'generating', 'message': 'Thinking...'})}\n\n"

    deps = Deps(semantic_layer=ctx.config.semantics, cust_id=ctx.user_id)
    generation_result = await sql_generator_user_agent.run(
        ctx.sanitized_query, deps=deps
    )

    # Clean the SQL: strip whitespace and trailing punctuation
    raw_sql = generation_result.output.sql
    ctx.generated_sql = raw_sql.strip().rstrip(".")

    logger.info("generated sql", generated_sql=ctx.generated_sql)

    yield f"data: {json.dumps({'step': 'generated_sql', 'sql': ctx.generated_sql})}\n\n"


async def step_generate_analyst_sql(ctx: WorkflowContext) -> AsyncIterator[str]:
    """Generate SQL from sanitized intent"""
    yield f"data: {json.dumps({'step': 'generating', 'message': 'Thinking...'})}\n\n"

    deps = Deps(semantic_layer=ctx.config.semantics, cust_id=ctx.user_id)
    generation_result = await sql_generator_analyst_agent.run(
        ctx.sanitized_query, deps=deps
    )

    # Clean the SQL: strip whitespace and trailing punctuation
    raw_sql = generation_result.output.sql
    ctx.generated_sql = raw_sql.strip().rstrip(".")

    logger.info("generated sql", generated_sql=ctx.generated_sql)

    yield f"data: {json.dumps({'step': 'generated_sql', 'sql': ctx.generated_sql})}\n\n"


async def step_validate_sql(ctx: WorkflowContext) -> AsyncIterator[str]:
    """Validate SQL for safety and security"""
    yield f"data: {json.dumps({'step': 'validating', 'message': 'Validating user request...'})}\n\n"

    validation_result = await sql_validator_agent.run(ctx.generated_sql)

    # add the validation results to the workflow context
    ctx.is_sql_valid = validation_result.output.is_valid
    # Ensure reason is never None - provide fallback
    ctx.is_valid_sql_reason = (
        validation_result.output.reason
        or "Validation completed without detailed reasoning."
    )

    if not ctx.is_sql_valid:
        yield f"data: {json.dumps({'error': 'Unsafe query detected.', 'reason': validation_result.output.reason})}\n\n"
        ctx.should_continue = False
        return


async def step_execute_sql(ctx: WorkflowContext) -> AsyncIterator[str]:
    """Execute a validated SQL query"""
    yield f"data: {json.dumps({'step': 'executing', 'message': 'Executing user request...'})}\n\n"

    ctx.db_results = await execute_query(ctx.generated_sql, ctx.config.db_client)

    logger.info(
        "sql execution results",
        user_id=ctx.user_id,
        step="executed",
        results=json.loads(json.dumps(ctx.db_results, default=json_serializer)),
    )

    yield f"data: {json.dumps({'step': 'executed', 'results': ctx.db_results}, default=json_serializer)}\n\n"


async def step_summarize(ctx: WorkflowContext) -> AsyncIterator[str]:
    """Generate a summary of findings and determine a render type"""
    yield f"data: {json.dumps({'step': 'summarizing', 'message': 'Generating summary and chart configuration...'})}\n\n"

    # Build the summary prompt with explicit empty-state handling
    if not ctx.db_results:
        summary_prompt = (
            f"User Query: {ctx.sanitized_query}\n\nDatabase Results: [] (no data found)"
        )
    else:
        summary_prompt = f"User Query: {ctx.sanitized_query}\n\nDatabase Results: {json.dumps(ctx.db_results, default=json_serializer)}"

    result = await summary_agent.run(summary_prompt)

    ctx.workflow_summary = result.output.summary_text

    # Final payload to the frontend
    final_payload = {
        "step": "complete",
        "summary": ctx.workflow_summary,
    }

    yield f"data: {json.dumps(final_payload, default=json_serializer)}\n\n"
