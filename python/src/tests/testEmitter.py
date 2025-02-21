import unittest

import asyncio
import typing

from wslink.emitter import EventEmitter


class TestEventEmitter(unittest.IsolatedAsyncioTestCase):
    async def test_add_listener(self):
        payloads = {}

        def on_foo(val):
            payloads["foo"] = val

        async def on_bar(val):
            await asyncio.sleep(0.05)
            payloads["bar"] = val

        emitter = EventEmitter()

        emitter.add_event_listener("foo", on_foo)
        emitter.add_event_listener("bar", on_bar)

        emitter.emit("foo", 0)
        emitter.emit("bar", 1)

        await asyncio.sleep(0.1)

        self.assertEqual(payloads.get("foo"), 0)
        self.assertEqual(payloads.get("bar"), 1)

    async def test_remove_listeners(self):
        payloads = {}

        def on_foo(val):
            payloads["foo"] = val

        async def on_bar(val):
            await asyncio.sleep(0.05)
            payloads["bar"] = val

        emitter = EventEmitter()

        emitter.add_event_listener("foo", on_foo)
        emitter.add_event_listener("bar", on_bar)

        emitter.remove_event_listener("bar", on_bar)

        emitter.emit("foo", 0)
        emitter.emit("bar", 1)

        await asyncio.sleep(0.1)

        self.assertEqual(payloads.get("foo"), 0)
        self.assertEqual(payloads.get("bar"), None)

    async def test_clear_listeners(self):
        payloads = {}

        def on_foo(val):
            payloads["foo"] = val

        async def on_bar(val):
            await asyncio.sleep(0.05)
            payloads["bar"] = val

        emitter = EventEmitter()

        emitter.add_event_listener("foo", on_foo)
        emitter.add_event_listener("bar", on_bar)

        emitter.clear()

        emitter.emit("foo", 0)
        emitter.emit("bar", 1)

        await asyncio.sleep(0.1)

        self.assertEqual(payloads.get("foo"), None)
        self.assertEqual(payloads.get("bar"), None)

    def test_event_type_generic(self):
        EventTypes = typing.Literal["foo", "bar"]
        emitter = EventEmitter[EventTypes]()

        emitter.emit("foo")
        emitter.emit("bar")
        self.assertRaises(ValueError, emitter.emit, "baz")

        self.assertSetEqual(emitter.allowed_events, {"foo", "bar"})

    def test_event_type_runtime(self):
        emitter = EventEmitter(allowed_events=("foo", "bar"))

        emitter.emit("foo")
        emitter.emit("bar")
        self.assertRaises(ValueError, emitter.emit, "baz")

        self.assertSetEqual(emitter.allowed_events, {"foo", "bar"})


if __name__ == "__main__":
    unittest.main()
