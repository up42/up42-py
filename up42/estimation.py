import pathlib
from typing import Any, Dict, List, Union

from up42 import auth as up42_auth
from up42 import host, utils

logger = utils.get_logger(__name__)


class Estimation:
    def __init__(
        self,
        auth: up42_auth.Auth,
        project_id: str,
        input_parameters: Union[dict, str, pathlib.Path],
        input_tasks: List[Dict[str, Any]],
    ):
        """
        The Estimation class provides facilities for getting estimation of a workflow.

        input_parameters: Job input parameters as from workflow.construct_parameters().
        input_tasks: List of dict of input_tasks, containing name, parentName, blockId
            and blockVersionTag. Example:
                [{
                    "name": "sobloo-s2-l1c-aoiclipped:1",
                    "parentName": None,
                    "blockId": "3a381e6b-acb7-4cec-ae65-50798ce80e64",
                    "blockVersionTag": "2.3.0",
                },]
        """
        self.auth = auth
        self.project_id = project_id
        self.input_parameters = input_parameters
        self.input_tasks = input_tasks
        self.payload: dict = {}

    def estimate(self) -> dict:
        """
        Estimation of price and duration of the workflow for the provided input parameters.

        Returns:
            A dictionary with credit cost & duration estimate for each workflow task.
        """
        url = host.endpoint(f"/projects/{self.project_id}/estimate/job")
        self.payload = {
            "tasks": self.input_tasks,
            "inputs": self.input_parameters,
        }

        response_json = self.auth.request(request_type="POST", url=url, data=self.payload)
        return response_json["data"]
