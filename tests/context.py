import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../up42")))

# Import the required classes and functions
# pylint: disable=unused-import,wrong-import-position
from up42.tools import Tools
from up42.utils import (
    is_notebook,
    folium_base_map,
    any_vector_to_fc,
    fc_to_query_geometry,
    download_results_from_gcs,
)
from up42.auth import Auth
from up42.project import Project
from up42.workflow import Workflow
from up42.job import Job
from up42.jobtask import JobTask
from up42.catalog import Catalog
from up42.__init__ import (
    authenticate,
    initialize_project,
    initialize_catalog,
    initialize_workflow,
    initialize_job,
    initialize_jobtask,
)
