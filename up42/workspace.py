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

def check_environment(func, *args):
    # pylint: disable=unused-argument
    def inner(self, environment_id:str, *args):
        print(f"check_environment {environment_id}")
        if environment_id not in [envon["id"] for envon in self.get_workspace_envs()]:
            raise ValueError(
                "Selected environment not in the current\
                             workspace."
            )
        return func(self, environment_id, *args)
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
        if "name" not in environment:
            logger.info("new env name not found in your input")
            return self
        if environment["name"] not in [
            envon["name"] for envon in self.get_workspace_envs()
        ]:
            url = f"{self.auth._endpoint()}/workspaces/{self.workspace_id}/environments"
            self.auth._request(
                request_type="POST",
                url=url,
                data=environment,
            )
            self.get_workspace_envs()
            return self
        else:
            raise ValueError(
                "environment name already exist in the selected\
                             workspace"
            )


    @check_environment
    @check_workspace
    def delete_env(self, environment_id: str) -> "Workspace":
        """
        Remove an environment from the selected workspace.
        The function checks if the env exists on the workspace
        else it raise a ValueError.
        Args:
            - env_id: An string with the Id of the environment to be remove.
        """
        url = f"{self.auth._endpoint()}/workspaces/{self.workspace_id}/environments/{environment_id}"
        data = {"workspace_id": self.workspace_id, "environment_id": environment_id}
        self.auth._request(
            request_type="DELETE",
            url=url,
            data=data,
        )
        self.get_workspace_envs()
        return self


    @check_environment
    @check_workspace
    def add_secret(self, environment_id: str, secret_data: Dict) -> "Workspace":
        """
        Add a secret to the selected environment.
        Args:
            environment_id: Id of the environment to add the key, value pair
            secret_data: Data to be added to the environment.
            (e.g
                {
                    "name": "env_name",
                    "secret": {
                        "var1_name": "var1_value",
                        "var2_name": "var2_value"
                    }
                }
            )
        """
        return self
