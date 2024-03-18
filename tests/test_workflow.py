import pytest

from up42.job import Job
from up42.jobcollection import JobCollection
from up42.workflow import Workflow

from .fixtures.fixtures_globals import API_HOST, JOB_ID, JSON_WORKFLOW_TASKS


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
    full_workflow_tasks_dict = workflow_mock._construct_full_workflow_tasks_dict(input_tasks=input_tasks)
    assert isinstance(full_workflow_tasks_dict, list)
    assert full_workflow_tasks_dict[0]["name"] == "esa-s2-l2a-gtiff-visual:1"
    assert full_workflow_tasks_dict[0]["parentName"] is None
    assert full_workflow_tasks_dict[1]["name"] == "tiling:1"
    assert full_workflow_tasks_dict[1]["parentName"] == "esa-s2-l2a-gtiff-visual:1"
    assert full_workflow_tasks_dict[1]["blockId"] == "4ed70368-d4e1-4462-bef6-14e768049471"


def test_get_parameter_info(workflow_mock):
    parameter_info = workflow_mock.get_parameters_info()
    assert isinstance(parameter_info, dict)
    assert {"tiling:1", "esa-s2-l2a-gtiff-visual:1"} <= set(parameter_info.keys())
    assert {"nodata", "tile_width"} <= set(parameter_info["tiling:1"].keys())


def test_get_default_parameters(workflow_mock):
    default_parameters = workflow_mock._get_default_parameters()

    assert isinstance(default_parameters, dict)
    assert {"tiling:1", "esa-s2-l2a-gtiff-visual:1"} <= set(default_parameters.keys())
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


def test_get_jobs(workflow_mock, requests_mock):
    url_job_info = f"{API_HOST}/projects/{workflow_mock.project_id}/jobs/{JOB_ID}"
    requests_mock.get(
        url=url_job_info,
        json={"data": {"xyz": 789, "mode": "DEFAULT"}, "error": {}},
    )

    jobcollection = workflow_mock.get_jobs()
    assert isinstance(jobcollection, JobCollection)
    assert isinstance(jobcollection.jobs[0], Job)
    assert jobcollection.jobs[0].job_id == JOB_ID
    assert len(jobcollection.jobs) == 1  # Filters out the job that is not associated with the workflow object


def test_delete(workflow_mock, requests_mock):
    delete_url = f"{API_HOST}/projects/{workflow_mock.project_id}/workflows/{workflow_mock.workflow_id}"
    requests_mock.delete(url=delete_url)

    workflow_mock.delete()
