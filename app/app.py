import logfire

from fastapi import FastAPI


logfire.configure()
logfire.instrument_pydantic_ai()
logfire.instrument_asyncpg()

app = FastAPI()
logfire.instrument_fastapi(app)
