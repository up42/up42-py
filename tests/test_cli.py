from click.testing import CliRunner
from up42 import cli

@pytest.fixture()
def auth_fixture():
    PID="something"
    PAPIKEY="something"

def test_main():
  runner = CliRunner()
  result = runner.invoke(cli.main)
  assert result.exit_code == 0

def test_auth():
  runner = CliRunner()
  result = runner.invoke(cli.main, ["auth"])
  assert result.exit_code == 0

def test_config():
  runner = CliRunner()
  with runner.isolated_filesystem():
      result = runner.invoke(cli.main, ["config"])
      assert result.exit_code == 0
