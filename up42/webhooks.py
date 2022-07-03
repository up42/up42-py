from typing import List, Optional

from up42.auth import Auth
from up42.utils import get_logger

logger = get_logger(__name__)


class Webhook:
    """
    # Webhook

    Webhook class to control a specific UP42 webhook, e.g. modify, test or delete the specific webhook.

    ```python
    webhook = webhook.trigger_test_event()
    ```
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

    def trigger_test_events(self) -> dict:
        """
        Triggers webhook test event to test your receiving side. The UP42 server will send test
        messages for each subscribed event to the specified webhook URL.

        Returns:
            A dict with information about the test events.
        """
        url = f"{self.auth._endpoint()}/workspaces/{self.workspace_id}/webhooks/{self.webhook_id}/tests"
        response_json = self.auth._request(
            request_type="POST",
            url=url,
        )
        return response_json["data"]

    def update(
        self,
        name: Optional[str] = None,
        url: Optional[str] = None,
        events: Optional[List[str]] = None,
        active: Optional[bool] = None,
        secret: Optional[str] = None,
    ) -> "Webhook":
        """
        Updates a registered webhook.

        Args:
            name: Updated webhook name
            url: Updated unique URL where the webhook will send the message (HTTPS required)
            events: Updated list of event types [order.status, job.status].
            active: Updated webhook status.
            secret: Updated string that acts as signature to the https request sent to the url.

        Returns:
            The updated webhook object.
        """
        self.info  # _info could be outdated. #pylint: disable=pointless-statement
        input_parameters = {
            "name": name if name is not None else self._info["name"],
            "url": url if url is not None else self._info["url"],
            "events": events if events is not None else self._info["events"],
            "secret": secret if secret is not None else self._info["secret"],
            "active": active if active is not None else self._info["active"],
        }
        url_put = f"{self.auth._endpoint()}/workspaces/{self.workspace_id}/webhooks/{self.webhook_id}"
        response_json = self.auth._request(
            request_type="PUT", url=url_put, data=input_parameters
        )
        self._info = response_json["data"]
        logger.info(f"Updated webhook {self}")
        return self

    def delete(self) -> None:
        """
        Deletes a registered webhook.
        """
        url = f"{self.auth._endpoint()}/workspaces/{self.workspace_id}/webhooks/{self.webhook_id}"
        self.auth._request(request_type="DELETE", url=url)
        logger.info(f"Successfully deleted Webhook: {self.webhook_id}")


class Webhooks:
    """
    Contains UP42 webhooks functionality to set up a custom callback e.g. when an order is finished
    he webhook is triggered and an event notification is transmitted via HTTPS to a specific URL.

    Also see the [full webhook documentation](https://docs.up42.com/account/webhooks).

    Create a new webhook or query a existing ones via the `up42` object, e.g.
    ```python
    webhooks = up42.get_webhooks()
    ```
    ```python
    webhook = up42.initialize_webhook(webhook_id = "...")
    ```

    The resulting Webhook object lets you modify, test or delete the specific webhook, e.g.
    ```python
    webhook = webhook.trigger_test_event()
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

    def get_webhooks(self, return_json: bool = False) -> List[Webhook]:
        """
        Gets all registered webhooks for this workspace.

        Args:
            return_json: If true returns the webhooks information as json instead of webhook class objects.

        Returns:
            A list of the registered webhooks for this workspace.
        """
        url = f"{self.auth._endpoint()}/workspaces/{self.workspace_id}/webhooks"
        response_json = self.auth._request(request_type="GET", url=url)
        logger.info(f"Queried {len(response_json['data'])} webhooks.")

        if return_json:
            return response_json["data"]
        webhooks = [
            Webhook(
                auth=self.auth, webhook_id=webhook_info["id"], webhook_info=webhook_info
            )
            for webhook_info in response_json["data"]
        ]
        return webhooks

    def create_webhook(
        self,
        name: str,
        url: str,
        events: List[str],
        active: bool = False,
        secret: Optional[str] = None,
    ) -> Webhook:
        """
        Registers a new webhook in the system.

        Args:
            name: Webhook name
            url: Unique URL where the webhook will send the message (HTTPS required)
            events: List of event types e.g. [order.status, job.status]
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
        webhook = Webhook(
            auth=self.auth,
            webhook_id=response_json["data"]["id"],
            webhook_info=response_json["data"],
        )
        logger.info(f"Created webhook {webhook}")
        return webhook
