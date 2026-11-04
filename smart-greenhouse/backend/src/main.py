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
from src.interfaces.api import (
    actuator_states,
    actuators,
    automation,
    devices,
    health,
    locations,
    overview,
    sensors,
)


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
                "Simulation sampler error: "
                f"{exc}"
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
    version="0.9.0",
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    health.router
)

app.include_router(
    sensors.router
)

app.include_router(
    devices.router
)

app.include_router(
    locations.router
)

app.include_router(
    automation.router
)

app.include_router(
    overview.router
)

app.include_router(
    actuator_states.router
)

app.include_router(
    actuators.router
)


@app.get("/")
def root():
    return {
        "message": "Smart Greenhouse API",
        "api_reference": "/scalar",
        "openapi": "/openapi.json",
        "endpoints": {
            "health": "/health",
            "sensors": "/api/sensors",
            "devices": "/api/devices",
            "locations": "/api/locations",
            "automation": (
                "/api/locations/"
                "{location_id}/automation"
            ),
            "overview": (
                "/api/locations/"
                "{location_id}/overview"
            ),
            "actuator_state": (
                "/api/devices/"
                "{device_id}/state"
            ),
            "actuator_transition": (
                "/api/devices/"
                "{device_id}/transition"
            ),
            "actuator_executions": (
                "/api/actuators/executions"
            ),
            "actuator_apply": (
                "/api/actuators/"
                "{device_id}/apply"
            ),
        },
    }


@app.get(
    "/scalar",
    include_in_schema=False,
)
def scalar_api_reference():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Smart Greenhouse API",
    )