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
import up42  # pylint: disable=wrong-import-order


def test_initialize_object_wo_auth_raises():
    with pytest.raises(RuntimeError):
        up42.initialize_project()
    with pytest.raises(RuntimeError):
        up42.initialize_catalog()
    with pytest.raises(RuntimeError):
        up42.initialize_workflow(workflow_id="1234")
    with pytest.raises(RuntimeError):
        up42.initialize_job(job_id="1234")
    with pytest.raises(RuntimeError):
        up42.initialize_jobtask(job_id="1234", jobtask_id="1234")


def test_global_auth_initialize_objects():
    up42.authenticate(
        project_id="1234",
        project_api_key="1234",
        authenticate=False,
        get_info=False,
        retry=False,
    )
    project = up42.initialize_project()
    assert isinstance(project, up42.Project)
    catalog = up42.initialize_catalog()
    assert isinstance(catalog, up42.Catalog)
    workflow = up42.initialize_workflow(workflow_id="1234")
    assert isinstance(workflow, up42.Workflow)
    job = up42.initialize_job(job_id="1234")
    assert isinstance(job, up42.Job)
    jobtask = up42.initialize_jobtask(job_id="1234", jobtask_id="1234")
    assert isinstance(jobtask, up42.JobTask)
