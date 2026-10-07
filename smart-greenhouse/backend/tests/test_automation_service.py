from uuid import uuid4

import pytest

from src.application.automation.service import (
    AutomationService,
)
from src.domain.automation.context import (
    LocationAutomationContext,
)


class FakeAutomationRepository:
    def __init__(
        self,
        location_exists=True,
        strategy_key="conservative",
        contexts=None,
    ):
        self.exists = location_exists
        self.strategy_key = strategy_key
        self.contexts = (
            contexts
            if contexts is not None
            else []
        )

    def location_exists(
        self,
        location_id,
    ):
        return self.exists

    def get_strategy_key(
        self,
        location_id,
    ):
        return self.strategy_key

    def upsert_strategy(
        self,
        location_id,
        strategy_key,
    ):
        self.strategy_key = strategy_key
        return strategy_key

    def build_contexts(
        self,
        location_id,
    ):
        return self.contexts


def make_context(
    location_id,
    moisture=0.40,
):
    return (
        "Zone 1",
        LocationAutomationContext(
            location_id=location_id,
            zone_id=uuid4(),
            moisture=moisture,
            moisture_threshold_low=0.30,
            moisture_threshold_high=0.50,
        ),
    )


def test_save_strategy():
    location_id = uuid4()

    repository = (
        FakeAutomationRepository()
    )

    service = AutomationService(
        repository
    )

    result = service.save_strategy(
        location_id,
        "aggressive",
    )

    assert (
        result.strategy_key
        == "aggressive"
    )

    assert (
        repository.strategy_key
        == "aggressive"
    )


def test_unknown_strategy_rejected():
    service = AutomationService(
        FakeAutomationRepository()
    )

    with pytest.raises(
        ValueError,
        match="Unknown strategy key",
    ):
        service.save_strategy(
            uuid4(),
            "invalid",
        )


def test_missing_location():
    service = AutomationService(
        FakeAutomationRepository(
            location_exists=False
        )
    )

    with pytest.raises(
        LookupError,
        match="Location not found",
    ):
        service.evaluate(
            uuid4()
        )


def test_conservative_evaluation_waits():
    location_id = uuid4()

    repository = (
        FakeAutomationRepository(
            strategy_key="conservative",
            contexts=[
                make_context(
                    location_id,
                    0.40,
                )
            ],
        )
    )

    service = AutomationService(
        repository
    )

    result = service.evaluate(
        location_id
    )

    assert (
        result.strategy_key
        == "conservative"
    )

    assert result.action == "wait"

    assert (
        result.zones[0].action
        == "wait"
    )


def test_aggressive_evaluation_irrigates():
    location_id = uuid4()

    repository = (
        FakeAutomationRepository(
            strategy_key="aggressive",
            contexts=[
                make_context(
                    location_id,
                    0.40,
                )
            ],
        )
    )

    service = AutomationService(
        repository
    )

    result = service.evaluate(
        location_id
    )

    assert (
        result.strategy_key
        == "aggressive"
    )

    assert (
        result.action
        == "irrigate"
    )

    assert (
        result.zones[0].action
        == "irrigate"
    )


def test_zone_without_reading_waits():
    location_id = uuid4()

    repository = (
        FakeAutomationRepository(
            strategy_key="aggressive",
            contexts=[
                make_context(
                    location_id,
                    None,
                )
            ],
        )
    )

    service = AutomationService(
        repository
    )

    result = service.evaluate(
        location_id
    )

    assert result.action == "wait"

    assert (
        result.zones[0].action
        == "wait"
    )

    assert (
        "No moisture sensor"
        in result.zones[0].reason
    )