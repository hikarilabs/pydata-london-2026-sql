from dataclasses import dataclass
from enum import Enum
from typing import Optional, Any


@dataclass
class Deps:
    """Dependencies for the agent, holding the semantic layer data."""

    semantic_layer: Optional[dict[str, Any] | str] = None


class QueryType(str, Enum):
    """Classification types for user query intent"""

    VALID_BANKING_QUERY = "valid_banking_query"
    MALICIOUS = "malicious"
    OFF_TOPIC = "off_topic"
    AMBIGUOUS = "ambiguous"
