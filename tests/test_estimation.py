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
