# pylint: disable=unused-import,wrong-import-order
from .fixtures import (
    auth_mock,
    estimation_mock,
    estimation_live,
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
    _ = estimation_mock.estimate_price()
    assert list(estimation_mock.payload.keys()) == ["tasks", "inputs"]
    assert estimation_mock.payload["tasks"] == input_tasks
