import stactools.core
from stactools.cli.registry import Registry

from stactools.canelevation.stac import create_collection, create_item

__all__ = ["create_collection", "create_item"]

stactools.core.use_fsspec()


def register_plugin(registry: Registry) -> None:
    from stactools.canelevation import commands

    registry.register_subcommand(commands.create_canelevation_command)


__version__ = "0.1.0"
