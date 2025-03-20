TOKEN = "token_123"
API_HOST = "https://api.up42.com"
SA_API_HOST = "https://api.sa.up42.com"
WORKSPACE_ID = "workspace_id_123"
USER_EMAIL = "user@up42.com"
PASSWORD = "<PASSWORD>"
DATA_PRODUCT_ID = "47dadb27-9532-4552-93a5-48f70a83eaef"
ORDER_ID = "da2310a2-c7fb-42ed-bead-fb49ad862c67"
URL_STAC_CATALOG = f"{API_HOST}/v2/assets/stac/"
URL_STAC_SEARCH = f"{API_HOST}/v2/assets/stac/search"

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
