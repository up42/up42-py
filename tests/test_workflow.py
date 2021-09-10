from pathlib import Path
import json
import copy

import pytest
import shapely

# pylint: disable=unused-import,wrong-import-order
from .context import Workflow, Job, JobCollection, Asset
from .fixtures import (
    auth_mock,
    auth_live,
    workflow_mock_empty,
    workflow_mock,
    workflow_live,
    job_mock,
    jobcollection_single_mock,
    jobtask_mock,
    project_mock,
    project_mock_max_concurrent_jobs,
    asset_mock,
)
from .fixtures import (
    JOB_ID,
    JOB_NAME,
    JOBTASK_ID,
    JSON_WORKFLOW_TASKS,
    JSON_WORKFLOW_ESTIMATION,
)


def test_workflow_info(workflow_mock):
    del workflow_mock._info

    assert isinstance(workflow_mock, Workflow)
    assert workflow_mock.info["xyz"] == 789
    assert workflow_mock._info["xyz"] == 789


def test_get_workflow_tasks_normal_and_basic(workflow_mock):
    tasks = workflow_mock.get_workflow_tasks(basic=False)

    assert len(tasks) == 2
    assert tasks[0] == JSON_WORKFLOW_TASKS["data"][0]

    tasks = workflow_mock.get_workflow_tasks(basic=True)
    assert len(tasks) == 2
    assert tasks["esa-s2-l2a-gtiff-visual:1"] == "1.0.1"
    assert tasks["tiling:1"] == "2.2.3"


@pytest.mark.live
def test_get_workflow_tasks_live(workflow_live):
    workflow_tasks = workflow_live.get_workflow_tasks(basic=True)
    assert isinstance(workflow_tasks, dict)
    assert "esa-s2-l2a-gtiff-visual:1" in list(workflow_tasks.keys())


def test_get_compatible_blocks(workflow_mock):
    compatible_blocks = workflow_mock.get_compatible_blocks()
    assert isinstance(compatible_blocks, dict)
    assert "aaa" in list(compatible_blocks.keys())


@pytest.mark.live
def test_get_compatible_blocks_live(workflow_live):
    compatible_blocks = workflow_live.get_compatible_blocks()
    assert isinstance(compatible_blocks, dict)
    assert "tiling" in list(compatible_blocks.keys())


def test_get_compatible_blocks_empty_workflow_returns_data_blocks(workflow_mock_empty):
    compatible_blocks = workflow_mock_empty.get_compatible_blocks()
    assert isinstance(compatible_blocks, dict)
    assert len(compatible_blocks) == 1
    assert "esa-s2-l2a-gtiff-visual" in list(compatible_blocks.keys())


def test_construct_full_workflow_tasks_dict_unkwown_block_raises(workflow_mock):
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


def test_add_workflow_tasks_full(workflow_mock, requests_mock):
    input_tasks_full = [
        {
            "name": "esa-s2-l2a-gtiff-visual:1",
            "parentName": None,
            "blockId": "a2daaab4-196d-4226-a018-a810444dcad1",
        },
        {
            "name": "sharpening:1",
            "parentName": "esa-s2-l2a-gtiff-visual",
            "blockId": "4ed70368-d4e1-4462-bef6-14e768049471",
        },
    ]
    job_url = (
        f"{workflow_mock.auth._endpoint()}/projects/{workflow_mock.project_id}/workflows/"
        f"{workflow_mock.workflow_id}/tasks/"
    )
    requests_mock.post(url=job_url, status_code=200)

    workflow_mock.add_workflow_tasks(input_tasks_full)
    # TODO:caplog, capture logger


@pytest.mark.live
def test_add_workflow_tasks_simple_not_existing_block_id_raises_live(workflow_live):
    input_tasks_simple = ["12345"]
    with pytest.raises(Exception):
        workflow_live.add_workflow_tasks(input_tasks_simple)


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


@pytest.mark.live
def test_get_parameter_info_live(workflow_live):
    parameter_info = workflow_live.get_parameters_info()
    assert isinstance(parameter_info, dict)
    assert all(
        x in list(parameter_info.keys())
        for x in ["tiling:1", "esa-s2-l2a-gtiff-visual:1"]
    )
    assert all(
        x in list(parameter_info["tiling:1"].keys())
        for x in ["nodata", "tile_width", "match_extents"]
    )


def test_get_default_parameters(workflow_mock):
    default_parameters = workflow_mock._get_default_parameters()

    assert isinstance(default_parameters, dict)
    assert all(
        x in list(default_parameters.keys())
        for x in ["tiling:1", "esa-s2-l2a-gtiff-visual:1"]
    )
    assert default_parameters["tiling:1"] == {"nodata": "None", "tile_width": 768}
    assert default_parameters["esa-s2-l2a-gtiff-visual:1"] == {
        "ids": "None",
        "bbox": "None",
        "time": "2018-01-01T00:00:00+00:00/2020-12-31T23:59:59+00:00",
    }


def test_construct_parameters_scene_ids(workflow_mock):
    parameters = workflow_mock.construct_parameters(
        geometry=shapely.geometry.point.Point(1, 3),
        geometry_operation="bbox",
        scene_ids=["s2_123223"],
    )
    assert isinstance(parameters, dict)
    assert parameters == {
        "esa-s2-l2a-gtiff-visual:1": {
            "ids": ["s2_123223"],
            "bbox": [0.99999, 2.99999, 1.00001, 3.00001],
            "limit": 1,
        },
        "tiling:1": {"nodata": "None", "tile_width": 768},
    }


def test_construct_parameter_scene_ids_without_geometry(workflow_mock):
    parameters = workflow_mock.construct_parameters(
        scene_ids=["s2_123223"],
    )
    assert isinstance(parameters, dict)
    assert parameters == {
        "esa-s2-l2a-gtiff-visual:1": {
            "ids": ["s2_123223"],
            "bbox": "None",
            "limit": 1,
        },
        "tiling:1": {"nodata": "None", "tile_width": 768},
    }


def test_construct_parameter_assets(workflow_mock, asset_mock, monkeypatch):
    parameters = workflow_mock.construct_parameters(assets=[asset_mock])
    assert isinstance(parameters, dict)
    assert parameters == {
        "esa-s2-l2a-gtiff-visual:1": {"asset_ids": [asset_mock.asset_id]},
        "tiling:1": {"nodata": "None", "tile_width": 768},
    }

    parameters = workflow_mock.construct_parameters(assets=[asset_mock, asset_mock])
    assert isinstance(parameters, dict)
    assert parameters == {
        "esa-s2-l2a-gtiff-visual:1": {
            "asset_ids": [asset_mock.asset_id, asset_mock.asset_id]
        },
        "tiling:1": {"nodata": "None", "tile_width": 768},
    }

    monkeypatch.setattr(Asset, "source", property(lambda self: "ORDER"))
    with pytest.raises(ValueError):
        workflow_mock.construct_parameters(assets=[asset_mock])


def test_construct_parameters_parallel(workflow_mock):
    parameters_list = workflow_mock.construct_parameters_parallel(
        geometries=[
            shapely.geometry.point.Point(1, 3),
            shapely.geometry.point.Point(1, 5),
        ],
        interval_dates=[("2014-01-01", "2016-12-31")],
        geometry_operation="bbox",
    )
    assert isinstance(parameters_list, list)
    assert len(parameters_list) == 2
    assert parameters_list[0] == {
        "esa-s2-l2a-gtiff-visual:1": {
            "ids": "None",
            "bbox": [0.99999, 2.99999, 1.00001, 3.00001],
            "time": "2014-01-01T00:00:00Z/2016-12-31T23:59:59Z",
            "limit": 1,
        },
        "tiling:1": {"nodata": "None", "tile_width": 768},
    }


def test_construct_parameters_parallel_multiple_intervals(workflow_mock):
    parameters_list = workflow_mock.construct_parameters_parallel(
        geometries=[
            shapely.geometry.point.Point(1, 3),
            shapely.geometry.point.Point(1, 5),
        ],
        interval_dates=[("2014-01-01", "2016-12-31"), ("2017-01-01", "2019-12-31")],
        geometry_operation="bbox",
    )
    assert len(parameters_list) == 4
    assert parameters_list[0] == {
        "esa-s2-l2a-gtiff-visual:1": {
            "ids": "None",
            "bbox": [0.99999, 2.99999, 1.00001, 3.00001],
            "time": "2014-01-01T00:00:00Z/2016-12-31T23:59:59Z",
            "limit": 1,
        },
        "tiling:1": {"nodata": "None", "tile_width": 768},
    }

    with pytest.raises(ValueError):
        workflow_mock.construct_parameters_parallel(geometries=None)


def test_construct_parameters_parallel_scene_ids(workflow_mock):
    parameters_list = workflow_mock.construct_parameters_parallel(
        scene_ids=["S2abc", "S2123"]
    )
    assert len(parameters_list) == 2
    assert parameters_list[0] == {
        "esa-s2-l2a-gtiff-visual:1": {"ids": ["S2abc"], "bbox": "None", "limit": 1},
        "tiling:1": {"nodata": "None", "tile_width": 768},
    }


def test_estimate_jobs(workflow_mock, auth_mock, requests_mock):
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
        f"{workflow_mock.auth._endpoint()}/projects/{workflow_mock.auth.project_id}/workflows/"
        f"{workflow_mock.workflow_id}/tasks"
    )
    url_workflow_estimation = (
        f"{auth_mock._endpoint()}/projects/{auth_mock.project_id}/estimate/job"
    )
    requests_mock.get(url=url_workflow_tasks, json=JSON_WORKFLOW_TASKS)
    requests_mock.post(url=url_workflow_estimation, json=JSON_WORKFLOW_ESTIMATION)

    estimation = workflow_mock.estimate_job(input_parameters)
    assert estimation == JSON_WORKFLOW_ESTIMATION["data"]


@pytest.mark.live
def test_estimate_jobs_live(workflow_live):
    input_parameters = {
        "esa-s2-l2a-gtiff-visual:1": {
            "time": "2018-01-01T00:00:00+00:00/2020-12-31T23:59:59+00:00",
            "limit": 1,
            "bbox": [13.33409, 52.474922, 13.38547, 52.500398],
        },
        "tiling:1": {"tile_width": 768, "tile_height": 768},
    }
    estimation = workflow_live.estimate_job(input_parameters)

    assert estimation.keys() == JSON_WORKFLOW_ESTIMATION["data"].keys()


def test_run_job(workflow_mock, job_mock, requests_mock):
    # job info
    url_job_info = (
        f"{job_mock.auth._endpoint()}/projects/{job_mock.project_id}/"
        f"jobs/{job_mock.job_id}"
    )
    requests_mock.get(url=url_job_info, json={"data": {}})

    input_parameters_json = (
        Path(__file__).resolve().parent / "mock_data/input_params_simple.json"
    )
    job = workflow_mock.run_job(input_parameters_json, name=JOB_NAME)
    assert isinstance(job, Job)
    assert job.job_id == job_mock.job_id


def test_helper_run_parallel_jobs_dry_run(
    workflow_mock, project_mock_max_concurrent_jobs
):
    # pylint: disable=dangerous-default-value
    input_parameters_list = [
        {"esa-s2-l2a-gtiff-visual:1": {"ids": ["S2abc"], "limit": 1}},
        {"esa-s2-l2a-gtiff-visual:1": {"ids": ["S2def"], "limit": 1}},
    ]

    example_response = {
        "error": None,
        "data": {"id": JOB_ID, "status": "SUCCEEDED", "mode": "DRY_RUN"},
    }

    with project_mock_max_concurrent_jobs(10) as m:
        for i, _ in enumerate(input_parameters_list):
            job_name = f"{workflow_mock._info['name']}_{i}_py"
            url_job = (
                f"{workflow_mock.auth._endpoint()}/projects/{workflow_mock.project_id}/"
                f"workflows/{workflow_mock.workflow_id}/jobs?name={job_name}"
            )
            print(url_job)
            m.post(url=url_job, json={"data": {"id": job_name}})
            m.get(
                url=f"{workflow_mock.auth._endpoint()}/projects/{workflow_mock.project_id}/"
                f"jobs/{job_name}",
                json=example_response,
            )

        jb = workflow_mock._helper_run_parallel_jobs(
            input_parameters_list, max_concurrent_jobs=2, test_job=True
        )
    assert isinstance(jb, JobCollection)
    assert len(jb.jobs) == 2
    for job in jb.jobs:
        assert job._info["mode"] == "DRY_RUN"


def test_helper_run_parallel_jobs_all_fails(
    workflow_mock, jobtask_mock, project_mock_max_concurrent_jobs
):
    # pylint: disable=dangerous-default-value
    input_parameters_list = [
        {"esa-s2-l2a-gtiff-visual:1": {"ids": ["S2abc"], "limit": 1}},
        {"esa-s2-l2a-gtiff-visual:1": {"ids": ["S2def"], "limit": 1}},
    ]

    response_failed = {
        "error": None,
        "data": {"id": JOB_ID, "status": "FAILED", "mode": "DRY_RUN"},
    }
    with project_mock_max_concurrent_jobs(10) as m:
        for i, _ in enumerate(input_parameters_list):
            job_name = f"{workflow_mock._info['name']}_{i}_py"
            job_url = (
                f"{workflow_mock.auth._endpoint()}/projects/{workflow_mock.project_id}/"
                f"workflows/{workflow_mock.workflow_id}/jobs?name={job_name}"
            )
            m.post(url=job_url, json={"data": {"id": job_name}})
            m.get(
                url=f"{workflow_mock.auth._endpoint()}/projects/{workflow_mock.project_id}/"
                f"jobs/{job_name}",
                json=response_failed,
            )
            url_job_tasks = (
                f"{workflow_mock.auth._endpoint()}/projects/{workflow_mock.project_id}/jobs/{job_name}"
                f"/tasks/"
            )
            m.get(url=url_job_tasks, json={"data": [{"id": jobtask_mock.jobtask_id}]})
            url_log = (
                f"{workflow_mock.auth._endpoint()}/projects/{workflow_mock.project_id}/jobs/"
                f"{job_name}/tasks/{jobtask_mock.jobtask_id}/logs"
            )
            m.get(url_log, json="")

        jb = workflow_mock._helper_run_parallel_jobs(
            input_parameters_list, max_concurrent_jobs=2, test_job=True
        )
        assert isinstance(jb, JobCollection)
        assert len(jb.jobs) == 2
        assert jb.status == {
            "workflow_name_123_0_py": "FAILED",
            "workflow_name_123_1_py": "FAILED",
        }


def test_helper_run_parallel_jobs_one_fails(
    workflow_mock, project_mock_max_concurrent_jobs
):
    input_parameters_list = [
        {"esa-s2-l2a-gtiff-visual:1": {"ids": ["S2abc"], "limit": 1}},
        {"esa-s2-l2a-gtiff-visual:1": {"ids": ["S2def"], "limit": 1}},
    ]

    responses = [
        {
            "error": None,
            "data": {"id": JOB_ID, "status": "SUCCEEDED", "mode": "DRY_RUN"},
        },
        {
            "error": None,
            "data": {"id": JOB_ID, "status": "FAILED", "mode": "DRY_RUN"},
        },
    ]

    with project_mock_max_concurrent_jobs(10) as m:
        for i, _ in enumerate(input_parameters_list):
            job_name = f"{workflow_mock._info['name']}_{i}_py"
            job_url = (
                f"{workflow_mock.auth._endpoint()}/projects/{workflow_mock.project_id}/"
                f"workflows/{workflow_mock.workflow_id}/jobs?name={job_name}"
            )
            m.post(url=job_url, json={"data": {"id": job_name}})
            m.get(
                url=f"{workflow_mock.auth._endpoint()}/projects/{workflow_mock.project_id}/"
                f"jobs/{job_name}",
                json=responses[i],
            )
            url_job_tasks = (
                f"{workflow_mock.auth._endpoint()}/projects/{workflow_mock.project_id}/jobs/{job_name}"
                f"/tasks/"
            )
            m.get(url=url_job_tasks, json={"data": [{"id": JOBTASK_ID}]})
            url_log = (
                f"{workflow_mock.auth._endpoint()}/projects/{workflow_mock.project_id}/jobs/"
                f"{job_name}/tasks/{JOBTASK_ID}/logs"
            )
            m.get(url_log, json="")

        jb = workflow_mock._helper_run_parallel_jobs(
            input_parameters_list, max_concurrent_jobs=2, test_job=True
        )
        assert isinstance(jb, JobCollection)
        assert len(jb.jobs) == 2
        assert jb.status == {
            "workflow_name_123_0_py": "SUCCEEDED",
            "workflow_name_123_1_py": "FAILED",
        }


@pytest.mark.skip
def test_helper_run_parallel_jobs_default(
    workflow_mock, project_mock_max_concurrent_jobs
):
    """Takes 100sec."""
    # pylint: disable=dangerous-default-value
    input_parameters_list = [
        {"esa-s2-l2a-gtiff-visual:1": {"ids": ["S2abc"], "limit": 1}},
        {"esa-s2-l2a-gtiff-visual:1": {"ids": ["S2def"], "limit": 1}},
    ] * 10
    example_response = {
        "error": None,
        "data": {"id": JOB_ID, "status": "SUCCEEDED", "mode": "DEFAULT"},
    }

    with project_mock_max_concurrent_jobs(10) as m:
        for i, _ in enumerate(input_parameters_list):
            job_name = f"{workflow_mock._info['name']}_{i}_py"
            job_url = (
                f"{workflow_mock.auth._endpoint()}/projects/{workflow_mock.project_id}/"
                f"workflows/{workflow_mock.workflow_id}/jobs?name={job_name}"
            )
            m.post(url=job_url, json={"data": {"id": job_name}})
            m.get(
                url=f"{workflow_mock.auth._endpoint()}/projects/{workflow_mock.project_id}/"
                f"jobs/{job_name}",
                json=example_response,
            )

        jb = workflow_mock._helper_run_parallel_jobs(
            input_parameters_list, max_concurrent_jobs=10
        )
    assert isinstance(jb, JobCollection)
    assert len(jb.jobs) == 20
    for job in jb.jobs:
        assert job._info["mode"] == "DEFAULT"


def test_helper_run_parallel_jobs_fail_concurrent_jobs(
    workflow_mock, project_mock_max_concurrent_jobs
):
    # pylint: disable=dangerous-default-value
    input_parameters_list = [
        {"esa-s2-l2a-gtiff-visual:1": {"ids": ["S2abc"], "limit": 1}},
        {"esa-s2-l2a-gtiff-visual:1": {"ids": ["S2def"], "limit": 1}},
    ] * 10
    example_response = {
        "error": None,
        "data": {"id": JOB_ID, "status": "SUCCEEDED", "mode": "DEFAULT"},
    }

    with project_mock_max_concurrent_jobs(1) as m:
        for i, _ in enumerate(input_parameters_list):
            job_name = f"{workflow_mock._info['name']}_{i}_py"
            job_url = (
                f"{workflow_mock.auth._endpoint()}/projects/{workflow_mock.project_id}/"
                f"workflows/{workflow_mock.workflow_id}/jobs?name={job_name}"
            )
            m.post(url=job_url, json={"data": {"id": job_name}})
            m.get(
                url=f"{workflow_mock.auth._endpoint()}/projects/{workflow_mock.project_id}/"
                f"jobs/{job_name}",
                json=example_response,
            )

        with pytest.raises(ValueError):
            workflow_mock._helper_run_parallel_jobs(
                input_parameters_list, max_concurrent_jobs=10
            )


@pytest.mark.live
def test_test_jobs_parallel_live(workflow_live):
    input_parameters_list = [
        {
            "esa-s2-l2a-gtiff-visual:1": {
                "time": "2019-01-01T00:00:00+00:00/2019-12-31T23:59:59+00:00",
                "limit": 1,
                "bbox": [13.375966, 52.515068, 13.378314, 52.516639],
            },
            "tiling:1": {"tile_width": 768, "tile_height": 768},
        },
        {
            "esa-s2-l2a-gtiff-visual:1": {
                "time": "2020-01-01T00:00:00+00:00/2020-12-31T23:59:59+00:00",
                "limit": 1,
                "bbox": [13.375966, 52.515068, 13.378314, 52.516639],
            },
            "tiling:1": {"tile_width": 768, "tile_height": 768},
        },
    ]

    jb = workflow_live.test_jobs_parallel(input_parameters_list=input_parameters_list)
    assert isinstance(jb, JobCollection)

    input_parameters_list = copy.deepcopy(input_parameters_list)
    for input_parameters in input_parameters_list:
        input_parameters.update({"config": {"mode": "DRY_RUN"}})
    for index, job in enumerate(jb.jobs):
        assert job.status == "SUCCEEDED"
        assert job._info["inputs"] == input_parameters_list[index]
        assert job._info["mode"] == "DRY_RUN"


@pytest.mark.live
def test_run_jobs_parallel_live(workflow_live):
    input_parameters_list = [
        {
            "esa-s2-l2a-gtiff-visual:1": {
                "time": "2019-01-01T00:00:00+00:00/2019-12-31T23:59:59+00:00",
                "limit": 1,
                "bbox": [13.375966, 52.515068, 13.378314, 52.516639],
            },
            "tiling:1": {"tile_width": 768, "tile_height": 768},
        },
        {
            "esa-s2-l2a-gtiff-visual:1": {
                "time": "2020-01-01T00:00:00+00:00/2020-12-31T23:59:59+00:00",
                "limit": 1,
                "bbox": [13.375966, 52.515068, 13.378314, 52.516639],
            },
            "tiling:1": {"tile_width": 768, "tile_height": 768},
        },
    ]

    jb = workflow_live.run_jobs_parallel(input_parameters_list=input_parameters_list)
    assert isinstance(jb, JobCollection)
    for index, job in enumerate(jb.jobs):
        assert job.status == "SUCCEEDED"
        assert job._info["inputs"] == input_parameters_list[index]
        assert job._info["mode"] == "DEFAULT"


@pytest.mark.live
def test_test_job_live(workflow_live):
    input_parameters_json = (
        Path(__file__).resolve().parent / "mock_data/input_params_simple.json"
    )
    jb = workflow_live.test_job(
        input_parameters=input_parameters_json, track_status=True
    )
    assert isinstance(jb, Job)
    with open(input_parameters_json) as src:
        job_info_params = json.load(src)
        job_info_params.update({"config": {"mode": "DRY_RUN"}})
        assert jb._info["inputs"] == job_info_params
        assert jb._info["mode"] == "DRY_RUN"
    assert jb.status == "SUCCEEDED"


@pytest.mark.live
def test_run_job_live(workflow_live):
    input_parameters_json = (
        Path(__file__).resolve().parent / "mock_data/input_params_simple.json"
    )
    jb = workflow_live.run_job(input_parameters_json, track_status=True, name=JOB_NAME)
    assert isinstance(jb, Job)
    with open(input_parameters_json) as src:
        assert jb._info["inputs"] == json.load(src)
        assert jb._info["mode"] == "DEFAULT"
    assert jb.status == "SUCCEEDED"
    assert jb._info["name"] == JOB_NAME + "_py"


def test_get_jobs(workflow_mock, requests_mock):
    url_job_info = (
        f"{workflow_mock.auth._endpoint()}/projects/"
        f"{workflow_mock.project_id}/jobs/{JOB_ID}"
    )

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


@pytest.mark.skip
@pytest.mark.live
def test_get_jobs_live(workflow_live):
    # Skip by default as too many jobs in test project, triggers too many job info requests.
    jobcollection = workflow_live.get_jobs()
    assert isinstance(jobcollection, list)
    assert isinstance(jobcollection.jobs[0], Job)
    assert all(
        j._info["workflowId"] == workflow_live.workflow_id for j in jobcollection.jobs
    )


def test_update_name(workflow_mock, requests_mock):
    new_name = "new_workflow_name"
    url_update_name = (
        f"{workflow_mock.auth._endpoint()}/projects/{workflow_mock.auth.project_id}/workflows/"
        f"{workflow_mock.workflow_id}"
    )
    json_new_properties = {"data": {}, "error": {}}
    requests_mock.put(
        url=url_update_name,
        json=json_new_properties,
    )

    workflow_mock.update_name(name=new_name)
    # TODO:caplog, capture logger


def test_delete(workflow_mock, requests_mock):
    delete_url = (
        f"{workflow_mock.auth._endpoint()}/projects/{workflow_mock.project_id}/workflows/"
        f"{workflow_mock.workflow_id}"
    )
    requests_mock.delete(url=delete_url)

    workflow_mock.delete()
    # TODO:caplog, capture logger
