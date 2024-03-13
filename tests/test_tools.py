import pathlib

import geopandas  # type: ignore
import pytest

from up42 import tools


@pytest.mark.parametrize("vector_format", ["geojson", "kml", "wkt"])
def test_read_vector_file_different_formats(vector_format):
    fp = pathlib.Path(__file__).resolve().parent / f"mock_data/aoi_berlin.{vector_format}"
    fc = tools.read_vector_file(filename=str(fp))
    assert isinstance(fc, dict)
    assert fc["type"] == "FeatureCollection"


def test_read_vector_file_as_df():
    fp = pathlib.Path(__file__).resolve().parent / "mock_data/aoi_berlin.geojson"
    df = tools.read_vector_file(filename=str(fp), as_dataframe=True)
    assert isinstance(df, geopandas.GeoDataFrame)
    assert df.crs.to_epsg() == 4326


def test_get_example_aoi():
    fc = tools.get_example_aoi("Berlin")
    assert isinstance(fc, dict)
    assert fc["type"] == "FeatureCollection"
