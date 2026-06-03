import uvicorn
from app.dependencies.logger import logger

if __name__ == "__main__":
    logger.info("starting", service="semantic-service")

    print(f"""
    {"=" * 80}
    |            S E M A N T I C   S E R V I C E          |
    {"=" * 80}

    Gateway: http://0.0.0.0:8000
    Semantic Layer for MARKDOWN LLM API interaction:  http://0.0.0.0:8000/semantic/markdown
    View: http://0.0.0.0:8000/semantic/view

    [Press Ctrl+C to shutdown server]
    """)
    uvicorn.run("app.app:app", host="0.0.0.0", port=8000, reload=True)
