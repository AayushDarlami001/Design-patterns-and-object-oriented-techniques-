import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference

from src.application.readings.sampler import SimulationSampler
from src.application.readings.service import ReadingIngest
from src.infrastructure.db import SessionLocal
from src.infrastructure.persistence.device_repository import DeviceRepository
from src.infrastructure.persistence.reading_repository import ReadingRepository
from src.infrastructure.settings import settings
from src.interfaces.api.devices import router as devices_router
from src.interfaces.api.health import router as health_router
from src.interfaces.api.locations import router as locations_router
from src.interfaces.api.sensors import router as sensors_router


async def simulation_sampler_loop():
    while True:
        db = SessionLocal()

        try:
            device_repository = DeviceRepository(db)
            reading_repository = ReadingRepository(db)

            ingest = ReadingIngest(
                device_repository=device_repository,
                reading_repository=reading_repository,
            )

            sampler = SimulationSampler(
                device_repository=device_repository,
                reading_repository=reading_repository,
                ingest=ingest,
            )

            sampler.run_once(
                datetime.now(timezone.utc)
            )

        except asyncio.CancelledError:
            raise

        except Exception as exc:
            print(
                f"Simulation sampler error: {exc}"
            )

        finally:
            db.close()

        await asyncio.sleep(1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    sampler_task = asyncio.create_task(
        simulation_sampler_loop()
    )

    try:
        yield

    finally:
        sampler_task.cancel()

        try:
            await sampler_task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title="Smart Greenhouse API",
    description="Backend API for the Smart Greenhouse project",
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan,
)


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


app.include_router(health_router)
app.include_router(sensors_router)
app.include_router(devices_router)
app.include_router(locations_router)


@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    return {
        "message": "Smart Greenhouse API",
        "health": "/health",
        "sensors": "/api/sensors",
        "devices": "/api/devices",
        "locations": "/api/locations",
        "scalar": "/scalar",
        "openapi": "/openapi.json",
    }


@app.get("/scalar", include_in_schema=False)
async def scalar():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )