"""
Tasking functionality
"""
from typing import Optional, Union
from datetime import datetime

from geopandas import GeoDataFrame
from shapely.geometry import Polygon, Point
from geojson import Feature, FeatureCollection

from up42.auth import Auth
from up42.catalog import CatalogBase
from up42.utils import (
    get_logger,
    format_time,
    any_vector_to_fc,
    fc_to_query_geometry,
    autocomplete_order_parameters,
    replace_page_query,
)

logger = get_logger(__name__)


class Tasking(CatalogBase):
    """
    The Tasking class enables access to the UP42 tasking functionality.

    Use tasking:
    ```python
    tasking = up42.initialize_tasking()
    ```
    """

    def __init__(self, auth: Auth):
        self.auth = auth
        self.type = "TASKING"

    def construct_order_parameters(
        self,
        data_product_id: str,
        name: str,
        acquisition_start: Union[str, datetime],
        acquisition_end: Union[str, datetime],
        geometry: Union[
            FeatureCollection, Feature, dict, list, GeoDataFrame, Polygon, Point
        ],
    ):
        """
        Helps constructing the parameters dictionary required for the tasking order. Each sensor has additional
        parameters that are added to the output dictionary with value None. The potential values for to select from
        are given in the logs, for more detail on the parameter use `tasking.get_data_product_schema()`.

        Args:
            data_product_id: Id of the desired UP42 data product, see `tasking.get_data_products`
            name: Name of the tasking order project.
            acquisition_start: Start date of the acquisition period, datetime or isoformat string e.g. "2022-11-01"
            acquisition_end: End date of the acquisition period, datetime or isoformat string e.g. "2022-11-01"
            geometry: Geometry of the area to be captured, default a Polygon. Allows Point feature for specific
                data products. One of FeatureCollection, Feature, dict (geojson geometry), list (bounds coordinates),
                GeoDataFrame, shapely.Polygon, shapely.Point. All assume EPSG 4326!

        Returns:
            The constructed order parameters dictionary.

        Example:
            ```python
            order_parameters = tasking.construct_order_parameters(
                data_product_id='647780db-5a06-4b61-b525-577a8b68bb54',
                name="My tasking order",
                acquisition_start=2022-11-01,
                acquisition_end=2022-12-01,
                geometry={'type': 'Polygon',
                   'coordinates': (((13.375966, 52.515068),
                     (13.375966, 52.516639),
                     (13.378314, 52.516639),
                     (13.378314, 52.515068),
                     (13.375966, 52.515068)),)}
                )
            ```
        """
        order_parameters = {
            "dataProduct": data_product_id,
            "params": {
                "displayName": name,
                "acquisitionStart": format_time(acquisition_start),
                "acquisitionEnd": format_time(acquisition_end, set_end_of_day=True),
            },
        }

        schema = self.get_data_product_schema(data_product_id)
        logger.info(
            "See `tasking.get_data_product_schema(data_product_id)` for more detail on the parameter options."
        )
        order_parameters = autocomplete_order_parameters(order_parameters, schema)

        geometry = any_vector_to_fc(vector=geometry)
        if geometry["features"][0]["geometry"]["type"] == "Point":
            # Tasking (e.g. Blacksky) can require Point geometry.
            order_parameters["params"]["geometry"] = geometry["features"][0]["geometry"]  # type: ignore
        else:
            geometry = fc_to_query_geometry(
                fc=geometry, geometry_operation="intersects"
            )
            order_parameters["params"]["geometry"] = geometry  # type: ignore

        return order_parameters

    def _query_paginated_output(self, url: str):
        page = 0
        response = self.auth._request(request_type="GET", url=url)
        json_results = response["content"]
        not_last_page = not (response["last"])
        while not_last_page:
            page += 1
            url = replace_page_query(url, page)
            response = self.auth._request(request_type="GET", url=url)
            json_results.extend(response["content"])
            not_last_page = not (response["last"])
        return json_results

    def get_quotations(
        self,
        workspace_id: Optional[str] = None,
        order_id: Optional[str] = None,
        decision: Optional[str] = None,
        sortby: str = "createdAt",
        descending: bool = True,
    ):
        """_summary_

        Args:
            workspace_id (Optional[str], optional): The workspace id (uuid) to filter the search. Defaults to None.
            order_id (Optional[str], optional): The order id (uuid) to filter the search. Defaults to None.
            decision (Optional[str], optional): the status of the quotation (NOT_DECIDED, ACCEPTED or REJECTED). Defaults to None.
            sortby (str, optional): The results sorting method that arranges elements in ascending or descending order based on a chosen field. The format is <field name>,<asc or desc>. . Defaults to "createdAt".
            descending (bool, optional): _description_. Defaults to True.

        Returns:
            JSON: The json representation with the quotations resulted from the search.
        """
        sort = f"{sortby},{'desc' if descending else 'asc'}"
        url = f"{self.auth._endpoint()}/v2/tasking/quotation?page=0&sort={sort}"
        if workspace_id is not None:
            url += f"&workspaceId={workspace_id}"
        if order_id is not None:
            url += f"&order_id={order_id}"
        if decision in ["NOT_DECIDED", "ACCEPTED", "REJECTED"]:
            url += f"&decision={decision}"
        elif decision is not None:
            logger.warning(
                f"Desicion values are NOT_DECIDED, ACCEPTED, REJECTED, otherwise desicion filter values ignored."
            )
        return self._query_paginated_output(url)

    def __repr__(self):
        return f"Tasking(auth={self.auth})"
