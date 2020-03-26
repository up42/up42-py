import click
import json
from pathlib import Path

from .api import Api
from .utils import get_logger

logger = get_logger(__name__)

ENV = "dev"
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])

# To activate bash autocompletion
# eval "$(_UP42_COMPLETE=source_bash up42)"


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option(
    "-CFG",
    "--CFG-FILE",
    "cfg_file",
    envvar="UP42_CFG_FILE",
    help="File path to the cfg.json with {project_id: '...', project_api_key: '...'}",
)
@click.option(
    "-PID",
    "--PROJECT-ID",
    "project_id",
    envvar="UP42_PROJECT_ID",
    help="Your project ID, get in the Project settings in the console.",
)
@click.option(
    "-PAPIKEY",
    "--PROJECT-API-KEY",
    "project_api_key",
    envvar="UP42_PROJECT_API_KEY",
    help="Your project API KEY, get in the Project settings in the console.",
)
@click.pass_context
def main(ctx, cfg_file, project_id, project_api_key):
    ctx.ensure_object(dict)
    if cfg_file:
        ctx.obj = Api(cfg_file, env=ENV)
    elif project_id and project_api_key:
        ctx.obj = Api(project_id, project_api_key, env=ENV)


COMMAND = main.command(context_settings=CONTEXT_SETTINGS)


@COMMAND
@click.pass_obj
def auth(api):
    """
    Check authentication.
    """
    logger.info(api)
    logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    logger.info("Run the following commands to persist with this authentication:")
    logger.info(f"export UP42_PROJECT_ID={api.project_id}")
    logger.info(f"export UP42_PROJECT_API_KEY={api.project_api_key}")
    logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")


@COMMAND
@click.pass_obj
def config(api):
    """
    Create a config file.
    """
    config_path = Path("~/UP42_CONFIG.json")
    config_path = config_path.expanduser()

    logger.info(f"Saving config to {config_path}")

    json_config = {"project_id": api.project_id, "project_api_key": api.project_api_key}

    with open(config_path, "w") as cfg:
        json.dump(json_config, cfg)

    api = Api(cfg_file=config_path, env=ENV)
    logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    logger.info("Run the following command to persist with this authentication:")
    logger.info(f"export UP42_CFG_FILE={api.cfg_file}")
    logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")


# Tools
@COMMAND
@click.option(
    "-t",
    "--block-type",
    type=click.Choice(["data", "processing"]),
    default=None,
    help="Filter by block type.",
)
@click.option(
    "--basic/--full", default=True, help="Show basic or full block information."
)
@click.pass_obj
def get_blocks(api, block_type, basic):
    """
    Get public blocks information.
    """
    logger.info(api.get_blocks(block_type, basic))


def blocks_from_context():
    class OptionChoiceFromContext(click.Option):
        def full_process_value(self, ctx, value):
            self.type = click.Choice(ctx.obj.get_blocks().keys())
            return super(OptionChoiceFromContext, self).full_process_value(ctx, value)

    return OptionChoiceFromContext


@COMMAND
@click.option(
    "-name",
    "--block-name",
    help="Block name to get details.",
    required=True,
    cls=blocks_from_context(),
)
@click.pass_obj
def get_block_details(api, block_name):
    """
    Get details of block by block name.
    """
    logger.info(api.get_block_details(api.get_blocks()[block_name]))


@COMMAND
@click.pass_obj
def get_environments(api):
    """
    Get all UP42 environments.
    """
    logger.info(api.get_environments())


@COMMAND
@click.argument("name")
@click.argument("environment-variables", type=click.File())
@click.pass_obj
def create_environment(api, name, environment_variables):
    """
    Create an UP42 environment.
    """
    logger.info(api.create_environment(name, json.load(environment_variables)))


def environments_from_context():
    class OptionChoiceFromContext(click.Option):
        def full_process_value(self, ctx, value):
            env_names = [env["name"] for env in ctx.obj.get_environments()]
            self.type = click.Choice(env_names)
            return super(OptionChoiceFromContext, self).full_process_value(ctx, value)

    return OptionChoiceFromContext


@COMMAND
@click.option(
    "-name",
    "--environment-name",
    help="Environment name to delete.",
    required=True,
    cls=environments_from_context(),
)
@click.pass_obj
def delete_environment(api, environment_name):
    """
    Delete an UP42 environment.
    """
    env_id = [
        env["id"] for env in api.get_environments() if env["name"] == environment_name
    ]
    if click.confirm(
        f"Are you sure you want to delete '{environment_name}'?", abort=True
    ):
        api.delete_environment(env_id)


@COMMAND
@click.argument("manifest-json", type=click.Path(exists=True))
@click.pass_obj
def validate_manifest(api, manifest_json):
    """
    Validate a block manifest.
    """
    logger.info(api.validate_manifest(manifest_json))


# Projects


# Workflows


# Jobs


# Catalog
