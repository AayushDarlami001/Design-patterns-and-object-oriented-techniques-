from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from src.application.commands.dto import (
    CommandLogDto,
    CommandRequest,
)
from src.application.commands.service import (
    CommandService,
    DeviceNotFoundError,
)
from src.domain.commands.invoker import (
    UnknownCommandError,
)
from src.infrastructure.db import get_db


router = APIRouter(
    prefix="/api/commands",
    tags=["commands"],
)


@router.post(
    "",
    response_model=CommandLogDto,
    status_code=status.HTTP_200_OK,
)
def execute_command(
    request: CommandRequest,
    db: Session = Depends(get_db),
):
    service = CommandService(db)

    try:
        result = service.execute(request)

    except DeviceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except UnknownCommandError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    if result.status == "rejected":
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=jsonable_encoder(
                result.model_dump()
            ),
        )

    return result


@router.get(
    "",
    response_model=list[CommandLogDto],
)
def list_commands(
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
    ),
    db: Session = Depends(get_db),
) -> list[CommandLogDto]:
    service = CommandService(db)

    return service.list_recent(
        limit=limit
    )