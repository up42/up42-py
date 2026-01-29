import dataclasses
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

TITLE = "title"
ITEM_URL = "https://item-url"
SECOND_ITEM_URL = "https://second-item-url"
COST = processing.Cost(strategy="discount", credits=-1)
item = mock.MagicMock(spec=pystac.Item)
second_item = mock.MagicMock(spec=pystac.Item)
item.get_self_href.return_value = ITEM_URL
second_item.get_self_href.return_value = SECOND_ITEM_URL
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
def template_post_init():
    def initialize(self):
        self.cost = COST

    with mock.patch.object(templates.JobTemplate, "__post_init__", initialize):
        yield

@pytest.fixture
def process_found_and_eula_accepted(requests_mock: req_mock.Mocker):
    requests_mock.get(PROCESS_URL, json=PROCESS_SUMMARY)
    requests_mock.get(EULA_URL, json={"isAccepted": True})

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
