import dataclasses
import datetime
import random
import uuid
from typing import Optional
from unittest import mock

import pystac
import pytest
import requests
import requests_mock as req_mock

from tests import constants, helpers
from up42 import processing
from up42 import processing_templates as templates

PROCESS_ID = "process-id"
TITLE = "title"
ITEM_URL = "https://item-url"
SECOND_ITEM_URL = "https://second-item-url"
COST = processing.Cost(strategy="discount", credits=-1)
item = mock.MagicMock(spec=pystac.Item)
second_item = mock.MagicMock(spec=pystac.Item)
item.get_self_href.return_value = ITEM_URL
second_item.get_self_href.return_value = SECOND_ITEM_URL
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
COLLECTION_ID = str(uuid.uuid4())
COLLECTION_URL = f"https://collections/{COLLECTION_ID}"
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


@pytest.fixture
def template_post_init():
    def initialize(self):
        self.cost = COST

    with mock.patch.object(templates.JobTemplate, "__post_init__", initialize):
        yield


@pytest.fixture
def process_found_and_eula_accepted(requests_mock: req_mock.Mocker):
    requests_mock.get(PROCESS_URL, json=PROCESS_SUMMARY)
    requests_mock.get(EULA_URL, json={"isAccepted": True})


@pytest.mark.usefixtures("template_post_init")
class TestParameterlessTemplates:
    @pytest.mark.parametrize(
        "template_class",
        [
            templates.DetectionBuildingsSpacept,
            templates.DetectionTreesSpacept,
            templates.DetectionShadowsSpacept,
            templates.DetectionShipsAirbus,
            templates.DetectionStorageTanksAirbus,
            templates.DetectionWindTurbinesAirbus,
            templates.DetectionCarsOI,
            templates.DetectionAircraftOI,
            templates.DetectionTrucksOI,
            templates.UpsamplingNS,
            templates.UpsamplingNSSentinel,
            templates.TrueColorConversion,
        ],
    )
    def test_should_construct_single_item_job_templates(self, template_class):
        template = template_class(title=TITLE, item=item, workspace_id=constants.WORKSPACE_ID)
        assert template.is_valid and template.cost == COST
        assert template.inputs == {"title": TITLE, "item": ITEM_URL}


@pytest.mark.usefixtures("template_post_init")
class TestPansharpening:
    @pytest.mark.parametrize("grey_weight", [templates.GreyWeight(band="red", weight=random.random()), None])
    def test_should_construct_template(self, grey_weight: Optional[templates.GreyWeight]):
        template = templates.Pansharpening(
            title=TITLE,
            item=item,
            grey_weights=[grey_weight] if grey_weight else None,
            workspace_id=constants.WORKSPACE_ID,
        )
        grey_weights = (
            {"greyWeights": [{"band": grey_weight.band, "weight": grey_weight.weight}]} if grey_weight else {}
        )
        assert template.is_valid and template.cost == COST
        assert template.inputs == {"title": TITLE, "item": ITEM_URL, **grey_weights}


@pytest.mark.usefixtures("template_post_init")
class TestSimularityProcesses:
    def test_should_construct_coregistration_template(self):
        template = templates.CoregistrationSimularity(
            title=TITLE,
            source_item=item,
            reference_item=second_item,
            workspace_id=constants.WORKSPACE_ID,
        )
        assert template.is_valid and template.cost == COST
        assert template.inputs == {
            "title": TITLE,
            "sourceItem": ITEM_URL,
            "referenceItem": SECOND_ITEM_URL,
        }

    def test_should_construct_detection_change_template(self):
        template = templates.DetectionChangeSimularity(
            title=TITLE,
            source_item=item,
            reference_item=second_item,
            workspace_id=constants.WORKSPACE_ID,
            sensitivity=5,
        )
        assert template.is_valid and template.cost == COST
        assert template.inputs == {
            "title": TITLE,
            "sourceItem": ITEM_URL,
            "referenceItem": SECOND_ITEM_URL,
            "sensitivity": 5,
        }


@dataclasses.dataclass
class SampleMultiItemJobTemplate(templates.MultiItemJobTemplate):
    process_id = PROCESS_ID


class TestMultiItemJobTemplate:
    @pytest.mark.usefixtures("process_found_and_eula_accepted")
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


@dataclasses.dataclass
class SampleSingleItemJobTemplate(templates.SingleItemJobTemplate):
    process_id = PROCESS_ID


class TestSingleItemJobTemplate:
    @pytest.mark.usefixtures("process_found_and_eula_accepted")
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
class SampleJobTemplate(templates.JobTemplate):
    title: str
    process_id = PROCESS_ID
    workspace_id = constants.WORKSPACE_ID

    @property
    def inputs(self) -> dict:
        return {"title": self.title}


class TestJobTemplate:
    def test_should_fail_to_construct_if_getting_process_fails(self, requests_mock: req_mock.Mocker):
        error_code = random.choice([x for x in range(400, 599) if x != 404])

        requests_mock.get(
            PROCESS_URL,
            status_code=error_code,
        )
        with pytest.raises(requests.exceptions.HTTPError) as error:
            _ = SampleJobTemplate(title=TITLE)
        assert error.value.response.status_code == error_code

    def test_should_be_invalid_if_process_not_found(self, requests_mock: req_mock.Mocker):
        error = processing.ValidationError(
            name="ProcessNotFound",
            message=f"The process {PROCESS_ID} does not exist.",
        )
        requests_mock.get(PROCESS_URL, status_code=404)
        template = SampleJobTemplate(title=TITLE)
        assert not template.is_valid
        assert template.errors == {error}

    def test_should_be_invalid_if_eula_not_accepted(self, requests_mock: req_mock.Mocker):
        error = processing.ValidationError(
            name="EulaNotAccepted",
            message=f"EULA for the process {PROCESS_ID} not accepted.",
        )
        requests_mock.get(PROCESS_URL, json=PROCESS_SUMMARY)
        requests_mock.get(EULA_URL, json={"isAccepted": False})
        template = SampleJobTemplate(title=TITLE)
        assert not template.is_valid
        assert template.errors == {error}

    @pytest.mark.usefixtures("process_found_and_eula_accepted")
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

    @pytest.mark.usefixtures("process_found_and_eula_accepted")
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

    @pytest.mark.usefixtures("process_found_and_eula_accepted")
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

    @pytest.mark.usefixtures("process_found_and_eula_accepted")
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

    @pytest.mark.parametrize(
        "cost",
        [
            processing.Cost(strategy="none", credits=1),
            processing.Cost(strategy="area", credits=1, size=5, unit="SKM"),
        ],
    )
    @pytest.mark.usefixtures("process_found_and_eula_accepted")
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

    @pytest.mark.usefixtures("process_found_and_eula_accepted")
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
