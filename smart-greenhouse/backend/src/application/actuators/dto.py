from pydantic import BaseModel


class ActuatorStateDto(BaseModel):
    state: str
    allowed_commands: list[str]


class ActuatorTransitionRequest(BaseModel):
    target: str