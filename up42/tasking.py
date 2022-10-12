"""
Tasking functionality
"""

from pathlib import Path
from typing import Union, List, Tuple, Dict, Any

from pandas import Series
from geopandas import GeoDataFrame
from shapely.geometry import Polygon
from geojson import Feature, FeatureCollection
from tqdm import tqdm

from up42.auth import Auth
from up42.order import Order
from up42.catalog import CatalogBase
from up42.utils import (
    get_logger,
    any_vector_to_fc,
    fc_to_query_geometry,
    format_time_period,
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
        image_id: str,
        aoi: Union[
            dict,
            Feature,
            FeatureCollection,
            list,
            GeoDataFrame,
            Polygon,
        ] = None,
    ):
        """
        Helps constructing the parameters dictionary required for the search.

        Args:
            data_product_id: Id of the desired UP42 data product, see `catalog.get_data_products`
            image_id: The id of the desired image (from search results)
            aoi: The geometry of the order, one of dict, Feature, FeatureCollection,
                list, GeoDataFrame, Polygon.

        Returns:
            The constructed parameters dictionary.

        Example:
            ```python
            order_parameters = catalog.construct_order_parameters(data_product_id='647780db-5a06-4b61-b525-577a8b68bb54',
                                                                  image_id='6434e7af-2d41-4ded-a789-fb1b2447ac92',
                                                                  aoi={'type': 'Polygon',
                                                                    'coordinates': (((13.375966, 52.515068),
                                                                      (13.375966, 52.516639),
                                                                      (13.378314, 52.516639),
                                                                      (13.378314, 52.515068),
                                                                      (13.375966, 52.515068)),)})
            ```
        """
        schema = self.get_data_product_schema(data_product_id)
        required_params = list(schema["properties"].keys())
        logger.info(
            f"This data product requires order_parameters {required_params}. Also see "
            f".get_data_product_schema()"
        )

        order_parameters = {
            "dataProduct": data_product_id,
            "params": {
                "id": image_id,
            },
        }
        if aoi is not None:
            aoi = any_vector_to_fc(vector=aoi)
            aoi = fc_to_query_geometry(fc=aoi, geometry_operation="intersects")
            order_parameters["params"]["aoi"] = aoi
        return order_parameters

        def __repr__(self):
            return f"Tasking(auth={self.auth})"
