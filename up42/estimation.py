from typing import Dict

from up42.auth import Auth
from up42.tools import Tools

from up42.utils import get_logger

logger = get_logger(__name__)


class Estimation(Tools):
    def __init__(
        self,
        auth: Auth,
        project_id: str,
        workflow_id: str,
        workflow_estimation: Dict,
        input_parameters,
    ):
        """
        The Estimation class provides facilities for getting estimation of a workflow.
        """
        self.auth = auth
        self.project_id = project_id
        self.workflow_id = workflow_id
        self.workflow_estimation = workflow_estimation
        self.input_parameters = input_parameters

    @property
    def info(self):
        """
        Gets the estimation information.
        """
        logger.info(f"Returned estimation: {self.workflow_estimation}")
        return self.workflow_estimation
