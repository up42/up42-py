from typing import Dict, Union

from up42.auth import AuthCredentials
from up42.utils import (
    get_logger,
)

logger = get_logger(__name__)

class Workspace:
    """
    The workspace class lets you query existing workspaces and configure
    environments related to the account workspace.
    """
    def __init__(self, auth: AuthCredentials ):
        self.auth = auth

    def get_workspaces(self) -> Dict[str, Union[str, Dict]]:
        """
        Get all workpaces in the user account with detailed information.
        """
        url = f"{self.auth._endpoint()}/accounts/me/workspaces"
        response_json = self.auth._request(request_type="GET", url=url)
        workspaces_json = response_json["data"]
        logger.info(
            f"Got {len(workspaces_json)} workspaces in your account"
        )
        return workspaces_json
