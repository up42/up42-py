import dataclasses
import datetime
import random
import urllib.parse
import uuid
from typing import Any
from unittest import mock

import pystac
import pytest
import requests
import requests_mock as req_mock

from tests import constants
from up42 import processing, utils

PROCESS_ID = "process-id"
EULA_ID = str(uuid.uuid4())
PROCESS_URL = f"{constants.API_HOST}/v2/processing/processes/{PROCESS_ID}"
PROCESS_SUMMARY = {
    "id": PROCESS_ID,
    "additionalParameters": {
        "parameters": [
            {"name": "eula-id", "value": [EULA_ID]},
            {"name": "price", "value": [{"credits": 1, "unit": "SQ_KM"}]},
        ]
    },
}
EULA_URL = f"{constants.API_HOST}/v2/eulas/{EULA_ID}"
VALIDATION_URL = f"{constants.API_HOST}/v2/processing/processes/{PROCESS_ID}/validation"
COST_URL = f"{constants.API_HOST}/v2/processing/processes/{PROCESS_ID}/cost"
EXECUTION_URL = (
    f"{constants.API_HOST}/v2/processing/processes/{PROCESS_ID}/execution?workspaceId={constants.WORKSPACE_ID}"
)
TITLE = "title"
COLLECTION_ID = str(uuid.uuid4())
COLLECTION_URL = f"https://collections/{COLLECTION_ID}"
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
NOW_AS_STR = datetime.datetime.now().isoformat(timespec="milliseconds")
NOW = datetime.datetime.fromisoformat(NOW_AS_STR)

MICROSECONDS = "123456Z"

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
    "created": f"{NOW_AS_STR}{MICROSECONDS}",
    "updated": f"{NOW_AS_STR}{MICROSECONDS}",
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


def as_java_timestamp(value: datetime.datetime):
    return value.isoformat(timespec="milliseconds") + MICROSECONDS


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

    @pytest.mark.parametrize("status", processing.TERMINAL_STATUSES)
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
                        "updated": as_java_timestamp(started),
                        "started": as_java_timestamp(started),
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
                        "updated": as_java_timestamp(updated),
                        "started": as_java_timestamp(started),
                        "finished": as_java_timestamp(finished),
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

    @pytest.mark.parametrize("process_id", [None, [PROCESS_ID, "another-id"]])
    @pytest.mark.parametrize("workspace_id", [None, constants.WORKSPACE_ID])
    @pytest.mark.parametrize("status", [None, random.choices(list(processing.JobStatus), k=2)])
    @pytest.mark.parametrize("min_duration", [None, 1])
    @pytest.mark.parametrize("max_duration", [None, 10])
    @pytest.mark.parametrize("sort_by", [None, processing.JobSorting.process_id.desc])
    @pytest.mark.parametrize("ids", [None, [str(uuid.uuid4()), str(uuid.uuid4())]])
    def test_should_get_all_jobs(
        self,
        requests_mock: req_mock.Mocker,
        process_id: list[str] | None,
        workspace_id: str | None,
        status: list[processing.JobStatus] | None,
        min_duration: int | None,
        max_duration: int | None,
        sort_by: utils.SortingField | None,
        ids: list[str] | None,
    ):
        query_params: dict[str, Any] = {}
        if process_id:
            query_params["processId"] = ",".join(process_id)
        if workspace_id:
            query_params["workspaceId"] = workspace_id
        if status:
            query_params["status"] = ",".join(entry.value for entry in status)
        if min_duration:
            query_params["minDuration"] = min_duration
        if max_duration:
            query_params["maxDuration"] = max_duration
        if sort_by:
            query_params["sort"] = str(sort_by)
        if ids:
            query_params["ids"] = ",".join(ids)

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
                    ids=ids,
                )
            )
            == [JOB] * 5
        )
