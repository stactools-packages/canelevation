import datetime

from pystac.extensions.pointcloud import PointcloudExtension
from stactools.canelevation import stac

from . import test_data


def test_create_collection() -> None:
    collection = stac.create_collection()
    collection.set_self_href(None)  # required for validation to pass
    assert collection.id == "nrcan-canelevation"
    collection.validate()


def test_create_item() -> None:
    # This function should be updated to exercise the attributes of interest on
    # a typical item

    item = stac.create_item(test_data.get_path("data/autzen_trim.las"))
    assert item.id == "autzen_trim"
    assert item.datetime == datetime.datetime(2015, 9, 10)
    print(item.properties.keys())
    assert item.properties["canelevation:campaign"] == "XXX"

    pointcloud = PointcloudExtension.ext(item)
    assert pointcloud.count == 110000
    assert pointcloud.type == "lidar"
    assert pointcloud.encoding == "las"
    assert pointcloud.statistics is None
    assert pointcloud.schemas is not None

    item.validate()


def test_create_item_from_url() -> None:
    url = "https://github.com/PDAL/PDAL/raw/2.2.0/test/data/las/autzen_trim.las"
    item = stac.create_item(url)
    item.validate()


def test_create_item_from_nrcan_s3() -> None:
    url = "https://ftp-maps-canada-ca.s3.amazonaws.com/pub/elevation/pointclouds_nuagespoints/NRCAN/Fort_McMurray_2018/AB_FortMcMurray2018_20180518_NAD83CSRS_UTMZ12_1km_E4760_N62940_CQL1_CLASS.copc.laz"  # noqa
    item = stac.create_item(url, None, False, "lidar", None, True)
    item.validate()
