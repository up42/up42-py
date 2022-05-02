from typing import Dict, List, Optional, Union

from up42.auth import AuthCredentials
from up42.utils import (
    get_logger,
)

logger = get_logger(__name__)


class Workspace:
    """
    The workspace class lets you query existing workspaces and configure
    environments related to one selected workspace within your account.
    """

    workspace_id = None
    environments: List[Dict] = []

    def __init__(self, auth: AuthCredentials, workspace_id: Optional[str] = None):
        self.auth = auth
        self.workspace_id = workspace_id

    def set_workspace_id(self, workspace_id: str):
        self.workspace_id = workspace_id

    def get_workspaces(self) -> Dict[str, Union[str, Dict]]:
        """
        Returns all workpaces within the user account with detailed information.
        """
        url = f"{self.auth._endpoint()}/accounts/me/workspaces"
        response_json = self.auth._request(request_type="GET", url=url)
        workspaces_json = response_json["data"]
        logger.info(f"Got {len(workspaces_json)} workspaces in your account")
        return workspaces_json

    def get_workspace_envs(self):
        """
        Returns all the environments within the selected workflow.
        """
        url = f"{self.auth._endpoint()}/workspaces/{self.workspace_id}/environments"
        response_json = self.auth._request(request_type="GET", url=url)
        environments_json = response_json["data"]
        logger.info(
            f"Got {len(environments_json)} environments in your\
                    selected workspace {self.workspace_id}."
        )
        self.environments = environments_json
