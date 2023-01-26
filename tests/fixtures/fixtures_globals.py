TOKEN = "token_123"
DOWNLOAD_URL = "http://up42.api.com/abcdef.tgz"

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

DATA_PRODUCT_ID = "data_product_id_123"

ORDER_ID = "order_id_123"
ASSET_ID = "asset_id_123"

WEBHOOK_ID = "123"

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
                    "time": {
                        "type": "dateRange",
                        "default": "2018-01-01T00:00:00+00:00/2020-12-31T23:59:59+00:00",
                    },
                    "ids": {"type": "array", "default": None},
                    "bbox": {"type": "array", "default": None},
                    "intersects": {"type": "geometry"},
                },
                "type": "DATA",
                "isDryRunSupported": True,
                "version": "1.0.1",
            },
            "environment": None,
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
                        "default": None,
                        "required": False,
                        "description": "Value representing ...",
                    },
                    "tile_width": {
                        "type": "number",
                        "default": 768,
                        "required": True,
                        "description": "Width of a tile in pixels",
                    },
                    "required_but_no_default": {
                        "type": "number",
                        "required": True,
                        "description": "case for tests",
                    },
                    "not_required_no_default": {
                        "type": "number",
                        "required": False,
                        "description": "2nd case for tests",
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
    "id": ASSET_ID,
    "accountId": "69353acb-f942-423f-8f32-11d6d67caa77",
    "workspaceId": WORKSPACE_ID,
    "size": 256248634,
    "name": "string",
    "createdAt": "2022-12-07T14:25:34.968Z",
    "updatedAt": "2022-12-07T14:25:34.968Z",
    "contentType": "string",
    "producerName": "string",
    "collectionName": "string",
    "productId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "source": "ARCHIVE",
    "order": {"id": "string", "status": "string", "hostId": "string"},
    "title": "string",
    "tags": ["string"],
}

JSON_ASSETS = {
    "content": [JSON_ASSET],
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

JSON_ORDERS = {
    "data": {
        "content": [JSON_ORDER["data"]],
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

JSON_WEBHOOK = {
    "data": {
        "url": "https://test-info-webhook.com",
        "name": "test_info_webhook",
        "active": False,
        "events": ["job.status"],
        "id": WEBHOOK_ID,
        "secret": "",
        "createdAt": "2022-06-20T04:05:31.755744Z",
        "updatedAt": "2022-06-20T04:05:31.755744Z",
    }
}

JSON_BALANCE = {"data": {"balance": 10693}}

MOCK_CREDITS = {
    "data": {
        "projectId": "20adecb9-97f6-42c0-8ba8-f1e2fa0bff39",
        "projectDisplayId": "20adecb9",
        "jobId": "feace0bb-ea26-4161-9026-852f26e46bc5",
        "jobDisplayId": "feace0bb",
        "creditsUsed": 100,
    },
    "error": None,
}
