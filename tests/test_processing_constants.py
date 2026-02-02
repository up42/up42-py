import dataclasses
import datetime
import uuid

import pystac

from tests import constants
from up42 import processing

# IDs and Primitives
PROCESS_ID = "process-id"
EULA_ID = str(uuid.uuid4())
TITLE = "title"
COLLECTION_ID = str(uuid.uuid4())
JOB_ID = str(uuid.uuid4())
ACCOUNT_ID = str(uuid.uuid4())
CREDITS = 1
MICROSECONDS = "123456Z"

# URLs
ITEM_URL = "https://item-url"
COLLECTION_URL = f"https://collections/{COLLECTION_ID}"
PROCESS_URL = f"{constants.API_HOST}/v2/processing/processes/{PROCESS_ID}"
EULA_URL = f"{constants.API_HOST}/v2/eulas/{EULA_ID}"
VALIDATION_URL = f"{constants.API_HOST}/v2/processing/processes/{PROCESS_ID}/validation"
COST_URL = f"{constants.API_HOST}/v2/processing/processes/{PROCESS_ID}/cost"
EXECUTION_URL = (
    f"{constants.API_HOST}/v2/processing/processes/{PROCESS_ID}/execution?workspaceId={constants.WORKSPACE_ID}"
)
JOBS_URL = f"{constants.API_HOST}/v2/processing/jobs"
JOB_URL = f"{JOBS_URL}/{JOB_ID}"

# Dates
NOW_AS_STR = datetime.datetime.now().isoformat(timespec="milliseconds")
NOW = datetime.datetime.fromisoformat(NOW_AS_STR)

# Complex Objects
PROCESS_SUMMARY = {
    "id": PROCESS_ID,
    "additionalParameters": {
        "parameters": [
            {"name": "eula-id", "value": [EULA_ID]},
            {"name": "price", "value": [{"credits": 1, "unit": "SQ_KM"}]},
        ]
    },
}

ITEM = pystac.Item.from_dict(
    {
        "type": "Feature",
        "stac_version": "1.0.0",
        "id": "id",
        "properties": {"datetime": "2024-01-01T00:00:00.000000Z"},
        "geometry": {"type": "Point", "coordinates": (0, 0)},
        "links": [{"rel": "self", "href": ITEM_URL}],
        "assets": {},
        "bbox": [0, 0, 0, 0],
        "stac_extensions": [],
    }
)

DEFINITION = {
    "inputs": {
        "item": ITEM_URL,
        "title": TITLE,
    }
}

INVALID_TITLE_ERROR = processing.ValidationError(name="InvalidTitle", message="title is too long")

JOB_METADATA: processing.JobMetadata = {
    "processID": PROCESS_ID,
    "jobID": JOB_ID,
    "accountID": ACCOUNT_ID,
    "workspaceID": constants.WORKSPACE_ID,
    "definition": DEFINITION,
    "results": {
        "collection": f"{COLLECTION_URL}",
        "errors": [dataclasses.asdict(INVALID_TITLE_ERROR)],
    },
    "creditConsumption": {"credits": CREDITS},
    "status": "created",
    "created": f"{NOW_AS_STR}{MICROSECONDS}",
    "updated": f"{NOW_AS_STR}{MICROSECONDS}",
    "started": None,
    "finished": None,
}

JOB = processing.Job(
    process_id=PROCESS_ID,
    id=JOB_ID,
    account_id=ACCOUNT_ID,
    workspace_id=constants.WORKSPACE_ID,
    definition=DEFINITION,
    collection_url=COLLECTION_URL,
    errors=[INVALID_TITLE_ERROR],
    credits=CREDITS,
    status=processing.JobStatus.CREATED,
    created=NOW,
    updated=NOW,
)
