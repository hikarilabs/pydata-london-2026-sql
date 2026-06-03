from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from uuid import uuid4

from dependencies.state import DbClient, DdlSchema, SemanticLayer
from workflows.chat.workflow import chat_workflow_processor
from workflows.context import AgentConfig

router = APIRouter()


class ChatRequest(BaseModel):
    cust_id: int
    customer_query: str


class Workflow(BaseModel):
    step: str = "complete"
    customer_query: str
    summary: str


class WorkflowResponse(BaseModel):
    workflows: list[Workflow]


@router.post("/api/chat/ddl/stream")
async def ddl(
    body: ChatRequest,
    db_client: DbClient,
    ddl_schema: DdlSchema,
):
    """
    Accepts a user query and streams the workflow steps back to the client via SSE.
    Semantic layer is injected as a dependency and pre-fetched.
    """
    config = AgentConfig(
        db_client=db_client,
        ddl_schema=ddl_schema,
    )

    return StreamingResponse(
        chat_workflow_processor(
            customer_id=body.cust_id,
            customer_query=body.customer_query,
            workflow_id=uuid4(),
            workflow_type="chat",
            config=config,
        ),
        media_type="text/event-stream",
    )


@router.post("/api/chat/semantic/stream")
async def semantic(
    body: ChatRequest,
    db_client: DbClient,
    semantic_layer: SemanticLayer,
):
    """
    Accepts a user query and streams the workflow steps back to the client via SSE.
    Semantic layer is injected as a dependency and pre-fetched.
    """
    config = AgentConfig(
        db_client=db_client,
        semantic_layer=semantic_layer,
    )

    return StreamingResponse(
        chat_workflow_processor(
            customer_id=body.cust_id,
            customer_query=body.customer_query,
            workflow_id=uuid4(),
            workflow_type="chat",
            config=config,
        ),
        media_type="text/event-stream",
    )