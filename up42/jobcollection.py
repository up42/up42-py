from typing import List

from .auth import Auth
from .job import Job
from .tools import Tools

from .utils import get_logger

logger = get_logger(__name__)

# pylint: disable=duplicate-code
class JobCollection(Tools):
    def __init__(self, auth: Auth, project_id: str, jobs: List[Job]):
        """
        The JobCollection class provides facilities for creating job parameters,
        running multiple jobs in parallel and merging job results.
        """
        self.auth = auth
        self.project_id = project_id
        self.jobs = jobs

    def __repr__(self):
        return (
            f"JobCollection(jobs={self.jobs}, project_id={self.project_id}, "
            f"auth={self.auth})"
        )
