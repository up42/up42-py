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
def cli_runner():
    return CliRunner()


PROJECT_ENVS = mock.patch.dict(
    "os.environ",
    {
        "UP42_PROJECT_ID": os.environ.get("TEST_UP42_PROJECT_ID"),
        "UP42_PROJECT_API_KEY": os.environ.get("TEST_UP42_PROJECT_API_KEY"),
    },
)

WORKFLOW_ENVS = mock.patch.dict(
    "os.environ", {"UP42_WORKFLOW_ID": os.environ.get("TEST_UP42_WORKFLOW_ID"),},
)

JOB_ENVS = mock.patch.dict(
    "os.environ", {"UP42_JOB_ID": os.environ.get("TEST_UP42_JOB_ID"),},
)


@PROJECT_ENVS
@pytest.mark.live()
def test_main_live(cli_runner):
    result = cli_runner.invoke(cli.main)
    assert result.exit_code == 0


@PROJECT_ENVS
@pytest.mark.live()
def test_auth_live(cli_runner):
    result = cli_runner.invoke(cli.main, ["auth"])
    assert result.exit_code == 0


@PROJECT_ENVS
@pytest.mark.live()
def test_config_live(cli_runner):
    with cli_runner.isolated_filesystem():
        result = cli_runner.invoke(cli.main, ["config"])
        assert result.exit_code == 0


@PROJECT_ENVS
@pytest.mark.live()
def test_get_blocks_live(cli_runner):
    result = cli_runner.invoke(cli.main, ["get-blocks"])
    assert result.exit_code == 0


@PROJECT_ENVS
@pytest.mark.live()
def test_get_block_details_live(cli_runner):
    result = cli_runner.invoke(cli.main, ["get-block-details", "-h"])
    assert result.exit_code == 0

    result = cli_runner.invoke(cli.main, ["get-block-details", "-n", "tiling"])
    assert result.exit_code == 0

    result = cli_runner.invoke(cli.main, ["get-block-details", "-n", "never_a_block"])
    assert result.exit_code == 2


@PROJECT_ENVS
@pytest.mark.live()
def test_validate_manifest_live(cli_runner):
    result = cli_runner.invoke(cli.main, ["validate-manifest", "-h"])
    assert result.exit_code == 0

    mock_manifest = Path(__file__).resolve().parent / "mock_data/manifest.json"
    result = cli_runner.invoke(cli.main, ["validate-manifest", str(mock_manifest)])
    assert result.exit_code == 0


@PROJECT_ENVS
@pytest.mark.live()
def test_project_live(cli_runner):
    result = cli_runner.invoke(cli.main, ["project"])
    assert result.exit_code == 0


@PROJECT_ENVS
@pytest.mark.live()
def test_create_workflow_live(cli_runner):
    result = cli_runner.invoke(cli.main, ["project", "create-workflow", "-h"])
    assert result.exit_code == 0

    # result = cli_runner.invoke(
    #    cli.main, ["project", "create-workflow", "a_cli_workflow"]
    # )
    # assert result.exit_code == 0


@PROJECT_ENVS
@pytest.mark.live()
def test_get_project_settings_live(cli_runner):
    result = cli_runner.invoke(cli.main, ["project", "get-project-settings"])
    assert result.exit_code == 0


@PROJECT_ENVS
@pytest.mark.live()
def test_get_workflows_live(cli_runner):
    result = cli_runner.invoke(cli.main, ["project", "get-workflows"])
    assert result.exit_code == 0


@PROJECT_ENVS
@pytest.mark.live()
def test_update_project_settings_live(cli_runner):
    result = cli_runner.invoke(cli.main, ["project", "update-project-settings", "-h"])
    assert result.exit_code == 0


@PROJECT_ENVS
@pytest.mark.live()
def test_workflow_from_name_live(cli_runner):
    result = cli_runner.invoke(cli.main, ["project", "workflow-from-name", "-h"])
    assert result.exit_code == 0

    result = cli_runner.invoke(
        cli.main, ["project", "workflow-from-name", "-n", "test_cli"]
    )
    assert result.exit_code == 0

    result = cli_runner.invoke(
        cli.main, ["project", "workflow-from-name", "-n", "never_a_workflow"]
    )
    assert result.exit_code == 2


@PROJECT_ENVS
@pytest.mark.live()
def test_workflow_live(cli_runner):
    result = cli_runner.invoke(cli.main, ["workflow", "-h"])
    assert result.exit_code == 0

    result = cli_runner.invoke(cli.main, ["workflow"])
    assert result.exit_code == 0


@PROJECT_ENVS
@WORKFLOW_ENVS
@pytest.mark.live()
def test_workflow_get_info_live(cli_runner):
    result = cli_runner.invoke(cli.main, ["workflow", "get-info"])
    assert result.exit_code == 0


@PROJECT_ENVS
@WORKFLOW_ENVS
@pytest.mark.live()
def test_workflow_update_name_live(cli_runner):
    result = cli_runner.invoke(cli.main, ["workflow", "update-name", "-h"])
    assert result.exit_code == 0


@PROJECT_ENVS
@WORKFLOW_ENVS
@pytest.mark.live()
def test_workflow_delete_live(cli_runner):
    result = cli_runner.invoke(cli.main, ["workflow", "delete", "-h"])
    assert result.exit_code == 0


@PROJECT_ENVS
@WORKFLOW_ENVS
@pytest.mark.live()
def test_get_jobs_live(cli_runner):
    result = cli_runner.invoke(cli.main, ["workflow", "get-jobs"])
    assert result.exit_code == 0


@PROJECT_ENVS
@WORKFLOW_ENVS
@pytest.mark.live()
def test_get_workflow_tasks_live(cli_runner):
    result = cli_runner.invoke(cli.main, ["workflow", "get-workflow-tasks"])
    assert result.exit_code == 0


@PROJECT_ENVS
@WORKFLOW_ENVS
@pytest.mark.live()
def test_get_parameters_info_live(cli_runner):
    result = cli_runner.invoke(cli.main, ["workflow", "get-parameters-info"])
    assert result.exit_code == 0


@PROJECT_ENVS
@WORKFLOW_ENVS
@pytest.mark.live()
def test_get_compatible_blocks_live(cli_runner):
    result = cli_runner.invoke(cli.main, ["workflow", "get-compatible-blocks"])
    assert result.exit_code == 0


@PROJECT_ENVS
@WORKFLOW_ENVS
@pytest.mark.live()
def test_add_workflow_tasks_live(cli_runner):
    result = cli_runner.invoke(cli.main, ["workflow", "add-workflow-tasks", "-h"])
    assert result.exit_code == 0

    input_tasks_json = (
        Path(__file__).resolve().parent / "mock_data/input_tasks_simple.json"
    )
    result = cli_runner.invoke(
        cli.main, ["workflow", "add-workflow-tasks", str(input_tasks_json)]
    )
    assert result.exit_code == 0


@PROJECT_ENVS
@WORKFLOW_ENVS
@pytest.mark.live()
def test_create_and_run_job_live(cli_runner):
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


@PROJECT_ENVS
@JOB_ENVS
@pytest.mark.live()
def test_job_live(cli_runner):
    result = cli_runner.invoke(cli.main, ["job", "-h"])
    assert result.exit_code == 0

    result = cli_runner.invoke(cli.main, ["job"])
    assert result.exit_code == 0


@PROJECT_ENVS
@JOB_ENVS
@pytest.mark.live()
def test_job_get_info_live(cli_runner):
    result = cli_runner.invoke(cli.main, ["job", "get-info"])
    assert result.exit_code == 0


@PROJECT_ENVS
@JOB_ENVS
@pytest.mark.live()
def test_cancel_job_live(cli_runner):
    result = cli_runner.invoke(cli.main, ["job", "cancel-job", "-h"])
    assert result.exit_code == 0


@PROJECT_ENVS
@JOB_ENVS
@pytest.mark.live()
def test_download_quicklooks_live(cli_runner):
    result = cli_runner.invoke(cli.main, ["job", "download-quicklooks", "-h"])
    assert result.exit_code == 0


@PROJECT_ENVS
@JOB_ENVS
@pytest.mark.live()
def test_download_results_live(cli_runner):
    result = cli_runner.invoke(cli.main, ["job", "download-results", "-h"])
    assert result.exit_code == 0


@PROJECT_ENVS
@JOB_ENVS
@pytest.mark.live()
def test_get_jobtasks_live(cli_runner):
    result = cli_runner.invoke(cli.main, ["job", "get-jobtasks"])
    assert result.exit_code == 0


@PROJECT_ENVS
@JOB_ENVS
@pytest.mark.live()
def test_jobtasks_results_json_live(cli_runner):
    result = cli_runner.invoke(cli.main, ["job", "get-jobtasks-results-json"])
    assert result.exit_code == 0


@PROJECT_ENVS
@JOB_ENVS
@pytest.mark.live()
def test_get_logs_live(cli_runner):
    result = cli_runner.invoke(cli.main, ["job", "get-logs"])
    assert result.exit_code == 0


@PROJECT_ENVS
@JOB_ENVS
@pytest.mark.live()
def test_get_results_json_live(cli_runner):
    result = cli_runner.invoke(cli.main, ["job", "get-results-json"])
    assert result.exit_code == 0


@PROJECT_ENVS
@JOB_ENVS
@pytest.mark.live()
def test_get_status_live(cli_runner):
    result = cli_runner.invoke(cli.main, ["job", "get-status"])
    assert result.exit_code == 0


@PROJECT_ENVS
@JOB_ENVS
@pytest.mark.live()
def test_track_status_live(cli_runner):
    result = cli_runner.invoke(cli.main, ["job", "track-status"])
    assert result.exit_code == 0


@PROJECT_ENVS
@pytest.mark.live()
def test_catalog_live(cli_runner):
    result = cli_runner.invoke(cli.main, ["catalog", "-h"])
    assert result.exit_code == 0


@PROJECT_ENVS
@pytest.mark.live()
def test_construct_parameters_live(cli_runner):
    result = cli_runner.invoke(cli.main, ["catalog", "construct-parameters", "-h"])
    assert result.exit_code == 0

    aoi_geojson = Path(__file__).resolve().parent / "mock_data/aoi_berlin.geojson"
    result = cli_runner.invoke(
        cli.main, ["catalog", "construct-parameters", str(aoi_geojson)]
    )
    assert result.exit_code == 0


@PROJECT_ENVS
@pytest.mark.live()
def test_catalog_search_live(cli_runner):
    search_parameters_json = (
        Path(__file__).resolve().parent / "mock_data/search_params_simple.json"
    )
    result = cli_runner.invoke(
        cli.main, ["catalog", "search", str(search_parameters_json)]
    )
    assert result.exit_code == 0
