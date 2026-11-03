class IllegalTransitionError(ValueError):
    pass


VALID_STATES = {
    "off",
    "idle",
    "running",
    "error",
    "maintenance",
}


TRANSITIONS: dict[str, dict[str, str]] = {
    "off": {
        "power_on": "idle",
        "enter_maintenance": "maintenance",
        "fault": "error",
    },
    "idle": {
        "start_pump": "running",
        "power_off": "off",
        "enter_maintenance": "maintenance",
        "fault": "error",
    },
    "running": {
        "stop_pump": "idle",
        "fault": "error",
    },
    "error": {
        "reset": "idle",
    },
    "maintenance": {
        "exit_maintenance": "idle",
        "fault": "error",
    },
}


def get_allowed_commands(state: str) -> list[str]:
    if state not in VALID_STATES:
        raise ValueError(
            f"Unknown actuator state: {state}"
        )

    return list(
        TRANSITIONS[state].keys()
    )


def transition_state(
    current_state: str,
    target_state: str,
) -> str:
    if current_state not in VALID_STATES:
        raise ValueError(
            f"Unknown actuator state: {current_state}"
        )

    if target_state not in VALID_STATES:
        raise IllegalTransitionError(
            f"Unknown target state: {target_state}"
        )

    allowed_targets = TRANSITIONS[
        current_state
    ].values()

    if target_state not in allowed_targets:
        raise IllegalTransitionError(
            f"Transition from {current_state} "
            f"to {target_state} is not allowed"
        )

    return target_state