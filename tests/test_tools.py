from pathlib import Path

import geopandas as gpd  # type: ignore
import pytest

from up42.tools import get_example_aoi, read_vector_file


@pytest.mark.parametrize("vector_format", ["geojson", "kml", "wkt"])
def test_read_vector_file_different_formats(vector_format):
    fp = Path(__file__).resolve().parent / f"mock_data/aoi_berlin.{vector_format}"
    fc = read_vector_file(filename=str(fp))
    assert isinstance(fc, dict)
    assert fc["type"] == "FeatureCollection"


def test_read_vector_file_as_df():
    fp = Path(__file__).resolve().parent / "mock_data/aoi_berlin.geojson"
    df = read_vector_file(filename=str(fp), as_dataframe=True)
    assert isinstance(df, gpd.GeoDataFrame)
    assert df.crs.to_epsg() == 4326


def test_get_example_aoi():
    fc = get_example_aoi("Berlin")
    assert isinstance(fc, dict)
    assert fc["type"] == "FeatureCollection"
