# Imports
import up42
import rasterio


# Authenticate
up42.authenticate(
    username="",
    password="",
)

# Get search results
catalog = up42.initialize_catalog()
search_results = catalog.search(
    search_parameters=catalog.construct_search_parameters(
        geometry=[13.488775, 52.49356, 13.491544, 52.495167],
        start_date="2020-01-01",
        end_date="2024-01-01",
        collections=["beijing-3a"],
        max_cloudcover=50,
        limit=1,
    )
)


# Download quicklooks
result = search_results.iloc[0]
catalog.download_quicklooks(
    image_ids=result.sceneId,
    collection=result.constellation,
    output_directory="./quicklooks/",
)


# define function to georeference quicklooks
def georeference_quicklooks(
    src_path: str, dst_path: str, ulx: float, uly: float, lrx: float, lry: float
):
    with rasterio.open(src_path) as src:
        data = src.read()
        transform = rasterio.transform.from_bounds(
            ulx, lry, lrx, uly, data.shape[2], data.shape[1]
        )

        with rasterio.open(
            dst_path,
            "w",
            driver=src.driver,
            height=src.height,
            width=src.width,
            count=src.count,
            dtype=src.dtypes[0],
            crs="EPSG:4326",
            transform=transform,
        ) as dst:
            dst.write(data)


# georefence the quicklook
src_path = f"./quicklooks/quicklook_{result.sceneId}.jpg"
out_path = f"./quicklooks/georeferenced_quicklook_{result.sceneId}.png"
georeference_quicklooks(
    src_path,
    out_path,
    result.geometry.bounds[0],
    result.geometry.bounds[3],
    result.geometry.bounds[2],
    result.geometry.bounds[1],
)
