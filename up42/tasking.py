"""
Tasking functionality
"""

import datetime
from typing import Any, Dict, List, Literal, Optional, Union

from shapely import geometry as geom  # type: ignore

from up42 import catalog, glossary, host, order, utils

logger = utils.get_logger(__name__)

Geometry = Union[catalog.Geometry, geom.Point]

QuotationDecision = Literal[
    "ACCEPTED",
    "REJECTED",
]
QuotationStatus = Union[Literal["NOT_DECIDED"], QuotationDecision]
FeasibilityStatus = Literal["NOT_DECIDED", "ACCEPTED"]


class InvalidDecision(ValueError):
    pass


class Tasking(catalog.CatalogBase):
    """
    The Tasking class enables access to the UP42 tasking functionality.

    Use tasking:
    ```python
    tasking = up42.initialize_tasking()
    ```
    """

    def __init__(self):
        super().__init__(glossary.CollectionType.TASKING)

    def construct_order_parameters(
        self,
        data_product_id: str,
        name: str,
        acquisition_start: Union[str, datetime.datetime],
        acquisition_end: Union[str, datetime.datetime],
        geometry: Geometry,
        tags: Optional[List[str]] = None,
    ) -> order.OrderParams:
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
        schema = self.get_data_product_schema(data_product_id)
        params: Dict[str, Any] = {param: None for param in schema["required"]}
        params |= {
            "displayName": name,
            "acquisitionStart": utils.format_time(acquisition_start),
            "acquisitionEnd": utils.format_time(acquisition_end, set_end_of_day=True),
        }
        order_parameters: order.OrderParams = {
            "dataProduct": data_product_id,
            "params": params,
        }
        if tags is not None:
            order_parameters["tags"] = tags
        geometry = utils.any_vector_to_fc(vector=geometry)
        if geometry["features"][0]["geometry"]["type"] == "Point":
            # Tasking (e.g. Blacksky) can require Point geometry.
            order_parameters["params"]["geometry"] = geometry["features"][0]["geometry"]
        else:
            geometry = utils.fc_to_query_geometry(fc=geometry, geometry_operation="intersects")
            order_parameters["params"]["geometry"] = geometry
        return order_parameters

    def get_quotations(
        self,
        quotation_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        order_id: Optional[str] = None,
        decision: Optional[List[QuotationStatus]] = None,
        sortby: str = "createdAt",
        descending: bool = True,
    ) -> list[dict]:
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
        params = {
            "workspaceId": workspace_id,
            "id": quotation_id,
            "orderId": order_id,
            "decision": decision,
            "sort": utils.SortingField(sortby, not descending),
        }
        return list(utils.paged_query(params, "/v2/tasking/quotation", self.session))

    def decide_quotation(self, quotation_id: str, decision: QuotationDecision) -> dict:
        """Accept or reject a quotation for a tasking order.
        This operation is only allowed on quotations with the NOT_DECIDED status.

        Args:
            quotation_id (str): The target quotation ID.
            decision (str): The decision made for this quotation.

        Returns:
            dict: The confirmation to the decided quotation plus metadata.
        """
        if decision not in ["ACCEPTED", "REJECTED"]:
            raise InvalidDecision("Possible decisions are only ACCEPTED or REJECTED.")
        url = host.endpoint(f"/v2/tasking/quotation/{quotation_id}")
        return self.session.patch(url, json={"decision": decision}).json()

    def get_feasibility(
        self,
        feasibility_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        order_id: Optional[str] = None,
        decision: Optional[List[FeasibilityStatus]] = None,
        sortby: str = "createdAt",
        descending: bool = True,
    ) -> list[dict]:
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
        params = {
            "id": feasibility_id,
            "workspaceId": workspace_id,
            "orderId": order_id,
            "decision": decision,
            "sort": utils.SortingField(sortby, not descending),
        }
        return list(utils.paged_query(params, "/v2/tasking/feasibility", self.session))

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
        return self.session.patch(url=url, json={"acceptedOptionId": accepted_option_id}).json()
