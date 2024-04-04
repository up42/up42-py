"""
Visualization tools available in various objects
"""

# pylint: disable=dangerous-default-value

import math
import warnings
from functools import wraps
from pathlib import Path
from typing import List, Optional, Tuple, Union
from warnings import warn

import geopandas as gpd
from geopandas import GeoDataFrame

try:
    import folium
    import matplotlib.pyplot as plt
    import rasterio
    from folium.plugins import Draw
    from rasterio.plot import show
except ImportError:
    _viz_installed = False
else:
    _viz_installed = True


from up42.utils import get_logger

# Folium map styling constants
VECTOR_STYLE = {
    "fillColor": "#5288c4",
    "color": "blue",
    "weight": 2.5,
    "dashArray": "5, 5",
}

HIGHLIGHT_STYLE = {
    "fillColor": "#ffaf00",
    "color": "red",
    "weight": 3.5,
    "dashArray": "5, 5",
}

try:
    from IPython import get_ipython

    get_ipython().run_line_magic("matplotlib", "inline")
except (ImportError, AttributeError):
    # No Ipython installed, Installed but run in shell
    pass

logger = get_logger(__name__)


def requires_viz(func):
    # @wraps line required for mkdocstrings to be able to pick up decorated functions see
    # https://mkdocstrings.github.io/troubleshooting/#my-wrapped-function-shows-documentationcode-for-its-wrapper-
    # instead-of-its-own
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        if not _viz_installed:
            raise ImportError(
                "Some dependencies for the optional up42-py visualizations are missing. "
                "You can install them via `install up42py[viz]`."
            )
        return func(*args, **kwargs)

    return wrapper_func


class VizTools:
    def __init__(self):
        """
        Visualization functionality
        """
        self.quicklooks = None
        self.results: Union[list, dict, None] = None

    @requires_viz
    def plot_results(
        self,
        figsize: Tuple[int, int] = (14, 8),
        bands: Optional[List[int]] = None,
        titles: Optional[List[str]] = None,
        filepaths: Union[List[Union[str, Path]], dict, None] = None,
        plot_file_format: List[str] = [".tif"],
        **kwargs,
    ) -> None:
        # pylint: disable=line-too-long
        """
        Plots image data (quicklooks or results)

        Requires installation of up42-py[viz] extra dependencies.

        Args:
            figsize: matplotlib figure size.
            bands: Image bands and order to plot, e.g. [1,2,3]. First band is 1.
            titles: Optional list of titles for the subplots.
            filepaths: Paths to images to plot. Optional, by default picks up the last
                downloaded results.
            plot_file_format: List of accepted image file formats e.g. [".tif"]
            kwargs: Accepts any additional args and kwargs of
                [rasterio.plot.show](https://rasterio.readthedocs.io/en/latest/api/rasterio.plot.html#rasterio.plot.show),
                 e.g. matplotlib cmap etc.
        """
        warnings.filterwarnings("ignore", category=rasterio.errors.NotGeoreferencedWarning)
        warn(
            "Visualization methods are deprecated. The current feature will be discontinued after March 31, 2024.",
            DeprecationWarning,
            stacklevel=2,
        )

        if filepaths is None:
            if self.results is None:
                raise ValueError("You first need to download the results!")
            filepaths = self.results
            # Unpack results path dict in case of jobcollection.
            if isinstance(filepaths, dict):
                filepaths_lists = list(filepaths.values())
                filepaths = [item for sublist in filepaths_lists for item in sublist]

        if not isinstance(filepaths, list):
            filepaths = [filepaths]  # type: ignore
        filepaths = [Path(path) for path in filepaths]

        imagepaths = [path for path in filepaths if str(path.suffix) in plot_file_format]  # type: ignore
        if not imagepaths:
            raise ValueError(f"This function only plots files of format {plot_file_format}.")

        if not titles:
            titles = [Path(fp).stem for fp in imagepaths]
        if not isinstance(titles, list):
            titles = [titles]  # type: ignore

        if len(imagepaths) < 2:
            nrows, ncols = 1, 1
        else:
            ncols = 3
            nrows = int(math.ceil(len(imagepaths) / float(ncols)))

        _, axs = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize)
        if len(imagepaths) > 1:
            axs = axs.ravel()
        else:
            axs = [axs]

        if bands is None:
            with rasterio.open(imagepaths[0]) as src:
                if src.count == 1:
                    bands = [1]
                else:
                    bands = [1, 2, 3]
        if len(bands) == 1:
            kwargs["cmap"] = "gray"
        if len(bands) not in [1, 3]:
            raise ValueError("Parameter bands can only contain one or three bands.")

        for idx, (fp, title) in enumerate(zip(imagepaths, titles)):
            with rasterio.open(fp) as src:
                img_array = src.read(bands)
                show(
                    img_array,
                    transform=src.transform,
                    title=title,
                    ax=axs[idx],
                    aspect="auto",
                    **kwargs,
                )
            axs[idx].set_axis_off()
        plt.axis("off")
        plt.tight_layout()
        plt.show()

    @requires_viz
    def map_results(
        self,
        bands: Optional[List[int]] = None,
        aoi: Optional[GeoDataFrame] = None,
        show_images: bool = True,
        show_features: bool = True,
        name_column: str = "uid",
        save_html: Path = None,
    ) -> "folium.Map":
        """
        Displays data.json, and if available, one or multiple results GeoTIFFs.

        Requires installation of up42-py[viz] extra dependencies.

        Args:
            bands: Image bands and order to plot, e.g. [1,2,3]. First band is 1.
            aoi: Optional visualization of AOI boundaries when given GeoDataFrame of AOI.
            show_images: Shows images if True (default).
            show_features: Shows features if True (default).
            name_column: Name of the feature property that provides the Feature/Layer name.
            save_html: The path for saving folium map as html file. With default None, no file is saved.
        """
        warn(
            "Visualization methods are deprecated. The current feature will be discontinued after March 31, 2024.",
            DeprecationWarning,
            stacklevel=2,
        )
        if self.results is None:
            raise ValueError("You first need to download the results via job.download_results()!")

        f_paths = []
        if isinstance(self.results, list):
            # Add features to map.
            # Some blocks store vector results in an additional GeoJSON file.
            # pylint: disable=not-an-iterable
            json_fp = [fp for fp in self.results if fp.endswith(".geojson")]
            if json_fp:
                json_fp = json_fp[0]  # why only one element is selected?
            else:
                # pylint: disable=not-an-iterable
                json_fp = [fp for fp in self.results if fp.endswith(".json")][0]
            f_paths = self.results

        elif isinstance(self.results, dict):
            # pylint: disable=unsubscriptable-object
            json_fp = self.results["merged_result"][0]

            f_paths = []
            for k, v in self.results.items():
                if k != "merged_result":
                    f_paths.append([i for i in v if i.endswith(".tif")][0])

        df: GeoDataFrame = gpd.read_file(json_fp)

        # Add image to map.
        m = self._map_images(
            bands=bands,
            plot_file_format=[".tif"],
            result_df=df,
            filepaths=f_paths,
            aoi=aoi,
            show_images=show_images,
            show_features=show_features,
            name_column=name_column,
            save_html=save_html,
        )

        return m

    class DrawFoliumOverride(Draw):
        def render(self, **kwargs):
            # pylint: disable=import-outside-toplevel
            from branca.element import CssLink, Element, Figure, JavascriptLink

            super().render(**kwargs)

            figure = self.get_root()
            assert isinstance(figure, Figure), "You cannot render this Element if it is not in a Figure."

            figure.header.add_child(
                JavascriptLink("https://cdnjs.cloudflare.com/ajax/libs/leaflet.draw/1.0.2/leaflet.draw.js")
            )  # noqa
            figure.header.add_child(
                CssLink("https://cdnjs.cloudflare.com/ajax/libs/leaflet.draw/1.0.2/leaflet.draw.css")
            )  # noqa

            export_style = """
                <style>
                    #export {
                        position: absolute;
                        top: 270px;
                        left: 11px;
                        z-index: 999;
                        padding: 6px;
                        border-radius: 3px;
                        box-sizing: border-box;
                        color: #333;
                        background-color: #fff;
                        border: 2px solid rgba(0,0,0,0.5);
                        box-shadow: None;
                        font-family: 'Helvetica Neue';
                        cursor: pointer;
                        font-size: 17px;
                        text-decoration: none;
                        text-align: center;
                        font-weight: bold;
                    }
                </style>
            """
            export_button = """<a href='#' id='export'>Export as<br/>GeoJson</a>"""
            if self.export:
                figure.header.add_child(Element(export_style), name="export")
                figure.html.add_child(Element(export_button), name="export_button")
