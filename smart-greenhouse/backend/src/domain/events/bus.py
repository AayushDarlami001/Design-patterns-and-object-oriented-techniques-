from collections import defaultdict
from collections.abc import Callable
from typing import Any


EventHandler = Callable[[Any], None]


class EventBus:
    def __init__(self):
        self._handlers: dict[
            type,
            list[EventHandler],
        ] = defaultdict(list)

    def subscribe(
        self,
        event_type: type,
        handler: EventHandler,
    ) -> None:
        self._handlers[event_type].append(
            handler
        )

    def publish(
        self,
        event: object,
    ) -> None:
        handlers = self._handlers.get(
            type(event),
            [],
        )

        for handler in handlers:
            handler(event)