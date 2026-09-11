from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference

from src.infrastructure.settings import settings
from src.interfaces.api.health import router as health_router
from src.interfaces.api.sensors import router as sensors_router


app = FastAPI(
    title="Smart Greenhouse API",
    description="Backend API for the Smart Greenhouse project",
    docs_url=None,
    redoc_url=None,
)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in settings.cors_origins.split(",")
        if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API routes
app.include_router(health_router)
app.include_router(sensors_router)


@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    return {
        "message": "Smart Greenhouse API",
        "health": "/health",
        "sensors": "/api/sensors",
        "scalar": "/scalar",
        "openapi": "/openapi.json",
    }


@app.get("/scalar", include_in_schema=False)
async def scalar():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )