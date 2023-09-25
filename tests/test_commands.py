from pathlib import Path

from click import Group
from click.testing import CliRunner
from pystac import Collection, Item
from stactools.canelevation.commands import create_canelevation_command

from . import test_data

command = create_canelevation_command(Group())


def test_create_collection_cmd(tmp_path: Path) -> None:
    # Smoke test for the command line create-collection command
    #
    # Most checks should be done in test_stac.py::test_create_collection
    path = str(tmp_path)

    runner = CliRunner()
    result = runner.invoke(command, ["create-collection", "-d", path])
    assert result.exit_code == 0, "\n{}".format(result.output)
    collection = Collection.from_file(path + "\collection.json")
    collection.validate()


def test_create_item(tmp_path: Path) -> None:
    # Smoke test for the command line create-item command
    #
    # Most checks should be done in test_stac.py::test_create_item
    asset_href = test_data.get_path("data/autzen_trim.las")
    path = str(tmp_path)
    runner = CliRunner()
    result = runner.invoke(command, ["create-item", asset_href, path])
    assert result.exit_code == 0, "\n{}".format(result.output)
    item = Item.from_file(path + "\\autzen_trim.json")
    item.validate()
