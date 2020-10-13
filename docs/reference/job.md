# Job

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