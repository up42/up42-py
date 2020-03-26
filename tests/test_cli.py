import pytest
from click.testing import CliRunner
from up42 import cli


@pytest.fixture()
def auth_fixture():
    PID = "something"
    PAPIKEY = "something"


@pytest.fixture()
def cli_runner():
    return CliRunner()


def test_main(cli_runner):
    result = cli_runner.invoke(cli.main)
    assert result.exit_code == 0


def test_auth(cli_runner):
    result = cli_runner.invoke(cli.main, ["auth"])
    assert result.exit_code == 0


def test_config(cli_runner):
    with cli_runner.isolated_filesystem():
        result = cli_runner.invoke(cli.main, ["config"])
        assert result.exit_code == 0


def test_get_blocks(cli_runner):
    result = cli_runner.invoke(cli.main, ["get-blocks"])
    assert result.exit_code == 0


def test_get_block_details(cli_runner):
    result = cli_runner.invoke(cli.main, ["get-block-details", "-h"])
    assert result.exit_code == 0


def test_get_environments(cli_runner):
    result = cli_runner.invoke(cli.main, ["get-environments"])
    assert result.exit_code == 0


def test_create_environment(cli_runner):
    result = cli_runner.invoke(cli.main, ["create-environment", "-h"])
    assert result.exit_code == 0


def test_delete_environment(cli_runner):
    result = cli_runner.invoke(cli.main, ["delete-environment", "-h"])
    assert result.exit_code == 0
    # Test prompt
    result = cli_runner.invoke(cli.main, ["delete-environment", "SOME_NAME"], input="y")
    assert result.exit_code == 0


def test_validate_manifest(cli_runner):
    result = cli_runner.invoke(cli.main, ["validate-manifest", "-h"])
    assert result.exit_code == 0
