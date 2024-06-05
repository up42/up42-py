import dataclasses
from unittest import mock

import pystac
import pytest
import requests
import requests_mock as req_mock

from up42 import ogc_job

from .fixtures import fixtures_globals as constants

JOB_ID = "21e447c4-56e5-4f29-bb5a-1358e756515a"
GET_JOB_URL = f"{constants.API_HOST}/v2/processing/jobs/{JOB_ID}"
RESULT_COLLECTION_ID = "d8ec4a66-18a2-40bb-b73d-86ff9540de51"
RESULT_ITEM_ID = "5cd3a187-26ee-4764-ad21-b2927610caca"
HOST_RESULTS = "https://api.up42.dev"
COLLECTION_DICT = {
    "type": "Collection",
    "stac_version": "1.0.0",
    "id": RESULT_COLLECTION_ID,
    "description": "A collection of sample items",
    "license": "proprietary",
    "extent": {
        "spatial": {"bbox": [[-180, -90, 180, 90]]},
        "temporal": {"interval": [["2023-01-01T00:00:00Z", None]]},
    },
    "links": [],
}
RESULT_COLLECTION = pystac.Collection.from_dict(COLLECTION_DICT)
JOB_SUCCESS_RESPONSE = {
    "processID": "pansharpening",
    "jobID": JOB_ID,
    "accountID": "8710edff-5fd8-4638-b75d-aa1110448370",
    "workspaceID": "8710edff-5fd8-4638-b75d-aa1110448370",
    "definition": {
        "inputs": {
            "item": "{HOST_RESULTS}/v2/assets/stac/collections/" "{RESULT_COLLECTION_ID}/items/{RESULT_ITEM_ID}",
            "title": "Test xbxw",
        }
    },
    "results": {"collection": f"{HOST_RESULTS}" "/v2/assets/stac/collections/{RESULT_COLLECTION_ID}"},
    "status": "captured",
    "type": "process",
    "created": "2024-06-05T13:12:48.124568Z",
    "updated": "2024-06-05T13:13:27.426795Z",
    "started": "2024-06-05T13:12:56.542773Z",
    "finished": "2024-06-05T13:13:27.320528Z",
    "creditConsumption": {
        "credits": 1,
        "holdID": "dfc30f18-c98c-42a7-83a9-3025e56cba4b",
        "consumptionID": "c1e96136-91ed-4d1d-8dd7-0ad448d93cfc",
    },
}


@pytest.fixture(autouse=True)
def workspace():
    with mock.patch("up42.base.workspace") as workspace_mock:
        session = requests.Session()
        session.hooks = {"response": lambda response, *args, **kwargs: response.raise_for_status()}
        workspace_mock.auth.session = session
        yield


@dataclasses.dataclass
class SampleJob(ogc_job.BaseJob):
    id: str


class TestJobBase:
    def test_should_construct(self, requests_mock: req_mock.Mocker):
        requests_mock.get(url=GET_JOB_URL, json=JOB_SUCCESS_RESPONSE)
        test_job = SampleJob(JOB_ID)
        assert test_job.status == ogc_job.JobStatuses.CAPTURED
