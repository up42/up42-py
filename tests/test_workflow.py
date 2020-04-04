from pathlib import Path
import json
import pytest
import requests_mock

# pylint: disable=unused-import,wrong-import-order
from .context import Workflow
from .fixtures import auth_mock, auth_live, workflow_mock, workflow_live, job_mock
import up42


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
    with requests_mock.Mocker() as m:
        url_workflow_tasks = (
            f"{workflow_mock.auth._endpoint()}/projects/{workflow_mock.auth.project_id}/workflows/"
            f"{workflow_mock.workflow_id}/tasks"
        )
        json_workflow_tasks = {
            "data": [
                {
                    "id": "c0d04ec3-98d7-4183-902f-5bcb2a176d89",
                    "name": "sobloo-s2-l1c-aoiclipped:1",
                    "block": {"name": "sobloo-s2-l1c-aoiclipped"},
                },
                {
                    "id": "af626c54-156e-4f13-a743-55efd27de533",
                    "name": "sharpening:1",
                    "block": {"name": "sharpening"},
                },
            ],
            "error": {},
        }
        m.get(url=url_workflow_tasks, json=json_workflow_tasks)

        url_compatible_blocks = (
            f"{workflow_mock.auth._endpoint()}/projects/{workflow_mock.project_id}/"
            f"workflows/{workflow_mock.workflow_id}/"
            f"compatible-blocks?parentTaskName=sharpening:1"
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
    json_workflow_tasks = {
        "data": [
            {
                "id": "c0d04ec3-98d7-4183-902f-5bcb2a176d89",
                "name": "sobloo-s2-l1c-aoiclipped:1",
                "block": {"name": "sobloo-s2-l1c-aoiclipped"},
            },
            {
                "id": "af626c54-156e-4f13-a743-55efd27de533",
                "name": "sharpening",
                "block": {"name": "sharpening"},
            },
        ],
        "error": {},
    }
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
        "block": {"name": "sobloo-s2-l1c-aoiclipped"},
    }

    with requests_mock.Mocker() as m:
        m.get(url=url_workflow_tasks, json=json_workflow_tasks)
        tasks = workflow_mock.get_workflow_tasks(basic=True)
    assert len(tasks) == 2
    assert tasks["sobloo-s2-l1c-aoiclipped:1"] == "c0d04ec3-98d7-4183-902f-5bcb2a176d89"


def test_get_workflow_tasks_live(workflow_live):
    workflow_tasks = workflow_live.get_workflow_tasks(basic=True)
    assert isinstance(workflow_tasks, dict)
    assert "sobloo-s2-l1c-aoiclipped:1" in list(workflow_tasks.keys())


def test_construct_full_workflow_tasks_dict():
    # TODO: Mock get_blocks!
    pass


def test_add_workflow_tasks():
    pass


@pytest.mark.live
def test_add_workflow_tasks_live():
    pass


def test_get_parameter_info():
    pass


def test_get_parameter_info_live():
    pass


def test_get_default_parameters():
    pass


def test_construct_parameter():
    pass


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


def test_get_jobs():
    pass


def test_get_jobs_live():
    pass


def test_update_name():
    pass


def test_delete():
    pass
