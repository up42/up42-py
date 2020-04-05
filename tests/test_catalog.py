from pathlib import Path
import json

import pytest

# pylint: disable=unused-import
from .fixtures import (
    auth_mock,
    catalog_mock,
    catalog_live,
)
import up42  # pylint: disable=wrong-import-order


def test_catalog(catalog_mock):
    assert isinstance(catalog_mock, up42.Catalog)


def test_construct_parameter(catalog_mock):
    fp = Path(__file__).resolve().parent / "mock_data/aoi_berlin.geojson"
    with open(fp) as json_file:
        fc = json.load(json_file)
    search_paramater = catalog_mock.construct_parameters(
        geometry=fc,
        start_date="2014-01-01",
        end_date="2016-12-31",
        sensors=["pleiades"],
        max_cloudcover=20,
        sortby="cloudCoverage",
        limit=4,
        ascending=False,
    )
    assert isinstance(search_paramater, dict)
    assert search_paramater["datetime"] == "2014-01-01T00:00:00Z/2016-12-31T00:00:00Z"
    assert search_paramater["intersects"]["type"] == "Polygon"
    assert search_paramater["limit"] == 4
    assert search_paramater["query"] == {
        "cloudCoverage": {"lte": 20},
        "dataBlock": {
            "in": ["oneatlas-pleiades-fullscene", "oneatlas-pleiades-aoiclipped"]
        },
    }
    assert search_paramater["sortby"] == [
        {"field": "properties.cloudCoverage", "direction": "desc"}
    ]


def test_search(catalog_mock):
    pass


@pytest.mark.live
def test_search_live(catalog_live):
    search_parameters = {
        "datetime": "2014-01-01T00:00:00Z/2016-12-31T00:00:00Z",
        "intersects": {
            "type": "Polygon",
            "coordinates": (
                (
                    (13.375966, 52.515068),
                    (13.375966, 52.516639),
                    (13.378314, 52.516639),
                    (13.378314, 52.515068),
                    (13.375966, 52.515068),
                ),
            ),
        },
        "limit": 4,
        "query": {
            "cloudCoverage": {"lte": 20},
            "dataBlock": {
                "in": ["oneatlas-pleiades-fullscene", "oneatlas-pleiades-aoiclipped"]
            },
        },
        "sortby": [{"field": "properties.cloudCoverage", "direction": "desc"}],
    }
    catalog_live.search(search_parameters)


def test_download_quicklook(catalog_mock):
    pass


@pytest.mark.live
def test_download_quicklook_live(catalog_live):
    pass
