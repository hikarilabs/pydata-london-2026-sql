from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from uuid import uuid4

from dependencies.state import DbClient, DdlSchema, SemanticLayer
from workflows.chat.workflow import (
    user_chat_workflow_processor,
    analyst_chat_workflow_processor,
)
from workflows.context import AgentConfig

router = APIRouter(
    prefix="/api/chat",
    tags=["SemanticRoutes"],
)


class ChatRequest(BaseModel):
    cust_id: int
    customer_query: str


class Workflow(BaseModel):
    step: str = "complete"
    customer_query: str
    summary: str


class WorkflowResponse(BaseModel):
    workflows: list[Workflow]


@router.post("/ddl/stream")
async def ddl(
    body: ChatRequest,
    db_client: DbClient,
    semantics: DdlSchema,
):
    """
    Accepts a user query and streams the workflow steps back to the client via SSE.
    DDL schema is injected as a dependency and pre-fetched.
    """
    config = AgentConfig(
        db_client=db_client,
        semantics=semantics,
    )

    return StreamingResponse(
        user_chat_workflow_processor(
            customer_id=body.cust_id,
            customer_query=body.customer_query,
            workflow_id=uuid4(),
            workflow_type="chat",
            config=config,
        ),
        media_type="text/event-stream",
    )


@router.post("/semantic/user/stream")
async def semantic(
    body: ChatRequest,
    db_client: DbClient,
    semantics: SemanticLayer,
):
    """
    Accepts a user query and streams the workflow steps back to the client via SSE.
    Semantic layer is injected as a dependency and pre-fetched.
    """
    config = AgentConfig(
        db_client=db_client,
        semantics=semantics,
    )

    return StreamingResponse(
        user_chat_workflow_processor(
            customer_id=body.cust_id,
            customer_query=body.customer_query,
            workflow_id=uuid4(),
            workflow_type="chat",
            config=config,
        ),
        media_type="text/event-stream",
    )


@router.post("/semantic/analyst/stream")
async def semantic(
    body: ChatRequest,
    db_client: DbClient,
    semantics: SemanticLayer,
):
    """
    Accepts a user query and streams the workflow steps back to the client via SSE.
    Semantic layer is injected as a dependency and pre-fetched.
    """
    config = AgentConfig(
        db_client=db_client,
        semantics=semantics,
    )

    return StreamingResponse(
        analyst_chat_workflow_processor(
            customer_id=body.cust_id,
            customer_query=body.customer_query,
            workflow_id=uuid4(),
            workflow_type="chat",
            config=config,
        ),
        media_type="text/event-stream",
    )
