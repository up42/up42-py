import os
from unittest import mock
import pytest
from click.testing import CliRunner
from up42 import cli


@pytest.fixture()
@mock.patch.dict(
    "os.environ",
    {
        "UP42_PROJECT_ID": os.environ.get("TEST_UP42_PROJECT_ID"),
        "UP42_PROJECT_API_KEY": os.environ.get("TEST_UP42_PROJECT_API_KEY"),
    },
)
def cli_runner():
    return CliRunner()


WORKFLOW_ENVS = mock.patch.dict(
    "os.environ", {"UP42_WORKFLOW_ID": os.environ.get("TEST_UP42_WORKFLOW_ID"),},
)


@pytest.mark.live()
def test_main(cli_runner):
    result = cli_runner.invoke(cli.main)
    assert result.exit_code == 0


@pytest.mark.live()
def test_auth(cli_runner):
    result = cli_runner.invoke(cli.main, ["auth"])
    assert result.exit_code == 0


@pytest.mark.live()
def test_config(cli_runner):
    with cli_runner.isolated_filesystem():
        result = cli_runner.invoke(cli.main, ["config"])
        assert result.exit_code == 0


@pytest.mark.live()
def test_get_blocks(cli_runner):
    result = cli_runner.invoke(cli.main, ["get-blocks"])
    assert result.exit_code == 0


@pytest.mark.live()
def test_get_block_details(cli_runner):
    result = cli_runner.invoke(cli.main, ["get-block-details", "-h"])
    assert result.exit_code == 0


@pytest.mark.live()
def test_get_environments(cli_runner):
    result = cli_runner.invoke(cli.main, ["get-environments"])
    assert result.exit_code == 0


@pytest.mark.live()
def test_create_environment(cli_runner):
    result = cli_runner.invoke(cli.main, ["create-environment", "-h"])
    assert result.exit_code == 0


@pytest.mark.live()
def test_delete_environment(cli_runner):
    result = cli_runner.invoke(cli.main, ["delete-environment", "-h"])
    assert result.exit_code == 0
    # Test prompt
    # result = cli_runner.invoke(cli.main, ["delete-environment", "SOME_NAME"], input="y")
    # assert result.exit_code == 0


@pytest.mark.live()
def test_validate_manifest(cli_runner):
    result = cli_runner.invoke(cli.main, ["validate-manifest", "-h"])
    assert result.exit_code == 0


@pytest.mark.live()
def test_project(cli_runner):
    result = cli_runner.invoke(cli.main, ["project"])
    assert result.exit_code == 0


@pytest.mark.live()
def test_create_workflow(cli_runner):
    result = cli_runner.invoke(cli.main, ["project", "create-workflow", "-h"])
    assert result.exit_code == 0


@pytest.mark.live()
def test_get_project_settings(cli_runner):
    result = cli_runner.invoke(cli.main, ["project", "get-project-settings"])
    assert result.exit_code == 0


@pytest.mark.live()
def test_get_workflows(cli_runner):
    result = cli_runner.invoke(cli.main, ["project", "get-workflows"])
    assert result.exit_code == 0


@pytest.mark.live()
def test_update_project_settings(cli_runner):
    result = cli_runner.invoke(cli.main, ["project", "update-project-settings", "-h"])
    assert result.exit_code == 0


@pytest.mark.live()
def test_workflow_from_name(cli_runner):
    result = cli_runner.invoke(cli.main, ["project", "workflow-from-name", "-h"])
    assert result.exit_code == 0


@pytest.mark.live()
def test_workflow(cli_runner):
    result = cli_runner.invoke(cli.main, ["project", "workflow", "-h"])
    assert result.exit_code == 0


@WORKFLOW_ENVS
@pytest.mark.live()
def test_workflow_get_info(cli_runner):
    result = cli_runner.invoke(cli.main, ["project", "workflow", "get-info"])
    assert result.exit_code == 0


@WORKFLOW_ENVS
@pytest.mark.live()
def test_workflow_update_name(cli_runner):
    result = cli_runner.invoke(cli.main, ["project", "workflow", "update-name", "-h"])
    assert result.exit_code == 0


@WORKFLOW_ENVS
@pytest.mark.live()
def test_workflow_delete(cli_runner):
    result = cli_runner.invoke(cli.main, ["project", "workflow", "delete", "-h"])
    assert result.exit_code == 0


@WORKFLOW_ENVS
@pytest.mark.live()
def test_get_jobs(cli_runner):
    result = cli_runner.invoke(cli.main, ["project", "workflow", "get-jobs"])
    assert result.exit_code == 0


@WORKFLOW_ENVS
@pytest.mark.live()
def test_get_workflow_tasks(cli_runner):
    result = cli_runner.invoke(cli.main, ["project", "workflow", "get-workflow-tasks"])
    assert result.exit_code == 0


@WORKFLOW_ENVS
@pytest.mark.live()
def test_get_parameter_info(cli_runner):
    result = cli_runner.invoke(cli.main, ["project", "workflow", "get-parameter-info"])
    assert result.exit_code == 0


@WORKFLOW_ENVS
@pytest.mark.live()
def test_get_compatible_blocks(cli_runner):
    result = cli_runner.invoke(
        cli.main, ["project", "workflow", "get-compatible-blocks"]
    )
    assert result.exit_code == 0
