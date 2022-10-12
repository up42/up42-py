"""
Tasking functionality
"""
from typing import Union, List, Dict, Any

from geopandas import GeoDataFrame
from shapely.geometry import Polygon
from geojson import Feature, FeatureCollection

from up42.auth import Auth
from up42.catalog import CatalogBase
from up42.utils import (
    get_logger,
    format_time_period,
    any_vector_to_fc,
    fc_to_query_geometry,
)

logger = get_logger(__name__)


# pylint: disable=duplicate-code
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
        start_date: str,
        end_date: str,
        geometry: Union[
            dict,
            Feature,
            FeatureCollection,
            list,
            GeoDataFrame,
            Polygon,
        ],
        **kwargs,
    ):
        """
        Helps constructing the parameters dictionary required for the tasking order.

        Args:
            data_product_id: Id of the desired UP42 data product, see `tasking.get_data_products`
            name:
            start_date:
            end_date:
            geometry:
            kwargs: Any additional required order parameters.

        Returns:
            The constructed parameters dictionary.

        Example:
            ```python
            order_parameters = tasking.construct_order_parameters(
                data_product_id='647780db-5a06-4b61-b525-577a8b68bb54')
            ```
        """
        start_date, end_date = format_time_period(
            start_date=start_date, end_date=end_date
        ).split("/")
        geometry = any_vector_to_fc(vector=geometry)
        geometry = fc_to_query_geometry(fc=geometry, geometry_operation="intersects")

        order_parameters = {
            "dataProduct": data_product_id,
            "params": {
                "displayName": name,
                "acquisitionStart": start_date,
                "acquisitionEnd": end_date,
                "geometry": geometry,
                **kwargs,
            },
        }
        # TODO: geometry handling, additional kwargs

        schema = self.get_data_product_schema(data_product_id)
        required_params = schema["required"]
        optional_params = list(
            set(list(schema["properties"].keys())).difference(required_params)
        )
        logger.info(
            f"Order parameters for this data product - Required: {required_params} - Optional: {optional_params}. "
            f"Also see catalog.get_data_product_schema()"
        )
        missing_params = list(
            set(required_params).difference(order_parameters["params"])
        )
        redundant_params = list(
            set(order_parameters["params"]).difference(
                required_params + optional_params
            )
        )

        if not missing_params and not redundant_params:
            logger.info("Correct order parameters!")
        elif missing_params:
            logger.info(f"Missing order parameters: {missing_params}")
        else:
            logger.info(f"Incorrect order parameters: {redundant_params}")

        return order_parameters

    def __repr__(self):
        return f"Tasking(auth={self.auth})"
