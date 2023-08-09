# stactools-canelevation

[![PyPI](https://img.shields.io/pypi/v/stactools-canelevation)](https://pypi.org/project/stactools-canelevation/)

- Name: canelevation
- Package: `stactools.canelevation`
- [stactools-canelevation on PyPI](https://pypi.org/project/stactools-canelevation/)
- Owner: @jbants
- [Dataset homepage](https://open.canada.ca/data/en/dataset/7069387e-9986-4297-9f55-0288e9676947)
- STAC extensions used:
  - [proj](https://github.com/stac-extensions/projection/)
  - [pointcloud](https://github.com/stac-extensions/pointcloud/)  
- [Browse the example in human-readable form](https://radiantearth.github.io/stac-browser/#/external/raw.githubusercontent.com/stactools-packages/canelevation/main/examples/collection.json)

A stactools package for working with Cloud Optimized Point Clouds (copc) data from the CanElevation
data series from NRCan.

## STAC Examples

- [Collection](examples/collection.json)
- [Item](examples/AB_FortMcMurray2018_20180518_NAD83CSRS_UTMZ12_1km_E4760_N62940_CQL1_CLASS.copc/AB_FortMcMurray2018_20180518_NAD83CSRS_UTMZ12_1km_E4760_N62940_CQL1_CLASS.copc.json)

## Installation

```shell
pip install stactools-canelevation
```

## Command-line Usage

Base use is below:

```shell
stac canelevation create-collection -d <destination>
stac canelevation create-item <source> <destination>

stac canelevation create-item https://ftp-maps-canada-ca.s3.amazonaws.com/pub/elevation/pointclouds_nuagespoints/NRCAN/Fort_McMurray_2018/AB_FortMcMurray2018_20180518_NAD83CSRS_UTMZ12_1km_E4760_N62940_CQL1_CLASS.copc.laz examples/
```

PDAL can read just the header of a COPC file using the `quicklook` function.
The `-q` or `--quick` flags allow PDAL to quickly gather some metadata without opening the file.

**This does not fill the [`schemas` property of the pointcloud stac extension](https://github.com/stac-extensions/pointcloud#schema-object)**.

Use `stac canelevation --help` to see all subcommands and options.

## Contributing

We use [pre-commit](https://pre-commit.com/) to check any changes.
To set up your development environment:

```shell
pip install -e .
pip install -r requirements-dev.txt
pre-commit install
```

To check all files:

```shell
pre-commit run --all-files
```

To run the tests:

```shell
pytest -vv
```
