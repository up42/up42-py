# JobCollection

## JobCollection object

The JobCollection object provides facilities for downloading and merging
multiple jobs results.

Initialize a collection of existing jobs:

```python
jobcollection = up42.initialize_jobcollection(job_ids=["12345", "6789"])
```

You also get a jobcollection as the result of e.g. running multiple jobs in parallel:
```python
jobcollection = workflow.run_jobs_parallel()
```

::: up42.jobcollection.JobCollection
    rendering:
        show_root_toc_entry: False
    selection:
        inherited_members: True
        members: ["info", "status", "download_results", "apply", "plot_results", 
            "map_results"]
