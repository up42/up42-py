import dataclasses
import datetime
import random
import urllib.parse
import uuid
from typing import Any, List, Optional
from unittest import mock

import pystac
import pytest
import requests
import requests_mock as req_mock

from tests import helpers
from tests.fixtures import fixtures_globals as constants
from up42 import processing, utils

PROCESS_ID = "process-id"
VALIDATION_URL = f"{constants.API_HOST}/v2/processing/processes/{PROCESS_ID}/validation"
COST_URL = f"{constants.API_HOST}/v2/processing/processes/{PROCESS_ID}/cost"
EXECUTION_URL = f"{constants.API_HOST}/v2/processing/processes/{PROCESS_ID}/execution"
TITLE = "title"
COLLECTION_ID = str(uuid.uuid4())
COLLECTION_URL = f"https://collections/{COLLECTION_ID}"
ITEM_URL = "https://item-url/"
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

JOB_ID = str(uuid.uuid4())
JOBS_URL = f"{constants.API_HOST}/v2/processing/jobs"
JOB_URL = f"{JOBS_URL}/{JOB_ID}"
CREDITS = 1
ACCOUNT_ID = str(uuid.uuid4())
DEFINITION = {
    "inputs": {
        "item": ITEM_URL,
        "title": TITLE,
    }
}
NOW = datetime.datetime.now()
INVALID_TITLE_ERROR = processing.ValidationError(name="InvalidTitle", message="title is too long")
JOB_METADATA: processing.JobMetadata = {
    "processID": PROCESS_ID,
    "jobID": JOB_ID,
    "accountID": ACCOUNT_ID,
    "workspaceID": constants.WORKSPACE_ID,
    "definition": DEFINITION,
    "results": {
        "collection": f"{COLLECTION_URL}",
        "errors": [dataclasses.asdict(INVALID_TITLE_ERROR)],
    },
    "creditConsumption": {"credits": CREDITS},
    "status": "created",
    "created": f"{NOW.isoformat()}Z",
    "updated": f"{NOW.isoformat()}Z",
    "started": None,
    "finished": None,
}

JOB = processing.Job(
    process_id=PROCESS_ID,
    id=JOB_ID,
    account_id=ACCOUNT_ID,
    workspace_id=constants.WORKSPACE_ID,
    definition=DEFINITION,
    collection_url=COLLECTION_URL,
    errors=[INVALID_TITLE_ERROR],
    credits=CREDITS,
    status=processing.JobStatus.CREATED,
    created=NOW,
    updated=NOW,
)


@pytest.fixture(autouse=True)
def set_status_raising_session():
    session = requests.Session()
    session.hooks = {"response": lambda response, *args, **kwargs: response.raise_for_status()}
    processing.Job.session = session  # type: ignore
    processing.JobTemplate.session = session  # type: ignore


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
        requests_mock.post(
            VALIDATION_URL,
            status_code=422,
            json={
                "title": "Unprocessable Entity",
                "status": 422,
                "errors": [dataclasses.asdict(INVALID_TITLE_ERROR)],
            },
            additional_matcher=helpers.match_request_body({"inputs": {"title": TITLE}}),
        )
        template = SampleJobTemplate(title=TITLE)
        assert not template.is_valid
        assert template.errors == {INVALID_TITLE_ERROR}

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

    def test_should_execute(self, requests_mock: req_mock.Mocker):
        cost = processing.Cost(strategy="none", credits=1)
        requests_mock.post(
            VALIDATION_URL,
            status_code=200,
            additional_matcher=helpers.match_request_body({"inputs": {"title": TITLE}}),
        )
        cost_payload = {"pricingStrategy": cost.strategy, "totalCredits": cost.credits}
        requests_mock.post(
            COST_URL,
            status_code=200,
            json=cost_payload,
            additional_matcher=helpers.match_request_body({"inputs": {"title": TITLE}}),
        )
        requests_mock.post(
            EXECUTION_URL,
            status_code=200,
            json=JOB_METADATA,
            additional_matcher=helpers.match_request_body({"inputs": {"title": TITLE}}),
        )
        template = SampleJobTemplate(title=TITLE)
        assert template.execute() == JOB
        assert template.is_valid and not template.errors
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


class TestJob:
    def test_should_get_job(self, requests_mock: req_mock.Mocker):
        requests_mock.get(url=JOB_URL, json=JOB_METADATA)
        assert processing.Job.get(JOB_ID) == JOB

    def test_should_get_collection(self):
        stac_client = JOB.stac_client = mock.MagicMock()
        assert JOB.collection == stac_client.get_collection.return_value
        stac_client.get_collection.assert_called_with(COLLECTION_ID)

    def test_should_get_no_collection_if_collection_url_is_missing(self):
        job = dataclasses.replace(JOB, collection_url=None)
        assert not job.collection

    @pytest.mark.parametrize("status", [processing.JobStatus.SUCCESSFUL, processing.JobStatus.FAILED])
    def test_should_track_until_job_finishes(self, requests_mock: req_mock.Mocker, status: processing.JobStatus):
        updated = NOW + datetime.timedelta(minutes=4)
        started = NOW + datetime.timedelta(minutes=2)
        finished = NOW + datetime.timedelta(minutes=3)
        requests_mock.get(
            url=JOB_URL,
            response_list=[
                {
                    "json": {
                        **JOB_METADATA,
                        "updated": f"{started}Z",
                        "started": f"{started}Z",
                        "status": processing.JobStatus.RUNNING.value,
                        "results": {
                            "collection": None,
                            "errors": None,
                        },
                    }
                },
                {
                    "json": {
                        **JOB_METADATA,
                        "updated": f"{updated}Z",
                        "started": f"{started}Z",
                        "finished": f"{finished}Z",
                        "status": status.value,
                    }
                },
            ],
        )
        job = dataclasses.replace(JOB)
        job.track(wait=1, retries=2)
        assert job == dataclasses.replace(JOB, finished=finished, started=started, updated=updated, status=status)

    def test_fails_to_track_if_job_retrieval_fails(self, requests_mock: req_mock.Mocker):
        requests_mock.get(
            url=JOB_URL,
            status_code=500,
        )
        job = dataclasses.replace(JOB)
        with pytest.raises(requests.exceptions.HTTPError):
            job.track(wait=1, retries=10)
        assert requests_mock.call_count == 1

    def test_fails_to_track_if_job_finishes_after_attempts_finished(self, requests_mock: req_mock.Mocker):
        requests_mock.get(
            url=JOB_URL,
            json=JOB_METADATA,
        )
        job = dataclasses.replace(JOB)
        with pytest.raises(processing.UnfinishedJob):
            job.track(wait=1, retries=2)
        assert requests_mock.call_count == 2

    @pytest.mark.parametrize("process_id", [None, [PROCESS_ID]])
    @pytest.mark.parametrize("workspace_id", [None, constants.WORKSPACE_ID])
    @pytest.mark.parametrize("status", [None, [processing.JobStatus.CAPTURED]])
    @pytest.mark.parametrize("min_duration", [None, 1])
    @pytest.mark.parametrize("max_duration", [None, 10])
    @pytest.mark.parametrize("sort_by", [None, processing.JobSorting.process_id.desc])
    def test_should_get_all_jobs(
        self,
        requests_mock: req_mock.Mocker,
        process_id: Optional[List[str]],
        workspace_id: Optional[str],
        status: Optional[List[processing.JobStatus]],
        min_duration: Optional[int],
        max_duration: Optional[int],
        sort_by: Optional[utils.SortingField],
    ):
        query_params: dict[str, Any] = {}
        if process_id:
            query_params["processId"] = process_id
        if workspace_id:
            query_params["workspaceId"] = workspace_id
        if status:
            query_params["status"] = [entry.value for entry in status]
        if min_duration:
            query_params["minDuration"] = min_duration
        if max_duration:
            query_params["maxDuration"] = max_duration
        if sort_by:
            query_params["sort"] = str(sort_by)

        query = urllib.parse.urlencode(query_params)

        next_page_url = "/v2/processing/jobs/next"
        requests_mock.get(
            url=JOBS_URL + (query and f"?{query}"),
            json={
                "jobs": [JOB_METADATA] * 3,
                "links": [{"rel": "next", "href": next_page_url}],
            },
        )
        requests_mock.get(
            url=f"{constants.API_HOST}{next_page_url}",
            json={
                "jobs": [JOB_METADATA] * 2,
                "links": [],
            },
        )
        assert (
            list(
                processing.Job.all(
                    process_id=process_id,
                    workspace_id=workspace_id,
                    status=status,
                    min_duration=min_duration,
                    max_duration=max_duration,
                    sort_by=sort_by,
                )
            )
            == [JOB] * 5
        )
