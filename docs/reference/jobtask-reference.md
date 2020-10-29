# JobTask

## Jobtask object

The JobTask object provides access to a specific intermediate result of a block in the 
workflow. Each job contains one or multiple JobTasks, one for each block.

Initialize an existing jobtask:

```python
jobtask = up42.initialize_jobtask(jobtask_id="12345", job_id="12345")
```

<br>

::: up42.jobtask.JobTask
    rendering:
        show_root_toc_entry: False
    selection:
        inherited_members: True
        members: ["info", "get_results_json", "download_results", "plot_results", 
            "map_results", "download_quicklooks", "plot_quicklooks"]
