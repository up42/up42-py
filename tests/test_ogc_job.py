import dataclasses
import datetime
from unittest import mock

import pystac
import pystac_client
import pytest
import requests
import requests_mock as req_mock

from up42 import ogc_job

from .fixtures import fixtures_globals as constants

JOB_ID = "21e447c4-56e5-4f29-bb5a-1358e756515a"
GET_JOB_URL = f"{constants.API_HOST}/v2/processing/jobs/{JOB_ID}"
RESULT_COLLECTION_ID = "d8ec4a66-18a2-40bb-b73d-86ff9540de51"
RESULT_ITEM_ID = "5cd3a187-26ee-4764-ad21-b2927610caca"
RESULT_CREDITS = 1
RESULT_JOB_WORKSPACE_ID = "8710edff-5fd8-4638-b75d-aa1110448370"
RESULT_ACCOUNT_ID = "04eb7366-f2a4-401f-953d-517aea4353d1"
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
    "accountID": RESULT_ACCOUNT_ID,
    "workspaceID": RESULT_JOB_WORKSPACE_ID,
    "definition": {
        "inputs": {
            "item": f"{HOST_RESULTS}/v2/assets/stac/collections/" f"{RESULT_COLLECTION_ID}/items/{RESULT_ITEM_ID}",
            "title": "Test xbxw",
        }
    },
    "results": {"collection": f"{HOST_RESULTS}" f"/v2/assets/stac/collections/{RESULT_COLLECTION_ID}"},
    "status": "captured",
    "type": "process",
    "created": "2024-06-05T13:12:48.124568Z",
    "updated": "2024-06-05T13:13:27.426795Z",
    "started": "2024-06-05T13:12:56.542773Z",
    "finished": "2024-06-05T13:13:27.320528Z",
    "creditConsumption": {
        "credits": RESULT_CREDITS,
        "holdID": "dfc30f18-c98c-42a7-83a9-3025e56cba4b",
        "consumptionID": "c1e96136-91ed-4d1d-8dd7-0ad448d93cfc",
    },
}

JOB_FAILED_RESPONSE = {
    "processID": "pansharpening",
    "type": "process",
    "jobID": JOB_ID,
    "accountID": RESULT_ACCOUNT_ID,
    "workspaceID": RESULT_JOB_WORKSPACE_ID,
    "definition": {
        "inputs": {
            "item": f"{HOST_RESULTS}/v2/assets/stac/collections/" f"{RESULT_COLLECTION_ID}/items/{RESULT_ITEM_ID}",
            "greyWeights": [{"blue": 0.2}, {"green": 0.34}, {"red": 0.23}],
        }
    },
    "results": {
        "errors": [
            {
                "name": "GreyWeightBandsNotUnique",
                "message": "Applied band grey weights are not unique.",
            }
        ]
    },
    "status": "invalid",
    "created": "2023-11-19T09:12:28Z",
    "started": "2023-11-19T09:12:45Z",
    "finished": "2023-11-19T09:18:26Z",
    "updated": "2023-11-19T09:18:26Z",
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
    @pytest.fixture
    def test_success_job(self, requests_mock: req_mock.Mocker):
        requests_mock.get(url=GET_JOB_URL, json=JOB_SUCCESS_RESPONSE)
        return SampleJob(JOB_ID)

    @pytest.fixture
    def test_job_with_error(self, requests_mock: req_mock.Mocker):
        requests_mock.get(url=GET_JOB_URL, json=JOB_FAILED_RESPONSE)
        return SampleJob(JOB_ID)

    def test_should_provide_correct_status(self, test_success_job):
        assert test_success_job.status == ogc_job.JobStatuses.CAPTURED

    def test_should_provide_credit_consumption(self, test_success_job):
        credits_consumed = test_success_job.credit_consumption
        assert isinstance(credits_consumed, ogc_job.JobCreditConsumption)
        assert credits_consumed.credits == RESULT_CREDITS

    def test_fail_provide_credit_consumption(self, test_job_with_error):
        with pytest.raises(ogc_job.JobResultError):
            _ = test_job_with_error.credit_consumption

    def test_should_provide_errors_failed_job(self, test_job_with_error):
        assert len(test_job_with_error.errors) > 0
        for error in test_job_with_error.errors:
            assert isinstance(error, ogc_job.JobError)

    def test_should_have_empty_errors_success_job(self, test_success_job):
        assert len(test_success_job.errors) == 0

    def test_should_provide_correct_datetime_properties(self, test_success_job):
        assert isinstance(test_success_job.created, datetime.datetime)
        assert isinstance(test_success_job.started, datetime.datetime)
        assert isinstance(test_success_job.finished, datetime.datetime)
        assert isinstance(test_success_job.updated, datetime.datetime)

    def test_should_provide_account_workspace_ids(self, test_success_job):
        assert test_success_job.account_id == RESULT_ACCOUNT_ID
        assert test_success_job.job_workspace_id == RESULT_JOB_WORKSPACE_ID

    def test_should_provide_correct_type_process(self, test_success_job):
        assert isinstance(test_success_job.type, str)
        assert isinstance(test_success_job.process_id, str)

    @mock.patch("up42.ogc_job.BaseJob._job_metadata", new_callable=mock.PropertyMock)
    @mock.patch("up42.ogc_job.BaseJob._pystac_client", new_callable=mock.PropertyMock)
    def test_collection_success(self, mock_pystac_client, mock_job_metadata, test_success_job):
        mock_job_metadata.return_value = JOB_SUCCESS_RESPONSE
        mock_collection = pystac.Collection.from_dict(COLLECTION_DICT)
        mock_pystac_client.return_value.get_collection.return_value = mock_collection
        result_collection = test_success_job.collection
        assert result_collection == mock_collection
        mock_pystac_client.return_value.get_collection.assert_called_once_with(collection_id=RESULT_COLLECTION_ID)

    @mock.patch("up42.ogc_job.BaseJob._job_metadata", new_callable=mock.PropertyMock)
    @mock.patch("up42.ogc_job.BaseJob._pystac_client", new_callable=mock.PropertyMock)
    def test_collection_invalid_stac(self, mock_pystac_client, mock_job_metadata):
        mock_job_metadata.return_value = {"results": {"collection": "invalid_url"}}
        mock_pystac_client.return_value.get_collection.return_value = mock.Mock(spec=pystac_client)
        mock_pystac_client.get_collection.return_value = mock.Mock(spec=pystac_client)
        mock_pystac_client.return_value.get_collection.side_effect = Exception("Invalid STAC collection")
        mock_pystac_client.return_value.get_collection.side_effect = Exception("Invalid STAC collection")
        job = SampleJob(RESULT_COLLECTION_ID)
        with pytest.raises(ogc_job.JobResultError):
            _ = job.collection

    def test_collection_no_result(self, test_job_with_error):
        with pytest.raises(ogc_job.JobResultError):
            _ = test_job_with_error.collection
