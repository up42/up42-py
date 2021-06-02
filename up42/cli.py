"""
Command Line Interface functionality with click
"""
import os
import json
from pathlib import Path
from datetime import datetime, timedelta
import click

from up42.auth import Auth
from up42.tools import Tools
from up42.project import Project
from up42.workflow import Workflow
from up42.job import Job
from up42.catalog import Catalog
from up42.utils import get_logger

logger = get_logger(__name__)

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"], show_default=True)

# To activate bash autocompletion
# eval "$(_UP42_COMPLETE=source_bash up42)"


def pprint_json(obj, indent=2):
    return "\n" + json.dumps(obj, indent=indent, sort_keys=True)


def cfg_default(defult_path="./config.json"):
    if Path(defult_path).exists():
        return defult_path
    else:
        return


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option(
    "-pid",
    "--project-id",
    "project_id",
    envvar="UP42_PROJECT_ID",
    help="Your project ID, get it in the Project settings in the console.",
)
@click.option(
    "-pkey",
    "--project-api-key",
    "project_api_key",
    envvar="UP42_PROJECT_API_KEY",
    help="Your project API KEY, get in the Project settings in the console.",
)
@click.option(
    "-cfg",
    "--config-file",
    "cfg_file",
    type=click.Path(),
    default=cfg_default(),
    envvar="UP42_CFG_FILE",
    help="File path to the config.json with {project_id: '...', project_api_key: '...'}",
)
@click.option("--env", default="com")
@click.pass_context
def up42(ctx, project_id, project_api_key, cfg_file, env):
    ctx.ensure_object(dict)
    if project_id and project_api_key:
        ctx.obj = Auth(project_id=project_id, project_api_key=project_api_key, env=env)
    elif cfg_file:
        ctx.obj = Auth(cfg_file=cfg_file, env=env)


COMMAND = up42.command(context_settings=CONTEXT_SETTINGS)


@COMMAND
@click.pass_obj
def auth(auth):
    """
    Check authentication.
    """
    if auth:
        click.echo(
            click.style(
                """
                                                         ▓▌  ▓▀▀▓
                ╟▓▓▓▓▌     ╟▓▓▓▓▌  ▓▓▓▓▓▓▓▓▓▓▓▓▄       ▄▀▀▌    ╓▓
                ▓▓▓▓▓▌     ▓▓▓▓▓▌  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓   ,▓▌╓▓▌,  ▓▀
                ▓▓▓▓▓▌     ▓▓▓▓▓▌  ▓▓▓▓▓    ╘▀▓▓▓▓▓      ▀▀  ████═
                ▓▓▓▓▓▌     ▓▓▓▓▓▌  ▓▓▓▓▌      ▀▓▓▓▓▌
                ╫▓▓▓▓▓     ▓▓▓▓▓▌  ▓▓▓▓▌      ▓▓▓▓▓▌
                 ▓▓▓▓▓▓▄▄▄▓▓▓▓▓▓   ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▀
                  █▓▓▓▓▓▓▓▓▓▓▓▀`   ▓▓▓▓▓▓▓▓▓▓▓▓▓▀
                    ▀▀█▓▓▓█▀▀      ▓▓▓▓▓▀▀▀▀▀▀'
                                   ▓▓▓▀
                                    └

        """,
                fg="blue",
            )
        )
        logger.info(auth)
        logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        logger.info("Run the following commands to persist with this authentication:")
        logger.info("export UP42_PROJECT_ID={}".format(auth.project_id))
        logger.info("export UP42_PROJECT_API_KEY={}".format(auth.project_api_key))
        logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    else:
        logger.error("Unable to authenticate! Check project keys or config file.")


@COMMAND
@click.option("--env", default="com")
@click.pass_obj
def config(auth, env):
    """
    Create a config file.
    """
    if auth:
        config_path = Path("./config.json").resolve()
        logger.info("Saving config to {}".format(config_path))

        json_config = {
            "project_id": auth.project_id,
            "project_api_key": auth.project_api_key,
        }

        with open(config_path, "w") as cfg:
            json.dump(json_config, cfg)

        auth = Auth(cfg_file=str(config_path), env=env)
        logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        logger.info("Run the following command to persist with this authentication:")
        logger.info("export UP42_CFG_FILE={}".format(auth.cfg_file))
        logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    else:
        logger.error("Unable to authenticate! Check project keys or config file.")


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
    logger.info(pprint_json(Tools(auth).get_blocks(block_type, basic)))


def blocks_from_context():
    class OptionChoiceFromContext(click.Option):
        def full_process_value(self, ctx, value):
            self.type = click.Choice(Tools(ctx.obj).get_blocks().keys())
            return super().full_process_value(ctx, value)  # pylint: disable=no-member

    return OptionChoiceFromContext


@COMMAND
@click.option(
    "-n",
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
    logger.info(
        pprint_json(Tools(auth).get_block_details(Tools(auth).get_blocks()[block_name]))
    )


@COMMAND
@click.argument("manifest-json", type=click.Path(exists=True))
@click.pass_obj
def validate_manifest(auth, manifest_json):
    """
    Validate a block manifest.
    """
    logger.info(pprint_json(Tools(auth).validate_manifest(manifest_json)))


# Project
@up42.group()
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
    wf = project.create_workflow(name)
    logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    logger.info("Run the following command to persist with this workflow:")
    logger.info("export UP42_WORKFLOW_ID={}".format(wf.workflow_id))
    logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")


@COMMAND_PROJECT
@click.pass_obj
def get_workflows(project):
    """
    Get the project workflows.
    """
    logger.info(pprint_json(project.get_workflows(return_json=True)))


@COMMAND_PROJECT
@click.pass_obj
def get_project_settings(project):
    """
    Get the project settings.
    """
    logger.info(pprint_json(project.get_project_settings()))


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
    logger.info("Previous project settings:{}".format(project.get_project_settings()))
    project.update_project_settings(
        max_aoi_size=max_aoi_size,
        max_concurrent_jobs=max_concurrent_jobs,
        number_of_images=number_of_images,
    )
    logger.info("New project settings: {}".format(project.get_project_settings()))


def workflows_from_context():
    class OptionChoiceFromContext(click.Option):
        def full_process_value(self, ctx, value):
            workflow_names = [wkf._info["name"] for wkf in ctx.obj.get_workflows()]
            self.type = click.Choice(workflow_names)
            return super().full_process_value(ctx, value)  # pylint: disable=no-member

    return OptionChoiceFromContext


@COMMAND_PROJECT
@click.option(
    "-n",
    "--workflow-name",
    help="Workflow name to use.",
    required=True,
    cls=workflows_from_context(),
)
@click.pass_obj
def workflow_from_name(project, workflow_name):
    """
    Use a workflow from name.
    """
    wf = project.create_workflow(workflow_name, use_existing=True)
    logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    logger.info("Run the following command to persist with this workflow:")
    logger.info("export UP42_WORKFLOW_ID={}".format(wf.workflow_id))
    logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")


# Workflows
@up42.group()
@click.pass_context
@click.option(
    "-wid",
    "--workflow-id",
    "workflow_id",
    envvar="UP42_WORKFLOW_ID",
    help="Your workflow ID, get it by creating a workflow or running 'up42 project get-workflows'",
    required=True,
)
def workflow(ctx, workflow_id):
    """
    Add workflow tasks, run a job and more.
    """
    ctx.obj = Workflow(ctx.obj, ctx.obj.project_id, workflow_id)
    if not os.environ.get("UP42_WORKFLOW_ID"):
        logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        logger.info("Run the following command to persist with this workflow:")
        logger.info("export UP42_WORKFLOW_ID={}".format(workflow_id))
        logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")


COMMAND_WORKFLOW = workflow.command(context_settings=CONTEXT_SETTINGS)


@workflow.command("info", context_settings=CONTEXT_SETTINGS)
@click.pass_obj
def workflow_info(workflow):
    """
    Get information about the workflow.
    """
    logger.info(pprint_json(workflow.info))


@COMMAND_WORKFLOW
@click.option(
    "-n",
    "--workflow-name",
    "name",
    type=str,
    help="New name for the workflow.",
    required=True,
)
@click.option(
    "--description",
    type=str,
    help="An optional description for the workflow.",
)
@click.pass_context
def update_name(ctx, name, description):
    """
    Update the workflow name.
    """
    logger.info("Current info: {}".format(ctx.obj._info))
    if click.confirm(
        f"Are you sure you want to change the name '{ctx.obj._info.get('name')}' to '{name}'?",
        abort=True,
    ):
        ctx.obj.update_name(name, description)
        ctx.obj = Workflow(ctx.obj.auth, ctx.obj.project_id, ctx.obj.workflow_id)
        logger.info("New info: {}".format(ctx.obj._info))


@COMMAND_WORKFLOW
@click.pass_obj
def delete(workflow):
    """
    Delete the workflow.
    """
    logger.info("Current info: {}".format(workflow._info))
    if click.confirm(
        f"Are you sure you want to delete workflow '{workflow._info.get('name')}'?",
        abort=True,
    ):
        workflow.delete()
        if os.environ.get("UP42_WORKFLOW_ID"):
            logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            logger.info("Make sure to remove the environment variable with:")
            logger.info("UP42_WORKFLOW_ID={}".format(workflow.workflow_id))
            logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")


@COMMAND_WORKFLOW
@click.pass_obj
def get_jobs(workflow):
    """
    Get the jobs ran with this workflow.
    """
    logger.info(pprint_json(workflow.get_jobs(return_json=True)))


@COMMAND_WORKFLOW
@click.pass_obj
@click.option(
    "--basic/--full", default=True, help="Show basic or full task information."
)
def get_workflow_tasks(workflow, basic):
    """
    Get the workflow tasks list (DAG).
    """
    logger.info(pprint_json(workflow.get_workflow_tasks(basic=basic)))


@COMMAND_WORKFLOW
@click.pass_obj
def get_parameters_info(workflow):
    """
    Get info about the parameters of each task in the workflow to make it easy to construct the desired parameters.
    """
    logger.info(pprint_json(workflow.get_parameters_info()))


@COMMAND_WORKFLOW
@click.pass_obj
def get_compatible_blocks(workflow):
    """
    Get all compatible blocks for the current workflow.
    """
    logger.info(pprint_json(workflow.get_compatible_blocks()))


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
def test_job(workflow, input_parameters_json, track):
    """
    Create a run a new test job (Test Query). With this test query you will not be
    charged with any data or processing credits, but have a preview of the job result.
    """
    input_parameters = json.load(input_parameters_json)
    jb = workflow.test_job(input_parameters, track)
    logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    logger.info("Run the following command to persist with this test job:")
    logger.info("export UP42_JOB_ID={}".format(jb.job_id))
    logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")


@COMMAND_WORKFLOW
@click.argument("input-parameters-json", type=click.File("rb"))
@click.option("--track", help="Track status of job in shell.", is_flag=True)
@click.pass_obj
def run_job(workflow, input_parameters_json, track):
    """
    Creates and runs a new job.
    """
    input_parameters = json.load(input_parameters_json)
    jb = workflow.run_job(input_parameters, track)
    logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    logger.info("Run the following command to persist with this job:")
    logger.info("export UP42_JOB_ID={}".format(jb.job_id))
    logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")


# Jobs
@up42.group()
@click.pass_context
@click.option(
    "-jid",
    "--job-id",
    "job_id",
    envvar="UP42_JOB_ID",
    help="Your job ID, get it by creating a job or running 'up42 project workflow get-jobs'",
    required=True,
)
def job(ctx, job_id):
    """
    Get job status, results and more.
    """
    ctx.obj = Job(ctx.obj, ctx.obj.project_id, job_id)
    if not os.environ.get("UP42_JOB_ID"):
        logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        logger.info("Run the following command to persist with this job:")
        logger.info("export UP42_JOB_ID={}".format(job_id))
        logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")


COMMAND_JOB = job.command(context_settings=CONTEXT_SETTINGS)


@job.command("info", context_settings=CONTEXT_SETTINGS)
@click.pass_obj
def job_info(job):
    """
    Get information about the job.
    """
    logger.info(pprint_json(job._info))


@COMMAND_JOB
@click.pass_obj
def cancel_job(job):
    """
    Cancel a job that is running.
    """
    logger.info(job.status)
    if click.confirm("Are you sure you want to cancel job with job id '{job.job_id}'?"):
        job.cancel_job()


@COMMAND_JOB
@click.argument(
    "output_directory",
    type=click.Path(exists=True, writable=True, file_okay=False, resolve_path=True),
)
@click.pass_obj
def download_quicklooks(job, output_directory):
    """
    Download a job's quicklooks.
    """
    logger.info(job.download_quicklooks(output_directory))


@COMMAND_JOB
@click.argument(
    "output_directory",
    type=click.Path(exists=True, writable=True, file_okay=False, resolve_path=True),
)
@click.pass_obj
def download_results(job, output_directory):
    """
    Download and unpack the job results.
    """
    logger.info(job.download_results(output_directory))


@COMMAND_JOB
@click.pass_obj
def get_jobtasks(job):
    """
    Get the individual items of the job.
    """
    logger.info(pprint_json(job.get_jobtasks(return_json=True)))


@COMMAND_JOB
@click.pass_obj
def get_jobtasks_results_json(job):
    """
    Convenience function to get the resulting data.json of all job tasks.
    """
    logger.info(pprint_json(job.get_jobtasks_results_json()))


@COMMAND_JOB
@click.pass_obj
def get_logs(job):
    """
    Convenience function to print or return the logs of all job tasks.
    """
    job.get_logs()


@COMMAND_JOB
@click.pass_obj
def get_results_json(job):
    """
    Get the job results data.json.
    """
    logger.info(pprint_json(job.get_results_json()))


@COMMAND_JOB
@click.pass_obj
def status(job):
    """
    Get the job status.
    """
    logger.info(job.status)


@COMMAND_JOB
@click.option(
    "-i",
    "--interval",
    help="Interval between getting job status in seconds.",
    default=30,
    type=click.IntRange(1, 300),
)
@click.pass_obj
def track_status(job, interval):
    """
    Track the job status with regular time intervals.
    """
    logger.info(job.track_status(interval))


# Catalog


@up42.group()
@click.pass_context
def catalog(ctx):
    """
    UP42 catalog search. You can search for satellite image scenes
    for different sensors and criteria like cloud cover.
    """
    ctx.obj = Catalog(ctx.obj)


COMMAND_CATALOG = catalog.command(context_settings=CONTEXT_SETTINGS)


@COMMAND_CATALOG
@click.argument(
    "geom_file", type=click.Path(exists=True, dir_okay=False, resolve_path=True)
)
@click.option(
    "--start-date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=(datetime.today() - timedelta(days=7)).strftime("%Y-%m-%d"),
    help="Query period starting day, format '2020-01-01'.",
)
@click.option(
    "--end-date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=datetime.today().strftime("%Y-%m-%d"),
    help="Query period ending day, format '2020-01-01'.",
)
@click.option(
    "--sensors",
    type=click.Choice(
        [
            "pleiades",
            "spot",
            "sentinel1",
            "sentinel2",
            "sentinel3",
            "sentinel5p",
        ]
    ),
    multiple=True,
    default=[
        "pleiades",
        "spot",
        "sentinel1",
        "sentinel2",
        "sentinel3",
        "sentinel5p",
    ],
    help="Imagery sensors to search for.",
)
@click.option(
    "--max-cloud-cover",
    type=click.IntRange(0, 100),
    default=20,
    help="Maximum cloudcover percentage. 100 will return all scenes,"
    "8.4 will return all scenes with 8.4 or less cloudcover.",
)
@click.option(
    "--limit", type=int, default=1, help="The maximum number of search results."
)
@click.pass_obj
def construct_parameters(
    catalog, geom_file, start_date, end_date, sensors, limit, max_cloud_cover
):
    """
    Follows STAC principles and property names to create a filter for
    catalog search.
    """
    geometry = Tools(catalog.auth).read_vector_file(geom_file)
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    logger.info(
        pprint_json(
            catalog.construct_parameters(
                geometry, start_date_str, end_date_str, sensors, limit, max_cloud_cover
            )
        )
    )


@COMMAND_CATALOG
@click.argument("search_parameters_json", type=click.File("r"))
@click.pass_obj
def search(catalog, search_parameters_json):
    """
    Searches the catalog for the search parameters and returns the metadata of
    the matching scenes. Generate search parameters with
    'up42 catalog construct-parameters'.
    """
    logger.info(
        pprint_json(
            catalog.search(json.load(search_parameters_json), as_dataframe=False)
        )
    )
