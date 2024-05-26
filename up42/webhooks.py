import dataclasses
from typing import List, Optional

import requests

from up42 import host, utils

logger = utils.get_logger(__name__)


class SessionMixin:
    session: requests.Session


@dataclasses.dataclass(eq=True)
class Webhook(SessionMixin):
    workspace_id: str
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
    Webhook class to control a specific UP42 webhook, e.g. create, modify, test or delete the specific webhook.
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
            url = host.endpoint(f"/workspaces/{self.workspace_id}/webhooks/{self.webhook_id}")
            response_json = self.session.put(url=url, json=payload).json()
            self.updated_at = response_json.get("updatedAt")
            logger.info("Updated webhook %s", self)
        else:
            url = host.endpoint(f"/workspaces/{self.workspace_id}/webhooks")
            response_json = self.session.post(url=url, json=payload).json()["data"]
            self.id = response_json["id"]
            self.created_at = response_json.get("createdAt")
            self.updated_at = response_json.get("updatedAt")
            logger.info("Created webhook %s", self)

    def delete(self) -> None:
        """
        Deletes a registered webhook.
        """
        url = host.endpoint(f"/workspaces/{self.workspace_id}/webhooks/{self.webhook_id}")
        self.session.delete(url)
        logger.info("Successfully deleted Webhook: %s", self.webhook_id)

    @staticmethod
    def _from_dict(metadata: dict, workspace_id: str) -> "Webhook":
        return Webhook(
            workspace_id=workspace_id,
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
    def get(cls, webhook_id: str, workspace_id: str) -> "Webhook":
        url = host.endpoint(f"/workspaces/{workspace_id}/webhooks/{webhook_id}")
        metadata = cls.session.get(url).json()["data"]
        return cls._from_dict(metadata, workspace_id)

    @classmethod
    def all(cls, workspace_id: str) -> List["Webhook"]:
        """
        Gets all registered webhooks for a workspace.

        Args:
            workspace_id: the id of the workspace

        Returns:
            A list of the registered webhooks for the workspace.
        """

        url = host.endpoint(f"/workspaces/{workspace_id}/webhooks")
        response_json = cls.session.get(url).json()
        logger.info("Queried %s webhooks.", len(response_json["data"]))

        return [cls._from_dict(metadata, workspace_id) for metadata in response_json["data"]]

    # TODO: model the response
    def trigger_test_events(self) -> dict:
        """
        Triggers webhook test event to test your receiving side. The UP42 server will send test
        messages for each subscribed event to the specified webhook URL.

        Returns:
            A dict with information about the test events.
        """
        url = host.endpoint(f"/workspaces/{self.workspace_id}/webhooks/{self.webhook_id}/tests")
        return self.session.post(url).json()["data"]

    # TODO: model the response
    @classmethod
    def all_webhook_events(cls) -> dict:
        """
        Gets all available webhook events.

        Returns:
            A dict of the available webhook events.
        """
        url = host.endpoint("/webhooks/events")
        return cls.session.get(url).json()["data"]

    # to deprecate
    @property
    def webhook_id(self):
        return self.id

    # to deprecate
    @property
    def info(self) -> dict:
        """
        Gets and updates the webhook metadata information.
        """
        return dataclasses.asdict(self)

    # to deprecate
    @classmethod
    def create(
        cls,
        name: str,
        url: str,
        events: List[str],
        workspace_id: str,
        active: bool,
        secret: Optional[str],
    ):
        webhook = Webhook(
            name=name,
            url=url,
            events=events,
            active=active,
            secret=secret,
            workspace_id=workspace_id,
        )
        webhook.save()
        return webhook

    # to deprecate
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
        if name:
            self.name = name
        if url:
            self.url = url
        if events:
            self.events = events
        if active:
            self.active = active
        # TODO: what was before?
        if secret:
            self.secret = secret
        self.save()
        return self
