import click
import json
from pathlib import Path

from .api import Api
from .utils import get_logger

logger = get_logger(__name__)


@click.group()
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
    ctx.obj = Api(cfg_file, project_id, project_api_key, env="dev")

@main.command()
@click.pass_obj
def auth(obj):
    """
    Check authentication.
    """
    logger.info(obj)

@main.command()
@click.pass_obj
def config(obj):
    """
    Create a config file.
    """
    config_path = Path('~/UP42_CONFIG.json')
    config_path = config_path.expanduser()

    logger.info(f"Saving config to {config_path}")

    json_config = {"project_id": obj.project_id, "project_api_key": obj.project_api_key}

    with open(config_path, 'w') as cfg:
        json.dump(json_config, cfg)

    obj = Api(cfg_file=config_path, env="dev")
