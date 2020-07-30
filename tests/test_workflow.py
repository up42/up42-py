from pathlib import Path
import json
import copy

# pylint: disable=unused-import
from unittest.mock import Mock, patch
import unittest.mock as mock

import pytest
import requests_mock
import shapely
from geojson import Feature

# pylint: disable=unused-import,wrong-import-order
from .context import Workflow, Job, JobCollection
from .fixtures import (
    auth_mock,
    auth_live,
    workflow_mock,
    workflow_live,
    job_mock,
    jobcollection_single_mock,
    jobtask_mock,
)
import up42


json_workflow_tasks = {
    "data": [
        {
            "id": "c0d04ec3-98d7-4183-902f-5bcb2a176d89",
            "name": "sobloo-s2-l1c-aoiclipped:1",
            "block": {
                "name": "sobloo-s2-l1c-aoiclipped",
                "parameters": {
                    "nodata": {"type": "number",},
                    "time": {
                        "type": "dateRange",
                        "default": "2018-01-01T00:00:00+00:00/2020-12-31T23:59:59+00:00",
                    },
                },
            },
        },
        {
            "id": "af626c54-156e-4f13-a743-55efd27de533",
            "name": "tiling:1",
            "block": {
                "name": "tiling",
                "parameters": {
                    "nodata": {
                        "type": "number",
                        "default": None,
                        "required": False,
                        "description": "Value representing..",
                    },
                    "tile_width": {
                        "type": "number",
                        "default": 768,
                        "required": True,
                        "description": "Width of a tile in pixels",
                    },
                },
            },
        },
    ],
    "error": {},
}

json_blocks = {
    "data": [
        {
            "id": "4ed70368-d4e1-4462-bef6-14e768049471",
            "name": "tiling",
            "displayName": "Raster Tiling",
        },
        {
            "id": "c0d04ec3-98d7-4183-902f-5bcb2a176d89",
            "name": "sharpening",
            "displayName": "Sharpening Filter",
        },
        {
            "id": "a2daaab4-196d-4226-a018-a810444dcad1",
            "name": "sobloo-s2-l1c-aoiclipped",
            "displayName": "Sentinel-2 L1C MSI AOI clipped",
        },
    ],
    "error": {},
}


def test_workflow_get_info(workflow_mock):
    del workflow_mock.info

    with requests_mock.Mocker() as m:
        url_workflow_info = (
            f"{workflow_mock.auth._endpoint()}/projects/"
            f"{workflow_mock.project_id}/workflows/"
            f"{workflow_mock.workflow_id}"
        )
        m.get(url=url_workflow_info, json={"data": {"xyz": 789}, "error": {}})

        info = workflow_mock._get_info()
    assert isinstance(workflow_mock, Workflow)
    assert info["xyz"] == 789
    assert workflow_mock.info["xyz"] == 789


def test_get_compatible_blocks(workflow_mock):
    url_workflow_tasks = (
        f"{workflow_mock.auth._endpoint()}/projects/{workflow_mock.auth.project_id}/workflows/"
        f"{workflow_mock.workflow_id}/tasks"
    )
    with requests_mock.Mocker() as m:
        m.get(url=url_workflow_tasks, json=json_workflow_tasks)

        url_compatible_blocks = (
            f"{workflow_mock.auth._endpoint()}/projects/{workflow_mock.project_id}/"
            f"workflows/{workflow_mock.workflow_id}/"
            f"compatible-blocks?parentTaskName=tiling:1"
        )
        json_compatible_blocks = {
            "data": {
                "blocks": [
                    {"blockId": "aaa123", "name": "aaa", "versionTag": "2.0"},
                    {"blockId": "bbb123", "name": "bbb", "versionTag": "2.0"},
                ],
                "error": {},
            }
        }
        m.get(url=url_compatible_blocks, json=json_compatible_blocks)

        compatible_blocks = workflow_mock.get_compatible_blocks()
    assert isinstance(compatible_blocks, dict)
    assert "aaa" in list(compatible_blocks.keys())


@pytest.mark.live
def test_get_compatible_blocks_live(workflow_live):
    compatible_blocks = workflow_live.get_compatible_blocks()
    assert isinstance(compatible_blocks, dict)
    assert "tiling" in list(compatible_blocks.keys())


def test_get_workflow_tasks_normal_and_basic(workflow_mock):
    url_workflow_tasks = (
        f"{workflow_mock.auth._endpoint()}/projects/{workflow_mock.auth.project_id}/workflows/"
        f"{workflow_mock.workflow_id}/tasks"
    )
    with requests_mock.Mocker() as m:
        m.get(url=url_workflow_tasks, json=json_workflow_tasks)
        tasks = workflow_mock.get_workflow_tasks(basic=False)
    assert len(tasks) == 2
    assert tasks[0] == {
        "id": "c0d04ec3-98d7-4183-902f-5bcb2a176d89",
        "name": "sobloo-s2-l1c-aoiclipped:1",
        "block": {
            "name": "sobloo-s2-l1c-aoiclipped",
            "parameters": {
                "nodata": {"type": "number"},
                "time": {
                    "type": "dateRange",
                    "default": "2018-01-01T00:00:00+00:00/2020-12-31T23:59:59+00:00",
                },
            },
        },
    }

    with requests_mock.Mocker() as m:
        m.get(url=url_workflow_tasks, json=json_workflow_tasks)
        tasks = workflow_mock.get_workflow_tasks(basic=True)
    assert len(tasks) == 2
    assert tasks["sobloo-s2-l1c-aoiclipped:1"] == "c0d04ec3-98d7-4183-902f-5bcb2a176d89"


@pytest.mark.live
def test_get_workflow_tasks_live(workflow_live):
    workflow_tasks = workflow_live.get_workflow_tasks(basic=True)
    assert isinstance(workflow_tasks, dict)
    assert "sobloo-s2-l1c-aoiclipped:1" in list(workflow_tasks.keys())


def test_construct_full_workflow_tasks_dict_unkwown_block_raises(workflow_mock):
    input_tasks = ["some_block"]
    with requests_mock.Mocker() as m:
        url_get_blocks = f"{workflow_mock.auth._endpoint()}/blocks"
        m.get(
            url=url_get_blocks, json=json_blocks,
        )
        with pytest.raises(ValueError):
            workflow_mock._construct_full_workflow_tasks_dict(input_tasks=input_tasks)


@pytest.mark.parametrize(
    "input_tasks",
    [
        [
            "a2daaab4-196d-4226-a018-a810444dcad1",
            "4ed70368-d4e1-4462-bef6-14e768049471",
        ],
        ["sobloo-s2-l1c-aoiclipped", "tiling"],
        ["Sentinel-2 L1C MSI AOI clipped", "Raster Tiling",],
        ["a2daaab4-196d-4226-a018-a810444dcad1", "tiling",],
        ["Sentinel-2 L1C MSI AOI clipped", "4ed70368-d4e1-4462-bef6-14e768049471",],
    ],
)
def test_construct_full_workflow_tasks_dict(workflow_mock, input_tasks):
    with requests_mock.Mocker() as m:
        url_get_blocks = f"{workflow_mock.auth._endpoint()}/blocks"
        m.get(
            url=url_get_blocks, json=json_blocks,
        )
        full_workflow_tasks_dict = workflow_mock._construct_full_workflow_tasks_dict(
            input_tasks=input_tasks
        )
    assert isinstance(full_workflow_tasks_dict, list)
    assert full_workflow_tasks_dict[0]["name"] == "sobloo-s2-l1c-aoiclipped:1"
    assert full_workflow_tasks_dict[0]["parentName"] is None
    assert full_workflow_tasks_dict[1]["name"] == "tiling:1"
    assert full_workflow_tasks_dict[1]["parentName"] == "sobloo-s2-l1c-aoiclipped:1"
    assert (
        full_workflow_tasks_dict[1]["blockId"] == "4ed70368-d4e1-4462-bef6-14e768049471"
    )


@pytest.mark.skip
# TODO: Resolve
def test_add_workflow_tasks_full(workflow_mock, caplog):
    input_tasks_full = [
        {
            "name": "sobloo-s2-l1c-aoiclipped:1",
            "parentName": None,
            "blockId": "a2daaab4-196d-4226-a018-a810444dcad1",
        },
        {
            "name": "sharpening:1",
            "parentName": "sobloo-s2-l1c-aoiclipped",
            "blockId": "4ed70368-d4e1-4462-bef6-14e768049471",
        },
    ]

    job_url = (
        f"{workflow_mock.auth._endpoint()}/projects/{workflow_mock.project_id}/workflows/"
        f"{workflow_mock.workflow_id}/tasks/"
    )
    with requests_mock.Mocker() as m:
        m.post(url=job_url, status_code=200)

        workflow_mock.add_workflow_tasks(input_tasks_full)
    assert f"Added tasks to workflow: {input_tasks_full}" in caplog.text


@pytest.mark.live
def test_add_workflow_tasks_simple_not_existing_block_id_raises_live(workflow_live):
    input_tasks_simple = ["12345"]
    with pytest.raises(Exception):
        workflow_live.add_workflow_tasks(input_tasks_simple)


def test_get_parameter_info(workflow_mock):
    url_workflow_tasks = (
        f"{workflow_mock.auth._endpoint()}/projects/{workflow_mock.auth.project_id}/workflows/"
        f"{workflow_mock.workflow_id}/tasks"
    )
    with requests_mock.Mocker() as m:
        m.get(url=url_workflow_tasks, json=json_workflow_tasks)
        parameter_info = workflow_mock.get_parameters_info()
    assert isinstance(parameter_info, dict)
    assert all(
        x in list(parameter_info.keys())
        for x in ["tiling:1", "sobloo-s2-l1c-aoiclipped:1"]
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
        for x in ["tiling:1", "sobloo-s2-l1c-aoiclipped:1"]
    )
    assert all(
        x in list(parameter_info["tiling:1"].keys())
        for x in ["nodata", "tile_width", "match_extents"]
    )


def test_get_default_parameters(workflow_mock):
    url_workflow_tasks = (
        f"{workflow_mock.auth._endpoint()}/projects/{workflow_mock.auth.project_id}/workflows/"
        f"{workflow_mock.workflow_id}/tasks"
    )
    with requests_mock.Mocker() as m:
        m.get(url=url_workflow_tasks, json=json_workflow_tasks)
        default_parameters = workflow_mock._get_default_parameters()
    assert isinstance(default_parameters, dict)
    assert all(
        x in list(default_parameters.keys())
        for x in ["tiling:1", "sobloo-s2-l1c-aoiclipped:1"]
    )
    assert default_parameters["tiling:1"] == {"tile_width": 768}
    assert default_parameters["sobloo-s2-l1c-aoiclipped:1"] == {
        "time": "2018-01-01T00:00:00+00:00/2020-12-31T23:59:59+00:00"
    }


def test_construct_parameters(workflow_mock):
    url_workflow_tasks = (
        f"{workflow_mock.auth._endpoint()}/projects/{workflow_mock.auth.project_id}/workflows/"
        f"{workflow_mock.workflow_id}/tasks"
    )
    with requests_mock.Mocker() as m:
        m.get(url=url_workflow_tasks, json=json_workflow_tasks)

        parameters = workflow_mock.construct_parameters(
            geometry=shapely.geometry.point.Point(1, 3),
            geometry_operation="bbox",
            start_date="2014-01-01",
            end_date="2016-12-31",
            limit=1,
        )
    assert isinstance(parameters, dict)
    assert parameters == {
        "sobloo-s2-l1c-aoiclipped:1": {
            "time": "2014-01-01T00:00:00Z/2016-12-31T00:00:00Z",
            "limit": 1,
            "bbox": [0.99999, 2.99999, 1.00001, 3.00001],
        },
        "tiling:1": {"tile_width": 768},
    }


def test_construct_parameters_scene_ids(workflow_mock):
    url_workflow_tasks = (
        f"{workflow_mock.auth._endpoint()}/projects/{workflow_mock.auth.project_id}/workflows/"
        f"{workflow_mock.workflow_id}/tasks"
    )
    with requests_mock.Mocker() as m:
        m.get(url=url_workflow_tasks, json=json_workflow_tasks)

        parameters = workflow_mock.construct_parameters(
            geometry=shapely.geometry.point.Point(1, 3),
            geometry_operation="bbox",
            scene_ids=["s2_123223"],
        )
    assert isinstance(parameters, dict)
    assert parameters == {
        "sobloo-s2-l1c-aoiclipped:1": {
            "ids": ["s2_123223"],
            "limit": 1,
            "bbox": [0.99999, 2.99999, 1.00001, 3.00001],
        },
        "tiling:1": {"tile_width": 768},
    }


def test_construct_parameter_only_ids(workflow_mock):
    url_workflow_tasks = (
        f"{workflow_mock.auth._endpoint()}/projects/{workflow_mock.auth.project_id}/workflows/"
        f"{workflow_mock.workflow_id}/tasks"
    )
    with requests_mock.Mocker() as m:
        m.get(url=url_workflow_tasks, json=json_workflow_tasks)

        parameters = workflow_mock.construct_parameters(scene_ids=["s2_123223"],)
    assert isinstance(parameters, dict)
    assert parameters == {
        "sobloo-s2-l1c-aoiclipped:1": {"ids": ["s2_123223"], "limit": 1},
        "tiling:1": {"tile_width": 768},
    }


def test_construct_parameter_order_ids(workflow_mock):
    url_workflow_tasks = (
        f"{workflow_mock.auth._endpoint()}/projects/{workflow_mock.auth.project_id}/workflows/"
        f"{workflow_mock.workflow_id}/tasks"
    )
    with requests_mock.Mocker() as m:
        m.get(url=url_workflow_tasks, json=json_workflow_tasks)

        parameters = workflow_mock.construct_parameters(order_ids=["8472712912"])
    assert isinstance(parameters, dict)
    assert parameters == {
        "sobloo-s2-l1c-aoiclipped:1": {"order_ids": ["8472712912"]},
        "tiling:1": {"tile_width": 768},
    }


def test_construct_parameters_parallel(workflow_mock):
    url_workflow_tasks = (
        f"{workflow_mock.auth._endpoint()}/projects/{workflow_mock.auth.project_id}/workflows/"
        f"{workflow_mock.workflow_id}/tasks"
    )
    with requests_mock.Mocker() as m:
        m.get(url=url_workflow_tasks, json=json_workflow_tasks)

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
        "sobloo-s2-l1c-aoiclipped:1": {
            "time": "2014-01-01T00:00:00Z/2016-12-31T00:00:00Z",
            "limit": 1,
            "bbox": [0.99999, 2.99999, 1.00001, 3.00001],
        },
        "tiling:1": {"tile_width": 768},
    }


def test_construct_parameters_parallel_multiple_intervals(workflow_mock):
    url_workflow_tasks = (
        f"{workflow_mock.auth._endpoint()}/projects/{workflow_mock.auth.project_id}/workflows/"
        f"{workflow_mock.workflow_id}/tasks"
    )
    with requests_mock.Mocker() as m:
        m.get(url=url_workflow_tasks, json=json_workflow_tasks)

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
        "sobloo-s2-l1c-aoiclipped:1": {
            "time": "2014-01-01T00:00:00Z/2016-12-31T00:00:00Z",
            "limit": 1,
            "bbox": [0.99999, 2.99999, 1.00001, 3.00001],
        },
        "tiling:1": {"tile_width": 768},
    }

    with requests_mock.Mocker() as m:
        m.get(url=url_workflow_tasks, json=json_workflow_tasks)
        with pytest.raises(ValueError):
            workflow_mock.construct_parameters_parallel(geometries=None)


def test_construct_parameters_parallel_scene_ids(workflow_mock):
    url_workflow_tasks = (
        f"{workflow_mock.auth._endpoint()}/projects/{workflow_mock.auth.project_id}/workflows/"
        f"{workflow_mock.workflow_id}/tasks"
    )
    with requests_mock.Mocker() as m:
        m.get(url=url_workflow_tasks, json=json_workflow_tasks)

        parameters_list = workflow_mock.construct_parameters_parallel(
            scene_ids=["S2abc", "S2123"]
        )
    assert len(parameters_list) == 2
    assert parameters_list[0] == {
        "sobloo-s2-l1c-aoiclipped:1": {"ids": ["S2abc"], "limit": 1},
        "tiling:1": {"tile_width": 768},
    }


def test_run_job(workflow_mock, job_mock):
    with requests_mock.Mocker() as m:
        job_name = f"{workflow_mock.info['name']}_py"
        job_url = (
            f"{workflow_mock.auth._endpoint()}/projects/{workflow_mock.project_id}/"
            f"workflows/{workflow_mock.workflow_id}/jobs?name={job_name}"
        )
        m.post(url=job_url, json={"data": {"id": job_mock.job_id}})
        input_parameters_json = (
            Path(__file__).resolve().parent / "mock_data/input_params_simple.json"
        )
        m.get(
            url=f"{job_mock.auth._endpoint()}/projects/{job_mock.project_id}/"
            f"jobs/{job_mock.job_id}",
            json={"data": {}},
        )

        jb = workflow_mock.run_job(input_parameters_json)
        assert isinstance(jb, Job)
        assert jb.job_id == job_mock.job_id


def test_helper_run_parallel_jobs_dry_run(auth_mock, workflow_mock, monkeypatch):
    # pylint: disable=dangerous-default-value
    input_parameters_list = [
        {"sobloo-s2-l1c-aoiclipped:1": {"ids": ["S2abc"], "limit": 1}},
        {"sobloo-s2-l1c-aoiclipped:1": {"ids": ["S2def"], "limit": 1}},
    ]

    example_response = {
        "error": None,
        "data": {"id": "jobid_123", "status": "SUCCEEDED", "mode": "DRY_RUN"},
    }

    def _mock_endpoint():
        return "http://example"

    def _mock_dict(request_type, url, data=input_parameters_list):
        del request_type, url, data
        return example_response

    monkeypatch.setattr(auth_mock, "_endpoint", _mock_endpoint)
    monkeypatch.setattr(auth_mock, "_request", _mock_dict)

    jb = workflow_mock._helper_run_parallel_jobs(
        input_parameters_list, max_concurrent_jobs=2, test_job=True
    )
    assert isinstance(jb, JobCollection)
    assert len(jb.jobs) == 2
    for job in jb.jobs:
        assert job.info["mode"] == "DRY_RUN"


def test_helper_run_parallel_jobs_all_fails(workflow_mock, jobtask_mock):
    # pylint: disable=dangerous-default-value
    input_parameters_list = [
        {"sobloo-s2-l1c-aoiclipped:1": {"ids": ["S2abc"], "limit": 1}},
        {"sobloo-s2-l1c-aoiclipped:1": {"ids": ["S2def"], "limit": 1}},
    ]

    response_failed = {
        "error": None,
        "data": {"id": "jobid_123", "status": "FAILED", "mode": "DRY_RUN"},
    }
    with requests_mock.Mocker() as m:
        for i, _ in enumerate(input_parameters_list):
            job_name = f"{workflow_mock.info['name']}_{i}_py"
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
        assert jb.get_jobs_status().values == ["FAILED", "FAILED"]


def test_helper_run_parallel_jobs_one_fails(workflow_mock, jobtask_mock):
    input_parameters_list = [
        {"sobloo-s2-l1c-aoiclipped:1": {"ids": ["S2abc"], "limit": 1}},
        {"sobloo-s2-l1c-aoiclipped:1": {"ids": ["S2def"], "limit": 1}},
    ]

    responses = [
        {
            "error": None,
            "data": {"id": "jobid_123", "status": "SUCCEEDED", "mode": "DRY_RUN"},
        },
        {
            "error": None,
            "data": {"id": "jobid_123", "status": "FAILED", "mode": "DRY_RUN"},
        },
    ]

    with requests_mock.Mocker() as m:
        for i, _ in enumerate(input_parameters_list):
            job_name = f"{workflow_mock.info['name']}_{i}_py"
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
        assert jb.get_jobs_status().values == ["SUCCEEDED", "FAILED"]


def test_helper_run_parallel_jobs_default(auth_mock, workflow_mock, monkeypatch):
    # pylint: disable=dangerous-default-value
    input_parameters_list = [
        {"sobloo-s2-l1c-aoiclipped:1": {"ids": ["S2abc"], "limit": 1}},
        {"sobloo-s2-l1c-aoiclipped:1": {"ids": ["S2def"], "limit": 1}},
    ] * 10
    example_response = {
        "error": None,
        "data": {"id": "jobid_123", "status": "SUCCEEDED", "mode": "DEFAULT"},
    }

    def _mock_endpoint():
        return "http://example"

    def _mock_dict(request_type, url, data=input_parameters_list):
        del request_type, url, data
        return example_response

    monkeypatch.setattr(auth_mock, "_endpoint", _mock_endpoint)
    monkeypatch.setattr(auth_mock, "_request", _mock_dict)

    jb = workflow_mock._helper_run_parallel_jobs(
        input_parameters_list, max_concurrent_jobs=10
    )
    assert isinstance(jb, JobCollection)
    assert len(jb.jobs) == 20
    for job in jb.jobs:
        assert job.info["mode"] == "DEFAULT"


@pytest.mark.live
def test_test_jobs_parallel_live(workflow_live):
    input_parameters_list = [
        {
            "sobloo-s2-l1c-aoiclipped:1": {
                "time": "2019-01-01T00:00:00Z/2020-12-31T00:00:00Z",
                "limit": 1,
                "bbox": [13.375966, 52.515068, 13.378314, 52.516639],
            },
            "tiling:1": {"tile_width": 768, "tile_height": 768},
        },
        {
            "sobloo-s2-l1c-aoiclipped:1": {
                "time": "2019-12-01T00:00:00Z/2020-12-31T00:00:00Z",
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
        assert job.get_status() == "SUCCEEDED"
        assert job.info["inputs"] == input_parameters_list[index]
        assert job.info["mode"] == "DRY_RUN"


@pytest.mark.live
def test_run_jobs_parallel_live(workflow_live):
    input_parameters_list = [
        {
            "sobloo-s2-l1c-aoiclipped:1": {
                "time": "2019-01-01T00:00:00Z/2020-12-31T00:00:00Z",
                "limit": 1,
                "bbox": [13.375966, 52.515068, 13.378314, 52.516639],
            },
            "tiling:1": {"tile_width": 768, "tile_height": 768},
        },
        {
            "sobloo-s2-l1c-aoiclipped:1": {
                "time": "2019-12-01T00:00:00Z/2020-12-31T00:00:00Z",
                "limit": 1,
                "bbox": [13.375966, 52.515068, 13.378314, 52.516639],
            },
            "tiling:1": {"tile_width": 768, "tile_height": 768},
        },
    ]

    jb = workflow_live.run_jobs_parallel(input_parameters_list=input_parameters_list)
    assert isinstance(jb, JobCollection)
    for index, job in enumerate(jb.jobs):
        assert job.get_status() == "SUCCEEDED"
        assert job.info["inputs"] == input_parameters_list[index]
        assert job.info["mode"] == "DEFAULT"


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
        assert jb.info["inputs"] == job_info_params
        assert jb.info["mode"] == "DRY_RUN"
    assert jb.get_status() == "SUCCEEDED"


@pytest.mark.live
def test_run_job_live(workflow_live):
    input_parameters_json = (
        Path(__file__).resolve().parent / "mock_data/input_params_simple.json"
    )
    jb = workflow_live.run_job(input_parameters_json, track_status=True, name="aa")
    assert isinstance(jb, Job)
    with open(input_parameters_json) as src:
        assert jb.info["inputs"] == json.load(src)
        assert jb.info["mode"] == "DEFAULT"
    assert jb.get_status() == "SUCCEEDED"
    assert jb.info["name"] == "aa_py"


def test_get_jobs(workflow_mock):
    job_id = "87c285b4-d69b-42a4-bdc5-6fe6d0ddcbbd"
    with requests_mock.Mocker() as m:
        url_jobs = (
            f"{workflow_mock.auth._endpoint()}/projects/{workflow_mock.project_id}/jobs"
        )
        json_jobs = {
            "data": [
                {
                    "id": job_id,
                    "status": "SUCCEEDED",
                    "inputs": {},
                    "error": {},
                    "workflowId": "123456",
                },
                {
                    "id": job_id,
                    "status": "SUCCEEDED",
                    "inputs": {},
                    "error": {},
                    "workflowId": workflow_mock.workflow_id,
                },
            ]
        }
        m.get(url=url_jobs, json=json_jobs)

        url_job_info = (
            f"{workflow_mock.auth._endpoint()}/projects/"
            f"{workflow_mock.project_id}/jobs/{job_id}"
        )
        m.get(url=url_job_info, json={"data": {"xyz": 789}, "error": {}})

        jobcollection = workflow_mock.get_jobs()
        assert isinstance(jobcollection, JobCollection)
        assert isinstance(jobcollection.jobs[0], Job)
        assert jobcollection.jobs[0].job_id == job_id
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
        [j.info["workflowId"] == workflow_live.workflow_id for j in jobcollection.jobs]
    )


# TODO: Resolve
# def test_update_name(workflow_mock, caplog):
#     new_name = "new_workflow_name"
#     with requests_mock.Mocker() as m:
#         url_update_name = (
#             f"{workflow_mock.auth._endpoint()}/projects/{workflow_mock.auth.project_id}/workflows/"
#             f"{workflow_mock.workflow_id}"
#         )
#         json_new_properties = {"data": {}, "error": {}}
#         m.post(
#             url=url_update_name,
#             json=json_new_properties,
#         )
#
#         workflow_mock.update_name(name=new_name)
#     assert f"Updated workflow name: {new_name}" in caplog.text


@pytest.mark.skip
# TODO: Resolve
def test_delete(workflow_mock, caplog):
    with requests_mock.Mocker() as m:
        delete_url = (
            f"{workflow_mock.auth._endpoint()}/projects/{workflow_mock.project_id}/workflows/"
            f"{workflow_mock.workflow_id}"
        )
        m.delete(url=delete_url)
        workflow_mock.delete()
    assert f"Successfully deleted workflow: {workflow_mock.workflow_id}" in caplog.text
