import json

from fastapi import APIRouter, HTTPException
from starlette.responses import Response, HTMLResponse, JSONResponse

from dependencies.state import app_state
from dependencies.convertors import json_to_markdown

router = APIRouter(
    prefix="/view",
    tags=["SemanticRoutes"],
)


@router.get("/ddl", response_class=Response)
async def semantic_markdown():
    """
    Returns the semantic layer as Markdown, optimized for LLM consumption.
    This format is more readable and provides better context for natural language queries.
    """
    try:
        # Parse the JSON semantic layer
        ddl = app_state.ddl_schema

        return Response(
            content=ddl,
            media_type="text/markdown; charset=utf-8",
            headers={
                "Content-Type": "text/markdown; charset=utf-8",
                "X-Content-Type-Options": "nosniff",
                "Cache-Control": "public, max-age=300",  # Cache for 5 minutes
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/semantic/markdown", response_class=Response)
async def semantic_markdown():
    """
    Returns the semantic layer as Markdown, optimized for LLM consumption.
    This format is more readable and provides better context for natural language queries.
    """
    try:
        # Parse the JSON semantic layer
        semantic_data = json.loads(app_state.semantic_layer)

        # Convert to Markdown
        markdown_output = json_to_markdown(semantic_data)

        return Response(
            content=markdown_output,
            media_type="text/markdown; charset=utf-8",
            headers={
                "Content-Type": "text/markdown; charset=utf-8",
                "X-Content-Type-Options": "nosniff",
                "Cache-Control": "public, max-age=300",  # Cache for 5 minutes
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/semantic")
async def semantic_view():
    """API root endpoint."""
    try:
        results = app_state.semantic_layer

        html_content = f"""
                       <html>
                           <head>
                               <title>MSemantic Model</title>
                               <style>
                                   body {{ 
                                       background-color: #ffffff; 
                                       color: #1a1a1a; 
                                       padding: 40px; 
                                       font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                                       line-height: 1.6;
                                   }}
                                   h2 {{ border-bottom: 2px solid #eeeeee; padding-bottom: 10px; color: #333333; }}
                                   pre {{ 
                                       background: #f8f9fa; 
                                       color: #212529;
                                       padding: 20px; 
                                       border: 1px solid #e9ecef;
                                       border-radius: 8px; 
                                       overflow: auto;
                                       font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
                                       font-size: 14px;
                                       box-shadow: inset 0 1px 2px rgba(0,0,0,0.05);
                                   }}
                               </style>
                           </head>
                           <body>
                               <h2>Semantic Mapping</h2>
                               <p style="color: #666;">Machine-readable schema generated from SQLAlchemy models.</p>
                               <pre><code>{results}</code></pre>
                           </body>
                       </html>
                       """
        return HTMLResponse(content=html_content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
