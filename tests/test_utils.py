import json
import tempfile
from pathlib import Path
from typing import Dict
from unittest.mock import Mock, patch

import geopandas as gpd  # type: ignore
import pandas as pd
import pytest
from dateutil.parser import parse
from geopandas import GeoDataFrame
from shapely.geometry import LinearRing, Polygon  # type: ignore

from up42.utils import (
    any_vector_to_fc,
    autocomplete_order_parameters,
    download_from_gcs_unpack,
    fc_to_query_geometry,
    filter_jobs_on_mode,
    format_time,
    get_up42_py_version,
    read_json,
)

POLY = Polygon([(0, 0), (1, 1), (1, 0)])


@pytest.mark.parametrize(
    "date,set_end_of_day,result_time",
    [
        ("2014-01-01", False, "2014-01-01T00:00:00Z"),
        ("2015-01-01T00:00:00", False, "2015-01-01T00:00:00Z"),
        (parse("2016-01-01"), False, "2016-01-01T00:00:00Z"),
        ("2017-01-01", True, "2017-01-01T23:59:59Z"),
        ("2018-01-01T00:10:00", True, "2018-01-01T00:10:00Z"),
        (parse("2019-01-01"), True, "2019-01-01T00:00:00Z"),
    ],
)
def test_format_time(date, set_end_of_day, result_time):
    formatted_time = format_time(date=date, set_end_of_day=set_end_of_day)
    assert isinstance(formatted_time, str)
    assert formatted_time == result_time


@pytest.mark.parametrize(
    "len_fc, in_vector",
    [
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


def test_any_vector_to_fc_raises_with_unaccepted_geometry_type():
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


def test_fc_to_query_geometry_multiple_raises():
    fp = Path(__file__).resolve().parent / "mock_data/search_results_limited_columns.geojson"
    with open(fp) as json_file:
        fc = json.load(json_file)

    with pytest.raises(ValueError) as e:
        fc_to_query_geometry(fc=fc, geometry_operation="intersects")
    assert str(e.value) == "UP42 only accepts single geometries, the provided geometry contains multiple geometries."

    with pytest.raises(ValueError) as e:
        fc_to_query_geometry(fc=fc, geometry_operation="bbox")
    assert str(e.value) == "UP42 only accepts single geometries, the provided geometry contains multiple geometries."


def test_fc_to_query_geometry_multipolygon_raises():
    fp = Path(__file__).resolve().parent / "mock_data/multipolygon.geojson"
    with open(fp) as json_file:
        fc = json.load(json_file)

    with pytest.raises(ValueError) as e:
        fc_to_query_geometry(fc=fc, geometry_operation="intersects")
    assert str(e.value) == "UP42 only accepts single geometries, the provided geometry is a MultiPolygon."


def test_download_gcs_unpack_tgz(requests_mock):
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
        out_files = download_from_gcs_unpack(
            download_url=cloud_storage_url,
            output_directory=tempdir,
        )

        for file in out_files:
            assert Path(file).exists()
        assert len(out_files) == 2
        assert not (Path(tempdir) / "output").exists()


def test_download_gcs_unpack_zip(requests_mock):
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
        out_files = download_from_gcs_unpack(
            download_url=cloud_storage_url,
            output_directory=tempdir,
        )

        for file in out_files:
            assert Path(file).exists()
        assert len(out_files) == 2
        assert not (Path(tempdir) / "output").exists()


def test_download_gcs_not_unpack(requests_mock):
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
            download_from_gcs_unpack(
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


def test_autocomplete_order_parameters():
    with open(Path(__file__).resolve().parent / "mock_data/data_product_spot_schema.json") as json_file:
        json_data_product_schema = json.load(json_file)
    order_parameters = {
        "dataProduct": "123",
        "params": {"existing_param1": "abc"},
    }
    order_parameters = autocomplete_order_parameters(order_parameters=order_parameters, schema=json_data_product_schema)

    assert "dataProduct" in order_parameters
    assert isinstance(order_parameters["params"], Dict)
    assert order_parameters["params"]["existing_param1"] is not None
    assert order_parameters["params"]["geometry"] is None
    assert order_parameters["params"]["acquisitionMode"] is None


@patch("importlib.metadata.version", return_value="some_version")
def test_get_up42_py_version(version: Mock):
    assert get_up42_py_version() == "some_version"
    version.assert_called_with("up42-py")


def test_read_json_should_skip_reading_if_path_is_none():
    assert not read_json(path_or_dict=None)


def test_read_json_should_skip_reading_if_dict_is_given():
    value = {"some": "data"}
    assert read_json(path_or_dict=value) == value


@pytest.fixture(params=[True, False], ids=["str", "path"])
def str_or_path(tmp_path, request):
    is_str = request.param
    result = tmp_path / "data.json"
    return str(result) if is_str else result


def test_should_read_json(str_or_path):
    value = {"some": "data"}
    with open(str_or_path, "w") as file:
        json.dump(value, file)

    assert read_json(path_or_dict=str_or_path) == value


def test_read_json_fails_if_path_not_found(str_or_path):
    with pytest.raises(ValueError) as ex:
        assert read_json(path_or_dict=str_or_path)

    assert str(str_or_path) in str(ex.value)
