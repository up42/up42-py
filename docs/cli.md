# :computer: Command Line Interface (CLI)

The CLI tool allows you to use the UP42 functionality from the command line. 
It is installed automatically with and based on the Python SDK. 

To check whether the tool is installed and functioning correctly, type the following on your
terminal or command line. This will print out a summary of the available commands.

```bash
up42 -h
```


To get help on a specific command, use:

```bash
up42 command -h
```

## Authenticate
You can authenticate with a `PROJECT_ID` and `PROJECT_API_KEY`
```bash
up42 -pid [PROJECT_ID] -pkey [PROJECT_API_KEY] auth
```

Or using a `config.json` file:
```bash
up42 -cfg [path to config.json] auth
```

You can make the authentication persistent by storing either the project key
pair or the path to the config file as an environment variable.

```bash
export UP42_PROJECT_ID=[PROJECT_ID]
export UP42_PROJECT_API_KEY=[PROJECT_API_KEY]
```

Or when using `config.json`.

```bash
export UP42_CFG_FILE=[path to config.json]
```

To save the authentication for future sessions make sure to append these variables
to your bash profile file:
```bash
# Linux
export UP42_CFG_FILE=[path to config.json] >> ~/.bashrc
# MacOS
export UP42_CFG_FILE=[path to config.json] >> ~/.bash_profile
```

If you want to create a `config.json` file from a project key pair, you can use the
config command.

```bash
up42 -pid [PROJECT_ID] -pkey [PROJECT_API_KEY] config
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

You can also add workflow tasks to the workflow via a json file (see [typical usage](detailed-example.md) for an example):
```bash
up42 workflow add-workflow-tasks new_workflow_tasks.json
```

## Jobs
```bash
up42 job -h
```

First create and run a new test job with parameters defined in a json file (see [typical usage](detailed-example.md) for an example):
```bash
up42 workflow test-job input_parameters.json --track
```

Then run the actual job with parameters:
```bash
up42 workflow run-job input_parameters.json --track
```

After running the command to persist the job you can download the quicklooks from
job in current working directory (note that not all data blocks support quicklooks):
```bash
up42 job download-quicklooks .
```
Or download and unpack the results:
```bash
up42 job download-results .
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