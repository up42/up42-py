# Job

## Job object

{{ class_job }}

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
        members: {{ funcs_job }}
