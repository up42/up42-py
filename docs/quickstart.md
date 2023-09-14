# Quickstart

Learn your way around the UP42 Python SDK.

## Get started

Before you can access UP42's geospatial collections and processing workflows via Python, you need to use the [console](https://console.up42.com/) to set up your UP42 account and workspace.

### Step 1. Set up an UP42 account

1. [Create an account](https://docs.up42.com/getting-started/registration)
2. [Upgrade to Professional](https://docs.up42.com/getting-started/account/plans#upgrade-to-professional)

### Step 2. Add users

1. [Invite users](https://docs.up42.com/getting-started/account/users)
2. [Navigate workspaces](https://docs.up42.com/getting-started/account/workspaces)

### Step 3. Buy UP42 credits

[Purchase credits](https://docs.up42.com/getting-started/credits/purchase)

### Step 4. Install the SDK

1. [Install](/up42-py/installation)
2. [Authenticate](/up42-py/authentication)

## Get data

### Step 1. Choose a data source

| Tasking                                                                                                                                                                                                                      | Catalog                                                                                                                                                                    |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. [Choose a tasking collection](/up42-py/examples/tasking/tasking-example/#step-1-choose-a-tasking-collection)<br/>2. [Request access to restricted data](/up42-py/examples/tasking/tasking-example/#step-2-request-access) | 1. [Choose a catalog collection](/up42-py/catalog/#step-1-choose-a-catalog-collection)<br/>2. [Request access to restricted data](/up42-py/catalog/#step-2-request-access) |

### Step 2. Create an order

| Tasking                                                                                                        | Catalog                                                                                                                                              |
| -------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Create a tasking order](/up42-py/examples/tasking/tasking-example/#step-4-get-a-json-schema-of-an-order-form) | 1.[Search the catalog](/up42-py/catalog/#step-4-search-the-catalog)<br/>2. [Create a catalog order](/up42-py/catalog/#step-5-fill-out-an-order-form) |

### Step 3. Download data

[Download assets](/up42-py/storage/)

## Apply analytics

### Step 1. Create a project and a workflow

1. [Create a project](/up42-py/reference/project-reference/)
2. [Create a workflow](/up42-py/analytics/#step-1-create-and-populate-a-workflow)

### Step 2. Choose a data source

| Option 1                                                     | Option 2                                                                                                                                                                                     |
| ------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Use a storage asset](/up42-py/reference/storage-reference/) | 1.[Choose a data block](https://docs.up42.com/processing-platform/blocks/data)<br/>2. [Request access to restricted data](https://docs.up42.com/getting-started/restrictions#request-access) |

### Step 3. Choose processing algorithms

| Option 1                                                                      | Option 2                                                                                                                                                                                                                                     |
| ----------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Use a custom block](https://docs.up42.com/processing-platform/custom-blocks) | 1. [Choose processing blocks](/up42-py/reference/workflow-reference/#up42.workflow.Workflow.get_compatible_blocks)<br/>2. [Request access to restricted data](https://docs.up42.com/getting-started/restrictions#data-and-processing-blocks) |

### Step 4. Download data

[Run a job and download outputs](/up42-py/analytics/#step-7-run-a-job)
