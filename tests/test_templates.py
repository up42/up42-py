import random
from typing import Optional
from unittest import mock

import pystac
import pytest

from tests.fixtures import fixtures_globals as constants
from up42 import processing, templates

TITLE = "title"
ITEM_URL = "https://item-url"
COST = processing.Cost(strategy="discount", credits=-1)
item = mock.MagicMock(spec=pystac.Item)
item.get_self_href.return_value = ITEM_URL


@pytest.fixture(autouse=True)
def template_post_init():
    def initialize(self):
        self.cost = COST

    with mock.patch.object(processing.JobTemplate, "__post_init__", initialize):
        yield


class TestParameterlessTemplates:
    @pytest.mark.parametrize(
        "template_class",
        [
            templates.SpaceptBuildingsDetection,
            templates.SpaceptTreesDetection,
            templates.SpaceptTreeHeightsDetection,
            templates.SpaceptShadowsDetection,
            templates.AirbusShipsDetection,
            templates.AirbusStorageTanksDetection,
            templates.AirbusWindTurbinesDetection,
            templates.OrbitalInsightCarsDetection,
            templates.OrbitalInsightAircraftDetection,
            templates.OrbitalInsightTrucksDetection,
        ],
    )
    def test_should_construct_single_item_job_templates(self, template_class):
        template = template_class(title=TITLE, item=item, workspace_id=constants.WORKSPACE_ID)
        assert template.is_valid and template.cost == COST
        assert template.inputs == {"title": TITLE, "item": ITEM_URL}

    @pytest.mark.parametrize(
        "template_class",
        [
            templates.SpaceptChangeDetection,
            templates.HypervergePleiadesChangeDetection,
            templates.HypervergeSpotChangeDetection,
        ],
    )
    def test_should_construct_multi_item_template(self, template_class):
        template = template_class(title=TITLE, items=[item], workspace_id=constants.WORKSPACE_ID)
        assert template.is_valid and template.cost == COST
        assert template.inputs == {"title": TITLE, "items": [ITEM_URL]}


class TestSpaceptAugmentation:
    def test_should_construct_template(self):
        denoising_factor = random.randint(0, 100)
        colour_denoising_factor = random.randint(0, 100)
        template = templates.SpaceptAugmentation(
            title=TITLE,
            item=item,
            denoising_factor=denoising_factor,
            colour_denoising_factor=colour_denoising_factor,
            workspace_id=constants.WORKSPACE_ID,
        )
        assert template.is_valid and template.cost == COST
        assert template.inputs == {
            "title": TITLE,
            "item": ITEM_URL,
            "denoising_factor": denoising_factor,
            "colour_denoising_factor": colour_denoising_factor,
        }


class TestNSUpsampling:
    def test_should_construct_template(self):
        ned, rgb = random.choices([True, False], k=2)
        template = templates.NSUpsamling(
            title=TITLE,
            item=item,
            ned=ned,
            rgb=rgb,
            workspace_id=constants.WORKSPACE_ID,
        )
        assert template.is_valid and template.cost == COST
        assert template.inputs == {
            "title": TITLE,
            "item": ITEM_URL,
            "NED": ned,
            "RGB": rgb,
        }


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
