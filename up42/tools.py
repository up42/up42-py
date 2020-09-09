import json
from pathlib import Path
from typing import Tuple, List, Union, Dict
import warnings

from geopandas import GeoDataFrame
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import shapely
import rasterio
import folium

from up42.utils import (
    get_logger,
    folium_base_map,
    DrawFoliumOverride,
    _plot_images,
    _map_images,
)

try:
    from IPython.display import display
    from IPython import get_ipython

    get_ipython().run_line_magic("matplotlib", "inline")
except (ImportError, AttributeError):
    # No Ipython installed, Installed but run in shell
    pass

logger = get_logger(__name__)


# pylint: disable=no-member, duplicate-code
class Tools:
    def __init__(self, auth=None):
        """
        The tools class contains functionality that is not bound to a specific UP42 object,
        e.g. for aoi handling etc., UP42 block information, validatin a block manifest etc.
        They can be accessed from every object and also from the imported up42 package directly.
        """
        if auth:
            self.auth = auth
        self.quicklooks = None
        self.results = None

    # pylint: disable=no-self-use
    def read_vector_file(
        self, filename: str = "aoi.geojson", as_dataframe: bool = False
    ) -> Union[Dict, GeoDataFrame]:
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
                df = GeoDataFrame(df, geometry="geometry", crs=4326)
        else:
            df = gpd.read_file(filename)

        if df.crs.to_string() != "EPSG:4326":
            df = df.to_crs(epsg=4326)
        # TODO: Explode multipolygons (if neccessary as union in aoi anyway most often).
        # TODO: Have both bboxes for each feature and overall?
        if as_dataframe:
            return df
        else:
            return df.__geo_interface__

    def get_example_aoi(
        self, location: str = "Berlin", as_dataframe: bool = False
    ) -> Union[dict, GeoDataFrame]:
        """
        Gets predefined, small, rectangular example aoi for the selected location.

        Args:
            location: Location, one of Berlin, Washington.
            as_dataframe: Returns a dataframe instead of dict FeatureColletions
                (default).

        Returns:
            Feature collection json with the selected aoi.
        """
        logger.info(f"Getting small example aoi in location '{location}'.")
        if location == "Berlin":
            example_aoi = self.read_vector_file(
                f"{str(Path(__file__).resolve().parent)}/data/aoi_berlin.geojson"
            )
        elif location == "Washington":
            example_aoi = self.read_vector_file(
                f"{str(Path(__file__).resolve().parent)}/data/aoi_washington.geojson"
            )
        else:
            raise ValueError(
                "Please select one of 'Berlin' or 'Washington' as the location!"
            )

        if as_dataframe:
            df = GeoDataFrame.from_features(example_aoi, crs=4326)
            return df
        else:
            return example_aoi

    # pylint: disable=no-self-use
    def draw_aoi(self):
        """
        Displays an interactive map to draw an aoi by hand, returns the folium object if
        not run in a Jupyter notebook.

        Export the drawn aoi via the export button, then read the geometries via
        read_aoi_file().
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

        try:
            assert get_ipython() is not None
            display(m)
        except (AssertionError, NameError):
            logger.info(
                "Returning folium map object. To display it directly run in a "
                "Jupyter notebook!"
            )
            return m

    @staticmethod
    def plot_coverage(
        scenes: GeoDataFrame,
        aoi: GeoDataFrame = None,
        legend_column: str = "scene_id",
        figsize=(12, 16),
    ) -> None:
        """
        Plots a coverage map of a dataframe with geometries e.g. the results of catalog.search())
        Args:
            scenes: GeoDataFrame of scenes, results of catalog.search()
            aoi: GeoDataFrame of aoi.
            legend_column: Dataframe column set to legend, default is "scene_id".
                Legend entries are sorted and this determines plotting order.
            figsize: Matplotlib figure size.
        """
        if legend_column not in scenes.columns:
            legend_column = None  # type: ignore
            logger.info(
                "Given legend_column name not in scene dataframe, "
                "plotting without legend."
            )

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

    def plot_quicklooks(
        self,
        figsize: Tuple[int, int] = (8, 8),
        filepaths: List = None,
        titles: List[str] = None,
    ) -> None:
        """
        Plots the downloaded quicklooks (filepaths saved to self.quicklooks of the
        respective object, e.g. job, catalog).

        Args:
            figsize: matplotlib figure size.
            filepaths: Paths to images to plot. Optional, by default picks up the last
                downloaded results.
            titles: List of titles for the subplots, optional.

        """
        if filepaths is None:
            if self.quicklooks is None:
                raise ValueError("You first need to download the quicklooks!")
            filepaths = self.quicklooks

        plot_file_format = [".jpg", ".jpeg", ".png"]
        warnings.filterwarnings(
            "ignore", category=rasterio.errors.NotGeoreferencedWarning
        )
        _plot_images(
            plot_file_format=plot_file_format,
            figsize=figsize,
            filepaths=filepaths,
            titles=titles,
        )

    def map_quicklooks(
        self,
        scenes: GeoDataFrame,
        aoi: GeoDataFrame = None,
        filepaths: List = None,
        name_column: str = "id",
        save_html: Path = None,
    ) -> folium.Map:
        """
        Plots the downloaded quicklooks (filepaths saved to self.quicklooks of the
        respective object, e.g. job, catalog).

        Args:
            scenes: GeoDataFrame of scenes, results of catalog.search()
            aoi: GeoDataFrame of aoi.
            filepaths: Paths to images to plot. Optional, by default picks up the last
                downloaded results.
            name_column: Name of the feature property that provides the Feature/Layer name.
            save_html: The path for saving folium map as html file. With default None, no file is saved.
        """
        if filepaths is None:
            if self.quicklooks is None:
                raise ValueError("You first need to download the quicklooks!")
            filepaths = self.quicklooks

        plot_file_format = [".jpg", ".jpeg", ".png"]
        warnings.filterwarnings(
            "ignore", category=rasterio.errors.NotGeoreferencedWarning
        )
        m = _map_images(
            plot_file_format=plot_file_format,
            result_df=scenes,
            filepaths=filepaths,
            aoi=aoi,
            name_column=name_column,
            save_html=save_html,
        )

        return m

    def plot_results(
        self,
        figsize: Tuple[int, int] = (14, 8),
        filepaths: List[Union[str, Path]] = None,
        titles: List[str] = None,
    ) -> None:
        """
        Plots the downloaded results data.

        Args:
            figsize: matplotlib figure size.
            filepaths: Paths to images to plot. Optional, by default picks up the last
                downloaded results.
            titles: Optional list of titles for the subplots.
        """
        if filepaths is None:
            if self.results is None:
                raise ValueError("You first need to download the results!")
            filepaths = self.results
            # Unpack results path dict in case of jobcollection.
            if isinstance(filepaths, dict):
                filepaths = [
                    item for sublist in list(filepaths.values()) for item in sublist  # type: ignore
                ]

        plot_file_format = [".tif"]  # TODO: Add other fileformats.
        _plot_images(
            plot_file_format=plot_file_format,
            figsize=figsize,
            filepaths=filepaths,
            titles=titles,
        )

    def get_blocks(
        self,
        block_type=None,
        basic: bool = True,
        as_dataframe=False,
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
        if not hasattr(self, "auth"):
            raise Exception(
                "Requires authentication with UP42, use up42.authenticate()!"
            )
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
                "Getting blocks name and id, use basic=False for all block details."
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
        Gets the detailed information about a specific public block from
        the server, includes all manifest.json and marketplace.json contents.

        Args:
            block_id: The block id.
            as_dataframe: Returns a dataframe instead of json (default).

        Returns:
            A dict of the block details metadata for the specific block.
        """
        if not hasattr(self, "auth"):
            raise Exception(
                "Requires authentication with UP42, use up42.authenticate()!"
            )
        url = f"{self.auth._endpoint()}/blocks/{block_id}"  # public blocks
        response_json = self.auth._request(request_type="GET", url=url)
        details_json = response_json["data"]

        if as_dataframe:
            return pd.DataFrame.from_dict(details_json, orient="index").transpose()
        else:
            return details_json

    def validate_manifest(self, path_or_json: Union[str, Path, Dict]) -> Dict:
        """
        Validates the block manifest, input either manifest json string or filepath.

        Args:
            path_or_json: The input manifest, either filepath or json string, see example.

        Returns:
            A dictionary with the validation results and potential validation errors.

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
        if not hasattr(self, "auth"):
            raise Exception(
                "Requires authentication with UP42, use up42.authenticate()!"
            )
        url = f"{self.auth._endpoint()}/validate-schema/block"
        response_json = self.auth._request(
            request_type="POST", url=url, data=manifest_json
        )
        logger.info("The manifest is valid.")
        return response_json["data"]
