import os

import pytest
import requests_mock

from .context import (
    Auth,
    Project,
    Workflow,
    Job,
    JobCollection,
    JobTask,
    Tools,
    Catalog,
)


TOKEN = "token_123"
DOWNLOAD_URL = "http://up42.api.com/abcdef"

PROJECT_ID = "project_id_123"
PROJECT_APIKEY = "project_apikey_123"
PROJECT_NAME = "project_name_123"
PROJECT_DESCRIPTION = "project_description_123"

WORKFLOW_ID = "workflow_id_123"
WORKFLOW_NAME = "workflow_name_123"
WORKFLOW_DESCRIPTION = "workflow_description_123"

JOB_ID = "job_id_123"
JOB_ID_2 = "jobid_456"
JOB_NAME = "job_name_123"

JOBTASK_ID = "jobtask_id_123"
JOBTASK_NAME = "jobtask_name_123"


JSON_WORKFLOW_TASKS = {
    "data": [
        {
            "id": "c0d04ec3-98d7-4183-902f-5bcb2a176d89",
            "name": "sobloo-s2-l1c-aoiclipped:1",
            "blockVersionTag": "2.2.2",
            "block": {
                "name": "sobloo-s2-l1c-aoiclipped",
                "parameters": {
                    "nodata": {
                        "type": "number",
                    },
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
            "blockVersionTag": "1.0.0",
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

JSON_BLOCKS = {
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


# TODO: Use patch.dict instead of 2 fictures?
@pytest.fixture()
def auth_mock_no_request(requests_mock):
    auth = Auth(
        project_id=PROJECT_ID,
        project_api_key=PROJECT_APIKEY,
        authenticate=False,
        retry=False,
        get_info=False,
    )

    url_get_token = (
        f"https://{auth.project_id}:{auth.project_api_key}@api.up42."
        f"{auth.env}/oauth/token"
    )
    json_get_token = {"data": {"accessToken": TOKEN}}
    requests_mock.post(
        url=url_get_token,
        json=json_get_token,
    )

    return auth


@pytest.fixture()
def auth_mock(requests_mock):
    # token for initial authentication
    url_get_token = f"https://{PROJECT_ID}:{PROJECT_APIKEY}@api.up42.com/oauth/token"
    json_get_token = {"data": {"accessToken": TOKEN}}
    requests_mock.post(
        url=url_get_token,
        json=json_get_token,
    )
    auth = Auth(
        project_id=PROJECT_ID,
        project_api_key=PROJECT_APIKEY,
        authenticate=True,
        retry=False,
        get_info=True,
    )

    # get_blocks
    url_get_blocks = f"{auth._endpoint()}/blocks"
    requests_mock.get(
        url=url_get_blocks,
        json=JSON_BLOCKS,
    )

    return auth


@pytest.fixture()
def auth_live():
    auth = Auth(
        project_id=os.getenv("TEST_UP42_PROJECT_ID"),
        project_api_key=os.getenv("TEST_UP42_PROJECT_API_KEY"),
    )
    return auth


@pytest.fixture()
def project_mock(auth_mock, requests_mock):
    # info
    url_project_info = f"{auth_mock._endpoint()}/projects/{auth_mock.project_id}"
    json_project_info = {"data": {"xyz": 789}, "error": {}}
    requests_mock.get(url=url_project_info, json=json_project_info)

    project = Project(auth=auth_mock, project_id=auth_mock.project_id)

    # create_workflow. If with use_existing=True, requires workflow info mock.
    url_create_workflow = (
        f"{project.auth._endpoint()}/projects/" f"{project.project_id}/workflows/"
    )
    json_create_workflow = {
        "error": {},
        "data": {"id": WORKFLOW_ID, "displayId": "workflow_displayId_123"},
    }
    requests_mock.post(url=url_create_workflow, json=json_create_workflow)

    # get_workflows
    url_get_workflows = (
        f"{project.auth._endpoint()}/projects/" f"{project.project_id}/workflows"
    )
    json_get_workflows = {
        "data": [{"id": WORKFLOW_ID}, {"id": WORKFLOW_ID}],
        "error": {},
    }  # Same workflow_id to not have to get multiple .info
    requests_mock.get(url=url_get_workflows, json=json_get_workflows)

    # get_jobs. Requires job_info mock.

    url_get_jobs = f"{project.auth._endpoint()}/projects/{project.project_id}/jobs"
    json_get_jobs = {
        "data": [
            {
                "id": JOB_ID,
                "status": "SUCCEEDED",
                "inputs": {},
                "error": {},
                "mode": "DEFAULT",
            }
        ]
    }
    requests_mock.get(url=url_get_jobs, json=json_get_jobs)

    # project_settings
    url_project_settings = (
        f"{project.auth._endpoint()}/projects/{project.project_id}/settings"
    )
    json_project_settings = {
        "data": [
            {"name": "MAX_CONCURRENT_JOBS"},
            {"name": "MAX_AOI_SIZE"},
            {"name": "JOB_QUERY_LIMIT_PARAMETER_MAX_VALUE"},
        ],
        "error": {},
    }
    requests_mock.get(url=url_project_settings, json=json_project_settings)

    return project


@pytest.fixture()
def project_live(auth_live):
    project = Project(auth=auth_live, project_id=auth_live.project_id)
    return project


@pytest.fixture()
def workflow_mock(auth_mock, requests_mock):
    # info
    url_workflow_info = (
        f"{auth_mock._endpoint()}/projects/"
        f"{auth_mock.project_id}/workflows/"
        f"{WORKFLOW_ID}"
    )
    json_workflow_info = {
        "data": {
            "name": WORKFLOW_NAME,
            "id": WORKFLOW_ID,
            "xyz": 789,
        },
        "error": {},
    }
    requests_mock.get(url=url_workflow_info, json=json_workflow_info)

    workflow = Workflow(
        auth=auth_mock,
        workflow_id=WORKFLOW_ID,
        project_id=auth_mock.project_id,
    )

    # get_workflow_tasks
    url_workflow_tasks = (
        f"{workflow.auth._endpoint()}/projects/{workflow.auth.project_id}/workflows/"
        f"{workflow.workflow_id}/tasks"
    )
    requests_mock.get(url=url_workflow_tasks, json=JSON_WORKFLOW_TASKS)

    # get_compatible_blocks
    url_compatible_blocks = (
        f"{workflow.auth._endpoint()}/projects/{workflow.project_id}/"
        f"workflows/{workflow.workflow_id}/compatible-blocks?parentTaskName=tiling:1"
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
    requests_mock.get(url=url_compatible_blocks, json=json_compatible_blocks)

    # run_job
    url_run_job = (
        f"{workflow.auth._endpoint()}/projects/{workflow.project_id}/"
        f"workflows/{workflow.workflow_id}/jobs?name={JOB_NAME + '_py'}"
    )
    json_run_job = {"data": {"id": JOB_ID}}
    requests_mock.post(url=url_run_job, json=json_run_job)

    # get_jobs
    url_get_jobs = f"{workflow.auth._endpoint()}/projects/{workflow.project_id}/jobs"
    json_get_jobs = {
        "data": [
            {
                "id": JOB_ID,
                "status": "SUCCEEDED",
                "inputs": {},
                "error": {},
                "mode": "DEFAULT",
                "workflowId": "123456",
            },
            {
                "id": JOB_ID,
                "status": "SUCCEEDED",
                "inputs": {},
                "error": {},
                "mode": "DEFAULT",
                "workflowId": workflow.workflow_id,
            },
        ]
    }
    requests_mock.get(url=url_get_jobs, json=json_get_jobs)

    return workflow


@pytest.fixture()
def workflow_live(auth_live):
    workflow = Workflow(
        auth=auth_live,
        project_id=auth_live.project_id,
        workflow_id=os.getenv("TEST_UP42_WORKFLOW_ID"),
    )
    return workflow


@pytest.fixture()
def job_mock(auth_mock, requests_mock):
    url_job_info = (
        f"{auth_mock._endpoint()}/projects/{auth_mock.project_id}/jobs/{JOB_ID}"
    )
    json_job_info = {"data": {"xyz": 789, "mode": "DEFAULT"}, "error": {}}
    requests_mock.get(url=url_job_info, json=json_job_info)

    job = Job(auth=auth_mock, project_id=auth_mock.project_id, job_id=JOB_ID)

    # get_jobtasks
    url_job_tasks = (
        f"{job.auth._endpoint()}/projects/{job.project_id}/jobs/{job.job_id}/tasks/"
    )
    requests_mock.get(url=url_job_tasks, json={"data": [{"id": JOBTASK_ID}]})

    # get_logs
    url_logs = (
        f"{job.auth._endpoint()}/projects/{job.project_id}/jobs/"
        f"{job.job_id}/tasks/{JOBTASK_ID}/logs"
    )
    requests_mock.get(url_logs, json="")

    # quicklooks
    url_quicklook = (
        f"{job.auth._endpoint()}/projects/{job.project_id}/jobs/{job.job_id}"
        f"/tasks/{JOBTASK_ID}/outputs/quicklooks/"
    )
    requests_mock.get(url_quicklook, json={"data": ["a_quicklook.png"]})

    # get_results_json
    url = (
        f"{job.auth._endpoint()}/projects/{job.project_id}/jobs/{job.job_id}"
        f"/outputs/data-json/"
    )
    requests_mock.get(url, json={"type": "FeatureCollection", "features": []})

    # get_jobtasks_results_json
    url = (
        f"{job.auth._endpoint()}/projects/{job.project_id}/jobs/{job.job_id}"
        f"/tasks/{JOBTASK_ID}/outputs/data-json"
    )
    requests_mock.get(url, json={"type": "FeatureCollection", "features": []})

    # get_download_url
    url_download_result = (
        f"{job.auth._endpoint()}/projects/"
        f"{job.project_id}/jobs/{job.job_id}/downloads/results/"
    )
    requests_mock.get(
        url_download_result, json={"data": {"url": DOWNLOAD_URL}, "error": {}}
    )

    return job


@pytest.fixture()
def job_live(auth_live):
    job = Job(
        auth=auth_live,
        project_id=auth_live.project_id,
        job_id=os.getenv("TEST_UP42_JOB_ID"),
    )
    return job


@pytest.fixture()
def jobs_mock(auth_mock, requests_mock):
    url_job_info = (
        f"{auth_mock._endpoint()}/projects/{auth_mock.project_id}/jobs/{JOB_ID}"
    )
    requests_mock.get(
        url=url_job_info,
        json={"data": {"xyz": 789, "mode": "DEFAULT"}, "error": {}},
    )

    job1 = Job(auth=auth_mock, project_id=auth_mock.project_id, job_id=JOB_ID)

    url_job_info = (
        f"{auth_mock._endpoint()}/projects/{auth_mock.project_id}/jobs/{JOB_ID_2}"
    )
    requests_mock.get(url=url_job_info, json={"data": {"xyz": 789}, "error": {}})

    job2 = Job(auth=auth_mock, project_id=auth_mock.project_id, job_id=JOB_ID_2)
    return [job1, job2]


@pytest.fixture()
def jobs_live(auth_live):
    job_1 = Job(
        auth=auth_live,
        project_id=auth_live.project_id,
        job_id=os.getenv("TEST_UP42_JOB_ID"),
    )

    job_2 = Job(
        auth=auth_live,
        project_id=auth_live.project_id,
        job_id=os.getenv("TEST_UP42_JOB_ID_2"),
    )

    return [job_1, job_2]


@pytest.fixture()
def jobcollection_single_mock(auth_mock, job_mock):
    return JobCollection(
        auth=auth_mock, project_id=auth_mock.project_id, jobs=[job_mock]
    )


@pytest.fixture()
def jobcollection_multiple_mock(auth_mock, jobs_mock):
    return JobCollection(
        auth=auth_mock, project_id=auth_mock.project_id, jobs=jobs_mock
    )


@pytest.fixture()
def jobcollection_empty_mock(auth_mock):
    return JobCollection(auth=auth_mock, project_id=auth_mock.project_id, jobs=[])


@pytest.fixture()
def jobcollection_live(auth_live, jobs_live):
    return JobCollection(
        auth=auth_live, project_id=auth_live.project_id, jobs=jobs_live
    )


@pytest.fixture()
def jobtask_mock(auth_mock, requests_mock):
    # info
    url_jobtask_info = (
        f"{auth_mock._endpoint()}/projects/{auth_mock.project_id}/jobs/{JOB_ID}"
        f"/tasks/"
    )
    requests_mock.get(url=url_jobtask_info, json={"data": {"xyz": 789}, "error": {}})

    jobtask = JobTask(
        auth=auth_mock,
        project_id=auth_mock.project_id,
        job_id=JOB_ID,
        jobtask_id=JOBTASK_ID,
    )

    # get_results_json
    url = (
        f"{jobtask.auth._endpoint()}/projects/{jobtask.auth.project_id}/"
        f"jobs/{jobtask.job_id}/tasks/{jobtask.jobtask_id}/"
        f"outputs/data-json/"
    )
    requests_mock.get(url, json={"type": "FeatureCollection", "features": []})

    # get_download_url
    url_download_result = (
        f"{jobtask.auth._endpoint()}/projects/{jobtask.project_id}/"
        f"jobs/{jobtask.job_id}/tasks/{jobtask.jobtask_id}/"
        f"downloads/results/"
    )
    requests_mock.get(
        url_download_result, json={"data": {"url": DOWNLOAD_URL}, "error": {}}
    )

    # quicklooks
    url_quicklook = (
        f"{jobtask.auth._endpoint()}/projects/{jobtask.project_id}/"
        f"jobs/{jobtask.job_id}"
        f"/tasks/{jobtask.jobtask_id}/outputs/quicklooks/"
    )
    requests_mock.get(url_quicklook, json={"data": ["a_quicklook.png"]})

    return jobtask


@pytest.fixture()
def jobtask_live(auth_live):
    jobtask = JobTask(
        auth=auth_live,
        project_id=auth_live.project_id,
        job_id=os.getenv("TEST_UP42_JOB_ID"),
        jobtask_id=os.getenv("TEST_UP42_JOBTASK_ID"),
    )
    return jobtask


@pytest.fixture()
def tools_mock(auth_mock):
    return Tools(auth=auth_mock)


@pytest.fixture()
def tools_live(auth_live):
    return Tools(auth=auth_live)


@pytest.fixture()
def catalog_mock(auth_mock):
    return Catalog(auth=auth_mock)


@pytest.fixture()
def catalog_live(auth_live):
    return Catalog(auth=auth_live)


@pytest.fixture()
def project_mock_max_concurrent_jobs(project_mock):
    def _project_mock_max_concurrent_jobs(maximum=5):
        m = requests_mock.Mocker()
        url_project_info = (
            f"{project_mock.auth._endpoint()}/projects/{project_mock.project_id}"
        )
        m.get(url=url_project_info, json={"data": {"xyz": 789}, "error": {}})
        url_project_settings = (
            f"{project_mock.auth._endpoint()}/projects"
            f"/{project_mock.project_id}/settings"
        )
        m.get(
            url=url_project_settings,
            json={
                "data": [
                    {"name": "MAX_CONCURRENT_JOBS", "value": str(maximum)},
                    {"name": "MAX_AOI_SIZE", "value": "1000"},
                    {"name": "JOB_QUERY_LIMIT_PARAMETER_MAX_VALUE", "value": "200"},
                ],
                "error": {},
            },
        )
        return m

    return _project_mock_max_concurrent_jobs
