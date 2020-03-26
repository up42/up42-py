import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)
from pathlib import Path
from typing import List, Union, Dict, Tuple

from geojson import FeatureCollection
import geopandas as gpd

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


def get_blocks(
    block_type=None, basic: bool = True, as_dataframe=False,
):
    tools = Tools(auth=_auth)
    return tools.get_blocks(block_type, basic, as_dataframe)


def get_block_details(block_id: str, as_dataframe=False) -> Dict:
    tools = Tools(auth=_auth)
    return tools.get_block_details(block_id, as_dataframe)


def validate_manifest(path_or_json: Union[str, Path, Dict]) -> Dict:
    tools = Tools(auth=_auth)
    return tools.validate_manifest(path_or_json)


def get_environments(as_dataframe=False) -> Dict:
    tools = Tools(auth=_auth)
    return tools.get_environments(as_dataframe)


def create_environment(name: str, environment_variables: Dict = None) -> Dict:
    tools = Tools(auth=_auth)
    return tools.create_environment(name, environment_variables)


def delete_environment(environment_id: str) -> None:
    tools = Tools(auth=_auth)
    tools.delete_environment(environment_id)

def read_vector_file(
    filename: str = "aoi.geojson", as_dataframe: bool = False
) -> FeatureCollection:
    tools = Tools(auth=_auth)
    tools.read_vector_file(filename, as_dataframe)

def get_example_aoi(
        location: str = "Berlin", as_dataframe: bool = False
) -> FeatureCollection:
    tools = Tools(auth=_auth)
    tools.get_example_aoi(location, as_dataframe)

def draw_aoi() -> None:
    tools = Tools(auth=_auth)
    tools.draw_aoi()

def plot_coverage(scenes: gpd.GeoDataFrame,
        aoi: gpd.GeoDataFrame = None,
        legend_column: str = None,
        figsize=(12, 16),
    ) -> None:
    tools = Tools(auth=_auth)
    tools.plot_coverage(scenes, aoi, legend_column, figsize)

def plot_quicklook(
    figsize: Tuple[int, int] = (8, 8), filepaths: List = None
) -> None:
    tools = Tools(auth=_auth)
    tools.plot_quicklook(figsize, filepaths)

def plot_results(
        figsize: Tuple[int, int] = (8, 8),
        filepaths: List[str] = None,
        titles: List[str] = None,
    ) -> None:
    tools = Tools(auth=_auth)
    tools.plot_results(figsize, filepaths, titles)
