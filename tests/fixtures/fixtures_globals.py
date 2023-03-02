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
    "accountId": "69353acb-f942-423f-8f32-11d6d67caa77",
    "createdAt": "2022-12-07T14:25:34.968Z",
    "updatedAt": "2022-12-07T14:25:34.968Z",
    "id": ASSET_ID,
    "name": "string",
    "size": 256248634,
    "workspaceId": WORKSPACE_ID,
    "order": {"id": "string", "status": "string", "hostId": "string"},
    "source": "ARCHIVE",
    "productId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "contentType": "string",
    "producerName": "string",
    "collectionName": "string",
    "geospatialMetadataExtraction": "SUCCESSFUL",
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

JSON_STORAGE_STAC = {
    "links": [
        {
            "href": "https://api.up42.dev/v2/assets/stac/",
            "rel": "root",
            "type": "application/json",
        },
        {
            "href": "https://api.up42.dev/v2/assets/stac/search",
            "rel": "next",
            "type": "application/json",
            "body": {
                "sortby": [{"field": "bbox", "direction": "desc"}],
                "filter": {},
                "token": "next:12345",
            },
            "method": "POST",
        },
    ],
    "type": "FeatureCollection",
    "features": [
        {
            "assets": {
                "data": {
                    "href": "https://api.up42.dev/v2/assets/01ad657e-12f7-4046-a94c-abc90d86106a"
                }
            },
            "links": [
                {
                    "href": "https://api.up42.dev/v2/assets/stac/collections/69ce89b4-fa35-4a1a-bcd8-1c2e5bbd2ee6/"
                    "items/e986e18a-0392-4b82-93c9-7a0af15846d0",
                    "rel": "self",
                    "type": "application/geo+json",
                },
                {
                    "href": "https://api.up42.dev/v2/assets/stac/collections/69ce89b4-fa35-4a1a-bcd8-1c2e5bbd2ee6",
                    "rel": "parent",
                    "type": "application/json",
                },
                {
                    "href": "https://api.up42.dev/v2/assets/stac/collections/69ce89b4-fa35-4a1a-bcd8-1c2e5bbd2ee6",
                    "rel": "collection",
                    "type": "application/json",
                },
                {
                    "href": "https://api.up42.dev/v2/assets/stac/",
                    "rel": "root",
                    "type": "application/json",
                },
            ],
            "stac_extensions": [
                "https://stac-extensions.github.io/projection/v1.0.0/schema.json",
                "https://api.up42.com/stac-extensions/up42-product/v1.0.0/schema.json",
            ],
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [52.4941111111112, 13.4025555555556],
                        [52.4941111111112, 13.4111666666667],
                        [52.4911111111112, 13.4111666666667],
                        [52.4911111111112, 13.4025555555556],
                        [52.4941111111112, 13.4025555555556],
                        [52.4941111111112, 13.4025555555556],
                    ]
                ],
            },
            "bbox": [
                52.4911111111112,
                13.4025555555556,
                52.4941111111112,
                13.4111666666667,
            ],
            "properties": {
                "up42-system:asset_id": ASSET_ID,
                "gsd": 9.118863577837482,
                "datetime": "2021-05-31T09:51:52.100000+00:00",
                "platform": "SPOT-7",
                "proj:epsg": 4326,
                "end_datetime": "2021-05-31T09:51:52.100000+00:00",
                "eo:cloud_cover": 0.0,
                "start_datetime": "2021-05-31T09:51:52.100000+00:00",
                "up42-system:workspace_id": "7d1cf222-1fa7-468c-a93a-3e3188875997",
                "up42-product:collection_name": "Collection No 1",
            },
            "type": "Feature",
            "stac_version": "1.0.0",
            "id": "e986e18a-0392-4b82-93c9-7a0af15846d0",
            "collection": "69ce89b4-fa35-4a1a-bcd8-1c2e5bbd2ee6",
        }
    ],
}

PYSTAC_MOCK_CLIENT = mock_pystac_client = {
    "conformsTo": [
        "https://api.stacspec.org/v1.0.0-rc.1/item-search#sort",
        "https://api.stacspec.org/v1.0.0-rc.1/collections",
        "https://api.stacspec.org/v1.0.0-rc.1/item-search#filter",
        "http://www.opengis.net/spec/ogcapi-features-4/1.0/conf/simpletx",
        "https://api.stacspec.org/v1.0.0-rc.1/item-search#filter:basic-cql",
        "https://api.stacspec.org/v1.0.0-rc.1/item-search",
        "https://api.stacspec.org/v1.0.0-rc.1/ogcapi-features/extensions/transaction",
        "https://api.stacspec.org/v1.0.0-rc.1/item-search#filter:cql-text",
        "http://www.opengis.net/spec/ogcapi-features-3/1.0/conf/features-filter",
        "http://www.opengis.net/spec/ogcapi-features-3/1.0/conf/filter",
        "https://api.stacspec.org/v1.0.0-rc.1/core",
        "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core",
        "https://api.stacspec.org/v1.0.0-rc.1/ogcapi-features",
        "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/geojson",
        "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/oas30",
    ],
    "links": [
        {
            "href": "https://api.up42.com/v2/assets/stac/",
            "rel": "self",
            "type": "application/json",
        },
        {
            "href": "https://api.up42.com/v2/assets/stac/",
            "rel": "root",
            "type": "application/json",
        },
        {
            "href": "https://api.up42.com/v2/assets/stac/collections",
            "rel": "data",
            "type": "application/json",
        },
        {
            "href": "https://api.up42.com/v2/assets/stac/search",
            "rel": "search",
            "type": "application/json",
            "method": "POST",
        },
    ],
    "stac_extensions": [],
    "title": "UP42 Storage",
    "description": "UP42 Storage STAC API",
    "stac_version": "1.0.0",
    "id": "up42-storage",
    "type": "Catalog",
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
