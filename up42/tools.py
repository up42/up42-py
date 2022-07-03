"""
Base functionality that is made available on the up42 import object (in the init) and
not bound to a specific higher level UP42 object.
"""

import json
from functools import wraps
from pathlib import Path
from typing import List, Union, Dict, Optional
from datetime import date, datetime, timedelta

import requests.exceptions
import geopandas as gpd
from geopandas import GeoDataFrame
import pandas as pd
import shapely

from up42.utils import get_logger, format_time_period

logger = get_logger(__name__)


def check_auth(func, *args, **kwargs):
    """
    Some functionality of the up42 import object (which integrates Tools functions) can theoretically be used
    before authentication with UP42, so the auth needs to be checked first.
    """
    # pylint: disable=unused-argument
    @wraps(func)  # required for mkdocstrings
    def inner(self, *args, **kwargs):
        if not hasattr(self, "auth"):
            raise Exception(
                "Requires authentication with UP42, use up42.authenticate()!"
            )
        return func(self, *args, **kwargs)

    return inner


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

    @check_auth
    def get_blocks(
        self,
        block_type: Optional[str] = None,
        basic: bool = True,
        as_dataframe: bool = False,
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

    @check_auth
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
        url = f"{self.auth._endpoint()}/blocks/{block_id}"  # public blocks
        response_json = self.auth._request(request_type="GET", url=url)
        details_json = response_json["data"]

        if as_dataframe:
            return pd.DataFrame.from_dict(details_json, orient="index").transpose()
        else:
            return details_json

    @check_auth
    def get_block_coverage(self, block_id: str) -> dict:
        # pylint: disable=unused-argument
        """
        Gets the spatial coverage of a data/processing block as
        url or GeoJson Feature Collection.

        Args:
            block_id: The block id.

        Returns:
            A dict of the spatial coverage for the specific block.
        """
        url = f"{self.auth._endpoint()}/blocks/{block_id}/coverage"
        response_json = self.auth._request(request_type="GET", url=url)
        details_json = response_json["data"]
        response_coverage = requests.get(details_json["url"]).json()
        return response_coverage

    @check_auth
    def get_credits_balance(self) -> dict:
        """
        Display the overall credits available in your account.

        Returns:
            A dict with the balance of credits available in your account.
        """
        endpoint_url = f"{self.auth._endpoint()}/accounts/me/credits/balance"
        response_json = self.auth._request(request_type="GET", url=endpoint_url)
        details_json = response_json["data"]
        return details_json

    @check_auth
    def get_credits_history(
        self,
        start_date: Optional[Union[str, datetime]] = None,
        end_date: Optional[Union[str, datetime]] = None,
    ) -> Dict[str, Union[str, int, Dict]]:
        """
        Display the overall credits history consumed in your account.
        The consumption history will be returned for all workspace_ids on your
        account.
        Args:
            start_date: The start date for the credit consumption search e.g.
                2021-12-01. Default start_date None uses 2000-01-01.
            end_date: The end date for the credit consumption search e.g.
                2021-12-31. Default end_date None uses current date.

        Returns:
            A dict with the information of the credit consumption records for
            all the users linked by the account_id.
            (see https://docs.up42.com/developers/api#operation/getHistory for
            output description)
        """
        if start_date is None:
            start_date = "2000-01-01"
        if end_date is None:
            tomorrow_date = date.today() + timedelta(days=1)
            tomorrow_datetime = datetime(
                year=tomorrow_date.year,
                month=tomorrow_date.month,
                day=tomorrow_date.day,
            )
            end_date = tomorrow_datetime.strftime("%Y-%m-%d")

        [start_formatted_date, end_formatted_date] = format_time_period(
            start_date=start_date, end_date=end_date
        ).split("/")
        search_parameters = dict(
            {
                "from": start_formatted_date,
                "to": end_formatted_date,
                "size": 2000,  # 2000 is the maximum page size for this call
                "page": 0,
            }
        )
        endpoint_url = f"{self.auth._endpoint()}/accounts/me/credits/history"
        response_json: dict = self.auth._request(
            request_type="GET", url=endpoint_url, querystring=search_parameters
        )
        isLastPage = response_json["data"]["last"]
        credit_history = response_json["data"]["content"].copy()
        result = dict(response_json["data"])
        del result["content"]
        while not isLastPage:
            search_parameters["page"] += 1
            response_json = self.auth._request(
                request_type="GET", url=endpoint_url, querystring=search_parameters
            )
            isLastPage = response_json["data"]["last"]
            credit_history.extend(response_json["data"]["content"].copy())
        result["content"] = credit_history
        return result

    @check_auth
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
        url = f"{self.auth._endpoint()}/validate-schema/block"
        response_json = self.auth._request(
            request_type="POST", url=url, data=manifest_json
        )
        logger.info("The manifest is valid.")
        return response_json["data"]
