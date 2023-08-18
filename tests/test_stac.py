import datetime
import os
import unittest

from pystac.extensions.pointcloud import PointcloudExtension
from pystac.extensions.projection import ProjectionExtension

from stactools.canelevation.stac import create_collection, create_item


class StacTest(unittest.TestCase):
    def test_create_collection(self) -> None:
        # Write tests for each for the creation of a STAC Collection
        # Create the STAC Collection...
        collection = create_collection()
        collection.set_self_href("")

        # Check that it has some required attributes
        assert collection.id == "nrcan-canelevation"

        # Validate
        collection.validate()

    def test_create_item(self) -> None:
        path = os.path.abspath("tests/data-files/autzen_trim.las")
        print(path)
        item = create_item(path)
        self.assertEqual(item.id, "autzen_trim")
        self.assertEqual(item.datetime, datetime.datetime(2015, 9, 10))

        projection = ProjectionExtension.ext(item)
        self.assertEqual(projection.epsg, 2994)

        pointcloud = PointcloudExtension.ext(item)
        self.assertEqual(pointcloud.count, 110000)
        self.assertEqual(pointcloud.type, "lidar")
        self.assertEqual(pointcloud.encoding, "las")
        self.assertEqual(pointcloud.statistics, None)
        self.assertTrue(pointcloud.schemas)
        self.assertEqual(item.properties["canelevation:campaign"], "XXX")

        item.validate()

    def test_create_item_from_url(self) -> None:
        url = "https://github.com/PDAL/PDAL/raw/2.2.0/test/data/las/autzen_trim.las"
        item = create_item(url)
        self.assertEqual(item.properties["canelevation:campaign"], "XXX")
        item.validate()

    def test_create_item_from_nrcan_s3(self) -> None:
        url = "https://ftp-maps-canada-ca.s3.amazonaws.com/pub/elevation/pointclouds_nuagespoints/NRCAN/Fort_McMurray_2018/AB_FortMcMurray2018_20180518_NAD83CSRS_UTMZ12_1km_E4760_N62940_CQL1_CLASS.copc.laz"  # noqa
        item = create_item(url, None, False, "Lidar", None, True)
        self.assertEqual(
            item.properties["canelevation:campaign"], "AB_FortMcMurray2018_2018"
        )
        item.validate()
