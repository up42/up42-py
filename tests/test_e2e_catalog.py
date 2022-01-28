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

    search_parameters = catalog.construct_parameters(
        geometry=aoi,
        start_date="2018-01-01",
        end_date="2020-12-31",
        collections=["PHR"],
        max_cloudcover=20,
        sortby="cloudCoverage",
        limit=10,
    )
    search_results = catalog.search(search_parameters=search_parameters)
    # display(search_results.head()), only works in notebook

    # catalog.plot_coverage(scenes=search_results, aoi=aoi, legend_column="sceneId")

    ## Download & visualize quicklooks

    catalog.download_quicklooks(
        image_ids=search_results.id.to_list(), sensor="pleiades"
    )

    # catalog.map_quicklooks(scenes=search_results, aoi=aoi)


if __name__ == "__main__":
    test_e2e_catalog()
