"""
Tasking functionality
"""

from up42.auth import Auth
from up42.catalog import CatalogBase
from up42.utils import (
    get_logger,
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
        **kwargs,
    ):
        """
        Helps constructing the parameters dictionary required for the tasking order.

        Args:
            data_product_id: Id of the desired UP42 data product, see `tasking.get_data_products`
            kwargs: Any additional required order parameters.

        Returns:
            The constructed parameters dictionary.

        Example:
            ```python
            order_parameters = tasking.construct_order_parameters(
                data_product_id='647780db-5a06-4b61-b525-577a8b68bb54')
            ```
        """
        order_parameters = {
            "dataProduct": data_product_id,
            "params": {**kwargs},
        }
        # TODO: geometry handling, additional kwargs

        schema = self.get_data_product_schema(data_product_id)
        required_params = list(schema["properties"].keys())
        logger.info(
            f"Required order parameters for this data product: {required_params}. Also see "
            f"tasking.get_data_product_schema()"
        )
        missing_params = set(required_params).difference(order_parameters["params"])
        redundant_params = set(order_parameters["params"]).difference(required_params)

        if not missing_params and not redundant_params:
            logger.info("Correct order parameters!")
        elif missing_params:
            logger.info(f"Missing order parameters: {missing_params}")
        else:
            logger.info(f"Incorrect order parameters: {redundant_params}")

        return order_parameters

    def __repr__(self):
        return f"Tasking(auth={self.auth})"
