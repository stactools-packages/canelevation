import json
import logging
import os

import click
import pystac
from click import Command, Group
from stactools.canelevation.constants import METADATA_URL
from stactools.canelevation.stac import create_collection, create_item

logger = logging.getLogger(__name__)


def create_canelevation_command(cli: Group) -> Command:
    """Creates a command group for commands working with
    canelevations.
    """

    @cli.group(
        "canelevation",
        short_help=("Commands for working with " "CanElevation point clouds."),
    )
    def canelevation() -> None:
        pass

    @canelevation.command(
        "create-collection",
        short_help="Creates a STAC collection from NRCan CanElevation",
    )
    @click.option(
        "-d",
        "--destination",
        required=True,
        help="The output directory for the STAC Collection json",
    )
    @click.option(
        "-m", "--metadata", help="URL to the NRCan metadata json", default=METADATA_URL
    )
    def create_collection_command(destination: str, metadata: str) -> None:
        """Creates a STAC Collection from NRCan Land Use CanElevation metadata

        Args:
            destination (str): Directory to create the collection json
            metadata (str, optional): Path to json metadata file - provided by NRCan

        Returns:
            Callable
        """
        # Collect the metadata as a dict and create the collection
        collection = create_collection(metadata)

        # Set the destination
        output_path = os.path.join(destination, "collection.json")
        collection.set_self_href(output_path)
        collection.normalize_hrefs(destination)

        # Save and validate
        collection.save()
        collection.validate()

    @canelevation.command(
        "create-item", short_help="Create a STAC Item from a las or laz file"
    )
    @click.argument("href")
    @click.argument("dst")
    @click.option("-r", "--reader", help="Override the default PDAL reader.")
    @click.option(
        "-q", "--quick", is_flag=True, help="Do a quick look at the COPC data."
    )
    @click.option(
        "-t",
        "--pointcloud-type",
        default="lidar",
        help="Set the pointcloud type (default: lidar)",
    )
    @click.option(
        "--compute-statistics/--no-compute-statistics",
        default=False,
        help="Compute statistics for the pointcloud (could take a while)",
    )
    @click.option(
        "-p",
        "--providers",
        help="Path to JSON file containing array of additional providers",
    )
    def create_item_command(
        href: str,
        dst: str,
        reader: str,
        pointcloud_type: str,
        compute_statistics: bool,
        providers: str,
        quick: bool,
    ) -> None:
        """Creates a STAC Item based on the header of a pointcloud.

        HREF is the pointcloud file.
        DST is directory that a STAC Item JSON file will be created
        in.
        """
        additional_providers = None
        if providers:
            with open(providers) as f:
                additional_providers = [
                    pystac.Provider.from_dict(d) for d in json.load(f)
                ]

        item = create_item(
            href,
            pdal_reader=reader,
            compute_statistics=compute_statistics,
            pointcloud_type=pointcloud_type,
            additional_providers=additional_providers,
            quick=quick,
        )

        item_path = os.path.join(dst, "{}.json".format(item.id))
        item.set_self_href(item_path)
        item.make_asset_hrefs_relative()
        item.save_object()
        item.validate()

    return canelevation
