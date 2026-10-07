from abc import ABC, abstractmethod

from src.domain.automation.context import (
    LocationAutomationContext,
    Recommendation,
)


class AutomationStrategy(ABC):
    key: str

    @abstractmethod
    def decide(
        self,
        context: LocationAutomationContext,
    ) -> Recommendation:
        raise NotImplementedError


class ConservativeMoistureStrategy(
    AutomationStrategy
):
    key = "conservative"

    def decide(
        self,
        context: LocationAutomationContext,
    ) -> Recommendation:
        if context.moisture is None:
            return Recommendation(
                action="wait",
                reason=(
                    "No moisture sensor reading "
                    "is available in this zone."
                ),
            )

        if (
            context.moisture
            < context.moisture_threshold_low
        ):
            return Recommendation(
                action="irrigate",
                reason=(
                    f"Moisture {context.moisture:.4f} "
                    f"is below the low threshold "
                    f"{context.moisture_threshold_low:.4f}."
                ),
                score=1.0,
            )

        return Recommendation(
            action="wait",
            reason=(
                f"Moisture {context.moisture:.4f} "
                "is not below the low threshold."
            ),
            score=0.0,
        )


class AggressiveMoistureStrategy(
    AutomationStrategy
):
    key = "aggressive"

    def decide(
        self,
        context: LocationAutomationContext,
    ) -> Recommendation:
        if context.moisture is None:
            return Recommendation(
                action="wait",
                reason=(
                    "No moisture sensor reading "
                    "is available in this zone."
                ),
            )

        if (
            context.moisture
            < context.moisture_threshold_high
        ):
            return Recommendation(
                action="irrigate",
                reason=(
                    f"Moisture {context.moisture:.4f} "
                    f"is below the high threshold "
                    f"{context.moisture_threshold_high:.4f}."
                ),
                score=1.0,
            )

        return Recommendation(
            action="wait",
            reason=(
                f"Moisture {context.moisture:.4f} "
                "is not below the high threshold."
            ),
            score=0.0,
        )


STRATEGIES: dict[str, AutomationStrategy] = {
    "conservative":
        ConservativeMoistureStrategy(),
    "aggressive":
        AggressiveMoistureStrategy(),
}


def get_automation_strategy(
    strategy_key: str,
) -> AutomationStrategy:
    strategy = STRATEGIES.get(strategy_key)

    if strategy is None:
        raise ValueError(
            f"Unknown strategy key: {strategy_key}"
        )

    return strategy


def get_strategy_keys() -> tuple[str, ...]:
    return tuple(STRATEGIES.keys())