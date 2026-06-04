from pydantic import BaseModel, Field
from pydantic_ai import Agent


class ValidationResponse(BaseModel):
    is_valid: bool = Field(
        description="True if the query is a safe SELECT statement, False if it contains dangerous commands."
    )
    reason: str = Field(
        description="Explanation of why the query is safe or unsafe. This field is REQUIRED and must never be empty."
    )


# Define the Validation Agent
sql_validator_agent = Agent(
    "openai:gpt-4o",
    output_type=ValidationResponse,
    system_prompt=(
        "You are a strict SQL security validator. "
        "Your job is to analyze the provided SQL query and determine if it is safe to execute on a read-only basis. "
        "A query is UNSAFE if it contains any data manipulation or schema modification commands "
        "such as DROP, TRUNCATE, DELETE, UPDATE, INSERT, ALTER, RENAME, or GRANT. "
        "Only standard SELECT queries are considered safe. "
        "If you detect any dangerous operations, mark is_valid as False and provide a clear reason. "
        "You MUST ALWAYS provide a detailed 'reason' field explaining your decision, whether the query is safe or unsafe. "
        "For safe queries, explain what makes them safe (e.g., 'This is a read-only SELECT query with no dangerous operations'). "
        "For unsafe queries, specify exactly which dangerous commands were detected."
    ),
)
