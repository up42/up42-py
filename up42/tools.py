"""
Base functionality that is made available on the up42 import object (in the init) and
not bound to a specific higher level UP42 object.
"""

import json
from pathlib import Path
from typing import List, Union, Dict, Optional

from geopandas import GeoDataFrame
import geopandas as gpd
import pandas as pd
import shapely

from up42.viztools import folium_base_map, DrawFoliumOverride
from up42.utils import (
    get_logger,
)

try:
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
        The tools class contains the base functionality that is not bound to a specific
        higher level UP42 object.
        """
        if auth:
            self.auth = auth
        self.quicklooks = None
        self.results = None

    # pylint: disable=no-self-use
    def read_vector_file(
        self, filename: str = "aoi.geojson", as_dataframe: bool = False
    ) -> Union[dict, GeoDataFrame]:
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

    @staticmethod
    def draw_aoi():
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
        return m

    def get_blocks(
        self,
        block_type: Optional[str] = None,
        basic: bool = True,
        as_dataframe=False,
    ) -> Union[List[Dict], dict]:
        """
        Gets a list of all public blocks on the marketplace. Can not access custom blocks.

        Args:
            block_type: Optionally filters to "data" or "processing" blocks, default None.
            basic: Optionally returns simple version {block_id : block_name}
            as_dataframe: Returns a dataframe instead of json (default).

        Returns:
            A list of the public blocks and their metadata. Optional a simpler version
            dict.
        """
        try:
            block_type = block_type.lower()  # type: ignore
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

    def get_block_details(self, block_id: str, as_dataframe: bool = False) -> dict:
        """
        Gets the detailed information about a specific public block from
        the server, includes all manifest.json and marketplace.json contents.
        Can not access custom blocks.

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

    def validate_manifest(self, path_or_json: Union[str, Path, dict]) -> dict:
        """
        Validates a block manifest json.

        The block manifest is required to build a custom block on UP42 and contains
        the metadata about the block as well as block input and output capabilities.
        Also see the
        [manifest chapter in the UP42 documentation](https://docs.up42.com/reference/block-manifest.html).

        Args:
            path_or_json: The input manifest, either a filepath or json string, see example.

        Returns:
            A dictionary with the validation results and potential validation errors.
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
