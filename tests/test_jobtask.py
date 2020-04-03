import requests_mock

# pylint: disable=unused-import
from .fixtures import auth_mock, auth_live, jobtask_mock, jobtask_live
import up42  # pylint: disable=wrong-import-order


def test_jobtask_get_info(jobtask_mock):
    del jobtask_mock.info

    with requests_mock.Mocker() as m:
        url_jobtask_info = (
            f"{jobtask_mock.auth._endpoint()}/"
            f"projects/{jobtask_mock.project_id}/jobs/"
            f"{jobtask_mock.job_id}/tasks/"
        )
        m.get(url=url_jobtask_info, text='{"data": {"xyz":789}, "error":{}}')

        info = jobtask_mock._get_info()
    assert isinstance(jobtask_mock, up42.JobTask)
    assert info["xyz"] == 789
    assert jobtask_mock.info["xyz"] == 789
