from pathlib import Path
import json
import pytest
import requests_mock
import shapely

# pylint: disable=unused-import,wrong-import-order
from .context import Workflow
from .fixtures import auth_mock, auth_live, workflow_mock, workflow_live, job_mock
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


def test_construct_full_workflow_tasks_dict(workflow_mock):
    input_tasks = [
        "a2daaab4-196d-4226-a018-a810444dcad1",
        "4ed70368-d4e1-4462-bef6-14e768049471",
    ]
    with requests_mock.Mocker() as m:
        url_get_blocks = f"{workflow_mock.auth._endpoint()}/blocks"
        m.get(
            url=url_get_blocks,
            json={
                "data": [
                    {"id": "4ed70368-d4e1-4462-bef6-14e768049471", "name": "tiling"},
                    {
                        "id": "c0d04ec3-98d7-4183-902f-5bcb2a176d89",
                        "name": "sharpening",
                    },
                    {
                        "id": "a2daaab4-196d-4226-a018-a810444dcad1",
                        "name": "sobloo-s2-l1c-aoiclipped",
                    },
                ],
                "error": {},
            },
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


def test_construct_parameter(workflow_mock):
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


def test_construct_parameter_scene_ids(workflow_mock):
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


def test_create_and_run_job(workflow_mock, job_mock):
    with requests_mock.Mocker() as m:
        job_url = (
            f"{workflow_mock.auth._endpoint()}/projects/{workflow_mock.project_id}/"
            f"workflows/{workflow_mock.workflow_id}/jobs?name=_py"
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

        jb = workflow_mock.create_and_run_job(input_parameters_json)
        assert isinstance(jb, up42.Job)
        assert jb.job_id == job_mock.job_id


@pytest.mark.live
def test_create_and_run_job_live(workflow_live):
    input_parameters_json = (
        Path(__file__).resolve().parent / "mock_data/input_params_simple.json"
    )
    jb = workflow_live.create_and_run_job(input_parameters_json, track_status=True)
    assert isinstance(jb, up42.Job)
    with open(input_parameters_json) as src:
        assert jb.info["inputs"] == json.load(src)
        assert jb.info["mode"] == "DEFAULT"
    assert jb.get_status() == "SUCCEEDED"


@pytest.mark.live
def test_create_and_run_job_test_query_live(workflow_live):
    input_parameters_json = (
        Path(__file__).resolve().parent / "mock_data/input_params_simple.json"
    )
    jb = workflow_live.create_and_run_job(
        input_parameters_json, test_query=True, track_status=True
    )
    assert isinstance(jb, up42.Job)
    with open(input_parameters_json) as src:
        job_info_params = json.load(src)
        job_info_params.update({"config": {"mode": "DRY_RUN"}})
        assert jb.info["inputs"] == job_info_params
        assert jb.info["mode"] == "DRY_RUN"
    assert jb.get_status() == "SUCCEEDED"


def test_get_jobs(workflow_mock):
    job_id = "87c285b4-d69b-42a4-bdc5-6fe6d0ddcbbd"
    with requests_mock.Mocker() as m:
        url_jobs = (
            f"{workflow_mock.auth._endpoint()}/projects/{workflow_mock.project_id}/jobs"
        )
        json_jobs = {
            "data": [{"id": job_id, "status": "SUCCEEDED", "inputs": {}, "error": {},}]
        }
        m.get(url=url_jobs, json=json_jobs)

        url_job_info = (
            f"{workflow_mock.auth._endpoint()}/projects/"
            f"{workflow_mock.project_id}/jobs/{job_id}"
        )
        m.get(url=url_job_info, json={"data": {"xyz": 789}, "error": {}})

        jobs = workflow_mock.get_jobs()
        assert isinstance(jobs, list)
        assert isinstance(jobs[0], up42.Job)
        assert jobs[0].job_id == job_id


@pytest.mark.skip
@pytest.mark.live
def test_get_jobs_live(workflow_live):
    # Too many jobs in test project
    jobs = workflow_live.get_jobs()
    assert isinstance(jobs, list)
    assert isinstance(jobs[0], up42.Job)


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
