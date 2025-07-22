import datetime as dt

import pystac
from pact.v3 import match

from up42 import stac, utils


def test_download_asset(create_pact):
    pact, mock_server = create_pact("Storage")

    path = "/v2/assets/897d47de-5100-4106-8e09-7b777d44d418"
    signed_url = "https://example.com/file"

    (
        pact.upon_receiving("a request for a signed download url")
        .given("the requested asset exists")
        .with_request("POST", f"{path}/download-url")
        .will_respond_with(200)
        .with_body({"url": match.regex(signed_url, regex=r"https://.*")})
    )

    with mock_server() as srv:
        asset = pystac.Asset(href=f"{srv.url}{path}")
        assert asset.file == utils.ImageFile(url=signed_url)  # type: ignore


def test_update_item(create_pact):
    contract, mock_server = create_pact("STAC")

    item = pystac.Item(
        id="3b1e07c1-ce7b-41be-ab4c-2bcc9e26575c",
        collection="61bed282-8dac-414c-a0b1-a2a7aee7a2a7",
        geometry=None,
        bbox=None,
        datetime=dt.datetime.fromisoformat("2025-07-18T14:26:45+00:00"),
        properties={
            stac.UP42_USER_TITLE_KEY: "title",
            stac.UP42_USER_TAGS_KEY: ["tag"],
        },
    )

    (
        contract.upon_receiving("a request to update item metadata")
        .given("the requested item exists")
        .with_request(
            "PATCH",
            f"/v2/assets/stac/collections/{item.collection_id}/items/{item.id}",
        )
        .with_header("Content-Type", "application/json")
        .with_body({stac.UP42_USER_TITLE_KEY: "title", stac.UP42_USER_TAGS_KEY: ["tag"]})
        .will_respond_with(200)
        .with_body(
            {
                "type": "Feature",
                "stac_version": "1.0.0",
                "id": match.uuid(item.id),
                "collection": match.uuid(item.collection_id),  # type: ignore
                "properties": {
                    "datetime": match.datetime(item.datetime),  # type: ignore
                    stac.UP42_USER_TITLE_KEY: match.string("response-title"),
                    stac.UP42_USER_TAGS_KEY: match.each_like(match.string("response-tag")),
                },
            }
        )
    )

    with mock_server():
        item.update()  # type: ignore

        assert item.up42.title == "response-title"  # type: ignore
        assert item.up42.tags == ["response-tag"]  # type: ignore
