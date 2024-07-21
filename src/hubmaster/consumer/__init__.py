import asyncio
import re
import firebase_admin
from firebase_admin import db as firebase_db

from . import miraie
from . import processor


drivers = {
    "miraie-ac": miraie.new_ac_processor,
}


class Listener:
    _path_expr = re.compile(r"\/[\w-]+\/([\w-]+)/([\w-]+):([\w-]+)\/([\w-]+)")
    _clusters = dict[str, dict[str, dict]]

    def listen(self, event: firebase_db.Event):
        if event.path == "/":
            self._build_state(event)
            return

        print(f"Received a {event.event_type} event on {event.path}")

        cmd = self._parse_command(event)
        driver = processor.registry.construct(cmd.device.type)

        asyncio.get_event_loop().run_until_complete(driver.process(cmd.device, cmd.parameter, cmd.value))

    def _parse_command(self, event: firebase_db.Event):
        path = event.path
        match = self._path_expr.match(path)
        if not match:
            raise ValueError(f"invalid path: {path}")

        cluster_name = match.group(1)
        device_name = match.group(2)
        device_type = match.group(3)
        parameter = match.group(4)

        dev = processor.Device(cluster_name, device_name, device_type)
        cmd = processor.Command(dev, parameter, event.data)

        return cmd

    def _build_state(self, event: firebase_db.Event):
        self._clusters = event.data.get("clusters")
        print(self._clusters)


def start(app: firebase_admin.App, url: str):
    ref = firebase_db.reference("devices", app, url)

    lis = Listener()
    ref.listen(lis.listen)
