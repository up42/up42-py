import dataclasses
import random
from unittest import mock

import pytest
import requests
import requests_mock as req_mock

from up42 import processing

from .fixtures import fixtures_globals as constants

PROCESS_ID = "process-id"
VALIDATION_URL = f"{constants.API_HOST}/v2/processing/processes/{PROCESS_ID}/validation"


@pytest.fixture(autouse=True)
def workspace():
    with mock.patch("up42.base.workspace") as workspace_mock:
        session = requests.Session()
        session.hooks = {"response": lambda r, *args, **kwargs: r.raise_for_status()}
        workspace_mock.auth.session = session
        yield


@dataclasses.dataclass(eq=True)
class TestJobTemplate(processing.BaseJobTemplate):
    title: str
    process_id = PROCESS_ID

    @property
    def inputs(self) -> dict:
        return {"title": self.title}


class TestBaseJobTemplate:
    # TODO: match request bodies

    def test_fails_to_construct_if_validation_fails(self, requests_mock: req_mock.Mocker):
        error_code = random.randint(430, 599)
        requests_mock.post(VALIDATION_URL, status_code=error_code)
        with pytest.raises(requests.exceptions.HTTPError) as error:
            _ = TestJobTemplate(title="title")
        assert error.value.response.status_code == error_code

    def test_should_be_invalid_if_inputs_are_malformed(self, requests_mock: req_mock.Mocker):
        error = processing.ValidationError(name="InvalidSchema", message="data.inputs must contain ['item'] properties")
        requests_mock.post(
            VALIDATION_URL,
            status_code=400,
            json={"title": "Bad Request", "status": 400, "schema-error": error.message},
        )
        template = TestJobTemplate(title="title")
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
        )
        template = TestJobTemplate(title="title")
        assert not template.is_valid
        assert template.errors == {error}


class TestSingleItemBaseJobTemplate:
    pass


class TestMultiItemBaseJobTemplate:
    pass
