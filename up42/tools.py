import json
import math
import os
from pathlib import Path
from typing import Tuple, List, Union, Dict

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import rasterio
import requests.exceptions
import shapely
from IPython import get_ipython
from IPython.display import display
from geojson import FeatureCollection
from rasterio.plot import show
from tenacity import RetryError

from .utils import get_logger, folium_base_map, DrawFoliumOverride, is_notebook

logger = get_logger(__name__)  # level=logging.CRITICAL  #INFO


# pylint: disable=no-member, duplicate-code
class Tools:
    def __init__(self, auth=None):
        """
        The tools class contains functionality that is not bound to a specific UP42 object,
        e.g. for aoi handling etc., UP42 block information, validatin a block manifest etc.
        They can be accessed from every object and also from the imported up42 package directly.

        Public methods:
            read_vector_file, get_example_aoi, draw_aoi, plot_coverage, plot_quicklook
        """
        if auth:
            self.auth = auth
        self.quicklook = None
        self.result = None

    # pylint: disable=no-self-use
    def read_vector_file(
        self, filename: str = "aoi.geojson", as_dataframe: bool = False
    ) -> FeatureCollection:
        """
        Reads vector files (geojson, shapefile, kml, wkt) to a feature collection,
        for use as the aoi geometry in the workflow input parameters
        (see get_input_parameters).

        Example aoi fiels are provided, e.g. example/data/aoi_Berlin.geojson

        Args:
            filename: File path of the vector file.
            as_dataframe: Return type, default FeatureCollection, GeoDataFrame if True.

        Returns:
            Feature Collection
        """
        suffix = Path(filename).suffix

        if suffix == ".kml":
            gpd.io.file.fiona.drvsupport.supported_drivers["KML"] = "rw"
            df = gpd.read_file(filename, driver="KML")
        elif suffix == ".wkt":
            with open(filename) as wkt_file:
                wkt = wkt_file.read()
                df = pd.DataFrame({"geometry": [wkt]})
                df["geometry"] = df["geometry"].apply(shapely.wkt.loads)
                df = gpd.GeoDataFrame(df, geometry="geometry", crs=4326)
        else:
            df = gpd.read_file(filename)

        if df.crs != "epsg:4326":
            df = df.to_crs(epsg=4326)
        df.geometry = df.geometry.buffer(0)
        # TODO: Explode multipolygons (if neccessary as union in aoi anyway most often).

        # TODO: Have both bboxes for each feature and overall?

        if as_dataframe:
            return df
        else:
            return df.__geo_interface__

    def get_example_aoi(
        self, location: str = "Berlin", as_dataframe: bool = False
    ) -> FeatureCollection:
        """
        Gets predefined, small, rectangular example aoi for the selected location.

        Args:
            location: Location, one of Berlin, Washingtion.
            as_dataframe:

        Returns:
            Feature collection json with the selected aoi.
        """
        # TODO: Add more geometries.
        logger.info("Getting small example aoi in %s.", location)
        if location == "Berlin":
            example_aoi = self.read_vector_file(
                f"{os.path.dirname(__file__)}/data/aoi_berlin.geojson"
            )
        elif location == "Washington":
            # TODO
            pass
        elif location == "Tokyo":
            pass
        else:
            raise ValueError("Please select one of 'Berlin', 'Washington' or 'Tokyo'!")

        if as_dataframe:
            df = gpd.GeoDataFrame.from_features(example_aoi, crs=4326)
            return df
        else:
            return example_aoi

    # pylint: disable=no-self-use
    def draw_aoi(self) -> None:
        """
        Opens a interactive map to draw an aoi by hand, export via the export button.
        Then read in via read_aoi_file().

        Currently no way to get the drawn geometry via a callback in Python, as not
        supported by folium.
        And ipyleaflet misses raster vizualization & folium plugins functionality.
        """
        m = folium_base_map(layer_control=True)
        DrawFoliumOverride(
            export=True,
            filename="aoi.geojson",
            position="topleft",
            draw_options={
                "rectangle": {"repeatMode": False, "showArea": True},
                "polygon": {"showArea": True, "allowIntersection": False},
                "polyline": False,
                "circle": False,
                "marker": False,
                "circlemarker": False,
            },
            edit_options={"polygon": {"allowIntersection": False}},
        ).add_to(m)
        display(m)

    @staticmethod
    def plot_coverage(
        scenes: gpd.GeoDataFrame,
        aoi: gpd.GeoDataFrame = None,
        legend_column: str = "scene_id",
        figsize=(12, 16),
    ) -> None:
        """
        Plots a coverage map of a dataframe with geometries e.g. the result of catalog.search())
        Args:
            scenes: GeoDataFrame of scenes, result of catalog.search()
            aoi: GeoDataFrame of aoi.
            legend_column: Dataframe column set to legend, default is "scene_id".
                Legend entries are sorted and this determines plotting order.
            figsize: Matplotlib figure size.
        """
        if is_notebook():
            get_ipython().run_line_magic("matplotlib", "inline")

        if legend_column not in scenes.columns:
            legend_column = None
            logger.info("Given legend_column name not in scene dataframe, "
                        "plotting without legend.")

        ax = scenes.plot(
            legend_column,
            categorical=True,
            figsize=figsize,
            cmap="Set3",
            legend=True,
            alpha=0.7,
            legend_kwds=dict(loc="upper left", bbox_to_anchor=(1, 1)),
        )

        if aoi is not None:
            aoi.plot(color="r", ax=ax, fc="None", edgecolor="r", lw=1)
            # TODO: Add aoi to legend.
            # from matplotlib.patches import Patch
            # patch = Patch(label="aoi", facecolor='None', edgecolor='r')
            # ax.legend(handles=handles, labels=labels)
            # TODO: Overlay quicklooks on geometry.
        ax.set_axis_off()
        plt.show()

    def plot_quicklook(
        self, figsize: Tuple[int, int] = (8, 8), filepaths: List = None
    ) -> None:
        """
        Plots the downloaded quicklooks (filepaths saved to self.quicklook of the
        respective object, e.g. job, catalog).

        Args:
            figsize: matplotlib figure size.
        """
        if filepaths is None:
            if self.quicklook is None:
                raise ValueError(
                    "You first need to download the quicklooks via .download_quicklook()."
                )
            filepaths = self.quicklook
        if is_notebook():
            get_ipython().run_line_magic("matplotlib", "inline")
        else:
            raise ValueError("Only works in Jupyter notebook.")

        if len(filepaths) < 2:
            nrows, ncols = 1, 1
        else:
            ncols = 2
            nrows = int(math.ceil(len(filepaths) / float(ncols)))

        fig, axs = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize)
        if len(filepaths) > 1:
            axs = axs.ravel()
        else:
            axs = [axs]
        for idx, fp in enumerate(filepaths):
            with rasterio.open(fp) as src:
                show(
                    src.read(),
                    transform=src.transform,
                    title=Path(fp).stem,
                    ax=axs[idx],
                )
        plt.tight_layout()
        plt.show()

    def plot_result(
        self,
        figsize: Tuple[int, int] = (8, 8),
        filepaths: List[str] = None,
        titles: List[str] = None,
    ) -> None:
        """
        Plots the downloaded data.

        Args:
            figsize: matplotlib figure size.
            filepaths: Paths to images to plot. Optional, by default picks up the downloaded results.
        """
        # TODO: Add other fileformats.
        # TODO: Handle more bands.
        # TODO: add histogram equalization? But requires skimage dependency.
        if filepaths is None:
            if self.result is None:
                raise ValueError("You first need to download the results.")
            filepaths = self.result
        if not titles:
            titles = [Path(fp).stem for fp in filepaths]

        if is_notebook():
            get_ipython().run_line_magic("matplotlib", "inline")
        else:
            raise ValueError("Only works in Jupyter notebook.")

        if len(filepaths) < 2:
            nrows, ncols = 1, 1
        else:
            ncols = 3
            nrows = int(math.ceil(len(filepaths) / float(ncols)))

        fig, axs = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize)
        if len(filepaths) > 1:
            axs = axs.ravel()
        else:
            axs = [axs]
        for idx, (fp, title) in enumerate(zip(filepaths, titles)):
            with rasterio.open(fp) as src:
                img_array = src.read()
                show(
                    img_array, transform=src.transform, title=title, ax=axs[idx],
                )
            axs[idx].set_axis_off()
        plt.tight_layout()
        plt.show()

    def get_blocks(
        self, block_type=None, basic: bool = True, as_dataframe=False,
    ) -> Union[List[Dict], Dict]:
        """
        Gets a list of all public blocks on the marketplace.

        Args:
            block_type: Optionally filters to "data" or "processing" blocks, default None.
            basic: Optionally returns simple version {block_id : block_name}
            as_dataframe: Returns a dataframe instead of json (default).

        Returns:
            A list of the public blocks and their metadata. Optional a simpler version
            dict.
        """
        try:
            block_type = block_type.lower()
        except AttributeError:
            pass

        url = f"{self.auth._endpoint()}/blocks"
        response_json = self.auth._request(request_type="GET", url=url)
        public_blocks_json = response_json["data"]

        if block_type == "data":
            logger.info("Getting only data blocks.")
            blocks_json = [
                block for block in public_blocks_json if block["type"] == "DATA"
            ]
        elif block_type == "processing":
            logger.info("Getting only processing blocks.")
            blocks_json = [
                block for block in public_blocks_json if block["type"] == "PROCESSING"
            ]
        else:
            blocks_json = public_blocks_json

        if basic:
            logger.info(
                "Getting basic information, use basic=False for all block details."
            )
            blocks_basic = {block["name"]: block["id"] for block in blocks_json}
            if as_dataframe:
                return pd.DataFrame.from_dict(blocks_basic, orient="index")
            else:
                return blocks_basic

        else:
            if as_dataframe:
                return pd.DataFrame(blocks_json)
            else:
                return blocks_json

    def get_block_details(self, block_id: str, as_dataframe=False) -> Dict:
        """
        Gets the detailed information about a specific (public or custom) block from
        the server, includes all manifest.json and marketplace.json contents.

        Args:
            block_id: The block id.
            as_dataframe: Returns a dataframe instead of json (default).

        Returns:
            A dict of the block details metadata for the specific block.
        """
        try:
            url = f"{self.auth._endpoint()}/blocks/{block_id}"  # public blocks
            response_json = self.auth._request(request_type="GET", url=url)
        except (requests.exceptions.HTTPError, RetryError):
            url = f"{self.auth._endpoint()}/users/me/blocks/{block_id}"  # custom blocks
            response_json = self.auth._request(request_type="GET", url=url)
        details_json = response_json["data"]

        if as_dataframe:
            return pd.DataFrame.from_dict(details_json, orient="index").transpose()
        else:
            return details_json

    def get_environments(self, as_dataframe=False) -> Dict:
        """
        Gets all existing UP42 environments, used for separating storage of API keys
        etc.

        Args:
            as_dataframe: Returns a dataframe instead of json (default).

        Returns:
            The environments as json info.
        """
        url = f"{self.auth._endpoint()}/environments"
        response_json = self.auth._request(request_type="GET", url=url)
        environments_json = response_json["data"]

        if as_dataframe:
            return pd.DataFrame(environments_json)
        else:
            return environments_json

    def create_environment(self, name: str, environment_variables: Dict = None) -> Dict:
        """
        Creates a new UP42 environments, used for separating storage of API keys
        etc.

        Args:
            name: Name of the new environment.
            environment_variables: The variables to add to the environment, see example.

        Returns:
            The json info of the newly created environment.

        Example:
            ```python
            environment_variables=
                {"username": "up42", "password": "password"}
            ```
        """
        existing_environment_names = [env["name"] for env in self.get_environments()]
        if name in existing_environment_names:
            raise Exception(f"An environment with the name {name} already exists.")
        payload = {"name": name, "secrets": environment_variables}
        url = f"{self.auth._endpoint()}/environments"
        response_json = self.auth._request(request_type="POST", url=url, data=payload)
        return response_json["data"]

    def delete_environment(self, environment_id: str) -> None:
        """
        Deletes a specific environment.

        Args:
            environment_id: The id of the environment to delete. See also get_environments.
        """
        url = f"{self.auth._endpoint()}/environments/{environment_id}"
        self.auth._request(request_type="DELETE", url=url, return_text=False)
        logger.info("Successfully deleted environment: %s", environment_id)

    def validate_manifest(self, path_or_json: Union[str, Path, Dict]) -> Dict:
        """
        Validates the block manifest, input either manifest json string or filepath.

        Args:
            path_or_json: The input manifest, either filepath or json string, see example.

        Returns:
            A dictionary with the validation result and potential validation errors.

        Example:
            ```json
                {
                    "_up42_specification_version": 2,
                    "name": "sharpening",
                    "type": "processing",
                    "tags": [
                        "imagery",
                        "processing"
                    ],
                    "display_name": "Sharpening Filter",
                    "description": "This block enhances the sharpness of a raster
                        image by applying an unsharp mask filter algorithm.",
                    "parameters": {
                        "strength": {"type": "string", "default": "medium"}
                    },
                    "machine": {
                        "type": "large"
                    },
                    "input_capabilities": {
                        "raster": {
                            "up42_standard": {
                                "format": "GTiff"
                            }
                        }
                    },
                    "output_capabilities": {
                        "raster": {
                            "up42_standard": {
                                "format": "GTiff",
                                "bands": ">",
                                "sensor": ">",
                                "resolution": ">",
                                "dtype": ">",
                                "processing_level": ">"
                            }
                        }
                    }
                }
            ```
        """
        if isinstance(path_or_json, (str, Path)):
            with open(path_or_json) as src:
                manifest_json = json.load(src)
        else:
            manifest_json = path_or_json
        url = f"{self.auth._endpoint()}/validate-schema/block"
        response_json = self.auth._request(
            request_type="POST", url=url, data=manifest_json
        )
        logger.info("The manifest is valid.")
        return response_json["data"]
