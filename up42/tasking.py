"""
Tasking functionality
"""

import datetime
from typing import List, Optional, Union

import geojson  # type: ignore
import geopandas  # type: ignore
from shapely import geometry as shp_geometry  # type: ignore

from up42 import auth as up42_auth
from up42 import catalog, glossary, host, order, utils

logger = utils.get_logger(__name__)


class Tasking(catalog.CatalogBase):
    """
    The Tasking class enables access to the UP42 tasking functionality.

    Use tasking:
    ```python
    tasking = up42.initialize_tasking()
    ```
    """

    def __init__(self, auth: up42_auth.Auth):
        super().__init__(glossary.CollectionType.TASKING)
        self.auth = auth

    def construct_order_parameters(
        self,
        data_product_id: str,
        name: str,
        acquisition_start: Union[str, datetime.datetime],
        acquisition_end: Union[str, datetime.datetime],
        geometry: Union[
            geojson.FeatureCollection,
            geojson.Feature,
            dict,
            list,
            geopandas.GeoDataFrame,
            shp_geometry.Polygon,
            shp_geometry.Point,
        ],
        tags: Optional[List[str]] = None,
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
            tags: A list of tags that categorize the order.

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
        order_parameters: order.OrderParams = {
            "dataProduct": data_product_id,
            "params": {
                "displayName": name,
                "acquisitionStart": utils.format_time(acquisition_start),
                "acquisitionEnd": utils.format_time(acquisition_end, set_end_of_day=True),
            },
        }
        if tags is not None:
            order_parameters["tags"] = tags

        schema = self.get_data_product_schema(data_product_id)
        logger.info("See `tasking.get_data_product_schema(data_product_id)` for more detail on the parameter options.")
        missing_params = {param: order_parameters["params"].get(param) for param in schema["required"]}
        order_parameters["params"].update(missing_params)

        geometry = utils.any_vector_to_fc(vector=geometry)
        assert isinstance(order_parameters["params"], dict)
        if geometry["features"][0]["geometry"]["type"] == "Point":
            # Tasking (e.g. Blacksky) can require Point geometry.
            order_parameters["params"]["geometry"] = geometry["features"][0]["geometry"]
        else:
            geometry = utils.fc_to_query_geometry(fc=geometry, geometry_operation="intersects")
            order_parameters["params"]["geometry"] = geometry

        return order_parameters

    def _query_paginated_output(self, url: str):
        page = 0
        response = self.auth.request(request_type="GET", url=url)
        json_results = response["content"]
        not_last_page = not response["last"]
        while not_last_page:
            page += 1
            url = utils.replace_page_query(url, page)
            response = self.auth.request(request_type="GET", url=url)
            json_results.extend(response["content"])
            not_last_page = not response["last"]
        return json_results

    def get_quotations(
        self,
        quotation_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        order_id: Optional[str] = None,
        decision: Optional[List[str]] = None,
        sortby: str = "createdAt",
        descending: bool = True,
    ) -> list:
        """
        This function returns the quotations for tasking by filtering and sorting by different parameters.

        Args:
            quotation_id (Optional[str], optional): The quotation Id for the specific quotation to retrieve.
            workspace_id (Optional[str], optional): The workspace id (uuid) to filter the search.
            order_id (Optional[str], optional): The order id (uuid) to filter the search.
            decision (Optional[list[str]], optional): quotation status (NOT_DECIDED, ACCEPTED or REJECTED).
            sortby: Param to sort the results. Default value set to createdAt
            descending (bool, optional): Descending or ascending sort.

        Returns:
            JSON: The json representation with the quotations resulted from the search.
        """
        sort = f"""{sortby},{"desc" if descending else "asc"}"""
        url = host.endpoint(f"/v2/tasking/quotation?page=0&sort={sort}")
        if quotation_id is not None:
            url += f"&id={quotation_id}"
        if workspace_id is not None:
            url += f"&workspaceId={workspace_id}"
        if order_id is not None:
            url += f"&orderId={order_id}"
        if decision is not None:
            decisions_validation = (
                single_decision in ["NOT_DECIDED", "ACCEPTED", "REJECTED"] for single_decision in decision
            )
            if all(decisions_validation):
                for single_decision in decision:
                    url += f"&decision={single_decision}"
            else:
                logger.warning(
                    "decision values are NOT_DECIDED, ACCEPTED, REJECTED, otherwise decision filter values ignored."
                )
        return self._query_paginated_output(url)

    def decide_quotation(self, quotation_id: str, decision: str) -> dict:
        """Accept or reject a quotation for a tasking order.
        This operation is only allowed on quotations with the NOT_DECIDED status.

        Args:
            quotation_id (str): The target quotation ID.
            decision (str): The decision made for this quotation.

        Returns:
            dict: The confirmation to the decided quotation plus metadata.
        """
        if decision not in ["ACCEPTED", "REJECTED"]:
            raise ValueError("Possible desicions are only ACCEPTED or REJECTED.")

        url = host.endpoint(f"/v2/tasking/quotation/{quotation_id}")

        decision_payload = {"decision": decision}

        response_json = self.auth.request(request_type="PATCH", url=url, data=decision_payload)

        return response_json

    def get_feasibility(
        self,
        feasibility_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        order_id: Optional[str] = None,
        decision: Optional[List[str]] = None,
        sortby: str = "createdAt",
        descending: bool = True,
    ) -> list:
        """
        This function returns the list of feasibility studies for tasking orders.

        Args:
            feasibility_id (Optional[str], optional): The feasibility Id for the specific feasibility study to retrieve.
            workspace_id (Optional[str], optional): The workspace id (uuid) to filter the search.
            order_id (Optional[str], optional): The order id (uuid) to filter the search.
            decision (Optional[list[str]], optional): The status of the quotation
            (NOT_DECIDED or ACCEPTED).
            sortby (str, optional): Arranges elements in asc or desc order based on a chosen field.
            The format is <field name>,<asc or desc>. Eg: "id,asc"
            descending (bool, optional): Descending or ascending sort.

        Returns:
            JSON: The json representation with the feasibility resulted from the search.
        """
        sort = f"""{sortby},{"desc" if descending else "asc"}"""
        url = host.endpoint(f"/v2/tasking/feasibility?page=0&sort={sort}")
        if feasibility_id is not None:
            url += f"&id={feasibility_id}"
        if workspace_id is not None:
            url += f"&workspaceId={workspace_id}"
        if order_id is not None:
            url += f"&orderId={order_id}"
        if decision is not None:
            decisions_validation = (single_decision in ["NOT_DECIDED", "ACCEPTED"] for single_decision in decision)
            if all(decisions_validation):
                for single_decision in decision:
                    url += f"&decision={single_decision}"
            else:
                logger.warning(
                    "decision values should be in NOT_DECIDED or ACCEPTED, "
                    "otherwise decision filter values will be ignored."
                )
        return self._query_paginated_output(url)

    def choose_feasibility(self, feasibility_id: str, accepted_option_id: str) -> dict:
        """Accept one of the proposed feasibility study options.
        This operation is only allowed on feasibility studies with the NOT_DECIDED status.

        Args:
            feasibility_id (str): The target feasibility study ID.
            accepted_option_id (str): The ID of the feasibility option to accept.

        Returns:
            dict: The confirmation to the decided quotation plus metadata.
        """
        url = host.endpoint(f"/v2/tasking/feasibility/{feasibility_id}")
        accepted_option_payload = {"acceptedOptionId": accepted_option_id}
        response_json = self.auth.request(request_type="PATCH", url=url, data=accepted_option_payload)
        return response_json
