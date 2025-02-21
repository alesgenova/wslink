from typing import (
    TypeVar,
    Generic,
    Literal,
    LiteralString,
    Optional,
    Iterable,
    get_args,
)

import asyncio
import functools


T = TypeVar("T", bound=LiteralString)


class EventEmitter(Generic[T]):
    def __init__(self, allowed_events: Optional[Iterable[str]] = None):
        self._listeners = {}
        if allowed_events is not None:
            self._allowed_events = set(allowed_events)
        else:
            self._allowed_events = None

    def clear(self):
        self._listeners = {}

    @property
    def allowed_events(self) -> set[str]:
        if self._allowed_events is None:
            self._allowed_events = self._infer_allowed_events()

        return self._allowed_events

    def _infer_allowed_events(self) -> set[str]:
        # Can't invoke this function from __init__() as __orig_class__ will not be available yet then

        # I don't know how much I trust the python API used here,
        # so wrap around a try/except block just in case.
        # This way we can default to no runtime checking if anything changes in the future and
        # don't break the entire ecosystem that depends on wslink
        try:
            if not hasattr(self, "__orig_class__"):
                return set()

            type_params = get_args(getattr(self, "__orig_class__"))
            if len(type_params) == 0:
                return set()

            events_param = type_params[0]

            if events_param.__origin__ is not Literal:
                return set()

            return set(get_args(events_param))

        except Exception:
            return set()

    def _validate_event(self, event: str):
        allowed_events = self.allowed_events

        if len(allowed_events) == 0:
            return

        if event not in allowed_events:
            raise ValueError(
                f"'{event}' is not a known event of this EventEmitter: {allowed_events}"
            )

    def __call__(self, event: T, *args, **kwargs):
        self.emit(event, *args, **kwargs)

    def __getattr__(self, name: T):
        if len(name) == 0 or name[0] == "_":
            return super().__getattribute__(name)

        return functools.partial(self.emit, name)

    def emit(self, event: T, *args, **kwargs):
        self._validate_event(event)

        listeners = self._listeners.get(event)
        if listeners is None:
            return

        loop = asyncio.get_running_loop()
        coroutine_run = (
            loop.create_task if (loop and loop.is_running()) else asyncio.run
        )

        for listener in listeners:
            if asyncio.iscoroutinefunction(listener):
                coroutine_run(listener(*args, **kwargs))
            else:
                listener(*args, **kwargs)

    def add_event_listener(self, event: T, listener):
        self._validate_event(event)

        listeners = self._listeners.get(event)
        if listeners is None:
            listeners = set()
            self._listeners[event] = listeners

        listeners.add(listener)

    def remove_event_listener(self, event: T, listener):
        self._validate_event(event)

        listeners = self._listeners.get(event)
        if listeners is None:
            return

        if listener in listeners:
            listeners.remove(listener)

    def has(self, event: T):
        return self.listeners_count(event) > 0

    def listeners_count(self, event: T):
        self._validate_event(event)

        listeners = self._listeners.get(event)
        if listeners is None:
            return 0

        return len(listeners)
