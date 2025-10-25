from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from app.core.config import settings
import warnings
warnings.filterwarnings("ignore")

from app.core.app_logger import setup_daily_logger
logger = setup_daily_logger(logger_name=__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.core.config import settings
    from app.services.chatbot_services import build_chat_graph

    logger.info("Starting up the application...")
    pool = AsyncConnectionPool(conninfo=settings.database_url, kwargs={"autocommit": True}, max_size=20)
    await pool.open()
    
    checkpointer = AsyncPostgresSaver(pool)
    await checkpointer.setup()
    
    graph = build_chat_graph()
    app.state.graph = graph.compile(checkpointer=checkpointer)
    
    try:
        yield
    finally:
        logger.info("Shutting down the application...")
        await pool.close()

app = FastAPI(lifespan=lifespan)

from app.api.auth import auth_app
from app.api.chatbot import chatbot_app

app.include_router(auth_app)
app.include_router(chatbot_app)


# CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}