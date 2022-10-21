import os
import pytest

import up42


@pytest.mark.live()
def test_e2e_catalog():
    _auth = up42.Auth(
        project_id=os.getenv("TEST_UP42_PROJECT_ID"),
        project_api_key=os.getenv("TEST_UP42_PROJECT_API_KEY"),
    )

    catalog = up42.Catalog(_auth)

    ## Search scenes in aoi
    aoi = up42.get_example_aoi(location="Berlin", as_dataframe=True)
    search_parameters = catalog.construct_search_parameters(
        geometry=aoi,
        start_date="2018-01-01",
        end_date="2022-12-31",
        collections=["phr"],
        max_cloudcover=20,
        sortby="cloudCoverage",
        limit=10,
    )
    search_results = catalog.search(search_parameters=search_parameters)
    catalog.download_quicklooks(image_ids=search_results.id.to_list(), collection="phr")


if __name__ == "__main__":
    test_e2e_catalog()
