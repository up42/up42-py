from typing import Dict, Union, List
from pathlib import Path

from up42.auth import Auth
from up42.tools import Tools

from up42.utils import get_logger

logger = get_logger(__name__)


class Estimation(Tools):
    def __init__(
        self,
        auth: Auth,
        project_id: str,
        input_parameters: Union[Dict, str, Path],
        input_tasks: List[Dict],
    ):
        """
        The Estimation class provides facilities for getting estimation of a workflow.
        """
        self.auth = auth
        self.project_id = project_id
        self.input_parameters = input_parameters
        self.input_tasks = input_tasks
        self.payload: Dict = {}

    def estimate_price(self) -> Dict:
        """
        This function return estimation for a workflow.
        :return:
        """
        url = f"{self.auth._endpoint()}/estimate/job"
        self.payload = {
            "tasks": self.input_tasks,
            "inputs": self.input_parameters,
        }

        response_json = self.auth._request(
            request_type="POST", url=url, data=self.payload
        )

        return response_json["data"]
