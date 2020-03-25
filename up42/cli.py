import click

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
    ctx.obj["api"] = Api(cfg_file, project_id, project_api_key, env="dev")

@main.command()
@click.pass_context
def auth(ctx):
    click.echo(click.style(repr(ctx.obj["api"]), fg='blue'))
