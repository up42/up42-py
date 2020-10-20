import json
from pathlib import Path
import tempfile

import folium
import geopandas as gpd
from geopandas import GeoDataFrame
import pandas as pd
import pytest
from shapely.geometry import Point, Polygon, LinearRing
from shapely import wkt

from .context import (
    any_vector_to_fc,
    fc_to_query_geometry,
    download_results_from_gcs,
    _map_images,
    filter_jobs_on_mode,
)





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
                        (
                            (10.00001, 6.0),
                            (10.0, 5.99),
                            (10.1, 6.00),
                            (10.00001, 6.0),
                        ),
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

    df = any_vector_to_fc(in_vector, as_dataframe=True)
    assert isinstance(df, GeoDataFrame)
    assert df.crs.to_string() == "EPSG:4326"


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
    query_geometry = fc_to_query_geometry(
        fc=fc, geometry_operation="intersects", squash_multiple_features="union"
    )
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
    query_geometry = fc_to_query_geometry(
        fc=fc, geometry_operation="bbox", squash_multiple_features="union"
    )
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


def test_download_result_from_gcs(requests_mock):
    cloud_storage_url = "http://clouddownload.api.com/abcdef"

    out_tgz = Path(__file__).resolve().parent / "mock_data/result_tif.tgz"
    out_tgz_file = open(out_tgz, "rb")
    requests_mock.get(
        url=cloud_storage_url,
        content=out_tgz_file.read(),
    )
    with tempfile.TemporaryDirectory() as tempdir:
        with open(Path(tempdir) / "dummy.txt", "w") as fp:
            fp.write("dummy")
        out_files = download_results_from_gcs(
            download_url=cloud_storage_url,
            output_directory=tempdir,
        )

        for file in out_files:
            assert Path(file).exists()
        assert len(out_files) == 2
        assert not (Path(tempdir) / "output").exists()


def test_map_images_2_scenes():
    plot_file_format = [".jpg"]

    result_csv = Path(__file__).resolve().parent / "mock_data/df_2scenes.csv"
    result_df = pd.read_csv(result_csv)
    result_df["geometry"] = result_df["geometry"].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(result_df, geometry="geometry")

    quicklook_1 = (
        Path(__file__).resolve().parent
        / "mock_data/quicklooks/quicklook_16e18e15-c941-4aae-97cd-d67b18dc9f6e.jpg"
    )
    quicklook_2 = (
        Path(__file__).resolve().parent
        / "mock_data/quicklooks/quicklook_f8c03432-cec1-41b7-a203-4d871a03290f.jpg"
    )
    filepaths = [quicklook_1, quicklook_2]

    m = _map_images(plot_file_format, gdf, filepaths)
    m._repr_html_()
    out = m._parent.render()

    assert "Image 1 - f8c03432-cec1-41b7-a203-4d871a03290f" in out
    assert "Image 2 - 16e18e15-c941-4aae-97cd-d67b18dc9f6e" in out


def test_map_images_2_scenes_no_column_name():
    plot_file_format = [".jpg"]

    result_csv = Path(__file__).resolve().parent / "mock_data/df_2scenes.csv"
    result_df = pd.read_csv(result_csv)
    result_df["geometry"] = result_df["geometry"].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(result_df, geometry="geometry")

    quicklook_1 = (
        Path(__file__).resolve().parent
        / "mock_data/quicklooks/quicklook_16e18e15-c941-4aae-97cd-d67b18dc9f6e.jpg"
    )
    quicklook_2 = (
        Path(__file__).resolve().parent
        / "mock_data/quicklooks/quicklook_f8c03432-cec1-41b7-a203-4d871a03290f.jpg"
    )
    filepaths = [quicklook_1, quicklook_2]

    m = _map_images(plot_file_format, gdf, filepaths, name_column="nikoo")
    m._repr_html_()
    out = m._parent.render()

    assert "Image 1 - " in out
    assert "Image 2 - " in out


def test_map_images_1_scene():
    plot_file_format = [".jpg"]

    result_csv = Path(__file__).resolve().parent / "mock_data/df_1scene.csv"
    result_df = pd.read_csv(result_csv)
    result_df["geometry"] = result_df["geometry"].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(result_df, geometry="geometry")

    quicklook = (
        Path(__file__).resolve().parent
        / "mock_data/quicklooks/quicklook_16e18e15-c941-4aae-97cd-d67b18dc9f6e.jpg"
    )
    filepaths = [quicklook]

    m = _map_images(plot_file_format, gdf, filepaths)
    m._repr_html_()
    out = m._parent.render()

    assert "Image 1 - 2a581680-17e4-4a61-8aa9-9e47e1bf36bb" in out


def test_filter_jobs_on_mode():
    job_json = [{"mode": "DEFAULT"}, {"mode": "DRY_RUN"}]
    r = filter_jobs_on_mode(job_json)
    assert len(r) == 2
    r = filter_jobs_on_mode(job_json, test_jobs=False, real_jobs=True)
    assert len(r) == 1
    r = filter_jobs_on_mode(job_json, test_jobs=True, real_jobs=False)
    assert len(r) == 1
    with pytest.raises(ValueError):
        filter_jobs_on_mode(job_json, test_jobs=False, real_jobs=False)
