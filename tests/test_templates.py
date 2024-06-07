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
