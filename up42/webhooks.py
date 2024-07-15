import dataclasses
import warnings
from typing import List, Optional

from up42 import base, host, utils

logger = utils.get_logger(__name__)


@dataclasses.dataclass
class Webhook:
    session = base.Session()
    workspace_id = base.WorkspaceId()
    url: str
    name: str
    events: List[str]
    active: bool = False
    secret: Optional[str] = None
    id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    """
    # Webhook
    Contains UP42 webhooks functionality to set up a custom callback e.g. when an order is finished
    a webhook is triggered and an event notification is transmitted via HTTPS to a specific URL.

    Also see the [full webhook documentation](https://docs.up42.com/account/webhooks).
    """

    def save(self):
        payload = {
            "name": self.name,
            "url": self.url,
            "events": self.events,
            "secret": self.secret,
            "active": self.active,
        }
        if self.id:
            url = host.endpoint(f"/workspaces/{self.workspace_id}/webhooks/{self.id}")
            response_json = self.session.put(url=url, json=payload).json()["data"]
            self.updated_at = response_json["updatedAt"]
            logger.info("Updated webhook %s", self)
        else:
            url = host.endpoint(f"/workspaces/{self.workspace_id}/webhooks")
            response_json = self.session.post(url=url, json=payload).json()["data"]
            self.id = response_json["id"]
            self.created_at = response_json["createdAt"]
            self.updated_at = response_json["updatedAt"]
            logger.info("Created webhook %s", self)

    @staticmethod
    def from_metadata(metadata: dict) -> "Webhook":
        return Webhook(
            id=metadata["id"],
            secret=metadata.get("secret"),
            active=metadata["active"],
            url=metadata["url"],
            name=metadata["name"],
            events=metadata["events"],
            created_at=metadata.get("createdAt"),
            updated_at=metadata.get("updatedAt"),
        )

    @classmethod
    def get(cls, webhook_id: str) -> "Webhook":
        url = host.endpoint(f"/workspaces/{cls.workspace_id}/webhooks/{webhook_id}")
        metadata = cls.session.get(url).json()["data"]
        return cls.from_metadata(metadata)

    @property
    @utils.deprecation("up42.Webhook properties", "2.0.0")
    def info(self) -> dict:
        return dataclasses.asdict(self)

    @property
    @utils.deprecation("up42.Webhook::id", "2.0.0")
    def webhook_id(self):
        return self.id

    def trigger_test_events(self) -> dict:
        """
        Triggers webhook test event to test your receiving side. The UP42 server will send test
        messages for each subscribed event to the specified webhook URL.

        Returns:
            A dict with information about the emitted test events.
        """
        url = host.endpoint(f"/workspaces/{self.workspace_id}/webhooks/{self.id}/tests")
        return self.session.post(url=url).json()["data"]

    @utils.deprecation("up42.Webhook::save", "2.0.0")
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
        self.name = name or self.name
        self.url = url or self.url
        self.events = events or self.events
        self.secret = secret or self.secret
        self.active = active if active is not None else self.active
        self.save()
        logger.info("Updated webhook %s", self)
        return self

    def delete(self) -> None:
        """
        Deletes a registered webhook.
        """
        url = host.endpoint(f"/workspaces/{self.workspace_id}/webhooks/{self.id}")
        self.session.delete(url=url)
        logger.info("Successfully deleted Webhook: %s", self.id)

    @classmethod
    def get_webhook_events(cls) -> list[dict]:
        """
        Gets all available webhook events.

        Returns:
            A dict of the available webhook events.
        """
        url = host.endpoint("/webhooks/events")
        return cls.session.get(url=url).json()["data"]

    @classmethod
    def all(cls, return_json: bool = False) -> List["Webhook"]:
        """
        Gets all registered webhooks for this workspace.

        Args:
            return_json: If true returns the webhooks information as JSON instead of webhook class objects.

        Returns:
            A list of the registered webhooks for this workspace.
        """
        url = host.endpoint(f"/workspaces/{cls.workspace_id}/webhooks")
        payload = cls.session.get(url=url).json()["data"]
        logger.info("Queried %s webhooks.", len(payload))

        if return_json:
            warnings.warn(
                "return_json is deprecated and will be dropped in version 2.0.0",
                DeprecationWarning,
                stacklevel=2,
            )
            return payload
        return [cls.from_metadata(metadata) for metadata in payload]

    @classmethod
    @utils.deprecation("up42.Webhook::save", "2.0.0")
    def create(
        cls,
        name: str,
        url: str,
        events: List[str],
        active: bool = False,
        secret: Optional[str] = None,
    ) -> "Webhook":
        """
        Registers a new webhook in the system.

        Args:
            name: Webhook name
            url: Unique URL where the webhook will send the message (HTTPS required)
            events: List of event types e.g. [order.status, job.status]
            active: Webhook status.
            secret: String that acts as signature to the https request sent to the url.

        Returns:
            The newly registered webhook.
        """
        webhook = cls(name=name, url=url, events=events, secret=secret, active=active)
        webhook.save()
        return webhook
