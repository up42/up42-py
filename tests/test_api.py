import json
import os
from pathlib import Path

import pytest
import requests_mock

import up42  # pylint-disable=wrong-import-order
from .fixtures import api_mock, api_live


@pytest.fixture()
def project_mock(api_mock):
    project = up42.Project(api=api_mock, project_id=api_mock.project_id)
    return project


def test_no_credentials_raises(api_mock):
    api_mock.project_id = None
    api_mock.project_api_key = None
    with pytest.raises(ValueError):
        api_mock._find_credentials()


def test_find_credentials_cfg_file(api_mock):
    api_mock.project_id = None
    api_mock.project_api_key = None

    fp = Path(__file__).parent / "mock_data" / "test_config.json"
    api_mock.cfg_file = fp

    api_mock._find_credentials()
    assert api_mock.project_id is not None
    assert api_mock.project_api_key is not None
    assert api_mock.auth_type == "project"


def test_endpoint(api_mock):
    api_mock.env = "com"
    assert api_mock._endpoint() == "https://api.up42.com"


def test_get_token_project(api_mock):
    api_mock.token = None
    with requests_mock.Mocker() as m:
        url_token = f"https://{api_mock.project_id}:{api_mock.project_api_key}@api.up42.{api_mock.env}/oauth/token"
        m.post(
            url=url_token, text='{"data":{"accessToken":"token_789"}}',
        )
        api_mock._get_token_project()
    assert api_mock.token == "token_789"


def test_generate_headers(api_mock):
    expected_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer token_1011",
        "cache-control": "no-cache",
    }
    assert api_mock._generate_headers(token="token_1011") == expected_headers


def test_request_helper(api_mock):
    with requests_mock.Mocker() as m:
        m.get(url="http://test.com", text='{"data": {"xyz":789}, "error":{}}')

        response = api_mock._request_helper(
            request_type="GET", url="http://test.com", data={}, querystring={}
        )
    response_json = json.loads(response.text)
    assert response_json == {"data": {"xyz": 789}, "error": {}}


def test_request(api_mock):
    api_mock.token = None
    with requests_mock.Mocker() as m:
        m.get(url="http://test.com", text='{"data": {"xyz":789}, "error":{}}')

        response_json = api_mock._request(request_type="GET", url="http://test.com")
    assert response_json == {"data": {"xyz": 789}, "error": {}}


def test_request_with_retry(api_mock):
    api_mock.retry = True
    with requests_mock.Mocker() as m:
        # Retry contains getting a new token, needs to be mocked separately.
        url_token = f"https://{api_mock.project_id}:{api_mock.project_api_key}@api.up42.{api_mock.env}/oauth/token"
        m.post(
            url=url_token, text='{"data":{"accessToken":"token_123"}}',
        )

        m.get(url="http://test.com", text='{"data": {"xyz":789}, "error":{}}')

        response_json = api_mock._request(request_type="GET", url="http://test.com")
    assert response_json == {"data": {"xyz": 789}, "error": {}}


def test_initialize_project(api_mock):
    project = api_mock.initialize_project()
    assert isinstance(project, up42.Project)


def test_initialize_project_with_get_info(api_mock):
    api_mock.authenticate = True

    with requests_mock.Mocker() as m:
        url_project_info = f"{api_mock._endpoint()}/projects/{api_mock.project_id}"
        m.get(url=url_project_info, text='{"data": {"xyz":789}, "error":{}}')

        project = api_mock.initialize_project()
    assert isinstance(project, up42.Project)
    assert project.info["xyz"] == 789


@pytest.mark.live
def test_initialize_project_live(api_live):
    project = api_live.initialize_project()
    assert isinstance(project, up42.Project)
    assert project.info["name"] == "python-sdk-test-project"


@pytest.mark.live
def test_validate_manifest_valid(api_live):
    _location_ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    fp = Path(_location_) / "mock_data/manifest.json"
    result = api_live.validate_manifest(path_or_json=fp)
    assert result == {"valid": True, "errors": []}


@pytest.mark.live
def test_validate_manifest_invalid(api_live):
    _location_ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    fp = Path(_location_) / "mock_data/manifest.json"
    with open(fp) as src:
        mainfest_json = json.load(src)
        mainfest_json.update(
            {
                "_up42_specification_version": 1,
                "input_capabilities": {
                    "invalidtype": {"up42_standard": {"format": "GTiff"}}
                },
            }
        )
    with pytest.raises(ValueError):
        api_live.validate_manifest(path_or_json=mainfest_json)
