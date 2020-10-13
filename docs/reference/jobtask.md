# JobTask

The JobTask object provides access to a specific intermediate result of a block in the 
workflow. Each job contains one or multiple JobTasks, one for each block.

Initialize an existing jobtask:

```python
jobtask = up42.initialize_jobtask(jobtask_id="12345", job_id="12345")
```

<br>

::: up42.jobtask.JobTask
