import dataclasses
from typing import Dict


@dataclasses.dataclass
class Device:
    cluster: str
    name: str
    type: str


@dataclasses.dataclass
class Command:
    device: Device
    parameter: str
    value: any


class Processor:
    async def process(self, param: str, value: any):
        raise NotImplementedError


class ProcessorRegistry:
    _type_config = None
    _loaders: Dict[str, Processor] = {}

    def init_loaders(self, config: dict):
        self._type_config = config

    def register(self, type: str, factory_fn):
        type = type.lower()

        driver_config = self._type_config.get(type)
        if not driver_config:
            raise ValueError(f"{type} is an unrecognized driver type")

        if self._loaders.get(type):
            raise ValueError(f"{type} has already been registered")

        self._loaders[type] = factory_fn

    def construct(self, type: str) -> Processor:
        type = type.lower()

        driver_config = self._type_config.get(type)
        if not driver_config:
            raise ValueError(f"{type} is an unrecognized driver type")

        factory_fn = self._loaders.get(type)
        if not factory_fn:
            raise ValueError(f"{type} has not been registered")

        return factory_fn(driver_config)


registry = ProcessorRegistry()
