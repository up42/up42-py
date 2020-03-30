import os
import json
from pathlib import Path
import click

from .auth import Auth
from .tools import Tools
from .project import Project
from .workflow import Workflow
from .utils import get_logger

logger = get_logger(__name__)

ENV = "dev"
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])

# To activate bash autocompletion
# eval "$(_UP42_COMPLETE=source_bash up42)"

# For usage of fstrings
# pylint: disable=logging-format-interpolation


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
        ctx.obj = Auth(cfg_file, env=ENV)
    elif project_id and project_api_key:
        ctx.obj = Auth(project_id, project_api_key, env=ENV)


COMMAND = main.command(context_settings=CONTEXT_SETTINGS)


@COMMAND
@click.pass_obj
def auth(auth):
    """
    Check authentication.
    """
    logger.info(auth)
    logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    logger.info("Run the following commands to persist with this authentication:")
    logger.info(f"export UP42_PROJECT_ID={auth.project_id}")
    logger.info(f"export UP42_PROJECT_API_KEY={auth.project_api_key}")
    logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")


@COMMAND
@click.pass_obj
def config(auth):
    """
    Create a config file.
    """
    config_path = Path("~/UP42_CONFIG.json")
    config_path = config_path.expanduser()

    logger.info(f"Saving config to {config_path}")

    json_config = {
        "project_id": auth.project_id,
        "project_api_key": auth.project_api_key,
    }

    with open(config_path, "w") as cfg:
        json.dump(json_config, cfg)

    auth = Auth(cfg_file=config_path, env=ENV)
    logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    logger.info("Run the following command to persist with this authentication:")
    logger.info(f"export UP42_CFG_FILE={auth.cfg_file}")
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
def get_blocks(auth, block_type, basic):
    """
    Get public blocks information.
    """
    logger.info(Tools(auth).get_blocks(block_type, basic))


def blocks_from_context():
    class OptionChoiceFromContext(click.Option):
        def full_process_value(self, ctx, value):
            self.type = click.Choice(Tools(ctx.obj).get_blocks().keys())
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
def get_block_details(auth, block_name):
    """
    Get details of block by block name.
    """
    logger.info(Tools(auth).get_block_details(Tools(auth).get_blocks()[block_name]))


@COMMAND
@click.pass_obj
def get_environments(auth):
    """
    Get all UP42 environments.
    """
    logger.info(Tools(auth).get_environments())


@COMMAND
@click.argument("name")
@click.argument("environment-variables", type=click.File())
@click.pass_obj
def create_environment(auth, name, environment_variables):
    """
    Create an UP42 environment.
    """
    logger.info(Tools(auth).create_environment(name, json.load(environment_variables)))


def environments_from_context():
    class OptionChoiceFromContext(click.Option):
        def full_process_value(self, ctx, value):
            env_names = [env["name"] for env in Tools(ctx.obj).get_environments()]
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
def delete_environment(auth, environment_name):
    """
    Delete an UP42 environment.
    """
    env_id = [
        env["id"]
        for env in Tools(auth).get_environments()
        if env["name"] == environment_name
    ]
    if click.confirm(
        f"Are you sure you want to delete '{environment_name}'?", abort=True
    ):
        auth.delete_environment(env_id)


@COMMAND
@click.argument("manifest-json", type=click.Path(exists=True))
@click.pass_obj
def validate_manifest(auth, manifest_json):
    """
    Validate a block manifest.
    """
    logger.info(Tools(auth).validate_manifest(manifest_json))


# Project
@main.group()
@click.pass_context
def project(ctx):
    """
    Create and get workflows, manage project settings and more.
    """
    ctx.obj = Project(ctx.obj, ctx.obj.project_id)


COMMAND_PROJECT = project.command(context_settings=CONTEXT_SETTINGS)


@COMMAND_PROJECT
@click.pass_obj
@click.argument("name")
def create_workflow(project, name):
    """
    Create a workflow.
    """
    project.create_workflow(name)


@COMMAND_PROJECT
@click.pass_obj
def get_workflows(project):
    """
    Get the project workflows.
    """
    logger.info(project.get_workflows())


@COMMAND_PROJECT
@click.pass_obj
def get_project_settings(project):
    """
    Get the project settings.
    """
    logger.info(project.get_project_settings())


@COMMAND_PROJECT
@click.option(
    "--max-aoi-size",
    type=click.IntRange(1, 10000),
    help="The maximum area of interest geometry size, from 1-1000 sqkm, default 10 sqkm.",
)
@click.option(
    "--max-concurrent-jobs",
    type=click.IntRange(1, 10),
    help="The maximum number of concurrent jobs, from 1-10, default 1.",
)
@click.option(
    "--number-of-images",
    type=click.IntRange(1, 20),
    help="The maximum number of images returned with each job, from 1-20, default 10.",
)
@click.pass_obj
def update_project_settings(
    project, max_aoi_size, max_concurrent_jobs, number_of_images
):
    """
    Update project settings.
    """
    logger.info(f"Previous project settings:{project.get_project_settings()}")
    project.update_project_settings(
        max_aoi_size=max_aoi_size,
        max_concurrent_jobs=max_concurrent_jobs,
        number_of_images=number_of_images,
    )
    logger.info(f"New project settings: {project.get_project_settings()}")


def workflows_from_context():
    class OptionChoiceFromContext(click.Option):
        def full_process_value(self, ctx, value):
            workflow_names = [wkf.info["name"] for wkf in ctx.obj.get_workflows()]
            self.type = click.Choice(workflow_names)
            return super(OptionChoiceFromContext, self).full_process_value(ctx, value)

    return OptionChoiceFromContext


@COMMAND_PROJECT
@click.option(
    "-name",
    "--workflow-name",
    help="Workflow name to use.",
    required=True,
    cls=workflows_from_context(),
)
@click.pass_context
def workflow_from_name(ctx, workflow_name):
    """
    Use a workflow from name.
    """
    wf = ctx.obj.create_workflow(workflow_name, use_existing=True)
    ctx.invoke(workflow, workflow_id=wf.workflow_id)


# Workflows
@project.group()
@click.pass_context
@click.option(
    "-WID",
    "--WORKFLOW-ID",
    "workflow_id",
    envvar="UP42_WORKFLOW_ID",
    help="Your workflow ID, get it by creating a workflow or running 'up42 project get-workflows'",
    required=True,
)
def workflow(ctx, workflow_id):
    """
    Add workflow tasks, run a job and more.
    """
    ctx.obj = Workflow(ctx.obj.auth, ctx.obj.project_id, workflow_id)
    if not os.environ.get("UP42_WORKFLOW_ID"):
        logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        logger.info("Run the following command to persist with this workflow:")
        logger.info(f"export UP42_WORKFLOW_ID={workflow_id}")
        logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")


COMMAND_WORKFLOW = workflow.command(context_settings=CONTEXT_SETTINGS)


@workflow.command("get-info", context_settings=CONTEXT_SETTINGS)
@click.pass_obj
def workflow_get_info(workflow):
    """
    Get information about the workflow.
    """
    logger.info(workflow.info)


@COMMAND_WORKFLOW
@click.option("--name", type=str, help="New name for the workflow.", required=True)
@click.option(
    "--description", type=str, help="An optional description for the workflow.",
)
@click.pass_context
def update_name(ctx, name, description):
    """
    Update the workflow name.
    """
    logger.info(f"Current info: {ctx.obj.info}")
    if click.confirm(
        f"Are you sure you want to change the name '{ctx.obj.info.get('name')}' to '{name}'?",
        abort=True,
    ):
        ctx.obj.update_name(name, description)
        ctx.obj = Workflow(ctx.obj.auth, ctx.obj.project_id, ctx.obj.workflow_id)
        logger.info(f"New info: {ctx.obj.info}")


@COMMAND_WORKFLOW
@click.pass_obj
def delete(workflow):
    """
    Delete the workflow.
    """
    logger.info(f"Current info: {workflow.info}")
    if click.confirm(
        f"Are you sure you want to delete workflow '{workflow.info.get('name')}'?",
        abort=True,
    ):
        workflow.delete()
        if os.environ.get("UP42_WORKFLOW_ID"):
            logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            logger.info("Make sure to remove the environment variable with:")
            logger.info(f"UP42_WORKFLOW_ID={workflow.workflow_id}")
            logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")


@COMMAND_WORKFLOW
@click.pass_obj
def get_jobs(workflow):
    """
    Get the jobs ran with this workflow.
    """
    logger.info(workflow.get_jobs())


@COMMAND_WORKFLOW
@click.pass_obj
@click.option(
    "--basic/--full", default=True, help="Show basic or full task information."
)
def get_workflow_tasks(workflow, basic):
    """
    Get the workflow tasks list (DAG).
    """
    logger.info(workflow.get_workflow_tasks(basic=basic))


@COMMAND_WORKFLOW
@click.pass_obj
def get_parameter_info(workflow):
    """
    Get info about the parameters of each task in the workflow to make it easy to construct the desired parameters.
    """
    logger.info(workflow.get_parameter_info())


@COMMAND_WORKFLOW
@click.pass_obj
def get_compatible_blocks(workflow):
    """
    Get all compatible blocks for the current workflow.
    """
    logger.info(workflow.get_compatible_blocks())


@COMMAND_WORKFLOW
@click.argument("input-tasks-json", type=click.File("rb"))
@click.pass_obj
def add_workflow_tasks(workflow, input_tasks_json):
    """
    Adds or overwrites workflow tasks.
    - Name is arbitrary but best use the block name. Always use :1 to be able to
    identify the order when two times the same workflow task is used.
    - API by itself validates if the underlying block for the selected block-id
    is available.
    """
    input_tasks = json.load(input_tasks_json)
    logger.info(workflow.add_workflow_tasks(input_tasks))


@COMMAND_WORKFLOW
@click.argument("input-parameters-json", type=click.File("rb"))
@click.option("--track", help="Track status of job in shell.", is_flag=True)
@click.pass_obj
def create_and_run_job(workflow, input_parameters_json, track):
    """
    Creates and runs a new job.
    """
    input_parameters = json.load(input_parameters_json)
    logger.info(workflow.create_and_run_job(input_parameters, track))


# Jobs


# Catalog
