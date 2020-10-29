# Job

## Job object

The Job object is the result of running a workflow. It lets you download, visualize and 
manipulate the results of the job, and keep track of the status or cancel a job while
still running.

Initialize an existing job:

```python
job = up42.initialize_job(job_id="12345")
```

Run a new job:
```python
job = workflow.run_job(name="new_job", input_parameters={...})
```

<br>

::: up42.job.Job
    rendering:
        show_root_toc_entry: False
    selection:
        inherited_members: True
        members: [  "info", "status", "download_results", "plot_results", "map_results", 
            "track_status", "cancel_job", "get_results_json", "get_logs", "download_quicklooks", 
            "plot_quicklooks", "upload_results_to_bucket", "get_jobtasks", "get_jobtasks_results_json"]
