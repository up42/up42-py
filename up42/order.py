from typing import Dict

from up42.auth import Auth
from up42.tools import Tools
from up42.viztools import VizTools

from up42.utils import (
    get_logger,
)

logger = get_logger(__name__)


class Order(VizTools, Tools):
    def __init__(
        self,
        auth: Auth,
        order_id: str,
    ):
        """
        The Order class provides access to the results, parameters and metadata of UP42
        Orders.
        """
        self.auth = auth
        self.workspace_id = auth.workspace_id
        self.order_id = order_id
        self.results = None
        if self.auth.get_info:
            self._info = self.info

    def __repr__(self):
        info = self.info
        return (
            f"Order(order_id: {self.order_id}, assets: {info['assets']}, dataProvider: {info['dataProvider']}, "
            f"status: {info['status']}, createdAt: {info['createdAt']}, updatedAt: {info['updatedAt']})"
        )

    @property
    def info(self) -> Dict:
        """
        Gets the Order information.
        """
        url = f"{self.auth._endpoint()}/workspaces/{self.workspace_id}/orders/{self.order_id}"
        response_json = self.auth._request(request_type="GET", url=url)
        self._info = response_json["data"]
        return response_json["data"]

    @property
    def status(self) -> str:
        """
        Gets the Order status. One of `PLACED`, `FULFILLED`...
        """
        status = self.info["status"]
        logger.info(f"Order is {status}")
        return status

    @property
    def is_fulfilled(self) -> bool:
        """
        Gets `True` if the order is fulfilled, `False` otherwise.
        Also see [status attribute](order.md#up42.order.Order.status).
        """
        return self.status == "FULFILLED"

    @property
    def metadata(self) -> Dict:
        """
        Gets the Order metadata.
        """
        url = f"{self.auth._endpoint()}/workspaces/{self.workspace_id}/orders/{self.order_id}/metadata"
        response_json = self.auth._request(request_type="GET", url=url)
        return response_json["data"]
