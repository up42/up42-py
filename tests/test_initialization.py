from __future__ import absolute_import

import pytest

# pylint: disable=unused-import
from .context import (
    authenticate,
    initialize_project,
    initialize_catalog,
    initialize_workflow,
    initialize_job,
    initialize_jobtask,
)
from .fixtures import (
    PROJECT_ID,
    PROJECT_APIKEY,
    WORKFLOW_ID,
    JOB_ID,
    JOBTASK_ID,
)
import up42  # pylint: disable=wrong-import-order


def test_initialize_object_wo_auth_raises():
    with pytest.raises(RuntimeError):
        up42.initialize_project()
    with pytest.raises(RuntimeError):
        up42.initialize_catalog()
    with pytest.raises(RuntimeError):
        up42.initialize_workflow(workflow_id=WORKFLOW_ID)
    with pytest.raises(RuntimeError):
        up42.initialize_job(job_id=JOB_ID)
    with pytest.raises(RuntimeError):
        up42.initialize_jobtask(job_id=JOB_ID, jobtask_id=JOBTASK_ID)


# TODO: Adjust and unskip after simplification of test authentication
@pytest.mark.skip
def test_global_auth_initialize_objects():
    up42.authenticate(
        project_id=PROJECT_ID,
        project_api_key=PROJECT_APIKEY,
        authenticate=False,
        get_info=False,
        retry=False,
    )
    project = up42.initialize_project()
    assert isinstance(project, up42.Project)
    catalog = up42.initialize_catalog()
    assert isinstance(catalog, up42.Catalog)
    workflow = up42.initialize_workflow(workflow_id=WORKFLOW_ID)
    assert isinstance(workflow, up42.Workflow)
    job = up42.initialize_job(job_id=JOB_ID)
    assert isinstance(job, up42.Job)
    jobtask = up42.initialize_jobtask(job_id=JOB_ID, jobtask_id=JOBTASK_ID)
    assert isinstance(jobtask, up42.JobTask)
