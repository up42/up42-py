import requests_mock

from .context import Workflow
from .fixtures import auth_mock, project_mock, workflow_mock


def test_workflow_get_info(workflow_mock):
    with requests_mock.Mocker() as m:
        url_workflow_info = f"{workflow_mock.auth._endpoint()}/projects/{workflow_mock.project_id}/workflows/{workflow_mock.workflow_id}"
        m.get(url=url_workflow_info, text='{"data": {"xyz":789}, "error":{}}')

        info = workflow_mock._get_info()
    assert isinstance(workflow_mock, Workflow)
    assert info["xyz"] == 789
    assert workflow_mock.info["xyz"] == 789


def test_get_workflow_tasks(workflow_mock):
    with requests_mock.Mocker() as m:
        url_workflow_tasks = (
            f"{workflow_mock.auth._endpoint()}/projects/{workflow_mock.auth.project_id}/workflows/"
            f"{workflow_mock.workflow_id}/tasks"
        )
        text_workflow_tasks = '{"data": [{"id": "c0d04ec3-98d7-4183-902f-5bcb2a176d89","block": {"name": "sobloo-s2-l1c-aoiclipped"}},{"id": "af626c54-156e-4f13-a743-55efd27de533","block": {"name": "sharpening"}}],"error": {}}'
        m.get(url=url_workflow_tasks, text=text_workflow_tasks)

        tasks = workflow_mock.get_workflow_tasks(basic=False)
    assert len(tasks) == 2
    assert tasks[0] == {
        "id": "c0d04ec3-98d7-4183-902f-5bcb2a176d89",
        "block": {"name": "sobloo-s2-l1c-aoiclipped"},
    }


def test_construct_full_workflow_tasks_dict(workflow_mock):
    # TODO: Mock get_blocks!
    pass
