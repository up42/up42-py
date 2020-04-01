import os
from unittest import mock
from pathlib import Path
import pytest
from click.testing import CliRunner
from up42 import cli


# VARS THAT NEED SETTINGS:
#  TEST_UP42_PROJECT_ID
#  TEST_UP42_PROJECT_API_KEY
#  TEST_UP42_WORKFLOW_ID
#  TEST_UP42_JOB_ID


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

JOB_ENVS = mock.patch.dict(
    "os.environ", {"UP42_JOB_ID": os.environ.get("TEST_UP42_JOB_ID"),},
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

    result = cli_runner.invoke(cli.main, ["get-block-details", "-n", "tiling"])
    assert result.exit_code == 0

    result = cli_runner.invoke(cli.main, ["get-block-details", "-n", "never_a_block"])
    assert result.exit_code == 2


@pytest.mark.live()
def test_get_environments(cli_runner):
    result = cli_runner.invoke(cli.main, ["get-environments"])
    assert result.exit_code == 0


@pytest.mark.live()
def test_create_environment(cli_runner):
    result = cli_runner.invoke(cli.main, ["create-environment", "-h"])
    assert result.exit_code == 0

    mock_env = Path(__file__).resolve().parent / "mock_data/env.json"
    result = cli_runner.invoke(
        cli.main, ["create-environment", "a_environment", str(mock_env)]
    )
    assert result.exit_code == 0


@pytest.mark.live()
def test_delete_environment(cli_runner):
    result = cli_runner.invoke(cli.main, ["delete-environment", "-h"])
    assert result.exit_code == 0
    # Test prompt
    result = cli_runner.invoke(
        cli.main, ["delete-environment", "-n", "a_environment"], input="y"
    )
    assert result.exit_code == 0


@pytest.mark.live()
def test_validate_manifest(cli_runner):
    result = cli_runner.invoke(cli.main, ["validate-manifest", "-h"])
    assert result.exit_code == 0

    mock_manifest = Path(__file__).resolve().parent / "mock_data/manifest.json"
    result = cli_runner.invoke(cli.main, ["validate-manifest", str(mock_manifest)])
    assert result.exit_code == 0


@pytest.mark.live()
def test_project(cli_runner):
    result = cli_runner.invoke(cli.main, ["project"])
    assert result.exit_code == 0


@pytest.mark.live()
def test_create_workflow(cli_runner):
    result = cli_runner.invoke(cli.main, ["project", "create-workflow", "-h"])
    assert result.exit_code == 0

    result = cli_runner.invoke(
        cli.main, ["project", "create-workflow", "a_cli_workflow"]
    )
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

    result = cli_runner.invoke(
        cli.main, ["project", "workflow-from-name", "-n", "a_cli_workflow"]
    )
    assert result.exit_code == 0

    result = cli_runner.invoke(
        cli.main, ["project", "workflow-from-name", "-n", "never_a_workflow"]
    )
    assert result.exit_code == 2


@pytest.mark.live()
def test_workflow(cli_runner):
    result = cli_runner.invoke(cli.main, ["workflow", "-h"])
    assert result.exit_code == 0

    result = cli_runner.invoke(cli.main, ["workflow"])
    assert result.exit_code == 0


@WORKFLOW_ENVS
@pytest.mark.live()
def test_workflow_get_info(cli_runner):
    result = cli_runner.invoke(cli.main, ["workflow", "get-info"])
    assert result.exit_code == 0


@WORKFLOW_ENVS
@pytest.mark.live()
def test_workflow_update_name(cli_runner):
    result = cli_runner.invoke(cli.main, ["workflow", "update-name", "-h"])
    assert result.exit_code == 0


@WORKFLOW_ENVS
@pytest.mark.live()
def test_workflow_delete(cli_runner):
    result = cli_runner.invoke(cli.main, ["workflow", "delete", "-h"])
    assert result.exit_code == 0


@WORKFLOW_ENVS
@pytest.mark.live()
def test_get_jobs(cli_runner):
    result = cli_runner.invoke(cli.main, ["workflow", "get-jobs"])
    assert result.exit_code == 0


@WORKFLOW_ENVS
@pytest.mark.live()
def test_get_workflow_tasks(cli_runner):
    result = cli_runner.invoke(cli.main, ["workflow", "get-workflow-tasks"])
    assert result.exit_code == 0


@WORKFLOW_ENVS
@pytest.mark.live()
def test_get_parameter_info(cli_runner):
    result = cli_runner.invoke(cli.main, ["workflow", "get-parameter-info"])
    assert result.exit_code == 0


@WORKFLOW_ENVS
@pytest.mark.live()
def test_get_compatible_blocks(cli_runner):
    result = cli_runner.invoke(cli.main, ["workflow", "get-compatible-blocks"])
    assert result.exit_code == 0


@WORKFLOW_ENVS
@pytest.mark.live()
def test_add_workflow_tasks(cli_runner):
    result = cli_runner.invoke(cli.main, ["workflow", "add-workflow-tasks", "-h"])
    assert result.exit_code == 0

    input_tasks_json = (
        Path(__file__).resolve().parent / "mock_data/input_tasks_simple.json"
    )
    result = cli_runner.invoke(
        cli.main, ["workflow", "add-workflow-tasks", str(input_tasks_json)]
    )
    assert result.exit_code == 0


@WORKFLOW_ENVS
@pytest.mark.live()
def test_create_and_run_job(cli_runner):
    result = cli_runner.invoke(cli.main, ["workflow", "create-and-run-job", "-h"])
    assert result.exit_code == 0

    input_parameters_json = (
        Path(__file__).resolve().parent / "mock_data/input_params_simple.json"
    )
    result = cli_runner.invoke(
        cli.main,
        ["workflow", "create-and-run-job", str(input_parameters_json), "--track",],
    )
    assert result.exit_code == 0


@JOB_ENVS
@pytest.mark.live()
def test_job(cli_runner):
    result = cli_runner.invoke(cli.main, ["job", "-h"])
    assert result.exit_code == 0

    result = cli_runner.invoke(cli.main, ["job"])
    assert result.exit_code == 0


@JOB_ENVS
@pytest.mark.live()
def test_job_get_info(cli_runner):
    result = cli_runner.invoke(cli.main, ["job", "get-info"])
    assert result.exit_code == 0


@JOB_ENVS
@pytest.mark.live()
def test_cancel_job(cli_runner):
    result = cli_runner.invoke(cli.main, ["job", "cancel-job", "-h"])
    assert result.exit_code == 0


@JOB_ENVS
@pytest.mark.live()
def test_download_quicklook(cli_runner):
    result = cli_runner.invoke(cli.main, ["job", "download-quicklook", "-h"])
    assert result.exit_code == 0


@JOB_ENVS
@pytest.mark.live()
def test_download_result(cli_runner):
    result = cli_runner.invoke(cli.main, ["job", "download-result", "-h"])
    assert result.exit_code == 0


@JOB_ENVS
@pytest.mark.live()
def test_get_job_tasks(cli_runner):
    result = cli_runner.invoke(cli.main, ["job", "get-job-tasks"])
    assert result.exit_code == 0


@JOB_ENVS
@pytest.mark.live()
def test_job_tasks_result_json(cli_runner):
    result = cli_runner.invoke(cli.main, ["job", "get-job-tasks-result-json"])
    assert result.exit_code == 0


@JOB_ENVS
@pytest.mark.live()
def test_get_log(cli_runner):
    result = cli_runner.invoke(cli.main, ["job", "get-log"])
    assert result.exit_code == 0


@JOB_ENVS
@pytest.mark.live()
def test_get_result_json(cli_runner):
    result = cli_runner.invoke(cli.main, ["job", "get-result-json"])
    assert result.exit_code == 0


@JOB_ENVS
@pytest.mark.live()
def test_get_status(cli_runner):
    result = cli_runner.invoke(cli.main, ["job", "get-status"])
    assert result.exit_code == 0


@JOB_ENVS
@pytest.mark.live()
def test_track_status(cli_runner):
    result = cli_runner.invoke(cli.main, ["job", "track-status"])
    assert result.exit_code == 0


@pytest.mark.live()
def test_catalog(cli_runner):
    result = cli_runner.invoke(cli.main, ["catalog", "-h"])
    assert result.exit_code == 0


@pytest.mark.live()
def test_construct_parameters(cli_runner):
    result = cli_runner.invoke(cli.main, ["catalog", "construct-parameters", "-h"])
    assert result.exit_code == 0

    aoi_geojson = Path(__file__).resolve().parent / "mock_data/aoi_berlin.geojson"
    result = cli_runner.invoke(
        cli.main, ["catalog", "construct-parameters", str(aoi_geojson)]
    )
    assert result.exit_code == 0


@pytest.mark.live()
def test_catalog_search(cli_runner):
    search_parameters_json = (
        Path(__file__).resolve().parent / "mock_data/search_params_simple.json"
    )
    result = cli_runner.invoke(
        cli.main, ["catalog", "search", str(search_parameters_json)]
    )
    assert result.exit_code == 0
