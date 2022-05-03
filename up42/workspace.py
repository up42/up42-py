from typing import Dict, List, Optional, Union

from up42.auth import AuthCredentials
from up42.utils import (
    get_logger,
)

logger = get_logger(__name__)


def check_workspace(func, *args):
    # pylint: disable=unused-argument
    def inner(self, *args):
        if not self.workspace_id:
            raise ValueError("Please set your workspace_id first.")
        return func(self, *args)

    return inner


class Workspace:
    """
    The workspace class lets you query existing workspaces and configure
    environments related to the selected workspaces within your account.
    """

    workspace_id: Optional[str] = None
    environments: List[Dict] = []

    def __init__(self, auth: AuthCredentials, workspace_id: Optional[str] = None):
        self.auth = auth
        if workspace_id is not None:
            self.set_workspace_id(workspace_id)

    def set_workspace_id(self, workspace_id: str) -> "Workspace":
        workspace_id_list = [
            ws["id"] for ws in self.get_workspaces()["content"]  # type: ignore
        ]
        if workspace_id in workspace_id_list:
            self.workspace_id = workspace_id
        else:
            raise ValueError(
                "make sure your workspace_id belongs to your\
                              account."
            )
        return self

    def get_workspaces(self) -> Dict[str, Union[str, Dict]]:
        """
        Returns all workpaces within the user account with detailed information.
        """
        url = f"{self.auth._endpoint()}/accounts/me/workspaces"
        response_json = self.auth._request(request_type="GET", url=url)
        workspaces_json = response_json["data"]
        logger.info(f"Got {len(workspaces_json)} workspaces in your account")
        return workspaces_json

    @check_workspace
    def get_workspace_envs(self) -> List:
        """
        Get the list of the environments within a selected workspace.
        """
        url = f"{self.auth._endpoint()}/workspaces/{self.workspace_id}/environments"
        response_json = self.auth._request(request_type="GET", url=url)
        environments_json = response_json["data"]
        logger.info(
            f"Got {len(environments_json)} environments in your\
            selected workspace {self.workspace_id}."
        )
        self.environments = environments_json
        return self.environments

    @check_workspace
    def create_env(self, environment: Dict[str, Union[str, Dict]]) -> "Workspace":
        """
        Create an environment in the selected workspace.
        Args:
            - environment is a dictionary with the info to be stored
            ( e.g.
                {
                    "name":"env_name",
                    "secrets": {
                        "var1_name": "var1_value",
                        ...,
                        "varn_name":"varn_value"
                        }
                }
            )
        """
        url = f"{self.auth._endpoint()}/workspaces/{self.workspace_id}/environments"
        self.auth._request(
            request_type="POST",
            url=url,
            data=environment,
        )
        self.get_workspace_envs()
        return self
