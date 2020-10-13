import warnings
from pathlib import Path
from typing import List, Union, Dict, Tuple
import logging

from geojson import FeatureCollection
from geopandas import GeoDataFrame

# pylint: disable=wrong-import-position
from up42.tools import Tools
from up42.auth import Auth
from up42.project import Project
from up42.workflow import Workflow
from up42.job import Job
from up42.jobtask import JobTask
from up42.catalog import Catalog
from up42.utils import get_logger

logger = get_logger(__name__, level=logging.INFO)

warnings.simplefilter(action="ignore", category=FutureWarning)

_auth = None


def authenticate(
    cfg_file: Union[str, Path] = None,
    project_id: str = None,
    project_api_key: str = None,
    **kwargs,
):
    global _auth  # pylint: disable=global-statement
    _auth = Auth(
        cfg_file=cfg_file,
        project_id=project_id,
        project_api_key=project_api_key,
        **kwargs,
    )


def initialize_project() -> "Project":
    """
    Returns the correct Project object (has to exist on UP42).
    """
    if _auth is None:
        raise RuntimeError("Not authenticated, call up42.authenticate() first")
    project = Project(auth=_auth, project_id=str(_auth.project_id))
    logger.info(f"Initialized {project}")
    return project


def initialize_catalog() -> "Catalog":
    """
    Returns a Catalog object for using the catalog search.
    """
    if _auth is None:
        raise RuntimeError("Not authenticated, call up42.authenticate() first")
    return Catalog(auth=_auth)


def initialize_workflow(workflow_id: str) -> "Workflow":
    """
    Returns a Workflow object (has to exist on UP42).

    Args:
        workflow_id: The UP42 workflow_id
    """
    if _auth is None:
        raise RuntimeError("Not authenticated, call up42.authenticate() first")
    workflow = Workflow(
        auth=_auth, workflow_id=workflow_id, project_id=str(_auth.project_id)
    )
    logger.info(f"Initialized {workflow}")
    return workflow


def initialize_job(job_id: str) -> "Job":
    """
    Returns a Job object (has to exist on UP42).

    Args:
        job_id: The UP42 job_id
    """
    if _auth is None:
        raise RuntimeError("Not authenticated, call up42.authenticate() first")
    job = Job(auth=_auth, job_id=job_id, project_id=str(_auth.project_id))
    logger.info(f"Initialized {job}")
    return job


def initialize_jobtask(jobtask_id, job_id) -> "JobTask":
    """
    Returns a JobTask object (has to exist on UP42).

    Args:
        jobtask_id: The UP42 jobtask_id
        job_id: The UP42 job_id
    """
    if _auth is None:
        raise RuntimeError("Not authenticated, call up42.authenticate() first")
    jobtask = JobTask(
        auth=_auth,
        jobtask_id=jobtask_id,
        job_id=job_id,
        project_id=str(_auth.project_id),
    )
    logger.info(f"Initialized {jobtask}")
    return jobtask


def get_blocks(
    block_type=None,
    basic: bool = True,
    as_dataframe=False,
):
    tools = Tools(auth=_auth)
    return tools.get_blocks(block_type, basic, as_dataframe)


def get_block_details(block_id: str, as_dataframe=False) -> Dict:
    tools = Tools(auth=_auth)
    return tools.get_block_details(block_id, as_dataframe)


def validate_manifest(path_or_json: Union[str, Path, Dict]) -> Dict:
    tools = Tools(auth=_auth)
    return tools.validate_manifest(path_or_json)


def read_vector_file(
    filename: str = "aoi.geojson", as_dataframe: bool = False
) -> FeatureCollection:
    tools = Tools(auth=_auth)
    return tools.read_vector_file(filename, as_dataframe)


def get_example_aoi(
    location: str = "Berlin", as_dataframe: bool = False
) -> FeatureCollection:
    tools = Tools(auth=_auth)
    return tools.get_example_aoi(location, as_dataframe)


def draw_aoi() -> None:
    tools = Tools(auth=_auth)
    tools.draw_aoi()


# pylint: disable=duplicate-code
def plot_coverage(
    scenes: GeoDataFrame,
    aoi: GeoDataFrame = None,
    legend_column: str = "scene_id",
    figsize=(12, 16),
) -> None:
    tools = Tools(auth=_auth)
    tools.plot_coverage(scenes, aoi, legend_column, figsize)


def plot_quicklooks(figsize: Tuple[int, int] = (8, 8), filepaths: List = None) -> None:
    tools = Tools(auth=_auth)
    tools.plot_quicklooks(figsize, filepaths)


def plot_results(
    figsize: Tuple[int, int] = (8, 8),
    filepaths: List[Union[str, Path]] = None,
    titles: List[str] = None,
) -> None:
    tools = Tools(auth=_auth)
    tools.plot_results(figsize, filepaths, titles)


def settings(log=True):
    """
    Configures settings about logging etc. when using the up42-py package.

    Args:
        log: Activates/deactivates logging, default True is activated logging.
    """
    if log:
        logger.info(
            "Logging enabled (default) - use up42.settings(log=False) to disable."
        )
    else:
        logger.info("Logging disabled - use up42.settings(log=True) to reactivate.")

    # pylint: disable=expression-not-assigned
    [
        setattr(logging.getLogger(name), "disabled", not log)
        for name in logging.root.manager.loggerDict
    ]
