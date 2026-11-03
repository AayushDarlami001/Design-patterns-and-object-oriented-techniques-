import pytest

from src.domain.actuators.state import (
    IllegalTransitionError,
    get_allowed_commands,
    transition_state,
)


def test_idle_can_transition_to_running():
    result = transition_state(
        current_state="idle",
        target_state="running",
    )

    assert result == "running"


def test_running_can_transition_to_idle():
    result = transition_state(
        current_state="running",
        target_state="idle",
    )

    assert result == "idle"


def test_illegal_transition_is_rejected():
    with pytest.raises(
        IllegalTransitionError
    ):
        transition_state(
            current_state="running",
            target_state="maintenance",
        )


def test_idle_allowed_commands():
    commands = get_allowed_commands(
        "idle"
    )

    assert "start_pump" in commands
    assert "power_off" in commands
    assert "enter_maintenance" in commands
    assert "fault" in commands


def test_running_allowed_commands():
    commands = get_allowed_commands(
        "running"
    )

    assert commands == [
        "stop_pump",
        "fault",
    ]


def test_error_can_reset_to_idle():
    result = transition_state(
        current_state="error",
        target_state="idle",
    )

    assert result == "idle"