# Workflow

The workflow class enables you to configure, run, and query jobs related to a workflow.

To create a new workflow, use the following:

```python
workflow = project.create_workflow(name="new_workflow")
```

To use an existing workflow, use the following:

```python
workflow = up42.initialize_workflow(workflow_id="7fb2ec8a-45be-41ad-a50f-98ba6b528b98")
```

## Projects

### max_concurrent_jobs

## Workflows

### info
### update_name()
### delete()
### get_parameters_info()
### construct_parameters()
### construct_parameters_parallel()
### get_compatible_blocks()

## Jobs

### estimate_job()
### get_jobs()
### test_job()
### test_jobs_parallel()
### run_job()
### run_jobs_parallel()


## JobTask

### workflow_tasks
### get workflow_tasks()
### add_workflow_tasks()


::: up42.workflow.Workflow
