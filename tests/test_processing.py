import dataclasses
import random
from typing import List
from unittest import mock

import pystac
import pytest
import requests
import requests_mock as req_mock

from up42 import processing

from . import helpers
from .fixtures import fixtures_globals as constants

PROCESS_ID = "process-id"
VALIDATION_URL = f"{constants.API_HOST}/v2/processing/processes/{PROCESS_ID}/validation"
TITLE = "title"
ITEM_URL = "https://item-url"
ITEM = pystac.Item.from_dict(
    {
        "type": "Feature",
        "stac_version": "1.0.0",
        "id": "id",
        "properties": {"datetime": "2024-01-01T00:00:00.000000Z"},
        "geometry": {"type": "Point", "coordinates": (0, 0)},
        "links": [{"rel": "self", "href": ITEM_URL}],
        "assets": {},
        "bbox": [0, 0, 0, 0],
        "stac_extensions": [],
    }
)


@pytest.fixture(autouse=True)
def workspace():
    with mock.patch("up42.base.workspace") as workspace_mock:
        session = requests.Session()
        session.hooks = {"response": lambda response, *args, **kwargs: response.raise_for_status()}
        workspace_mock.auth.session = session
        yield


@dataclasses.dataclass
class SampleJobTemplate(processing.JobTemplate):
    title: str
    process_id = PROCESS_ID

    @property
    def inputs(self) -> dict:
        return {"title": self.title}


class TestJobTemplate:
    def test_fails_to_construct_if_validation_fails(self, requests_mock: req_mock.Mocker):
        error_code = random.randint(430, 599)
        requests_mock.post(
            VALIDATION_URL,
            status_code=error_code,
            additional_matcher=helpers.match_request_body({"inputs": {"title": TITLE}}),
        )
        with pytest.raises(requests.exceptions.HTTPError) as error:
            _ = SampleJobTemplate(title=TITLE)
        assert error.value.response.status_code == error_code

    def test_should_be_invalid_if_inputs_are_malformed(self, requests_mock: req_mock.Mocker):
        error = processing.ValidationError(name="InvalidSchema", message="data.inputs must contain ['item'] properties")
        requests_mock.post(
            VALIDATION_URL,
            status_code=400,
            json={"title": "Bad Request", "status": 400, "schema-error": error.message},
            additional_matcher=helpers.match_request_body({"inputs": {"title": TITLE}}),
        )
        template = SampleJobTemplate(title=TITLE)
        assert not template.is_valid
        assert template.errors == {error}

    def test_should_be_invalid_if_inputs_are_invalid(self, requests_mock: req_mock.Mocker):
        error = processing.ValidationError(name="InvalidTitle", message="title is too long")
        requests_mock.post(
            VALIDATION_URL,
            status_code=422,
            json={
                "title": "Unprocessable Entity",
                "status": 422,
                "errors": [dataclasses.asdict(error)],
            },
            additional_matcher=helpers.match_request_body({"inputs": {"title": TITLE}}),
        )
        template = SampleJobTemplate(title=TITLE)
        assert not template.is_valid
        assert template.errors == {error}

    def test_should_construct(self, requests_mock: req_mock.Mocker):
        requests_mock.post(
            VALIDATION_URL,
            status_code=200,
            additional_matcher=helpers.match_request_body({"inputs": {"title": TITLE}}),
        )
        template = SampleJobTemplate(title=TITLE)
        assert template.is_valid
        assert not template.errors


@dataclasses.dataclass
class SampleSingleItemJobTemplate(processing.SingleItemJobTemplate):
    item: pystac.Item
    title: str
    process_id = PROCESS_ID


class TestSingleItemJobTemplate:
    def test_should_provide_inputs(self, requests_mock: req_mock.Mocker):
        requests_mock.post(
            VALIDATION_URL,
            status_code=200,
            additional_matcher=helpers.match_request_body({"inputs": {"title": TITLE, "item": ITEM_URL}}),
        )
        template = SampleSingleItemJobTemplate(
            item=ITEM,
            title=TITLE,
        )
        assert template.is_valid
        assert template.inputs == {"title": TITLE, "item": ITEM_URL}


@dataclasses.dataclass
class SampleMultiItemJobTemplate(processing.MultiItemJobTemplate):
    items: List[pystac.Item]
    title: str
    process_id = PROCESS_ID


class TestMultiItemJobTemplate:
    def test_should_provide_inputs(self, requests_mock: req_mock.Mocker):
        requests_mock.post(VALIDATION_URL, status_code=200)
        template = SampleMultiItemJobTemplate(
            items=[ITEM],
            title=TITLE,
        )
        assert template.is_valid
        assert template.inputs == {"title": TITLE, "items": [ITEM_URL]}
