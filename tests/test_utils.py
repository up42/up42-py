import json
from pathlib import Path
import tempfile

import folium
import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import Point, Polygon, LinearRing
import requests_mock

from .context import (
    is_notebook,
    folium_base_map,
    any_vector_to_fc,
    fc_to_query_geometry,
    download_results_from_gcs,
)


def test_is_notebook():
    notebook_available = is_notebook()
    assert not notebook_available


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
        (
            1,
            {
                "type": "Polygon",
                "coordinates": [
                    [
                        [-97.324448, 37.72246],
                        [-97.349682, 37.722732],
                        [-97.349939, 37.708405],
                        [-97.322989, 37.708202],
                        [-97.320414, 37.708473],
                        [-97.324448, 37.72246],
                    ]
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


def test_fc_to_query_geometry_single_intersects():
    fp = Path(__file__).resolve().parent / "mock_data/aoi_berlin.geojson"
    with open(fp) as json_file:
        fc = json.load(json_file)
    query_geometry = fc_to_query_geometry(fc=fc, geometry_operation="intersects")
    assert isinstance(query_geometry, dict)
    assert query_geometry["type"] == "Polygon"
    assert query_geometry["coordinates"] == [
        [
            [13.375966, 52.515068],
            [13.375966, 52.516639],
            [13.378314, 52.516639],
            [13.378314, 52.515068],
            [13.375966, 52.515068],
        ]
    ]


def test_fc_to_query_geometry_single_bbox():
    fp = Path(__file__).resolve().parent / "mock_data/aoi_berlin.geojson"
    with open(fp) as json_file:
        fc = json.load(json_file)
    query_geometry = fc_to_query_geometry(fc=fc, geometry_operation="bbox")
    assert isinstance(query_geometry, list)
    assert len(query_geometry) == 4
    assert query_geometry == [13.375966, 52.515068, 13.378314, 52.516639]


def test_fc_to_query_geometry_multiple_intersects_union_default():
    fp = (
        Path(__file__).resolve().parent
        / "mock_data/search_results_limited_columns.geojson"
    )
    with open(fp) as json_file:
        fc = json.load(json_file)
    query_geometry = fc_to_query_geometry(fc=fc, geometry_operation="intersects")
    assert isinstance(query_geometry, dict)

    # TODO: Reduce coordinate precision.
    assert query_geometry == {
        "type": "Polygon",
        "coordinates": (
            (
                (-17.55563746, 14.8339349),
                (-17.526764600314, 14.830882430200507),
                (-17.45205267, 14.83313312),
                (-17.45204926020147, 14.82760344506775),
                (-17.43369713, 14.82682434),
                (-17.433685006674313, 14.821041955386997),
                (-17.33084166135773, 14.81016924623828),
                (-17.3306027, 14.99399093),
                (-17.13627232, 14.98980934),
                (-17.1360538, 14.63913086),
                (-17.323060876683464, 14.645227997249702),
                (-17.32295241, 14.60807946),
                (-17.55634002, 14.63571323),
                (-17.556321337772165, 14.640984270766547),
                (-17.59660485506847, 14.643182953986058),
                (-17.64723461, 14.64196829),
                (-17.64722943826006, 14.64594605485283),
                (-17.66426739, 14.64687599),
                (-17.66356696, 14.83658303),
                (-17.555644313012035, 14.83200137761032),
                (-17.55563746, 14.8339349),
            ),
        ),
    }


def test_fc_to_query_geometry_multiple_bbox_union_default():
    fp = (
        Path(__file__).resolve().parent
        / "mock_data/search_results_limited_columns.geojson"
    )
    with open(fp) as json_file:
        fc = json.load(json_file)
    query_geometry = fc_to_query_geometry(fc=fc, geometry_operation="bbox")
    assert isinstance(query_geometry, list)
    assert len(query_geometry) == 4
    assert query_geometry == [-17.66426739, 14.60807946, -17.1360538, 14.99399093]


def test_fc_to_query_geometry_multiple_intersects_first():
    fp = (
        Path(__file__).resolve().parent
        / "mock_data/search_results_limited_columns.geojson"
    )
    with open(fp) as json_file:
        fc = json.load(json_file)
    query_geometry = fc_to_query_geometry(
        fc=fc, geometry_operation="intersects", squash_multiple_features="first"
    )
    assert isinstance(query_geometry, dict)
    assert query_geometry == {
        "type": "Polygon",
        "coordinates": [
            [
                [-17.6469937, 14.82726054],
                [-17.45205267, 14.83313312],
                [-17.45193768, 14.64665368],
                [-17.64723461, 14.64196829],
                [-17.6469937, 14.82726054],
            ]
        ],
    }


def test_fc_to_query_geometry_multiple_bbox_first():
    fp = (
        Path(__file__).resolve().parent
        / "mock_data/search_results_limited_columns.geojson"
    )
    with open(fp) as json_file:
        fc = json.load(json_file)
    query_geometry = fc_to_query_geometry(
        fc=fc, geometry_operation="bbox", squash_multiple_features="first"
    )
    assert isinstance(query_geometry, list)
    assert len(query_geometry) == 4
    assert query_geometry == [-17.64723461, 14.64196829, -17.45193768, 14.83313312]


def test_fc_to_query_geometry_raises_with_not_accepted():
    ring = LinearRing([(0, 0), (1, 1), (1, 0)])
    with pytest.raises(ValueError):
        fc_to_query_geometry(ring, geometry_operation="bbox")


def test_download_result_from_gcs():
    cloud_storage_url = "http://clouddownload.api.com/abcdef"

    def _simplified_get_download_url():
        return cloud_storage_url

    with requests_mock.Mocker() as m:
        out_tgz = Path(__file__).resolve().parent / "mock_data/result_tif.tgz"
        out_tgz_file = open(out_tgz, "rb")
        m.get(
            url=cloud_storage_url,
            content=out_tgz_file.read(),
            headers={"x-goog-stored-content-length": f"20000001"},
        )
        with tempfile.TemporaryDirectory() as tempdir:
            out_files = download_results_from_gcs(
                func_get_download_url=_simplified_get_download_url,
                output_directory=tempdir,
            )
            for file in out_files:
                assert Path(file).exists()
            assert len(out_files) == 1
