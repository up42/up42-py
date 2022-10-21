import pytest

from ..context import (
    JobCollection,
)


@pytest.fixture()
def jobcollection_single_mock(auth_mock, job_mock):
    return JobCollection(
        auth=auth_mock, project_id=auth_mock.project_id, jobs=[job_mock]
    )


@pytest.fixture()
def jobcollection_multiple_mock(auth_mock, jobs_mock):
    return JobCollection(
        auth=auth_mock, project_id=auth_mock.project_id, jobs=jobs_mock
    )


@pytest.fixture()
def jobcollection_empty_mock(auth_mock):
    return JobCollection(auth=auth_mock, project_id=auth_mock.project_id, jobs=[])


@pytest.fixture()
def jobcollection_live(auth_live, jobs_live):
    return JobCollection(
        auth=auth_live, project_id=auth_live.project_id, jobs=jobs_live
    )
