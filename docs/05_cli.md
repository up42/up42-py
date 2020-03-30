# CLI

This is an overview of the included python based CLI (Command Line Interface).

```bash
up42 -h
```

## Authenticate
You can authenticate with a `PROJECT_ID` and `PROJECT_API_KEY`
```bash
up42 -PID [PROJECT_ID] -PAPIKEY [PROJECT_API_KEY] auth
```

Or using a `config.json` file:
```bash
up42 -CFG [path to config.json] auth
```

If you want to create a `config.json` file from a project key pair, you can use the
config command.

```bash
up42 -PID [PROJECT_ID] -PAPIKEY [PROJECT_API_KEY] config
```

You can persist with the authentication by saving either the
project key pair or path to the config file as an environment variable.

```bash
export UP42_PROJECT_ID=[PROJECT_ID]
export UP42_PROJECT_API_KEY=[PROJECT_API_KEY]
```

Or when using `config.json`.

```bash
export UP42_CFG_FILE=[path to config.json]
```

To save the authentication for future sessions make sure to append this variables
to your bash profile file:
```bash
# Linux
export UP42_CFG_FILE=[path to config.json] >> ~/.bashrc
# MacOS
export UP42_CFG_FILE=[path to config.json] >> ~/.bash_profile
```

## Workflows
```bash
up42 workflow -h
```

Create a new workflow:
```bash
up42 project create-workflow a_test
```

Or check which workflows already exist:
```bash
up42 project get-workflows
```

And get a workflow by its name:
```bash
up42 project workflow-from-name -name a_test
```

After running the command to persist the workflow you can get the workflow tasks:

```bash
up42 workflow get-workflow-tasks
```

You can also add workflow tasks to the workflow via a json file (see [typical usage](04_typical_usage.md) for an example):
```bash
up42 workflow add-workflow-tasks new_workflow_tasks.json
```

## Jobs
```bash
up42 job -h
```

Create a run a new job with parameters defined in a json file (see [typical usage](04_typical_usage.md) for an example):
```bash
up42 workflow create-and-run-job input_parameters.json --track
```

After running the command to persist the job you can download the quicklooks from
job in current working directory:
```bash
up42 job download-quicklooks .
```
Or download and unpack the results:
```bash
up42 job download-result .
```

You can also print out the logs of the job:
```bash
up42 job get-log
```

## Catalog
```bash
up42 catalog -h
```

With the catalog commands you can easily search the UP42 catalog for data. First,
create a parameter configuration:
```bash
up42 catalog construct-parameters example_aoi.geojson --sensors pleiades --max-cloud-cover 5
```

Then get the results:
```bash
up42 catalog search example_search_params.json
```

## General tools

Get all public blocks in the platform:
```bash
up42 get-blocks
```

Get block details by name:
```bash
up42 get-block-details -name oneatlas-pleiades-aoiclipped
```

Get all environments in the platform:
```bash
up42 get-environments
```
