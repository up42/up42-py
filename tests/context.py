import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../up42")))

# Import the required classes and functions
# pylint: disable=unused-import,wrong-import-position
from up42.tools import read_vector_file, get_example_aoi
from up42.viztools import folium_base_map, VizTools
from up42.utils import (
    format_time_period,
    any_vector_to_fc,
    fc_to_query_geometry,
    download_from_gcs_unpack,
    filter_jobs_on_mode,
    autocomplete_order_parameters,
)
from up42.auth import Auth
from up42.project import Project
from up42.workflow import Workflow
from up42.job import Job
from up42.jobcollection import JobCollection
from up42.jobtask import JobTask
from up42.catalog import Catalog
from up42.tasking import Tasking
from up42.estimation import Estimation
from up42.storage import Storage
from up42.asset import Asset
from up42.order import Order
from up42.webhooks import Webhooks, Webhook
from up42 import main
from up42.main import (
    authenticate,
    get_webhooks,
    create_webhook,
    get_webhook_events,
    get_blocks,
    get_block_details,
    get_block_coverage,
    get_credits_balance,
    get_credits_history,
    validate_manifest,
)
from up42.initialization import (
    initialize_project,
    initialize_catalog,
    initialize_tasking,
    initialize_workflow,
    initialize_job,
    initialize_jobtask,
    initialize_jobcollection,
    initialize_storage,
    initialize_order,
    initialize_asset,
    initialize_webhook,
)
