import json
from pathlib import Path
import tempfile
from dateutil.parser import parse

import geopandas as gpd
from geopandas import GeoDataFrame
import pandas as pd
import pytest
from shapely.geometry import Point, Polygon, LinearRing

from .context import (
    format_time_period,
    any_vector_to_fc,
    fc_to_query_geometry,
    download_results_from_gcs,
    filter_jobs_on_mode,
)


POLY = Polygon([(0, 0), (1, 1), (1, 0)])


def test_format_time_period():
    @pytest.mark.parametrize(
        "start_date,end_date,result_time",
        [
            ("2014-01-01", "2016-12-31", "2014-01-01T00:00:00Z/2016-12-31T23:59:59Z"),
            (
                "2014-01-01T00:00:00",
                "2016-12-31T10:11:12",
                "2014-01-01T00:00:00Z/2016-12-31T10:11:12Z",
            ),
            (
                "2014-01-01T00:00:00",
                "2016-12-31",
                "2014-01-01T00:00:00Z/2016-12-31T23:59:59Z",
            ),
            (
                parse("2014-01-01"),
                parse("2016-12-31T10:11:12"),
                "2014-01-01T00:00:00Z/2016-12-31T10:11:12Z",
            ),
            (
                parse("2014-01-01"),
                "2016-12-31",
                "2014-01-01T00:00:00Z/2016-12-31T23:59:59Z",
            ),
            (
                parse("2014-01-01"),
                "2016-12-31T10:11:12",
                "2014-01-01T00:00:00Z/2016-12-31T10:11:12Z",
            ),
        ],
    )
    def test_format_time_period(start_date, end_date, result_time):
        time_period = format_time_period(
            start_date=start_date,
            end_date=end_date,
        )
        assert isinstance(time_period, str)
        assert time_period == result_time


@pytest.mark.parametrize(
    "start_date,end_date",
    [(None, "2014-01-01"), ("2014-01-01", None)],
)
def test_format_time_period_raises_with_missing_dates(start_date, end_date):
    with pytest.raises(ValueError) as e:
        format_time_period(
            start_date=start_date,
            end_date=end_date,
        )
        assert (
            "When using dates, both start_date and end_date need to be provided."
            in str(e.value)
        )


@pytest.mark.parametrize(
    "start_date,end_date",
    [(None, "2016-01-01"), ("2014-01-01", None)],
)
def test_format_time_period_raises_with_mixed_up_dates(start_date, end_date):
    with pytest.raises(ValueError) as e:
        format_time_period(
            start_date=start_date,
            end_date=end_date,
        )
        assert "The start_date needs to be earlier than the end_date!" in str(e.value)


@pytest.mark.parametrize(
    "len_fc, in_vector",
    [
        (1, Point((10, 6))),
        (1, POLY),
        (
            1,
            gpd.GeoDataFrame(
                pd.DataFrame([0], columns=["id"]),
                crs={"init": "epsg:4326"},
                geometry=[POLY],
            ),
        ),
        (
            2,
            gpd.GeoDataFrame(
                pd.DataFrame([0, 1], columns=["id"]),
                crs={"init": "epsg:4326"},
                geometry=[POLY, POLY],
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
    with open(out_tgz, "rb") as src_tgz:
        out_tgz_file = src_tgz.read()
    requests_mock.get(
        url=cloud_storage_url,
        content=out_tgz_file,
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


def test_download_result_from_gcs_zip(requests_mock):
    cloud_storage_url = "http://clouddownload.api.com/abcdef"

    out_zip = Path(__file__).resolve().parent / "mock_data/result_tif.zip"
    with open(out_zip, "rb") as src_zip:
        out_zip_file = src_zip.read()

    requests_mock.get(
        url=cloud_storage_url,
        content=out_zip_file,
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


def test_download_result_from_gcs_not_compressed(requests_mock):
    cloud_storage_url = "http://clouddownload.api.com/abcdef"

    out_zip = Path(__file__).resolve().parent / "mock_data/aoi_berlin.geojson"
    with open(out_zip, "rb") as src_zip:
        out_zip_file = src_zip.read()

    requests_mock.get(
        url=cloud_storage_url,
        content=out_zip_file,
    )
    with tempfile.TemporaryDirectory() as tempdir:
        with open(Path(tempdir) / "dummy.txt", "w") as fp:
            fp.write("dummy")
        with pytest.raises(ValueError):
            download_results_from_gcs(
                download_url=cloud_storage_url,
                output_directory=tempdir,
            )


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
