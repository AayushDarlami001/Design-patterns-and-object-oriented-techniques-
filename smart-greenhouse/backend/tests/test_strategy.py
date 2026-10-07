from uuid import uuid4

import pytest

from src.domain.automation.context import (
    LocationAutomationContext,
)
from src.domain.automation.strategy import (
    AggressiveMoistureStrategy,
    ConservativeMoistureStrategy,
    get_automation_strategy,
)


def make_context(
    moisture: float | None = 0.40,
):
    return LocationAutomationContext(
        location_id=uuid4(),
        zone_id=uuid4(),
        moisture=moisture,
        moisture_threshold_low=0.30,
        moisture_threshold_high=0.50,
    )


def test_conservative_waits_between_thresholds():
    strategy = (
        ConservativeMoistureStrategy()
    )

    result = strategy.decide(
        make_context(0.40)
    )

    assert result.action == "wait"


def test_aggressive_irrigates_between_thresholds():
    strategy = (
        AggressiveMoistureStrategy()
    )

    result = strategy.decide(
        make_context(0.40)
    )

    assert result.action == "irrigate"


def test_strategies_produce_different_results():
    context = make_context(0.40)

    conservative = (
        ConservativeMoistureStrategy()
    ).decide(context)

    aggressive = (
        AggressiveMoistureStrategy()
    ).decide(context)

    assert (
        conservative.action
        != aggressive.action
    )


def test_conservative_irrigates_below_low():
    result = (
        ConservativeMoistureStrategy()
    ).decide(
        make_context(0.20)
    )

    assert result.action == "irrigate"


def test_aggressive_waits_above_high():
    result = (
        AggressiveMoistureStrategy()
    ).decide(
        make_context(0.60)
    )

    assert result.action == "wait"


def test_missing_moisture_returns_wait():
    result = (
        ConservativeMoistureStrategy()
    ).decide(
        make_context(None)
    )

    assert result.action == "wait"

    assert (
        "No moisture sensor"
        in result.reason
    )


def test_known_strategy_keys():
    conservative = (
        get_automation_strategy(
            "conservative"
        )
    )

    aggressive = (
        get_automation_strategy(
            "aggressive"
        )
    )

    assert (
        conservative.key
        == "conservative"
    )

    assert (
        aggressive.key
        == "aggressive"
    )


def test_unknown_strategy_is_rejected():
    with pytest.raises(
        ValueError,
        match="Unknown strategy key",
    ):
        get_automation_strategy(
            "unknown"
        )