import asyncio
import threading

from miraie_ac import MirAIeHub, MirAIeBroker, PowerMode

from hubmaster.consumer.processor import Command
from .processor import Device, Processor


class ACProcessor(Processor):

    def __init__(self, config):
        self._username = config.get("username")
        self._password = config.get("password")

    async def process(self, dev: Device, param: str, value: any):
        broker = MirAIeBroker()
        hub = MirAIeHub()

        await hub.init(self._username, self._password, broker)

        match param:
            case "power":
                await self._set_power(broker, dev.name, value)
            case _:
                print(f"unknown parameter: {param}")

    async def _set_power(self, broker: MirAIeBroker, name, value):
        await broker.set_power(name, PowerMode.ON if value == "on" else PowerMode.OFF)


def new_ac_processor(config: dict) -> Processor:
    return ACProcessor(config)
