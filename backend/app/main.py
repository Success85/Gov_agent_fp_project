import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.api import application, chat, payment, services, upload, users
from app.core.config import get_settings
from app.db.database import init_db
from app.db.database import SessionLocal
from app.schemas import HealthResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


settings = get_settings()

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("Starting Gov Agent API server")


app.include_router(chat.router)
app.include_router(users.router)
app.include_router(services.router)
app.include_router(application.router)
app.include_router(upload.router)
app.include_router(payment.router)


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    from sqlalchemy import text

    db_status = "ok"
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
    except Exception:
        db_status = "error"
    return HealthResponse(status="ok", database=db_status)


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
