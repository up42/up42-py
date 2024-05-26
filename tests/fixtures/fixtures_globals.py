TOKEN = "token_123"
API_HOST = "https://api.up42.com"
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
STAC_ASSET_URL = (
    "https://storage.googleapis.com/user-storage-interstellar-staging/assets/"
    "3f581f3d-534a-4e1f-869d-901a7f2bff55?response-content-disposition="
    "attachment%3B%20filename%3Dbsg-104-20230522-044750-90756881_ortho.tiff"
    "&GoogleAccessId=asset-service@interstellar-staging-env.iam.gserviceaccount.com"
    "&Expires=1697201515&Signature=CJl3qL9xits6XXoRv7e%2FaROMar8rlu%2BXdbIlao2UjrMwS"
    "CosttAhIBXM93%2BX48FxOrSDsBZblSGvTAhKWkuahhOOr25DeSBnSolHMjeaWQG65L6v6TGZglxI"
    "hP%2BgMhIJ%2Feg34HLaTrqlf1L1TEvTYklwpFoYdDYQCOh8O6UaE0ChEy5GoKHeOYPbjpFMYTeg"
    "%2FKaVTaa3HKpH90irZHA8HPeShk%2Bk8M3tks7bRIbG56gdyl3cwWPLgq8%2FPENb4GTKxLIkn1y"
    "vW%2FWw%2B2%2FWIzq9IFsx3AEPe%2F2ZeaU180lZDgEyBmsSdrCMQYA1J9IKAD0rIjYrg%2Bo90"
    "MsgdNhs3HuTDA%3D%3D"
)
STAC_ASSET_HREF = "https://api.up42.com/v2/assets/v3b3e203-346d-4f67-b79b-895c36983fb8"
STAC_ASSET_ID = "v3b3e203-346d-4f67-b79b-895c36983fb8"

# tasking constants
QUOTATION_ID = "805b1f27-1025-43d2-90d0-0bd3416238fb"
WRONG_FEASIBILITY_ID = "296ef160-d890-430d-8d14-e9b579ab08ba"
WRONG_OPTION_ID = "296ef160-7890-430d-8d14-e9b579ab08ba"
TEST_FEASIBILITY_ID = "6f93f754-5594-42da-b6af-9064225b89e9"
TEST_OPTION_ID = "cc3c869d-9215-4dcd-b535-b49aa28228fa"

WORKSPACE_ID = "workspace_id_123"
USER_ID = "1094497b-11d8-4fb8-9d6a-5e24a88aa825"
USER_EMAIL = "user@up42.com"
PASSWORD = "<PASSWORD>"

DATA_PRODUCT_ID = "47dadb27-9532-4552-93a5-48f70a83eaef"

ORDER_ID = "da2310a2-c7fb-42ed-bead-fb49ad862c67"
ASSET_ID = "363f89c1-3586-4b14-9a49-03a890c3b593"
ASSET_ID2 = "88ddc9d8-f179-4821-acef-e7b2abddecr0"
ASSET_ORDER_ID = "22d0b8e9-b649-4971-8adc-1a5eac1fa6f3"
STAC_COLLECTION_ID = "e459db4c-3b9d-4aa1-8931-5df2517b49ba"

URL_STAC_CATALOG = "https://api.up42.com/v2/assets/stac/"
URL_STAC_SEARCH = "https://api.up42.com/v2/assets/stac/search"

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

STAC_SEARCH_RESPONSE = {
    "type": "FeatureCollection",
    "features": [
        {
            "assets": {"data": {"href": "https://api.up42.com/v2/assets/01ad657e-12f7-4046-a94c-abc90d86106a"}},
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
                    "href": URL_STAC_CATALOG,
                    "rel": "root",
                    "type": "application/json",
                    "title": "UP42 Storage",
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


STAC_CATALOG_RESPONSE = {
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
            "href": URL_STAC_CATALOG,
            "rel": "self",
            "type": "application/json",
        },
        {
            "href": URL_STAC_CATALOG,
            "rel": "root",
            "type": "application/json",
        },
        {
            "href": "https://api.up42.com/v2/assets/stac/collections",
            "rel": "data",
            "type": "application/json",
        },
        {
            "href": URL_STAC_SEARCH,
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
        "createdBy": {
            "id": "1094497b-11d8-4fb8-9d6a-5e24a88aa825",
            "type": "USER",
        },
        "updatedBy": {"id": "system", "type": "INTERNAL"},
    },
    "error": None,
}

JSON_ORDERS = {
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
}
