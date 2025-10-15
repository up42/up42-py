import itertools
import json
import pathlib
from unittest import mock

import pytest
import requests
import requests_mock as req_mock
from dateutil import parser

from tests import constants
from up42 import utils


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
            DeprecationWarning,
            match="`deprecated_function` is deprecated and will be removed in version 2.0.0.",
        ):
            deprecated_function()

    def test_deprecation_warning_on_class(self):
        with pytest.warns(
            DeprecationWarning,
            match="`DeprecatedClass` is deprecated and will be removed in version 2.0.0 Use `NewClass` instead.",
        ):
            DeprecatedClass()
