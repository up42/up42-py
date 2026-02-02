import dataclasses
import datetime
import random
import urllib.parse
import uuid
from typing import Any
from unittest import mock

import pytest
import requests
import requests_mock as req_mock

from tests import constants
from tests import test_processing_constants as tpc
from up42 import processing, utils


def as_java_timestamp(value: datetime.datetime):
    return value.isoformat(timespec="milliseconds") + tpc.MICROSECONDS


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
        requests_mock.get(url=tpc.JOB_URL, json=tpc.JOB_METADATA)
        assert processing.Job.get(tpc.JOB_ID) == tpc.JOB

    def test_should_get_collection(self):
        stac_client = tpc.JOB.stac_client = mock.MagicMock()
        assert tpc.JOB.collection == stac_client.get_collection.return_value
        stac_client.get_collection.assert_called_with(tpc.COLLECTION_ID)

    def test_should_get_no_collection_if_collection_url_is_missing(self):
        job = dataclasses.replace(tpc.JOB, collection_url=None)
        assert not job.collection

    @pytest.mark.parametrize("status", processing.TERMINAL_STATUSES)
    def test_should_track_until_job_finishes(self, requests_mock: req_mock.Mocker, status: processing.JobStatus):
        updated = tpc.NOW + datetime.timedelta(minutes=4)
        started = tpc.NOW + datetime.timedelta(minutes=2)
        finished = tpc.NOW + datetime.timedelta(minutes=3)
        requests_mock.get(
            url=tpc.JOB_URL,
            response_list=[
                {
                    "json": {
                        **tpc.JOB_METADATA,
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
                        **tpc.JOB_METADATA,
                        "updated": as_java_timestamp(updated),
                        "started": as_java_timestamp(started),
                        "finished": as_java_timestamp(finished),
                        "status": status.value,
                    }
                },
            ],
        )
        job = dataclasses.replace(tpc.JOB)
        job.track(wait=1, retries=2)
        assert job == dataclasses.replace(tpc.JOB, finished=finished, started=started, updated=updated, status=status)

    def test_fails_to_track_if_job_retrieval_fails(self, requests_mock: req_mock.Mocker):
        requests_mock.get(
            url=tpc.JOB_URL,
            status_code=500,
        )
        job = dataclasses.replace(tpc.JOB)
        with pytest.raises(requests.exceptions.HTTPError):
            job.track(wait=1, retries=10)
        assert requests_mock.call_count == 1

    def test_fails_to_track_if_job_finishes_after_attempts_finished(self, requests_mock: req_mock.Mocker):
        requests_mock.get(
            url=tpc.JOB_URL,
            json=tpc.JOB_METADATA,
        )
        job = dataclasses.replace(tpc.JOB)
        with pytest.raises(processing.UnfinishedJob):
            job.track(wait=1, retries=2)
        assert requests_mock.call_count == 2

    @pytest.mark.parametrize("process_id", [None, [tpc.PROCESS_ID, "another-id"]])
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
            url=tpc.JOBS_URL + (query and f"?{query}"),
            json={
                "jobs": [tpc.JOB_METADATA] * 3,
                "links": [{"rel": "next", "href": next_page_url}],
            },
        )
        requests_mock.get(
            url=f"{constants.API_HOST}{next_page_url}",
            json={
                "jobs": [tpc.JOB_METADATA] * 2,
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
            == [tpc.JOB] * 5
        )
