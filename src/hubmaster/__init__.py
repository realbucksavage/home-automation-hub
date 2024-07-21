import asyncio
import os
import os.path
import yaml


def load_config():
    home = os.getenv("HOME")
    default_config_file = str(os.path.join(home, "hubmaster.yaml"))

    config_location = os.getenv("HUBMASTER_CONFIG", default_config_file)
    print(f"loading config from {config_location}")

    with open(config_location, "r") as config_file:
        return yaml.load(config_file, yaml.SafeLoader)


def start_consumer():
    config = load_config()

    import firebase_admin

    firebase_config = config.get("firebase")
    if not firebase_config:
        print("firebase is required")
        exit(1)

    sdk_json_location = firebase_config.get("certificate")
    if not sdk_json_location:
        print("firebase.cerificate is required")
        exit(1)

    print(f"loading firebase sdk from {sdk_json_location}")

    creds = firebase_admin.credentials.Certificate(sdk_json_location)
    app = firebase_admin.initialize_app(creds)

    from . import consumer

    consumer.processor.registry.init_loaders(config.get("drivers"))

    for type in consumer.drivers.keys():
        factory_fn = consumer.drivers[type]
        consumer.processor.registry.register(type, factory_fn)

    db_url = firebase_config.get("db")
    if not db_url:
        print("firebase.db is required")
        exit(1)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    consumer.start(app, db_url)
    loop.run_forever()
