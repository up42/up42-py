"""
Defined snippets and macros for repeated use in mkdocs.

Used primarily for the definition of class descriptions and class functionality (used in the class
chapters structure.md & and the code reference.
"""


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
	env.variables.classes_up42 = "up42 is the base object imported to Python. It provides the " \
	                             "elementary functionality that is not bound to a specific object " \
	                             "of the UP42 structure (Project > Workflow > Job etc.). From it you " \
	                             "can initialize existing objects, get information about UP42 data & " \
	                             "processing blocks, read or draw vector data, and adjust the SDK settings."

	env.variables.functions_job = ["info", "status", "download_results",
	                               "plot_results", "map_results",
	                               "track_status", "cancel_job", "get_results_json",
	                               "get_logs", "download_quicklooks",
	                               "plot_quicklooks", "upload_results_to_bucket",
	                               "get_jobtasks", "get_jobtasks_results_json"]
