import dataclasses
import datetime
import random
from unittest import mock

import pystac
import pytest
import requests
import requests_mock as req_mock

from tests import helpers
from tests.fixtures import fixtures_globals as constants
from up42 import processing

PROCESS_ID = "process-id"
VALIDATION_URL = f"{constants.API_HOST}/v2/processing/processes/{PROCESS_ID}/validation"
COST_URL = f"{constants.API_HOST}/v2/processing/processes/{PROCESS_ID}/cost"
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


class TestCost:
    @pytest.mark.parametrize("high_value", [11, 11.0, processing.Cost(strategy="strategy", credits=11)])
    @pytest.mark.parametrize("low_value", [9, 9.0, processing.Cost(strategy="strategy", credits=9)])
    def test_should_compare_with_numbers_and_costs_using_credits(
        self,
        high_value: processing.CostType,
        low_value: processing.CostType,
    ):
        cost = processing.Cost(strategy="strategy", credits=10)
        assert cost > low_value and cost >= low_value
        assert cost < high_value and cost <= high_value


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
        assert requests_mock.call_count == 1

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

    def test_fails_to_construct_if_evaluation_fails(self, requests_mock: req_mock.Mocker):
        error_code = random.randint(400, 599)
        requests_mock.post(
            VALIDATION_URL,
            status_code=200,
            additional_matcher=helpers.match_request_body({"inputs": {"title": TITLE}}),
        )
        requests_mock.post(
            COST_URL,
            status_code=error_code,
            additional_matcher=helpers.match_request_body({"inputs": {"title": TITLE}}),
        )

        with pytest.raises(requests.exceptions.HTTPError) as error:
            _ = SampleJobTemplate(title=TITLE)
        assert error.value.response.status_code == error_code
        assert requests_mock.call_count == 2

    @pytest.mark.parametrize(
        "cost",
        [
            processing.Cost(strategy="none", credits=1),
            processing.Cost(strategy="area", credits=1, size=5, unit="SKM"),
        ],
    )
    def test_should_construct(self, requests_mock: req_mock.Mocker, cost: processing.Cost):
        requests_mock.post(
            VALIDATION_URL,
            status_code=200,
            additional_matcher=helpers.match_request_body({"inputs": {"title": TITLE}}),
        )
        cost_payload = {
            key: value
            for key, value in {
                "pricingStrategy": cost.strategy,
                "totalCredits": cost.credits,
                "totalSize": cost.size,
                "unit": cost.unit,
            }.items()
            if value
        }
        requests_mock.post(
            COST_URL,
            status_code=200,
            json=cost_payload,
            additional_matcher=helpers.match_request_body({"inputs": {"title": TITLE}}),
        )
        template = SampleJobTemplate(title=TITLE)
        assert template.is_valid
        assert not template.errors
        assert template.cost == cost


@dataclasses.dataclass
class SampleSingleItemJobTemplate(processing.SingleItemJobTemplate):
    process_id = PROCESS_ID


class TestSingleItemJobTemplate:
    def test_should_provide_inputs(self, requests_mock: req_mock.Mocker):
        cost = processing.Cost(strategy="discount", credits=-1)
        body_matcher = helpers.match_request_body({"inputs": {"title": TITLE, "item": ITEM_URL}})
        requests_mock.post(
            VALIDATION_URL,
            status_code=200,
            additional_matcher=body_matcher,
        )
        requests_mock.post(
            COST_URL,
            status_code=200,
            json={"pricingStrategy": cost.strategy, "totalCredits": cost.credits},
            additional_matcher=body_matcher,
        )
        template = SampleSingleItemJobTemplate(
            item=ITEM,
            title=TITLE,
        )
        assert template.is_valid
        assert template.cost == cost
        assert template.inputs == {"title": TITLE, "item": ITEM_URL}


@dataclasses.dataclass
class SampleMultiItemJobTemplate(processing.MultiItemJobTemplate):
    process_id = PROCESS_ID


class TestMultiItemJobTemplate:
    def test_should_provide_inputs(self, requests_mock: req_mock.Mocker):
        cost = processing.Cost(strategy="discount", credits=-1)
        body_matcher = helpers.match_request_body({"inputs": {"title": TITLE, "items": [ITEM_URL]}})
        requests_mock.post(
            VALIDATION_URL,
            status_code=200,
            additional_matcher=body_matcher,
        )
        requests_mock.post(
            COST_URL,
            status_code=200,
            json={"pricingStrategy": cost.strategy, "totalCredits": cost.credits},
            additional_matcher=body_matcher,
        )
        template = SampleMultiItemJobTemplate(
            items=[ITEM],
            title=TITLE,
        )
        assert template.is_valid
        assert template.cost == cost
        assert template.inputs == {"title": TITLE, "items": [ITEM_URL]}


JOB_ID = "21e447c4-56e5-4f29-bb5a-1358e756515a"
GET_JOB_URL = f"{constants.API_HOST}/v2/processing/jobs/{JOB_ID}"
HOST_RESULTS = "https://api.up42.dev"
RESULT_COLLECTION_ID = "d8ec4a66-18a2-40bb-b73d-86ff9540de51"
RESULT_ITEM_ID = "5cd3a187-26ee-4764-ad21-b2927610caca"
RESULT_CREDITS = 1
RESULT_JOB_WORKSPACE_ID = "8710edff-5fd8-4638-b75d-aa1110448370"
RESULT_ACCOUNT_ID = "04eb7366-f2a4-401f-953d-517aea4353d1"
RESULTS_DEFINITION = {
    "inputs": {
        "item": f"{HOST_RESULTS}/v2/assets/stac/collections/" f"{RESULT_COLLECTION_ID}/items/{RESULT_ITEM_ID}",
        "title": "Test xbxw",
    }
}
JOB_SUCCESS_RESPONSE: processing.JobMetadata = {
    "processID": "pansharpening",
    "jobID": JOB_ID,
    "accountID": RESULT_ACCOUNT_ID,
    "workspaceID": RESULT_JOB_WORKSPACE_ID,
    "definition": RESULTS_DEFINITION,
    "status": "captured",
    "created": "2024-06-05T13:12:48.124568Z",
    "updated": "2024-06-05T13:13:27.426795Z",
    "started": "2024-06-05T13:12:56.542773Z",
    "finished": "2024-06-05T13:13:27.320528Z",
}


@pytest.fixture(name="job")
def _job():
    created = datetime.datetime.fromisoformat(str(JOB_SUCCESS_RESPONSE["created"]))
    started = datetime.datetime.fromisoformat(str(JOB_SUCCESS_RESPONSE["started"]))
    finished = datetime.datetime.fromisoformat(str(JOB_SUCCESS_RESPONSE["finished"]))
    updated = datetime.datetime.fromisoformat(str(JOB_SUCCESS_RESPONSE["updated"]))
    return processing.Job(
        process_id=JOB_SUCCESS_RESPONSE["processID"],
        id=JOB_SUCCESS_RESPONSE["jobID"],
        account_id=JOB_SUCCESS_RESPONSE["accountID"],
        workspace_id=JOB_SUCCESS_RESPONSE["workspaceID"],
        definition=JOB_SUCCESS_RESPONSE["definition"],
        status=processing.JobStatuses(JOB_SUCCESS_RESPONSE["status"]),
        created=created,
        started=started,
        finished=finished,
        updated=updated,
    )


class TestJob:
    @pytest.fixture
    def test_success_job(self, requests_mock: req_mock.Mocker):
        requests_mock.get(url=GET_JOB_URL, json=JOB_SUCCESS_RESPONSE)
        return processing.Job.get(JOB_ID)

    def test_should_get_job(self, requests_mock: req_mock.Mocker, job: processing.Job):
        requests_mock.get(url=GET_JOB_URL, json=JOB_SUCCESS_RESPONSE)
        assert processing.Job.get(JOB_ID) == job

    def test_should_return_job_properties(self, test_success_job):
        assert test_success_job.status == processing.JobStatuses.CAPTURED
        assert test_success_job.account_id == RESULT_ACCOUNT_ID
        assert test_success_job.workspace_id == RESULT_JOB_WORKSPACE_ID
        assert test_success_job.definition == RESULTS_DEFINITION

    def test_should_format_datetime_properties(self, test_success_job):
        assert isinstance(test_success_job.created, datetime.datetime)
        assert isinstance(test_success_job.started, datetime.datetime)
        assert isinstance(test_success_job.finished, datetime.datetime)
        assert isinstance(test_success_job.updated, datetime.datetime)
