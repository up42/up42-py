from typing import Any, Dict, List

import pytest

from up42 import estimation

from .fixtures import fixtures_globals as constants


def test_estimate_price(requests_mock, estimation_mock):
    input_tasks = [
        {
            "name": "esa-s2-l2a-gtiff-visual:1",
            "parentName": None,
            "blockId": "c4cb8913-2ef3-4e82-a426-65ea8faacd9a",
            "blockVersionTag": "1.0.1",
        },
        {
            "name": "tiling:1",
            "parentName": "esa-s2-l2a-gtiff-visual:1",
            "blockId": "3e146dd6-2b67-4d6e-a422-bb3d973e32ff",
            "blockVersionTag": "2.2.3",
        },
    ]

    url_workflow_estimation = f"{constants.API_HOST}/projects/{constants.PROJECT_ID}/estimate/job"
    requests_mock.post(url=url_workflow_estimation, json=constants.JSON_WORKFLOW_ESTIMATION)
    _ = estimation_mock.estimate()
    assert list(estimation_mock.payload.keys()) == ["tasks", "inputs"]
    assert estimation_mock.payload["tasks"] == input_tasks


@pytest.mark.live
def test_estimate_price_live(auth_live, project_id_live):
    input_parameters = {
        "esa-s2-l2a-gtiff-visual:1": {
            "time": "2018-01-01T00:00:00+00:00/2020-12-31T23:59:59+00:00",
            "limit": 1,
            "bbox": [13.33409, 52.474922, 13.38547, 52.500398],
        },
        "tiling:1": {"tile_width": 768, "tile_height": 768},
    }
    input_tasks: List[Dict[str, Any]] = [
        {
            "name": "esa-s2-l2a-gtiff-visual:1",
            "parentName": None,
            "blockId": "c4cb8913-2ef3-4e82-a426-65ea8faacd9a",
            "blockVersionTag": "1.2.1",
        },
        {
            "name": "tiling:1",
            "parentName": "esa-s2-l2a-gtiff-visual:1",
            "blockId": "3e146dd6-2b67-4d6e-a422-bb3d973e32ff",
            "blockVersionTag": "2.2.3",
        },
    ]
    estimation_result = estimation.Estimation(
        auth=auth_live,
        project_id=project_id_live,
        input_parameters=input_parameters,
        input_tasks=input_tasks,
    ).estimate()
    assert isinstance(estimation_result, dict)
    assert len(estimation_result) == 2
    assert list(estimation_result.keys()) == ["esa-s2-l2a-gtiff-visual:1", "tiling:1"]
    assert list(estimation_result["esa-s2-l2a-gtiff-visual:1"].keys()) == [
        "blockConsumption",
        "machineConsumption",
    ]
