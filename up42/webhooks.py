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
def get_webhook(self, webhook_id: str) -> dict:
    """
    Gets a specific webhook by its id.

    Returns:
        A dict of the specified webhook in this workspace.
    """
    url = f"{self.auth._endpoint()}/workspaces/{self.auth.workspace_id}/webhooks/{webhook_id}"
    response_json = self.auth._request(request_type="GET", url=url)

    return response_json["data"]


@check_auth
def create_webhook(
    self,
    name: str,
    url: str,
    events: List[str],
    secret: Optional[str] = None,
    active: bool = False,
) -> dict:
    """
    Registers a new webhook in the system.

    Returns:
        A dict with details of the registered webhook.
    """
    input_parameters = {
        "name": name,
        url: url,
        events: events,
        secret: secret,
        active: False,
    }
    url_post = f"{self.auth._endpoint()}/workspaces/{self.auth.workspace_id}/webhooks"
    response_json = self.auth._request(
        request_type="POST", url=url_post, data=input_parameters
    )
    return response_json["data"]


@check_auth
def update_webhook(
    self,
    webhook_id: str,
    name: str,
    url: str,
    events: List[str],
    secret: Optional[str] = None,
    active: bool = False,
) -> dict:
    """
    Updates a registered webhook.

    Returns:
        A dict with details of the updated webhook.
    """
    input_parameters = {
        "name": name,
        url: url,
        events: events,
        secret: secret,
        active: False,
    }
    url_post = f"{self.auth._endpoint()}/workspaces/{self.auth.workspace_id}/webhooks/{webhook_id}"
    response_json = self.auth._request(
        request_type="POST", url=url_post, data=input_parameters
    )
    return response_json["data"]


@check_auth
def delete_webhook(self, webhook_id: str) -> None:
    """
    Deletes a registered webhook.
    """
    url = f"{self.auth._endpoint()}/workspaces/{self.auth.workspace_id}/webhooks/{webhook_id}"
    self.auth._request(request_type="DELETE", url=url)


@check_auth
def trigger_webhook_test_event(self, webhook_id: str) -> dict:
    """
    Triggers webhook test event to test your receiving side. The UP42 server will Our server will send test
    messages for each subscribed event to the specified webhook URL.

    Returns:
        A dict with details of the updated webhook.
    """
    # TODO: Event names specification
    url = f"{self.auth._endpoint()}/workspaces/{self.auth.workspace_id}/webhooks/{webhook_id}/tests"
    response_json = self.auth._request(
        request_type="POST", url=url, data=input_parameters
    )
    return response_json["data"]
