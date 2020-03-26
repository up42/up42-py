import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)
from typing import List

# pylint: disable=wrong-import-position
from .tools import Tools
from .auth import Auth
from .project import Project
from .workflow import Workflow
from .job import Job
from .jobtask import JobTask
from .catalog import Catalog


_auth = None


def authenticate(cfg_file=None, project_id=None, project_api_key=None, **kwargs):
    global _auth
    _auth = Auth(
        cfg_file=cfg_file,
        project_id=project_id,
        project_api_key=project_api_key,
        **kwargs
    )


def initialize_project() -> "Project":
    """Directly returns the correct Project object (has to exist on UP42)."""
    if _auth is None:
        raise RuntimeError("Not authenticated, call up42.authenticate() first")
    return Project(auth=_auth, project_id=_auth.project_id)


def initialize_catalog(backend: str = "ONE_ATLAS") -> "Catalog":
    """Directly returns a Catalog object."""
    if _auth is None:
        raise RuntimeError("Not authenticated, call up42.authenticate() first")
    return Catalog(auth=_auth, backend=backend)


def initialize_workflow(workflow_id) -> "Workflow":
    """Directly returns a Workflow object (has to exist on UP42)."""
    if _auth is None:
        raise RuntimeError("Not authenticated, call up42.authenticate() first")
    return Workflow(auth=_auth, workflow_id=workflow_id, project_id=_auth.project_id)


def initialize_job(job_id, order_ids: List[str] = [""]) -> "Job":
    """Directly returns a Job object (has to exist on UP42)."""
    if _auth is None:
        raise RuntimeError("Not authenticated, call up42.authenticate() first")
    return Job(
        auth=_auth, job_id=job_id, project_id=_auth.project_id, order_ids=order_ids
    )


def initialize_jobtask(job_task_id, job_id) -> "JobTask":
    """Directly returns a JobTask object (has to exist on UP42)."""
    if _auth is None:
        raise RuntimeError("Not authenticated, call up42.authenticate() first")
    return JobTask(
        auth=_auth, job_task_id=job_task_id, job_id=job_id, project_id=_auth.project_id
    )
