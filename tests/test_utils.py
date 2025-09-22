import itertools
import json
import pathlib
from unittest import mock

import geopandas  # type: ignore
import pandas
import pytest
import requests
import requests_mock as req_mock
from dateutil import parser
from shapely import geometry  # type: ignore

from tests import constants
from up42 import utils

POLY = geometry.Polygon([(0, 0), (1, 1), (1, 0)])


@pytest.mark.parametrize(
    "date,set_end_of_day,result_time",
    [
        ("2014-01-01", False, "2014-01-01T00:00:00Z"),
        ("2015-01-01T00:00:00", False, "2015-01-01T00:00:00Z"),
        (parser.parse("2016-01-01"), False, "2016-01-01T00:00:00Z"),
        ("2017-01-01", True, "2017-01-01T23:59:59Z"),
        ("2018-01-01T00:10:00", True, "2018-01-01T00:10:00Z"),
        (parser.parse("2019-01-01"), True, "2019-01-01T00:00:00Z"),
    ],
)
def test_format_time(date, set_end_of_day, result_time):
    formatted_time = utils.format_time(date=date, set_end_of_day=set_end_of_day)
    assert isinstance(formatted_time, str)
    assert formatted_time == result_time


@pytest.mark.parametrize(
    "len_fc, in_vector",
    [
        (1, POLY),
        (
            1,
            geopandas.GeoDataFrame(
                pandas.DataFrame([0], columns=["id"]),
                crs={"init": "epsg:4326"},
                geometry=[POLY],
            ),
        ),
        (
            2,
            geopandas.GeoDataFrame(
                pandas.DataFrame([0, 1], columns=["id"]),
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
    fc = utils.any_vector_to_fc(in_vector)
    assert isinstance(fc, dict)
    assert fc["type"] == "FeatureCollection"
    assert fc.get("bbox") is not None
    assert fc["features"][0].get("bbox") is not None
    assert len(fc["features"]) != 0
    assert len(fc["features"]) == len_fc
    assert fc["features"][0]["geometry"].get("coordinates") is not None

    df = utils.any_vector_to_fc(in_vector, as_dataframe=True)
    assert isinstance(df, geopandas.GeoDataFrame)
    assert df.crs.to_string() == "EPSG:4326"


def test_any_vector_to_fc_raises_with_unaccepted_geometry_type():
    ring = geometry.LinearRing([(0, 0), (1, 1), (1, 0)])
    with pytest.raises(ValueError):
        utils.any_vector_to_fc(ring)


def test_fc_to_query_geometry_single_intersects():
    fp = pathlib.Path(__file__).resolve().parent / "mock_data/aoi_berlin.geojson"
    with open(fp, encoding="utf-8") as json_file:
        fc = json.load(json_file)
    query_geometry = utils.fc_to_query_geometry(fc=fc, geometry_operation="intersects")
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
    fp = pathlib.Path(__file__).resolve().parent / "mock_data/aoi_berlin.geojson"
    with open(fp, encoding="utf-8") as json_file:
        fc = json.load(json_file)
    query_geometry = utils.fc_to_query_geometry(fc=fc, geometry_operation="bbox")
    assert isinstance(query_geometry, list)
    assert len(query_geometry) == 4
    assert query_geometry == [13.375966, 52.515068, 13.378314, 52.516639]


def test_fc_to_query_geometry_multiple_raises():
    fp = pathlib.Path(__file__).resolve().parent / "mock_data/search_results_limited_columns.geojson"
    with open(fp, encoding="utf-8") as json_file:
        fc = json.load(json_file)

    with pytest.raises(ValueError) as e:
        utils.fc_to_query_geometry(fc=fc, geometry_operation="intersects")
    assert str(e.value) == "UP42 only accepts single geometries, the provided geometry contains multiple geometries."

    with pytest.raises(ValueError) as e:
        utils.fc_to_query_geometry(fc=fc, geometry_operation="bbox")
    assert str(e.value) == "UP42 only accepts single geometries, the provided geometry contains multiple geometries."


def test_fc_to_query_geometry_multipolygon_raises():
    fp = pathlib.Path(__file__).resolve().parent / "mock_data/multipolygon.geojson"
    with open(fp, encoding="utf-8") as json_file:
        fc = json.load(json_file)

    with pytest.raises(ValueError) as e:
        utils.fc_to_query_geometry(fc=fc, geometry_operation="intersects")
    assert str(e.value) == "UP42 only accepts single geometries, the provided geometry is a MultiPolygon."


class TestDownloadArchive:
    archive_url = "https://clouddownload.api.com/abcdef"

    @pytest.mark.parametrize("source", ["tests/mock_data/result_tif.tgz", "tests/mock_data/result_tif.zip"])
    def test_should_download_archive(self, requests_mock: req_mock.Mocker, tmp_path, source: str):
        requests_mock.get(
            url=self.archive_url,
            content=pathlib.Path(source).read_bytes(),
        )
        out_files = utils.download_archive(
            download_url=self.archive_url,
            output_directory=tmp_path,
        )
        for file in out_files:
            assert pathlib.Path(file).exists()
            assert pathlib.Path(file).suffix in [".tif", ".json"]
        assert len(out_files) == 2

    def test_fail_to_download_non_archive_file(self, requests_mock, tmp_path):
        source = pathlib.Path("tests/mock_data/aoi_berlin.geojson")

        requests_mock.get(
            url=self.archive_url,
            content=source.read_bytes(),
        )
        with pytest.raises(utils.UnsupportedArchive):
            utils.download_archive(
                download_url=self.archive_url,
                output_directory=tmp_path,
            )


@mock.patch("importlib.metadata.version", return_value="some_version")
def test_get_up42_py_version(version: mock.Mock):
    assert utils.get_up42_py_version() == "some_version"
    version.assert_called_with("up42-py")


def test_read_json_should_skip_reading_if_path_is_none():
    assert not utils.read_json(path_or_dict=None)


def test_read_json_should_skip_reading_if_dict_is_given():
    value = {"some": "data"}
    assert utils.read_json(path_or_dict=value) == value


@pytest.fixture(params=[True, False], ids=["str", "path"], name="str_or_path")
def _str_or_path(tmp_path, request):
    is_str = request.param
    result = tmp_path / "data.json"
    return str(result) if is_str else result


def test_should_read_json(str_or_path):
    value = {"some": "data"}
    with open(str_or_path, "w", encoding="utf-8") as file:
        json.dump(value, file)

    assert utils.read_json(path_or_dict=str_or_path) == value


def test_read_json_fails_if_path_not_found(str_or_path):
    with pytest.raises(ValueError) as ex:
        assert utils.read_json(path_or_dict=str_or_path)

    assert str(str_or_path) in str(ex.value)


class TestSortingField:
    @pytest.mark.parametrize("ascending", [True, False])
    def test_should_provide_directions(self, ascending: bool):
        field = utils.SortingField(name="name", ascending=ascending)
        assert field.asc == utils.SortingField(name="name", ascending=True)
        assert field.desc == utils.SortingField(name="name", ascending=False)

    def test_should_stringify(self):
        field = utils.SortingField(name="name")
        assert str(field.asc) == "name,asc"
        assert str(field.desc) == "name,desc"


class TestPagedQuery:
    params = {"param": "value"}
    endpoint = "/some-end-point"
    base_url = constants.API_HOST + endpoint + "?param=value"
    content = [{"id": f"id{idx}"} for idx in [1, 2]]

    def query(self):
        return utils.paged_query(self.params | {"ignored": None}, self.endpoint, requests.Session())

    def test_should_query_all_pages(self, requests_mock: req_mock.Mocker):
        for page in [0, 1]:
            response = {"content": self.content, "totalPages": 2}
            requests_mock.get(url=self.base_url + f"&page={page}", json=response)
        assert list(self.query()) == self.content * 2

    def test_should_query_empty_pages(self, requests_mock: req_mock.Mocker):
        response = {"content": [], "totalPages": 0}
        requests_mock.get(url=self.base_url + "&page=0", json=response)
        assert not list(self.query())

    def test_should_lazily_query_pages(self, requests_mock: req_mock.Mocker):
        response = {"content": self.content, "totalPages": 2}
        requests_mock.get(url=self.base_url + "&page=0", json=response)
        assert list(itertools.islice(self.query(), 2)) == self.content


@utils.deprecation(replacement_name=None, version="2.0.0")
def deprecated_function():
    pass


@utils.deprecation(replacement_name="NewClass", version="2.0.0")
class DeprecatedClass:
    pass


class TestDeprecationDecorator:
    def test_deprecation_warning_on_function(self):
        with pytest.warns(
            DeprecationWarning, match="`deprecated_function` is deprecated and will be removed in version 2.0.0."
        ):
            deprecated_function()

    def test_deprecation_warning_on_class(self):
        with pytest.warns(
            DeprecationWarning,
            match="`DeprecatedClass` is deprecated and will be removed in version 2.0.0 Use `NewClass` instead.",
        ):
            DeprecatedClass()
