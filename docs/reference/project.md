# Project

The Project is the top level object of the UP42 hierachy. With it you can create 
new workflows, query already existing workflows & jobs in the project and 
manage the project settings.

To initialize an existing project, first [authenticate](authentication.md#authenticate)
with UP42, then use:

```python
project = up42.initialize_project()
```

To create a new project use the [UP42 website interface](authentication.md#authenticate). 
This functionality will soon also be available via the UP42 API & Python SDK.

<br>

::: up42.project.Project
