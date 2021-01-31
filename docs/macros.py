"""
Defined snippets and macros for repeated use in mkdocs.

Used primarily for the definition of class descriptions and class functionality (used in the class
chapters structure.md & and the code reference.

Use as {{ hello }} or {{ format_upper(list_of_strings)}}

To include markdown files:
{% include 'class_descriptions/project.md' %}

Changes in macro code require restart of mkdocs serve.
"""

from typing import List, Callable
import up42


def define_env(env):
    """
    This is the hook for defining variables, macros and filters.

    For more functionality see https://mkdocs-macros-plugin.readthedocs.io/en/latest/macros/

    Examples:
            # Use a variable/snippet, e.g. {{ name1 }}
            env.variables.name1 = "John Doe"

            # Use a Python function e.g. {{ calculation(x=5) }}
            @env.macro
            def calculation(x):
                    return (2.3 * x) + 7

            # Or to export some predefined function
            import math
            env.macro(math.floor) # will be exported as 'floor'
    """

    def get_class_funcs(
        c: Callable,
        exclude: List[str] = None,
        exclude_tools=True,
        exclude_viztools=False,
    ) -> List[str]:
        """
        Gets all class methods, excluding specifically excluded ones.

        Args:
                c: The class.
                exclude: Exclude specific methids.
                exclude_tools: Exclude inherited functions from Tools. Only relevant for up42 module.
        """
        funcs = dir(c)
        function_names = [
            f
            for f in funcs
            if not f.startswith("_")
            and not f.startswith("__")
            and not f[0].isupper()
            and not f.capitalize() in funcs
            and not f in ["jobcollection", "jobtask", "utils", "viztools", "estimation", "warnings", "logger", "get_logger"]
        ]
        if exclude_tools:
            function_names = [f for f in function_names if f not in dir(up42.Tools)]
        if exclude_viztools:
            function_names = [f for f in function_names if f not in dir(up42.VizTools)]
        return function_names

    @env.macro
    def format_funcs(functions: List[str]) -> str:
        """
        Formats a list of function names to a formatted list for the "Available Functionality" box
        in the structure chapter.
        """
        # Two tabs to stay within the tabbed code box.
        # Requires Python linebreak and markdown linebreak (two spaces)!
        # "\n\t\t• `abc`  \n\t\t• `cde`  \n\t\t• `cde`

        formatted = [f"\n\t\t&emsp; • `.{func}()`  " for func in functions]
        return "".join(formatted)

    # Variables

    # needs to fit the indention of the structure chapter box.
    env.variables.docstring_up42 = up42.__doc__.replace("\n", "\n\t")  # init module docstring
    env.variables.docstring_project = up42.Project.__doc__.replace("\n", "\n\t")
    env.variables.docstring_workflow = up42.Workflow.__doc__.replace("\n", "\n\t")
    env.variables.docstring_job = up42.Job.__doc__.replace("\n", "\n\t")
    env.variables.docstring_jobtask = up42.JobTask.__doc__.replace("\n", "\n\t")
    env.variables.docstring_jobcollection = up42.JobCollection.__doc__.replace(
        "\n", "\n\t"
    )
    env.variables.docstring_catalog = up42.Catalog.__doc__.replace("\n", "\n\t")
    env.variables.docstring_order = up42.Order.__doc__.replace("\n", "\n\t")
    env.variables.docstring_storage = up42.Storage.__doc__.replace("\n", "\n\t")
    env.variables.docstring_asset = up42.Asset.__doc__.replace("\n", "\n\t")

    env.variables.funcs_up42 = get_class_funcs(
        up42, exclude_tools=False, exclude_viztools=True
    )
    env.variables.funcs_project = get_class_funcs(up42.Project)
    env.variables.funcs_workflow = get_class_funcs(up42.Workflow)
    env.variables.funcs_job = get_class_funcs(up42.Job)
    env.variables.funcs_jobtask = get_class_funcs(up42.JobTask)
    env.variables.funcs_jobcollection = get_class_funcs(up42.JobCollection)
    env.variables.funcs_catalog = get_class_funcs(up42.Catalog)
    env.variables.funcs_order = get_class_funcs(up42.Order)
    env.variables.funcs_storage = get_class_funcs(up42.Storage)
    env.variables.funcs_asset = get_class_funcs(up42.Asset)
