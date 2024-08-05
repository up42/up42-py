import dataclasses
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

    def trigger_test_events(self) -> dict:
        """
        Triggers webhook test event to test your receiving side. The UP42 server will send test
        messages for each subscribed event to the specified webhook URL.

        Returns:
            A dict with information about the emitted test events.
        """
        url = host.endpoint(f"/workspaces/{self.workspace_id}/webhooks/{self.id}/tests")
        return self.session.post(url=url).json()["data"]

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
    def all(cls) -> List["Webhook"]:
        """
        Gets all registered webhooks for this workspace.

        Returns:
            A list of the registered webhooks for this workspace.
        """
        url = host.endpoint(f"/workspaces/{cls.workspace_id}/webhooks")
        payload = cls.session.get(url=url).json()["data"]
        logger.info("Queried %s webhooks.", len(payload))

        return [cls.from_metadata(metadata) for metadata in payload]
