from uuid import UUID

from src.application.automation.dto import (
    AutomationEvaluationDto,
    StrategyDto,
    ZoneRecommendationDto,
)
from src.domain.automation.strategy import (
    get_automation_strategy,
)
from src.infrastructure.persistence.automation_repository import (
    AutomationRepository,
)


class AutomationService:
    def __init__(
        self,
        repository: AutomationRepository,
    ):
        self.repository = repository

    def save_strategy(
        self,
        location_id: UUID,
        strategy_key: str,
    ) -> StrategyDto:
        if not self.repository.location_exists(
            location_id
        ):
            raise LookupError(
                "Location not found"
            )

        normalized_key = (
            strategy_key.strip().lower()
        )

        get_automation_strategy(
            normalized_key
        )

        saved_key = (
            self.repository.upsert_strategy(
                location_id=location_id,
                strategy_key=normalized_key,
            )
        )

        return StrategyDto(
            location_id=location_id,
            strategy_key=saved_key,
        )

    def get_strategy(
        self,
        location_id: UUID,
    ) -> StrategyDto:
        if not self.repository.location_exists(
            location_id
        ):
            raise LookupError(
                "Location not found"
            )

        strategy_key = (
            self.repository.get_strategy_key(
                location_id
            )
        )

        if strategy_key is None:
            strategy_key = (
                self.repository.upsert_strategy(
                    location_id=location_id,
                    strategy_key=(
                        "conservative"
                    ),
                )
            )

        return StrategyDto(
            location_id=location_id,
            strategy_key=strategy_key,
        )

    def evaluate(
        self,
        location_id: UUID,
    ) -> AutomationEvaluationDto:
        if not self.repository.location_exists(
            location_id
        ):
            raise LookupError(
                "Location not found"
            )

        strategy_key = (
            self.repository.get_strategy_key(
                location_id
            )
        )

        if strategy_key is None:
            strategy_key = (
                self.repository.upsert_strategy(
                    location_id=location_id,
                    strategy_key=(
                        "conservative"
                    ),
                )
            )

        strategy = get_automation_strategy(
            strategy_key
        )

        contexts = (
            self.repository.build_contexts(
                location_id
            )
        )

        if len(contexts) == 0:
            return AutomationEvaluationDto(
                location_id=location_id,
                strategy_key=strategy_key,
                action="wait",
                reason=(
                    "Location has no zones "
                    "to evaluate."
                ),
                zones=[],
            )

        zone_results = []

        for zone_name, context in contexts:
            recommendation = (
                strategy.decide(
                    context
                )
            )

            zone_results.append(
                ZoneRecommendationDto(
                    zone_id=context.zone_id,
                    zone_name=zone_name,
                    action=(
                        recommendation.action
                    ),
                    reason=(
                        recommendation.reason
                    ),
                    score=(
                        recommendation.score
                    ),
                )
            )

        irrigation_zones = [
            result
            for result in zone_results
            if result.action
            == "irrigate"
        ]

        if irrigation_zones:
            action = "irrigate"

            names = ", ".join(
                result.zone_name
                for result
                in irrigation_zones
            )

            reason = (
                "Irrigation recommended "
                f"for: {names}."
            )

        else:
            action = "wait"

            reason = (
                "No zone currently "
                "requires irrigation."
            )

        return AutomationEvaluationDto(
            location_id=location_id,
            strategy_key=strategy_key,
            action=action,
            reason=reason,
            zones=zone_results,
        )