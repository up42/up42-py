from typing import List, Optional

from up42.auth import Auth
from up42.utils import get_logger

logger = get_logger(__name__)


class Webhooks:
    """
    Contains UP42 webhooks functionality to set up a custom callback e.g. when an order is finished
    he webhook is triggered and an event notification is transmitted via HTTPS to a specific URL.

    Also see the [full webhook documentation](https://docs.up42.com/account/webhooks).

    All functionality to create new webhooks or query existing webhooks is accessible via the `up42`
    object, e.g.
    ```python
    webhook = up42.get_webhook(webhook_id = "...")
    ```

    The webhook object can then be further modified, e.g.
    ```python
    webhook.trigger_test_event()
    ```
    """

    def __init__(self, auth: Auth):
        self.auth = auth
        self.workspace_id = auth.workspace_id

    def get_webhook_events(self) -> dict:
        """
        Gets all available webhook events.

        Returns:
            A dict of the available webhook events.
        """
        url = f"{self.auth._endpoint()}/webhooks/events"
        response_json = self.auth._request(request_type="GET", url=url)
        return response_json["data"]

    # def get_webhook(self, webhook_id: str) -> dict:
    #     """
    #     Gets a specific webhook by its id.
    #
    #     Args:
    #         webhook_id: Id of a specific webhook to query.
    #
    #     Returns:
    #         A dict of the specified webhook in this workspace.
    #     """
    #     url = f"{self.auth._endpoint()}/workspaces/{self.workspace_id}/webhooks/{webhook_id}"
    #     response_json = self.auth._request(request_type="GET", url=url)
    #     webhook = Webhook(auth=self.auth, webhook_id=webhook_id, webhook_info=response_json["data"])
    #     logger.info(f"Queried webhook with id {webhook_id}")
    #     return webhook

    def get_webhooks(self) -> list:
        """
        Gets all registered webhooks for this workspace.

        Returns:
            A list of the registered webhooks for this workspace.
        """
        # TODO: pagination?
        url = f"{self.auth._endpoint()}/workspaces/{self.workspace_id}/webhooks"
        response_json = self.auth._request(request_type="GET", url=url)
        webhooks = [
            Webhook(
                auth=self.auth, webhook_id=webhook_info["id"], webhook_info=webhook_info
            )
            for webhook_info in response_json["data"]
        ]
        logger.info(f"Queried {len(webhooks)} webhooks.")
        return webhooks

    def create_webhook(
        self,
        name: str,
        url: str,
        events: List[str],
        active: bool = False,
        secret: Optional[str] = None,
    ) -> dict:
        """
        Registers a new webhook in the system.

        Args:
            name: Webhook name
            url: Unique URL where the webhook will send the message (HTTPS required)
            events: List of event types (order status / job task status)
            active: Webhook status.
            secret: String that acts as signature to the https request sent to the url.

        Returns:
            A dict with details of the registered webhook.
        """
        input_parameters = {
            "name": name,
            "url": url,
            "events": events,
            "secret": secret,
            "active": active,
        }
        url_post = f"{self.auth._endpoint()}/workspaces/{self.workspace_id}/webhooks"
        response_json = self.auth._request(
            request_type="POST", url=url_post, data=input_parameters
        )
        # TODO
        logger.info("Created webhook")
        return response_json["data"]


class Webhook:
    """
    A specific UP42 webhook.
    """

    def __init__(self, auth: Auth, webhook_id: str, webhook_info: dict = None):
        self.auth = auth
        self.workspace_id = auth.workspace_id
        self.webhook_id = webhook_id
        if webhook_info is not None:
            self._info = webhook_info
        else:
            self._info = self.info

    def __repr__(self):
        return f"Webhook(name: {self._info['name']}, webhook_id: {self.webhook_id}, active: {self._info['active']}"

    @property
    def info(self) -> dict:
        """
        Gets and updates the webhook metadata information.
        """
        url = f"{self.auth._endpoint()}/workspaces/{self.workspace_id}/webhooks/{self.webhook_id}"
        response_json = self.auth._request(request_type="GET", url=url)
        self._info = response_json["data"]
        return self._info

    def trigger_test_event(self, webhook_id: str) -> dict:
        """
        Triggers webhook test event to test your receiving side. The UP42 server will Our server will send test
        messages for each subscribed event to the specified webhook URL.

        Returns:
            A dict with details of the updated webhook.
        """
        # TODO: Event names specification
        url = f"{self.auth._endpoint()}/workspaces/{self.workspace_id}/webhooks/{webhook_id}/tests"
        response_json = self.auth._request(
            request_type="POST",
            url=url,
        )
        return response_json["data"]

    def update(
        self,
        webhook_id: str,
        name: str,
        url: str,
        events: List[str],
        active: bool = False,
        secret: Optional[str] = None,
    ) -> dict:
        """
        Updates a registered webhook.

        Args:
            webhook_id: Id of a specific webhook to update.
            name: Webhook name
            url: Unique URL where the webhook will send the message (HTTPS required)
            events: List of event types (order status / job task status)
            active: Webhook status.
            secret: String that acts as signature to the https request sent to the url.

        Returns:
            A dict with details of the updated webhook.
        """
        input_parameters = {
            "name": name,
            "url": url,
            "events": events,
            "secret": secret,
            "active": active,
        }
        url_post = f"{self.auth._endpoint()}/workspaces/{self.workspace_id}/webhooks/{webhook_id}"
        response_json = self.auth._request(
            request_type="POST", url=url_post, data=input_parameters
        )
        return response_json["data"]

    def delete(self, webhook_id: str) -> None:
        """
        Deletes a registered webhook.
        """
        url = f"{self.auth._endpoint()}/workspaces/{self.workspace_id}/webhooks/{webhook_id}"
        self.auth._request(request_type="DELETE", url=url)
        # TODO
        logger.info(f"Successfully deleted Webhook: ")
