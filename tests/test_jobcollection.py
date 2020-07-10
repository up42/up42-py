# pylint: disable=unused-import,wrong-import-order
from .fixtures import auth_mock, job_mock, jobcollection_mock


def test_jobcollection(jobcollection_mock):
    assert len(jobcollection_mock.jobs) == 1
