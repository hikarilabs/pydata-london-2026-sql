from pydantic import BaseModel, Field
from pydantic_ai import Agent, ModelSettings


class SummaryResponse(BaseModel):
    summary_text: str = Field(
        description=(
            "Two concise sentences at maximum answering the user's question directly using the exact values from the data. "
            "Rules:\n"
            "- Derive metric names from the database column name: replace underscores with spaces and apply title case only.\n"
            "  Never expand, paraphrase, or add words beyond what the column name contains.\n"
            "- Use 'all-time' when no time filter was applied, not 'so far', 'to date', or similar\n"
        )
    )


# Define the Summarizer Agent
summary_agent = Agent(
    "openai:gpt-4o",
    output_type=SummaryResponse,
    model_settings=ModelSettings(temperature=0.25),
    system_prompt=(
        "You are a helpful data analyst. Your job is to look at the user's original intent "
        "and the JSON data returned from the database, and determine the best way to present it.\n\n"
        "CRITICAL RULES FOR RENDER_TYPE (IN ORDER OF PRIORITY):\n\n"
        "IMPORTANT: If the database returned rows with data, you MUST present that data.\n"
        "When mentioning dates in the summary, format them as 'February 4, 2026', not '2026-02-04'.\n\n"
        "RULES FOR SUMMARY_TEXT:\n"
        "1. Answer in three sentences at maximum.\n"
        "2. Use the metric name derived directly from the database column name — apply minimal formatting only:\n"
        "   - Replace underscores with spaces\n"
        "   - Apply title case\n"
        "   - Do NOT expand, paraphrase, or add words beyond what the column name contains\n"
        "3. When no time filter was applied, use 'all-time' — never 'so far', 'to date', 'until now'.\n"
        "4. If a value is 0 or null, still report it directly\n"
        "5. Never treat 0 or null as missing data"
    ),
)
