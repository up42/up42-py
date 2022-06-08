from typing import List, Optional

from up42.tools import check_auth


@check_auth
def get_webhook_events(self) -> dict:
    """
    Gets all available webhook events.

    Returns:
        A dict of the available webhook events.
    """
    url = f"{self.auth._endpoint()}/webhook/events"
    response_json = self.auth._request(request_type="GET", url=url)
    return response_json["data"]


@check_auth
def get_webhooks(self) -> dict:
    """
    Gets all registered webhooks for this workspace.

    Returns:
        A dict of the registered webhooks for this workspace.
    """
    url = f"{self.auth._endpoint()}/workspaces/{self.auth.workspace_id}/webhooks"
    response_json = self.auth._request(request_type="GET", url=url)
    return response_json["data"]

@check_auth
def get_webhook(self, webhook_id) -> dict:
    """
    Gets all registered webhooks for this workspace.

    Returns:
        A dict of the registered webhooks for this workspace.
    """
    url = f"{self.auth._endpoint()}/workspaces/{self.auth.workspace_id}/webhooks"
    response_json = self.auth._request(request_type="GET", url=url)
    return response_json["data"]


@check_auth
def create_webhook(self, name: str, url: str, events: List[str], secret: Optional[str]=None, active: bool=False) -> dict:
    """
    Registers a new webhook in the system.

    Returns:
        A dict with details of the registered webhook.
    """
    url = f"{self.auth._endpoint()}/workspaces/{self.auth.workspace_id}/webhooks"
    input_parameters = {"name": name, url: url, events: events, secret: secret, active: False}
    response_json = self.auth._request(request_type="POST", url=url, data=input_parameters)
    return response_json["data"]