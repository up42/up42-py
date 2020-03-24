import folium
import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import Point, Polygon, LinearRing

from up42.utils import folium_base_map, any_vector_to_fc


def test_folium_base_map():
    m = folium_base_map()
    assert isinstance(m, folium.Map)
    assert m.crs == "EPSG3857"


poly = Polygon([(0, 0), (1, 1), (1, 0)])


@pytest.mark.parametrize(
    "len_fc, in_vector",
    [
        (1, Point((10, 6))),
        (1, poly),
        (
            1,
            gpd.GeoDataFrame(
                pd.DataFrame([0], columns=["id"]),
                crs={"init": "epsg:4326"},
                geometry=[poly],
            ),
        ),
        (
            2,
            gpd.GeoDataFrame(
                pd.DataFrame([0, 1], columns=["id"]),
                crs={"init": "epsg:4326"},
                geometry=[poly, poly],
            ),
        ),
        (1, [0.0, 0.0, 1.0, 1.0]),
        (
            1,
            {
                "id": "0",
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": (
                        ((10.00001, 6.0), (10.0, 5.99), (10.1, 6.00), (10.00001, 6.0),),
                    ),
                },
            },
        ),
        (
            1,
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "id": "0",
                        "type": "Feature",
                        "properties": {},
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": (
                                (
                                    (10.00001, 6.0),
                                    (10.0, 5.999),
                                    (10.00, 6.0),
                                    (10.00001, 6.0),
                                ),
                            ),
                        },
                    }
                ],
            },
        ),
    ],
)
def test_any_vector_to_fc(len_fc, in_vector):
    fc = any_vector_to_fc(in_vector)
    assert isinstance(fc, dict)
    assert fc["type"] == "FeatureCollection"
    assert fc.get("bbox") is not None
    assert fc["features"][0].get("bbox") is not None
    assert len(fc["features"]) != 0
    assert len(fc["features"]) == len_fc
    assert fc["features"][0]["geometry"].get("coordinates") is not None


def test_any_vector_to_fc_raises_with_not_accepted():
    ring = LinearRing([(0, 0), (1, 1), (1, 0)])
    with pytest.raises(ValueError):
        any_vector_to_fc(ring)
