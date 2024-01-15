from pathlib import Path

import pytest
from shapely.geometry import box

# pylint: disable=unused-import,wrong-import-order
from .context import Job, JobCollection, Workflow
from .fixtures import (
    ASSET_ID,
    JOB_ID,
    JOB_NAME,
    JOBTASK_ID,
    JSON_WORKFLOW_ESTIMATION,
    JSON_WORKFLOW_TASKS,
    PROJECT_ID,
    asset_mock,
    auth_account_live,
    auth_account_mock,
    auth_live,
    auth_mock,
    auth_project_live,
    auth_project_mock,
    job_mock,
    jobcollection_single_mock,
    jobtask_mock,
    password_test_live,
    project_api_key_live,
    project_id_live,
    project_mock,
    project_mock_max_concurrent_jobs,
    username_test_live,
    workflow_mock,
    workflow_mock_empty,
)
from .fixtures.fixtures_globals import API_HOST


def test_workflow_info(workflow_mock):
    del workflow_mock._info

    assert isinstance(workflow_mock, Workflow)
    assert workflow_mock.info["xyz"] == 789
    assert workflow_mock._info["xyz"] == 789


def test_get_workflow_tasks(workflow_mock):
    tasks = workflow_mock.get_workflow_tasks(basic=False)
    assert len(tasks) == 2
    assert tasks[0] == JSON_WORKFLOW_TASKS["data"][0]


def test_get_workflow_tasks_basic(workflow_mock):
    tasks = workflow_mock.get_workflow_tasks(basic=True)
    assert len(tasks) == 2
    assert tasks["esa-s2-l2a-gtiff-visual:1"] == "1.0.1"
    assert tasks["tiling:1"] == "2.2.3"


def test_get_compatible_blocks(workflow_mock):
    compatible_blocks = workflow_mock.get_compatible_blocks()
    assert isinstance(compatible_blocks, dict)
    assert "aaa" in list(compatible_blocks.keys())


def test_get_compatible_blocks_empty_workflow_returns_data_blocks(workflow_mock_empty):
    compatible_blocks = workflow_mock_empty.get_compatible_blocks()
    assert isinstance(compatible_blocks, dict)
    assert len(compatible_blocks) == 1
    assert "esa-s2-l2a-gtiff-visual" in list(compatible_blocks.keys())


def test_construct_full_workflow_tasks_dict_unknown_block_raises(workflow_mock):
    input_tasks = ["some_block"]
    with pytest.raises(ValueError):
        workflow_mock._construct_full_workflow_tasks_dict(input_tasks=input_tasks)


@pytest.mark.parametrize(
    "input_tasks",
    [
        [
            "c4cb8913-2ef3-4e82-a426-65ea8faacd9a",
            "4ed70368-d4e1-4462-bef6-14e768049471",
        ],
        ["esa-s2-l2a-gtiff-visual", "tiling"],
        [
            "Sentinel-2 L2A Visual (GeoTIFF)",
            "Raster Tiling",
        ],
        [
            "c4cb8913-2ef3-4e82-a426-65ea8faacd9a",
            "tiling",
        ],
        [
            "Sentinel-2 L2A Visual (GeoTIFF)",
            "4ed70368-d4e1-4462-bef6-14e768049471",
        ],
    ],
)
def test_construct_full_workflow_tasks_dict(workflow_mock, input_tasks):
    full_workflow_tasks_dict = workflow_mock._construct_full_workflow_tasks_dict(
        input_tasks=input_tasks
    )
    assert isinstance(full_workflow_tasks_dict, list)
    assert full_workflow_tasks_dict[0]["name"] == "esa-s2-l2a-gtiff-visual:1"
    assert full_workflow_tasks_dict[0]["parentName"] is None
    assert full_workflow_tasks_dict[1]["name"] == "tiling:1"
    assert full_workflow_tasks_dict[1]["parentName"] == "esa-s2-l2a-gtiff-visual:1"
    assert (
        full_workflow_tasks_dict[1]["blockId"] == "4ed70368-d4e1-4462-bef6-14e768049471"
    )


def test_get_parameter_info(workflow_mock):
    parameter_info = workflow_mock.get_parameters_info()
    assert isinstance(parameter_info, dict)
    assert all(
        x in list(parameter_info.keys())
        for x in ["tiling:1", "esa-s2-l2a-gtiff-visual:1"]
    )
    assert all(
        x in list(parameter_info["tiling:1"].keys()) for x in ["nodata", "tile_width"]
    )


def test_get_default_parameters(workflow_mock):
    default_parameters = workflow_mock._get_default_parameters()

    assert isinstance(default_parameters, dict)
    assert all(
        x in list(default_parameters.keys())
        for x in ["tiling:1", "esa-s2-l2a-gtiff-visual:1"]
    )
    assert default_parameters["tiling:1"] == {
        "nodata": None,
        "tile_width": 768,
        "required_but_no_default": None,
    }
    assert "not_required_no_default" not in default_parameters["tiling:1"]

    assert default_parameters["esa-s2-l2a-gtiff-visual:1"] == {
        "ids": None,
        "bbox": None,
        "time": "2018-01-01T00:00:00+00:00/2020-12-31T23:59:59+00:00",
    }
    assert "intersects" not in default_parameters["esa-s2-l2a-gtiff-visual:1"]


def test_estimate_jobs(workflow_mock, requests_mock):
    input_parameters = {
        "esa-s2-l2a-gtiff-visual:1": {
            "time": "2018-01-01T00:00:00+00:00/2020-12-31T23:59:59+00:00",
            "limit": 1,
            "bbox": [13.33409, 52.474922, 13.38547, 52.500398],
        },
        "tiling:1": {"tile_width": 768},
    }
    # get_workflow_tasks
    url_workflow_tasks = (
        f"{API_HOST}/projects/{workflow_mock.project_id}/workflows/"
        f"{workflow_mock.workflow_id}/tasks"
    )
    url_workflow_estimation = f"{API_HOST}/projects/{PROJECT_ID}/estimate/job"
    requests_mock.get(url=url_workflow_tasks, json=JSON_WORKFLOW_TASKS)
    requests_mock.post(url=url_workflow_estimation, json=JSON_WORKFLOW_ESTIMATION)

    estimation = workflow_mock.estimate_job(input_parameters)
    assert estimation == JSON_WORKFLOW_ESTIMATION["data"]


def test_get_jobs(workflow_mock, requests_mock):
    url_job_info = f"{API_HOST}/projects/" f"{workflow_mock.project_id}/jobs/{JOB_ID}"
    requests_mock.get(
        url=url_job_info,
        json={"data": {"xyz": 789, "mode": "DEFAULT"}, "error": {}},
    )

    jobcollection = workflow_mock.get_jobs()
    assert isinstance(jobcollection, JobCollection)
    assert isinstance(jobcollection.jobs[0], Job)
    assert jobcollection.jobs[0].job_id == JOB_ID
    assert (
        len(jobcollection.jobs) == 1
    )  # Filters out the job that is not associated with the workflow object


@pytest.mark.skip(
    reason="too many jobs in test project, triggers too many job info requests."
)
@pytest.mark.live
def test_get_jobs_live(workflow_live):
    jobcollection = workflow_live.get_jobs()
    assert isinstance(jobcollection, list)
    assert isinstance(jobcollection.jobs[0], Job)
    assert all(
        j._info["workflowId"] == workflow_live.workflow_id for j in jobcollection.jobs
    )


def test_delete(workflow_mock, requests_mock):
    delete_url = (
        f"{API_HOST}/projects/{workflow_mock.project_id}/workflows/"
        f"{workflow_mock.workflow_id}"
    )
    requests_mock.delete(url=delete_url)

    workflow_mock.delete()
