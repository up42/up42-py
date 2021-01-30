"""
Defined snippets and macros for repeated use in mkdocs.

Used primarily for the definition of class descriptions and class functionality (used in the class
chapters structure.md & and the code reference.

Use as {{ hello }} or {{ format_functions(func_project)}}
"""

from typing import List, Callable
import up42


def define_env(env):
    """
    This is the hook for defining variables, macros and filters.

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

            # Plot inline:
    # Inspired by https://github.com/fralau/mkdocs_macros_plugin/issues/37#issuecomment-636555341
    ...
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    html_string = f"<img alt='{alt_text}' width='{width}' height='{height}' src='data:image/png;base64,{data}'/>"
    return html_string

            For more functionality see https://mkdocs-macros-plugin.readthedocs.io/en/latest/macros/
    """

    def get_class_funcs(
        c: Callable, exclude: List[str] = None, exclude_tools=True
    ) -> List[str]:
        """
        Gets all class methods, excluding specifically excluded ones.

        Args:
                c: The class.
                exclude: Exclude specific methids.
                exclude_tools: Exclude inherited functions from Tools. Only relevant for up42 module.
        """
        function_names = [
            func
            for func in dir(c)
            if callable(getattr(c, func))
            and not func.startswith("_")
            and not func.startswith("__")
            and not func[0].isupper()
        ]
        if exclude_tools:
            function_names = [
                func for func in function_names if func not in dir(up42.Tools)
            ]
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

    env.variables.class_up42 = """up42 is the base object imported to Python. It provides the 
	                             elementary functionality that is not bound to a specific object 
	                             of the UP42 structure (Project > Workflow > Job etc.). From it you 
	                             can initialize existing objects, get information about UP42 data & 
	                             processing blocks, read or draw vector data, and adjust the SDK settings."""
    env.variables.funcs_up42 = get_class_funcs(up42, exclude_tools=False)

    env.variables.class_project = """The Project is the top level object of the UP42 hierarchy. With it you 
	                              can create new workflows, query already existing workflows & jobs in the 
	                              project and manage the project settings."""
    env.variables.funcs_project = get_class_funcs(up42.Project)

    env.variables.class_workflow = """The Workflow object lets you configure & run jobs and query exisiting jobs related
				to this workflow."""
    env.variables.funcs_workflow = get_class_funcs(up42.Workflow)

    env.variables.class_job = """The Job class is the result of running a workflow. It lets you download, visualize and 
					manipulate the results of the job, and keep track of the status or cancel a job while
					still running."""
    env.variables.funcs_job = get_class_funcs(up42.Job)
