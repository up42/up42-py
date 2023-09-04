TOKEN = "token_123"
DOWNLOAD_URL = "http://up42.api.com/abcdef.tgz"
DOWNLOAD_URL2 = (
    "https://storage.googleapis.com/user-storage-interstellar-prod/workspace/"
    "a917e589-1187-402f-8bf8-38937d6fe713/block-output/"
    "78ddc9d8-f179-4821-acef-e7b2abddece0/data.tgz?"
    "response-content-disposition=attachment%3B%20filename%3DDS_SPOT6_202206240959075_"
    "FR1_FR1_SV1_SV1_E013N52_01709&GoogleAccessId=asset-service@interstellar-prod-env."
    "iam.gserviceaccount.com&Expires=1691664318&Signature=py7zPKQdqE%2FnVNOVz1eNkc4dR"
    "C465zAnRPcX2UOeKsYSJeEkkkBCnCqFyhG07qXlMd7xi5Rz7KCe3ZZUgFNmLjkoCEV6CEhX4zaf"
    "LR2219MteRM8EURVxYvL8MAbcxjqscKcjm10CGXnOb1e4C4Ap7NW9lqUPp6WS%2BJjNe5mYyZuv"
    "xsD2vPiVpoYsuuqFIr5Dp2JQsOriuV4xdwRx6EiGkjo2VkadH%2BfEr3o2wjDstvxCmtV6BE8W"
    "cjvDcUPTeIYjHYjBMV0yBOO0FHnzZLRFtpmoXQ5LjIuDb8NYiPcf044XiLIWIdrDhPliMAWZr"
    "whx5CG98M2Y4buui4C24JD6Q%3D%3D"
)
STAC_ASSET_DOWNLOAD_URL = "https://api.up42.com/v2/assets/v3b3e203-346d-4f67-b79b-895c36983fb8"
PROJECT_ID = "f19e833d-e698-4d9e-a037-2e6dbd8791ef"
PROJECT_APIKEY = "project_apikey_123"
PROJECT_NAME = "project_name_123"
PROJECT_DESCRIPTION = "project_description_123"

# tasking constants
QUOTATION_ID = "805b1f27-1025-43d2-90d0-0bd3416238fb"
WRONG_FEASIBILITY_ID = "296ef160-d890-430d-8d14-e9b579ab08ba"
WRONG_OPTION_ID = "296ef160-7890-430d-8d14-e9b579ab08ba"

WORKFLOW_ID = "c74d73c0-6929-4549-a5c9-5a3f517f6d63"
WORKFLOW_NAME = "workflow_name_123"
WORKFLOW_DESCRIPTION = "workflow_description_123"
WORKSPACE_ID = "workspace_id_123"

JOB_ID = "13ba070a-55b7-4b3f-95f1-7b11ac8f1175"
JOB_ID_2 = "ce6286e2-aebb-49ce-8a09-272d6466f3c5"
JOB_NAME = "job_name_123"

JOBTASK_ID = "a16615e2-6944-4143-879e-416f2fe52de8"
JOBTASK_NAME = "jobtask_name_123"

DATA_PRODUCT_ID = "47dadb27-9532-4552-93a5-48f70a83eaef"

ORDER_ID = "ddb207c0-3b7f-4186-bc0b-c033f0d2f32b"
ASSET_ID = "363f89c1-3586-4b14-9a49-03a890c3b593"
ASSET_ID2 = "88ddc9d8-f179-4821-acef-e7b2abddecr0"
STAC_COLLECTION_ID = "e459db4c-3b9d-4aa1-8931-5df2517b49ba"

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
            "href": "https://api.up42.com/v2/assets/stac/",
            "rel": "root",
            "type": "application/json",
        },
        {
            "href": "https://api.up42.com/v2/assets/stac/search",
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
                    "href": "https://api.up42.com/v2/assets/01ad657e-12f7-4046-a94c-abc90d86106a"
                }
            },
            "links": [
                {
                    "href": "https://api.up42.com/v2/assets/stac/collections/69ce89b4-fa35-4a1a-bcd8-1c2e5bbd2ee6/"
                    "items/e986e18a-0392-4b82-93c9-7a0af15846d0",
                    "rel": "self",
                    "type": "application/geo+json",
                },
                {
                    "href": "https://api.up42.com/v2/assets/stac/collections/69ce89b4-fa35-4a1a-bcd8-1c2e5bbd2ee6",
                    "rel": "parent",
                    "type": "application/json",
                },
                {
                    "href": "https://api.up42.com/v2/assets/stac/collections/69ce89b4-fa35-4a1a-bcd8-1c2e5bbd2ee6",
                    "rel": "collection",
                    "type": "application/json",
                },
                {
                    "href": "https://api.up42.com/v2/assets/stac/",
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
            "collection": STAC_COLLECTION_ID,
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
