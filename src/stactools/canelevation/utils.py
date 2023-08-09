import json
import os
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any, Dict, List, Tuple, Union

import rasterio
import requests
from dateutil.parser import parse
from pyproj import CRS, Transformer
from shapely.geometry import box, shape, mapping

class StacMetadata(SimpleNamespace):
    """
    AAFC Land Use Stac Metadata namespace
    """
    @staticmethod
    def get_datetime(dt_text: str) -> datetime:
        """
        Parse a string into a datetime in UTC

        Args:
            dt_text (str): Date/time text to parse

        Returns:
            datetime: Datetime object in the UTC timezone
        """
        dt = parse(dt_text)
        assert isinstance(dt, datetime)
        return dt.astimezone(timezone.utc)

    @staticmethod
    def get_bbox(geojson: str) -> List[float]:
        """
        Parse a geojson string and collect a shapely polygon

        Args:
            geojson (str): Geojson string (can be parsed with loads)

        Returns:
            List[float]: Bounding box as a list of floats representing the coordinates
        """
        geo = shape(json.loads(geojson))
        return list(geo.bounds)

def get_raster_metadata(raster_path: str) -> Tuple[List[float], List[float], List[int]]:
    """
    Retrieve the bounding box, transform and shape from a raster file.

    Args:
        raster_path (str): Path to the raster file

    Returns:
        Tuple[List[float], List[float], List[int]]: The bounding box, transform, and shape of the raster
    """
    with rasterio.open(raster_path) as dataset:
        bbox = list(dataset.bounds)
        transform = list(dataset.transform)
        shape = [dataset.height, dataset.width]

    return bbox, transform, shape

def bounds_to_geojson(bbox: List[float], in_crs: int) -> Dict[str, Any]:
    """
    Transform bounding box to geojson format.

    Args:
        bbox (List[float]): List of coordinates representing the bounding box
        in_crs (int): The CRS of the input bounding box

    Returns:
        Dict[str, Any]: The bounding box in geojson format
    """
    transformer = Transformer.from_crs(CRS.from_epsg(in_crs),
                                       CRS.from_epsg(4326),
                                       always_xy=True)
    xmin, ymin, xmax, ymax = bbox
    bbox_transformed = list(transformer.transform_bounds(xmin, ymin, xmax, ymax))
    box_shape = box(*bbox_transformed, ccw=True)
    return dict(mapping(box_shape))

def get_metadata(metadata_path: str) -> StacMetadata:
    """
    Collect remote metadata published by AAFC

    Args:
        metadata_path (str): Local path or href to metadata json.

    Returns:
        StacMetadata: AAFC Land Use Metadata for use in
        `stac.create_collection` and `stac.create_item`
    """
    stac_metadata = StacMetadata()

    if os.path.isfile(metadata_path):
        with open(metadata_path) as f:
            remote_metadata = json.load(f)
    else:
        metadata_response = requests.get(metadata_path)
        remote_metadata = metadata_response.json()["result"]

    stac_metadata.title = remote_metadata["title"]
    stac_metadata.description = remote_metadata["notes"]
    stac_metadata.provider = remote_metadata["organization"]["title"]
    stac_metadata.license_id = remote_metadata["license_id"]
    stac_metadata.license_title = remote_metadata["license_title"]
    stac_metadata.license_url = remote_metadata["license_url"]

    # Temporal extent
    stac_metadata.datetime_start = StacMetadata.get_datetime(remote_metadata["time_period_coverage_start"])

    if "time_period_coverage_end" in remote_metadata:
        stac_metadata.datetime_end = StacMetadata.get_datetime(remote_metadata["time_period_coverage_end"])
    else:
        stac_metadata.datetime_end = None  # Ongoing data capture

    # Bounding box
    stac_metadata.bbox_polygon = StacMetadata.get_bbox(remote_metadata["spatial"])

    return stac_metadata
