import pytest

# pylint: disable=unused-import,wrong-import-order
from .context import Estimation
from .fixtures import (
    auth_mock,
    auth_live,
    estimation_mock,
    JSON_WORKFLOW_ESTIMATION,
)


def test_estimate_price(requests_mock, auth_mock, estimation_mock):
    input_tasks = [
        {
            "name": "sobloo-s2-l1c-aoiclipped:1",
            "parentName": None,
            "blockId": "3a381e6b-acb7-4cec-ae65-50798ce80e64",
            "blockVersionTag": "2.3.0",
        },
        {
            "name": "tiling:1",
            "parentName": "sobloo-s2-l1c-aoiclipped:1",
            "blockId": "3e146dd6-2b67-4d6e-a422-bb3d973e32ff",
            "blockVersionTag": "2.2.3",
        },
    ]

    url_workflow_estimation = f"{auth_mock._endpoint()}/estimate/job"
    requests_mock.post(url=url_workflow_estimation, json=JSON_WORKFLOW_ESTIMATION)
    _ = estimation_mock.estimate()
    assert list(estimation_mock.payload.keys()) == ["tasks", "inputs"]
    assert estimation_mock.payload["tasks"] == input_tasks


@pytest.mark.live
def test_estimate_price_live(auth_live):
    input_parameters = {
        "sobloo-s2-l1c-aoiclipped:1": {
            "time": "2018-01-01T00:00:00+00:00/2020-12-31T23:59:59+00:00",
            "limit": 1,
            "bbox": [13.33409, 52.474922, 13.38547, 52.500398],
        },
        "tiling:1": {"tile_width": 768},
    }

    input_tasks = [
        {
            "name": "sobloo-s2-l1c-aoiclipped:1",
            "parentName": None,
            "blockId": "3a381e6b-acb7-4cec-ae65-50798ce80e64",
            "blockVersionTag": "2.3.0",
        },
        {
            "name": "tiling:1",
            "parentName": "sobloo-s2-l1c-aoiclipped:1",
            "blockId": "3e146dd6-2b67-4d6e-a422-bb3d973e32ff",
            "blockVersionTag": "2.2.3",
        },
    ]
    estimation = Estimation(auth_live, input_parameters, input_tasks).estimate()
    assert isinstance(estimation, dict)
    assert len(estimation) == 2
    assert list(estimation.keys()) == ["sobloo-s2-l1c-aoiclipped:1", "tiling:1"]
    assert list(estimation["sobloo-s2-l1c-aoiclipped:1"].keys()) == [
        "blockConsumption",
        "machineConsumption",
    ]
