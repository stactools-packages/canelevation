import datetime
import json
import logging
import os.path
import re
from typing import Any, Dict, List, Optional

import pdal
import pystac
from pyproj import CRS
from pystac.extensions.pointcloud import (
    PointcloudExtension,
    Schema,
    SchemaType,
    Statistic,
)
from pystac.extensions.projection import ProjectionExtension
from pystac.link import Link
from pystac.provider import Provider, ProviderRole
from shapely.geometry import box, mapping, shape
from stactools.core.projection import reproject_geom

from stactools.canelevation.constants import (
    KEYWORDS,
    METADATA_URL,
    PROVIDER_URL,
    STAC_ID,
)
from stactools.canelevation.utils import get_metadata

logger = logging.getLogger(__name__)


def _extract_reader_key(metadata: Dict[str, Any]) -> str:
    for key in metadata.keys():
        if key.startswith("readers"):
            return key
    raise Exception("Could not find reader key in pipeline metadata")


def create_collection(metadata_url: str = METADATA_URL) -> pystac.Collection:
    """Create a STAC Collection for CanElevation

    Args:
        metadata_url (str): The url from which to get metadata

    Returns:
        pystac.Collection: pystac collection object
    """
    metadata = get_metadata(metadata_url)

    provider = Provider(
        name=metadata.provider,
        roles=[
            ProviderRole.HOST,
            ProviderRole.LICENSOR,
            ProviderRole.PROCESSOR,
            ProviderRole.PRODUCER,
        ],
        url=PROVIDER_URL,
    )

    extent = pystac.Extent(
        pystac.SpatialExtent([metadata.bbox_polygon]),
        pystac.TemporalExtent([[metadata.datetime_start, metadata.datetime_end]]),
    )

    collection = pystac.Collection(
        id=STAC_ID,
        title=metadata.title,
        description=metadata.description,
        providers=[provider],
        license=metadata.license_id,
        extent=extent,
        catalog_type=pystac.CatalogType.RELATIVE_PUBLISHED,
        keywords=KEYWORDS,
    )

    collection.add_link(
        Link(rel="license", target=metadata.license_url, title=metadata.license_title)
    )

    return collection


def create_item(
    href: str,
    pdal_reader: Optional[str] = None,
    compute_statistics: bool = False,
    pointcloud_type: str = "lidar",
    additional_providers: Optional[List[Provider]] = None,
    quick: bool = False,
) -> pystac.Item:
    """Creates a STAC Item from a point cloud.

    Args:
        href (str): The href to the point cloud.
        pdal_reader (str): Override the default PDAL reader for this file extension.
        compute_statistics (bool): Set to true to compute statistics for the
        point cloud. Could take a while.
        pointcloud_type (str): The point cloud type, e.g. "lidar", "eopc",
        "radar", "sonar", or "other". Default is "lidar".
        quick (bool): Do a quick look into the point cloud

    Return:
        pystac.Item: A STAC Item representing this point cloud.
    """
    reader = href

    pipeline = pdal.Pipeline(json.dumps([reader, {"type": "filters.head", "count": 0}]))

    if quick:
        metadata = pipeline.quickinfo
    else:
        pipeline.execute()
        metadata = pipeline.metadata["metadata"]

    reader_key = _extract_reader_key(metadata)
    metadata = metadata[reader_key]
    id = os.path.splitext(os.path.basename(href))[0]
    encoding = os.path.splitext(href)[1][1:]

    if quick:
        spatialreference = CRS.from_wkt(metadata["srs"]["compoundwkt"])
    else:
        spatialreference = CRS.from_string(metadata["spatialreference"])

    if quick:
        original_bbox = box(
            metadata["bounds"]["minx"],
            metadata["bounds"]["miny"],
            metadata["bounds"]["maxx"],
            metadata["bounds"]["maxy"],
        )
    else:
        original_bbox = box(
            metadata["minx"], metadata["miny"], metadata["maxx"], metadata["maxy"]
        )

    geometry = reproject_geom(
        spatialreference, "EPSG:4326", mapping(original_bbox), precision=6
    )
    bbox = list(shape(geometry).bounds)

    # THESE DATES ARE DIFFERENT!!!
    if quick:
        # add try statement here because there is an error
        try:
            filedate = re.findall(r"\d{8}", id)[0]
        except IndexError:
            print(id)
            filedate = "19010101"
        dt = datetime.datetime.strptime(filedate, "%Y%m%d")

    else:
        dt = datetime.datetime(metadata["creation_year"], 1, 1) + datetime.timedelta(
            metadata["creation_doy"] - 1
        )
    id_name = os.path.splitext(id)[0]
    item = pystac.Item(
        id=id_name, geometry=geometry, bbox=bbox, datetime=dt, properties={}
    )

    # Create a campaign property
    pattern = r"([A-Z]{2}_\w+_\d{4})"
    match = re.search(pattern, os.path.splitext(id_name)[0])
    if match is not None:
        item.properties["canelevation:campaign"] = match.group(1)
    else:
        item.properties["canelevation:campaign"] = "XXX"

    item.add_asset(
        "pointcloud",
        pystac.Asset(
            href=href,
            media_type="application/octet-stream",
            roles=["data"],
            title=f"{encoding} point cloud",
        ),
    )

    # if additional_providers:
    #     item.common_metadata.providers.extend(additional_providers)

    pc_ext = PointcloudExtension.ext(item, add_if_missing=True)
    pc_ext.count = metadata["num_points"] if quick else metadata["count"]
    pc_ext.type = pointcloud_type
    pc_ext.encoding = encoding

    if quick:
        # We are filling the data with empty values. Since we did a quicklook, we only looked
        # at the header and not the full dataset.
        pc_ext.schemas = [
            Schema.create(dim, 0, SchemaType.SIGNED)
            for dim in metadata["dimensions"].split(",")
        ]
    else:
        schema = pipeline.schema["schema"]["dimensions"]
        pc_ext.schemas = [Schema(schema) for schema in schema]

    if compute_statistics:
        pc_ext.statistics = _compute_statistics(reader)

    epsg = spatialreference.to_epsg()
    if epsg:
        proj_ext = ProjectionExtension.ext(item, add_if_missing=True)
        proj_ext.epsg = epsg
        proj_ext.wkt2 = spatialreference.to_wkt()
        proj_ext.bbox = list(original_bbox.bounds)

    return item


def _compute_statistics(reader: str | dict[str, str]) -> Any:
    pipeline = pdal.Pipeline(json.dumps([reader, {"type": "filters.stats"}]))
    pipeline.execute()
    stats = json.loads(pipeline.get_metadata())["metadata"]["filters.stats"][
        "statistic"
    ]
    stats = [Statistic(stats) for stats in stats]
    return stats
