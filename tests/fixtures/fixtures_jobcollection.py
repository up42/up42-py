import pytest

from up42.jobcollection import JobCollection

from .fixtures_globals import PROJECT_ID


@pytest.fixture()
def jobcollection_single_mock(auth_mock, job_mock):
    return JobCollection(auth=auth_mock, project_id=PROJECT_ID, jobs=[job_mock])


@pytest.fixture()
def jobcollection_multiple_mock(auth_mock, jobs_mock):
    return JobCollection(auth=auth_mock, project_id=PROJECT_ID, jobs=jobs_mock)


@pytest.fixture()
def jobcollection_empty_mock(auth_mock):
    return JobCollection(auth=auth_mock, project_id=PROJECT_ID, jobs=[])
