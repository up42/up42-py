import os
import json
from pathlib import Path
import copy

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
    Estimation,
    Storage,
    Asset,
    Order,
)


TOKEN = "token_123"
DOWNLOAD_URL = "http://up42.api.com/abcdef"

PROJECT_ID = "project_id_123"
PROJECT_APIKEY = "project_apikey_123"
WORKSPACE_ID = "workspace_id_123"
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

ORDER_ID = "order_id_123"
ASSET_ID = "asset_id_123"

JSON_WORKFLOW_TASKS = {
    "error": "None",
    "data": [
        {
            "id": "aa2cba17-d35c-4395-ab01-a0fd8191a4b3",
            "name": "esa-s2-l2a-gtiff-visual:1",
            "parentsIds": [],
            "blockName": "esa-s2-l2a-gtiff-visual",
            "blockVersionTag": "1.0.1",
            "block": {
                "id": "c4cb8913-2ef3-4e82-a426-65ea8faacd9a",
                "name": "esa-s2-l2a-gtiff-visual",
                "displayName": "Sentinel-2 L2A Visual (GeoTIFF)",
                "parameters": {
                    "ids": {"type": "array", "default": "None"},
                    "bbox": {"type": "array", "default": "None"},
                    "time": {
                        "type": "dateRange",
                        "default": "2018-01-01T00:00:00+00:00/2020-12-31T23:59:59+00:00",
                    },
                },
                "type": "DATA",
                "isDryRunSupported": True,
                "version": "1.0.1",
            },
            "environment": "None",
        },
        {
            "id": "24375b2a-288b-46c8-b404-53e48d4e7b25",
            "name": "tiling:1",
            "parentsIds": ["aa2cba17-d35c-4395-ab01-a0fd8191a4b3"],
            "blockName": "tiling",
            "blockVersionTag": "2.2.3",
            "block": {
                "id": "3e146dd6-2b67-4d6e-a422-bb3d973e32ff",
                "name": "tiling",
                "displayName": "Raster Tiling",
                "parameters": {
                    "nodata": {
                        "type": "number",
                        "default": "None",
                        "required": False,
                        "description": "Value representing ...",
                    },
                    "tile_width": {
                        "type": "number",
                        "default": 768,
                        "required": True,
                        "description": "Width of a tile in pixels",
                    },
                },
                "type": "PROCESSING",
                "isDryRunSupported": False,
                "version": "2.2.3",
            },
            "environment": "None",
        },
    ],
}

JSON_BLOCKS = {
    "data": [
        {
            "id": "4ed70368-d4e1-4462-bef6-14e768049471",
            "name": "tiling",
            "displayName": "Raster Tiling",
            "type": "PROCESSING",
        },
        {
            "id": "c0d04ec3-98d7-4183-902f-5bcb2a176d89",
            "name": "sharpening",
            "displayName": "Sharpening Filter",
            "type": "PROCESSING",
        },
        {
            "id": "c4cb8913-2ef3-4e82-a426-65ea8faacd9a",
            "name": "esa-s2-l2a-gtiff-visual",
            "displayName": "Sentinel-2 L2A Visual (GeoTIFF)",
            "type": "DATA",
        },
    ],
    "error": {},
}

JSON_WORKFLOW_ESTIMATION = {
    "data": {
        "esa-s2-l2a-gtiff-visual:1": {
            "blockConsumption": {
                "credit": {"max": 0, "min": 0},
                "resources": {"max": 0, "min": 0, "unit": "SQUARE_KM"},
            },
            "machineConsumption": {
                "credit": {"max": 1, "min": 1},
                "duration": {"max": 0, "min": 0},
            },
        },
        "tiling:1": {
            "blockConsumption": {
                "credit": {"max": 0, "min": 0},
                "resources": {"max": 3.145728, "min": 3.145728, "unit": "MEGABYTE"},
            },
            "machineConsumption": {
                "credit": {"max": 9, "min": 2},
                "duration": {"max": 428927, "min": 80930},
            },
        },
    },
    "error": {},
}

JSON_ASSET = {
    "data": {
        "id": ASSET_ID,
        "workspaceId": WORKSPACE_ID,
        "createdAt": "2020-12-17T10:41:24.774111Z",
        "type": "ARCHIVED",
        "source": "BLOCK",
        "name": "DS_PHR1B_201903161028440_FR1_PX_E008N47_0606_04372",
        "size": 3920650,
        "createdBy": {"id": "system", "type": "INTERNAL"},
        "updatedBy": {"id": "system", "type": "INTERNAL"},
        "updatedAt": "2020-12-17T10:41:24.774111Z",
    },
    "error": None,
}

JSON_ASSETS = {
    "data": {
        "content": [JSON_ASSET["data"]],
        "pageable": {
            "sort": {"sorted": True, "unsorted": False, "empty": False},
            "pageNumber": 0,
            "pageSize": 10,
            "offset": 0,
            "paged": True,
            "unpaged": False,
        },
        "totalPages": 1,
        "totalElements": 1,
        "last": True,
        "sort": {"sorted": True, "unsorted": False, "empty": False},
        "numberOfElements": 1,
        "first": True,
        "size": 10,
        "number": 0,
        "empty": False,
    },
    "error": None,
}

JSON_ORDER = {
    "data": {
        "id": ORDER_ID,
        "userId": "1094497b-11d8-4fb8-9d6a-5e24a88aa825",
        "workspaceId": WORKSPACE_ID,
        "dataProvider": "OneAtlas",
        "status": "FULFILLED",
        "createdAt": "2021-01-18T16:18:16.105851Z",
        "updatedAt": "2021-01-18T16:21:31.966805Z",
        "assets": [ASSET_ID],
        "createdBy": {"id": "1094497b-11d8-4fb8-9d6a-5e24a88aa825", "type": "USER"},
        "updatedBy": {"id": "system", "type": "INTERNAL"},
    },
    "error": None,
}

JSON_ORDERS = {"data": {"orders": [JSON_ORDER["data"]]}, "error": None}


@pytest.fixture()
def auth_mock(requests_mock):
    # token for initial authentication
    url_get_token = "https://api.up42.com/oauth/token"
    json_get_token = {
        "data": {"accessToken": TOKEN},
        "access_token": TOKEN,
        "token_type": "bearer",
    }
    requests_mock.post(url_get_token, json=json_get_token)

    url_get_workspace = f"https://api.up42.com/projects/{PROJECT_ID}"
    json_get_workspace = {"data": {"workspaceId": WORKSPACE_ID}}
    requests_mock.get(
        url=url_get_workspace,
        json=json_get_workspace,
    )
    auth = Auth(
        project_id=PROJECT_ID,
        project_api_key=PROJECT_APIKEY,
        authenticate=True,
        retry=False,
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
    json_project_info = {
        "data": {
            "xyz": 789,
            "workspaceId": WORKSPACE_ID,
            "name": PROJECT_NAME,
            "description": PROJECT_DESCRIPTION,
            "createdAt": "some_date",
        },
        "error": {},
    }
    requests_mock.get(url=url_project_info, json=json_project_info)

    project = Project(auth=auth_mock, project_id=auth_mock.project_id)

    # create_workflow.
    url_create_workflow = (
        f"{project.auth._endpoint()}/projects/" f"{project.project_id}/workflows/"
    )
    json_create_workflow = {
        "error": {},
        "data": {"id": WORKFLOW_ID, "displayId": "workflow_displayId_123"},
    }
    requests_mock.post(url=url_create_workflow, json=json_create_workflow)

    # workflow.info (for create_workflow)
    url_workflow_info = (
        f"{project.auth._endpoint()}/projects/"
        f"{project.project_id}/workflows/{WORKFLOW_ID}"
    )
    json_workflow_info = {
        "data": {
            "name": WORKFLOW_NAME,
            "description": WORKFLOW_DESCRIPTION,
        },
        "error": {},
    }
    requests_mock.get(url=url_workflow_info, json=json_workflow_info)

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
            {"name": "MAX_CONCURRENT_JOBS", "value": "10"},
            {"name": "MAX_AOI_SIZE", "value": "5000"},
            {"name": "JOB_QUERY_LIMIT_PARAMETER_MAX_VALUE", "value": "20"},
        ],
        "error": {},
    }
    requests_mock.get(url=url_project_settings, json=json_project_settings)

    # project settings update
    url_projects_settings_update = (
        f"{project.auth._endpoint()}/projects/project_id_123/settings"
    )
    json_desired_project_settings = {
        "data": [
            {"name": "MAX_CONCURRENT_JOBS", "value": "500"},
            {"name": "MAX_AOI_SIZE", "value": "5"},
            {"name": "JOB_QUERY_LIMIT_PARAMETER_MAX_VALUE", "value": "20"},
        ],
        "error": {},
    }
    requests_mock.post(
        url_projects_settings_update,
        [
            {"status_code": 404, "json": json_desired_project_settings},
            {"status_code": 201, "json": json_desired_project_settings},
        ],
    )

    return project


@pytest.fixture()
def project_live(auth_live):
    project = Project(auth=auth_live, project_id=auth_live.project_id)
    return project


@pytest.fixture()
def workflow_mock_empty(auth_mock, requests_mock):
    """
    Only to test error handling of functions that don't correctly work on workflows
    without tasks (blocks). For the fully mocked workflow see workflow_mock fixture.
    """
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
            "description": PROJECT_DESCRIPTION,
            "createdAt": "some_date",
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
    json_empty_workflow_tasks = {
        "error": "None",
        "data": [],
    }
    url_workflow_tasks = (
        f"{workflow.auth._endpoint()}/projects/{workflow.auth.project_id}/workflows/"
        f"{workflow.workflow_id}/tasks"
    )
    requests_mock.get(url=url_workflow_tasks, json=json_empty_workflow_tasks)

    return workflow


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
            "description": PROJECT_DESCRIPTION,
            "createdAt": "some_date",
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
    json_job_info = {
        "data": {
            "xyz": 789,
            "mode": "DEFAULT",
            "description": "some_description",
            "startedAt": "some_date",
            "workflowName": WORKFLOW_NAME,
            "name": JOB_NAME,
            "finishedAt": "some_date",
            "status": "SUCCESSFULL",
            "inputs": "some_inputs",
        },
        "error": {},
    }
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
def estimation_mock(auth_mock):
    input_parameters = {
        "esa-s2-l2a-gtiff-visual:1": {
            "time": "2018-01-01T00:00:00+00:00/2020-12-31T23:59:59+00:00",
            "limit": 1,
            "bbox": [13.33409, 52.474922, 13.38547, 52.500398],
        },
        "tiling:1": {"tile_width": 768},
    }

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

    return Estimation(auth_mock, input_parameters, input_tasks)


@pytest.fixture()
def estimation_live(auth_live):
    input_parameters = {
        "esa-s2-l2a-gtiff-visual:1": {
            "time": "2018-01-01T00:00:00+00:00/2020-12-31T23:59:59+00:00",
            "limit": 1,
            "bbox": [13.33409, 52.474922, 13.38547, 52.500398],
        },
        "tiling:1": {"tile_width": 768},
    }

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
    return Estimation(auth_live, input_parameters, input_tasks)


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
    requests_mock.get(
        url=url_jobtask_info,
        json={
            "data": [
                {
                    "xyz": 789,
                    "name": JOBTASK_NAME,
                    "status": "SUCCESSFULL",
                    "startedAt": "some_date",
                    "finishedAt": "some_date",
                    "block": {"name": "a_block"},
                    "blockVersion": "1.0.0",
                }
            ],
            "error": {},
        },
    )

    jobtask = JobTask(
        auth=auth_mock,
        project_id=auth_mock.project_id,
        job_id=JOB_ID,
        jobtask_id=JOBTASK_ID,
    )

    # get_results_json
    url_results_json = (
        f"{jobtask.auth._endpoint()}/projects/{jobtask.auth.project_id}/"
        f"jobs/{jobtask.job_id}/tasks/{jobtask.jobtask_id}/"
        f"outputs/data-json/"
    )
    requests_mock.get(
        url_results_json, json={"type": "FeatureCollection", "features": []}
    )

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
def storage_mock(auth_mock, requests_mock):
    # assets
    url_storage_assets = (
        f"{auth_mock._endpoint()}/workspaces/{auth_mock.workspace_id}/assets"
    )
    requests_mock.get(url=url_storage_assets, json=JSON_ASSETS)

    # asset info
    url_asset_info = (
        f"{auth_mock._endpoint()}/workspaces/{auth_mock.workspace_id}/assets/{ASSET_ID}"
    )
    requests_mock.get(url=url_asset_info, json=JSON_ASSET)

    # orders
    url_storage_assets = (
        f"{auth_mock._endpoint()}/workspaces/{auth_mock.workspace_id}/orders"
    )
    requests_mock.get(url=url_storage_assets, json=JSON_ORDERS)

    # orders info
    url_order_info = (
        f"{auth_mock._endpoint()}/workspaces/{auth_mock.workspace_id}/orders/{ORDER_ID}"
    )
    requests_mock.get(url=url_order_info, json=JSON_ORDER)

    storage = Storage(auth=auth_mock)

    return storage


@pytest.fixture()
def storage_live(auth_live):
    storage = Storage(auth=auth_live)
    return storage


@pytest.fixture()
def asset_mock(auth_mock, requests_mock):

    # asset info
    url_asset_info = (
        f"{auth_mock._endpoint()}/workspaces/{auth_mock.workspace_id}/assets/{ASSET_ID}"
    )
    requests_mock.get(url=url_asset_info, json=JSON_ASSET)

    # url
    requests_mock.get(
        url=f"{auth_mock._endpoint()}/workspaces/{auth_mock.workspace_id}/assets/{ASSET_ID}/downloadUrl",
        json={"data": {"url": DOWNLOAD_URL}},
    )

    asset = Asset(auth=auth_mock, asset_id=ASSET_ID)

    return asset


@pytest.fixture()
def asset_live(auth_live):
    asset = Asset(auth=auth_live, asset_id=os.getenv("TEST_UP42_ASSET_ID"))
    return asset


@pytest.fixture()
def order_mock(auth_mock, requests_mock):
    # order info
    url_order_info = (
        f"{auth_mock._endpoint()}/workspaces/{auth_mock.workspace_id}/orders/{ORDER_ID}"
    )
    requests_mock.get(url=url_order_info, json=JSON_ORDER)

    # metadata
    requests_mock.get(
        url=f"{auth_mock._endpoint()}/workspaces/{auth_mock.workspace_id}/orders/{ORDER_ID}/metadata",
        json={
            "data": {
                "id": ORDER_ID,
                "userId": "1094497b-11d8-4fb8-9d6a-5e24a88aa825",
                "customerReference": "158e8ca9-c5e9-4705-8f44-7aefee1d33ff",
                "sqKmArea": 0.1,
                "createdAt": "2021-01-18T16:18:19.395198Z",
                "updatedAt": "2021-01-18T16:18:19.395198Z",
            },
            "error": None,
        },
    )

    order = Order(auth=auth_mock, order_id=ORDER_ID)

    return order


@pytest.fixture()
def order_live(auth_live):
    order = Order(auth=auth_live, order_id=os.getenv("TEST_UP42_ORDER_ID"))
    return order


@pytest.fixture()
def tools_mock(auth_mock):
    return Tools(auth=auth_mock)


@pytest.fixture()
def tools_live(auth_live):
    return Tools(auth=auth_live)


@pytest.fixture()
def catalog_mock(auth_mock, requests_mock):
    with open(
        Path(__file__).resolve().parent / "mock_data/search_response.json"
    ) as json_file:
        json_search_response = json.load(json_file)
    url_search = f"{auth_mock._endpoint()}/catalog/stac/search"
    requests_mock.post(
        url=url_search,
        json=json_search_response,
    )

    return Catalog(auth=auth_mock)


@pytest.fixture()
def catalog_live(auth_live):
    return Catalog(auth=auth_live)


@pytest.fixture()
def catalog_pagination_mock(auth_mock, requests_mock):
    with open(
        Path(__file__).resolve().parent / "mock_data/search_response.json"
    ) as json_file:
        search_response_json = json.load(json_file)
    search_response_json["features"] = search_response_json["features"] * 500

    pagination_response_json = copy.deepcopy(search_response_json)
    pagination_response_json["features"] = pagination_response_json["features"][:50]
    pagination_response_json["links"][1] = pagination_response_json["links"][
        0
    ]  # indicator of pagination exhaustion (after first page)

    url_search = f"{auth_mock._endpoint()}/catalog/stac/search"
    requests_mock.post(
        url_search,
        [{"json": search_response_json}, {"json": pagination_response_json}],
    )

    return Catalog(auth=auth_mock)


@pytest.fixture()
def catalog_usagetype_mock(auth_mock, requests_mock):
    with open(
        Path(__file__).resolve().parent / "mock_data/search_response.json"
    ) as json_file:
        search_response_json = json.load(
            json_file
        )  # original response is usagetype data

    response_analytics = copy.deepcopy(search_response_json)
    response_analytics["features"][0]["properties"]["up42:usageType"] = ["ANALYTICS"]
    response_data_and_analytics = copy.deepcopy(search_response_json)
    response_data_and_analytics["features"][0]["properties"]["up42:usageType"] = [
        "DATA",
        "ANALYTICS",
    ]

    url_search = f"{auth_mock._endpoint()}/catalog/stac/search"
    requests_mock.post(
        url_search,
        [
            {"json": search_response_json},
            {"json": response_analytics},
            {"json": response_data_and_analytics},
        ],
    )

    return Catalog(auth=auth_mock)


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
