"""
Define snippets and macros for repeated use via mkdocs-macros plugin.

Include variables and macros like regular Python expressions, wrapped in double curly brackets:
{{ some_variable }} or {{ calculation(x=5) }}

Include external markdown files:
{% include 'some_folder/some_md_file.md' %}

Changes in macros.py code, for some operations, requires restart of `mkdocs serve`.

Docs: https://mkdocs-macros-plugin.readthedocs.io/en/latest/macros/
"""

from typing import List, Callable
import up42


def define_env(env):
    """
    This is the hook for defining variables, macros and filters.
    """

    def indent(input_string: str):
        return input_string.replace("\n", "\n\t")

    def get_methods(
        c: Callable,
        exclude: List[str] = None,
        exclude_viztools=False,
    ) -> List[str]:
        """
        Gets all class methods and properties, excluding specifically excluded ones.

        Args:
                c: The class object.
                exclude: Exclude specific methods.
                exclude_viztools: Exclude inherited functions from VizTools.
        """
        property_methods = [
            name for name, value in vars(c).items() if isinstance(value, property)
        ]
        function_methods = [
            name
            for name in dir(c)
            if callable(getattr(c, name))
            and not name.startswith("_")
            and not name.startswith("__")
            and not name[0].isupper()
        ]

        # TODO: Could also return separatly for separated formatting.
        function_methods = function_methods + property_methods

        if exclude_viztools:
            function_methods = [
                f for f in function_methods if f not in dir(up42.viztools.VizTools)
            ]
        if exclude:
            function_methods = [f for f in function_methods if f not in exclude]

        return function_methods

    # pylint: disable=unused-variable
    @env.macro
    def format_funcs(function_methods: List[str]) -> str:
        """
        Formats a list of function names to a formatted list for
        the "Available Functionality" box in the structure chapter.
        """
        # Two tabs to stay within the tabbed code box.
        # Requires Python linebreak and markdown linebreak (two spaces)!
        # "\n\t\t• `abc`  \n\t\t• `cde`  \n\t\t• `cde`

        formatted = [f"\n\t\t&emsp; • `.{func}()`  " for func in function_methods]
        return "".join(formatted)

    # Class docstrings variables for use in the structure chapter.
    # (In code reference added automatically by mkdocstrings).
    # Every class requires a docstring, otherwise mkdocs fails!
    env.variables.docstring_up42 = indent(up42.__doc__)  # init module docstring
    env.variables.docstring_project = indent(up42.project.Project.__doc__)
    env.variables.docstring_workflow = indent(up42.workflow.Workflow.__doc__)
    env.variables.docstring_job = indent(up42.job.Job.__doc__)
    env.variables.docstring_jobtask = indent(up42.jobtask.JobTask.__doc__)
    env.variables.docstring_jobcollection = indent(
        up42.jobcollection.JobCollection.__doc__
    )
    env.variables.docstring_catalog = indent(up42.catalog.Catalog.__doc__)
    env.variables.docstring_tasking = indent(up42.tasking.Tasking.__doc__)
    env.variables.docstring_order = indent(up42.order.Order.__doc__)
    env.variables.docstring_storage = indent(up42.storage.Storage.__doc__)
    env.variables.docstring_asset = indent(up42.asset.Asset.__doc__)
    env.variables.docstring_webhooks = indent(up42.webhooks.Webhooks.__doc__)

    # Class functions for reference and structure chapter
    env.variables.funcs_up42 = get_methods(up42, exclude_viztools=True)
    env.variables.funcs_project = get_methods(up42.project.Project)
    env.variables.funcs_workflow = get_methods(up42.workflow.Workflow)
    env.variables.funcs_job = get_methods(up42.job.Job, exclude=["plot_coverage"])
    env.variables.funcs_jobtask = get_methods(
        up42.jobtask.JobTask, exclude=["map_quicklooks", "plot_coverage"]
    )
    env.variables.funcs_jobcollection = get_methods(
        up42.jobcollection.JobCollection,
        exclude=[
            "plot_quicklooks",
            "map_quicklooks",
            "plot_coverage",
        ],
    )
    env.variables.funcs_catalog = get_methods(
        up42.catalog.Catalog, exclude=["plot_results", "map_results"]
    )
    env.variables.funcs_tasking = get_methods(up42.tasking.Tasking)
    env.variables.funcs_order = get_methods(up42.order.Order)
    env.variables.funcs_storage = get_methods(up42.storage.Storage)
    env.variables.funcs_asset = get_methods(up42.asset.Asset)
    env.variables.funcs_webhooks = get_methods(up42.webhooks.Webhooks)
    env.variables.funcs_webhook = get_methods(up42.webhooks.Webhook)
