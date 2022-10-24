"""
Tasking functionality
"""
from typing import Union

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
    autocomplete_order_parameters,
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
        acquisition_start: str,
        acquisition_end: str,
        geometry: Union[
            dict,
            Feature,
            FeatureCollection,
            list,
            GeoDataFrame,
            Polygon,
        ],
    ):
        """
        Helps constructing the parameters dictionary required for the tasking order. Each sensor has additional
        parameters that are added to the output dictionary with value None. The potential values for to select from
        are given in the logs, for more detail on the parameter use `tasking.get_data_product_schema()`.

        Args:
            data_product_id: Id of the desired UP42 data product, see `tasking.get_data_products`
            name: Name of the tasking order project.
            acquisition_start: Start date of the acquisition period, e.g. "2022-11-01"
            acquisition_end: End date of the acquisition period, e.g. "2022-11-01"
            geometry: Polygon geometry of the area to be captured.

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
        # TODO: Balcksky optional parameters?
        start_date, end_date = format_time_period(
            start_date=acquisition_start, end_date=acquisition_end
        ).split("/")
        geometry = any_vector_to_fc(vector=geometry)
        geometry = fc_to_query_geometry(fc=geometry, geometry_operation="intersects")

        params = {
            "displayName": name,
            "acquisitionStart": start_date,
            "acquisitionEnd": end_date,
            "geometry": geometry,
        }
        schema = self.get_data_product_schema(data_product_id)
        logger.info(
            "See `tasking.get_data_product_schema(data_product_id)` for more detail on the parameter options."
        )

        order_parameters = autocomplete_order_parameters(
            data_product_id, schema, params
        )

        return order_parameters

    def __repr__(self):
        return f"Tasking(auth={self.auth})"
