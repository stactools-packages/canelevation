import os
from tempfile import TemporaryDirectory
from typing import Callable, List

import pystac
from click import Command, Group
from stactools.testing import CliTestCase

from stactools.canelevation.commands import create_canelevation_command


class CommandsTest(CliTestCase):
    def create_subcommand_functions(self) -> List[Callable[[Group], Command]]:
        return [create_canelevation_command]

    def test_create_collection_cmd(self) -> None:
        with TemporaryDirectory() as directory:
            # Run command to create collection in the temporary directory
            self.run_command(["canelevation", "create-collection", "-d", directory])

            # Validate that one json file has been created in the directory
            json_files = [p for p in os.listdir(directory) if p.endswith(".json")]
            self.assertEqual(len(json_files), 1)

            # Validate the created collection
            collection_path = os.path.join(directory, json_files[0])
            collection = pystac.read_file(collection_path)
            collection.validate()

    def test_create_item_cmd(self) -> None:
        href = os.path.abspath("tests/data-files/autzen_trim.las")

        with TemporaryDirectory() as directory:
            # Run command to create item in the temporary directory
            self.run_command(["canelevation", "create-item", href, directory])

            # Validate that one json file has been created in the directory
            json_files = [p for p in os.listdir(directory) if p.endswith(".json")]
            self.assertEqual(len(json_files), 1)

            # Validate the created item
            item_path = os.path.join(directory, json_files[0])
            item = pystac.read_file(item_path)
            item.validate()
