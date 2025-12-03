from dependency_injector import containers, providers
from src.core.config import get_config


class ConfigContainer(containers.DeclarativeContainer):
    config = providers.Configuration(pydantic_settings=[get_config()])
    wiring_config = containers.WiringConfiguration(
        modules=[
            __name__,
        ],
    )

config_container = ConfigContainer()
# This is used for when config required before config init.
# e.g. main.py, migrations
config = config_container.config
