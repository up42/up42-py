import os
from pathlib import Path
from typing import Tuple, List
import math

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import rasterio
import shapely
from IPython import get_ipython
from IPython.display import display
from geojson import FeatureCollection
from rasterio.plot import show

from .utils import get_logger, folium_base_map, DrawFoliumOverride, is_notebook

logger = get_logger(__name__)  # level=logging.CRITICAL  #INFO


# pylint: disable=no-member
class Tools:
    def __init__(self,):
        """
        The tools class contains class independent functionality for e.g. aoi handling etc.
        They can be accessed from every object.

        Public methods:
            read_vector_file, get_example_aoi, draw_aoi, plot_coverage, plot_quicklook
        """

    # pylint: disable=no-self-use
    def read_vector_file(
        self, filename: str = "aoi.geojson", as_dataframe: bool = False
    ) -> FeatureCollection:
        """
        Reads vector files (geojson, shapefile, kml, wkt) to a feature collection,
        for use as the aoi geometry in the workflow input parameters
        (see get_input_parameters).

        Example aoi fiels are provided, e.g. example/data/aoi_Berlin.geojson

        Args:
            filename: File path of the vector file.
            as_dataframe: Return type, default FeatureCollection, GeoDataFrame if True.

        Returns:
            Feature Collection
        """
        suffix = Path(filename).suffix

        if suffix == ".kml":
            gpd.io.file.fiona.drvsupport.supported_drivers["KML"] = "rw"
            df = gpd.read_file(filename, driver="KML")
        elif suffix == ".wkt":
            with open(filename) as wkt_file:
                wkt = wkt_file.read()
                df = pd.DataFrame({"geometry": [wkt]})
                df["geometry"] = df["geometry"].apply(shapely.wkt.loads)
                df = gpd.GeoDataFrame(df, geometry="geometry", crs=4326)
        else:
            df = gpd.read_file(filename)

        if df.crs != "epsg:4326":
            df = df.to_crs(epsg=4326)
        df.geometry = df.geometry.buffer(0)
        # TODO: Explode multipolygons (if neccessary as union in aoi anyway most often).

        # TODO: Have both bboxes for each feature and overall?

        if as_dataframe:
            return df
        else:
            return df.__geo_interface__

    def read_vector(self):
        pass

    def get_example_aoi(
        self, location: str = "Berlin", as_dataframe: bool = False
    ) -> FeatureCollection:
        """
        Gets predefined, small, rectangular example aoi for the selected location.

        Args:
            location: Location, one of Berlin, Washingtion.
            as_dataframe:

        Returns:
            Feature collection json with the selected aoi.
        """
        # TODO: Add more geometries.
        logger.info("Getting small example aoi in %s.", location)
        if location == "Berlin":
            example_aoi = self.read_vector_file(
                f"{os.path.dirname(__file__)}/data/aoi_berlin.geojson"
            )
        elif location == "Washington":
            # TODO
            pass
        elif location == "Tokyo":
            pass
        else:
            raise ValueError("Please select one of 'Berlin', 'Washington' or 'Tokyo'!")

        if as_dataframe:
            df = gpd.GeoDataFrame.from_features(example_aoi, crs=4326)
            return df
        else:
            return example_aoi

    @staticmethod
    def draw_aoi() -> None:
        """
        Opens a interactive map to draw an aoi by hand, export via the export button.
        Then read in via read_aoi_file().

        Currently no way to get the drawn geometry via a callback in Python, as not
        supported by folium.
        And ipyleaflet misses raster vizualization & folium plugins functionality.
        """
        m = folium_base_map(layer_control=True)
        DrawFoliumOverride(
            export=True,
            filename="aoi.geojson",
            position="topleft",
            draw_options={
                "rectangle": {"repeatMode": False, "showArea": True},
                "polygon": {"showArea": True, "allowIntersection": False},
                "polyline": False,
                "circle": False,
                "marker": False,
                "circlemarker": False,
            },
            edit_options={"polygon": {"allowIntersection": False}},
        ).add_to(m)
        display(m)

    @staticmethod
    def plot_coverage(
        scenes: gpd.GeoDataFrame,
        aoi: gpd.GeoDataFrame = None,
        legend_column: str = None,
        figsize=(12, 16),
    ) -> None:
        """
        Plots a coverage map of a dataframe with geometries e.g. the result of catalog.search())
        Args:
            scenes: GeoDataFrame of scenes, result of catalog.search()
            aoi: GeoDataFrame of aoi.
            legend_column: Dataframe column set to legend, e.g. "scene_id".
                If None is provided, no legend is plotted.
            figsize: Matplotlib figure size.
        """
        if is_notebook():
            get_ipython().run_line_magic("matplotlib", "inline")

        ax = scenes.plot(
            legend_column,
            categorical=True,
            figsize=figsize,
            cmap="Set3",
            legend=True,
            alpha=0.7,
            legend_kwds=dict(loc="upper left", bbox_to_anchor=(1, 1)),
        )
        if aoi is not None:
            aoi.plot(color="r", ax=ax, fc="None", edgecolor="r", lw=1)
            # TODO: Add aoi to legend.
            # from matplotlib.patches import Patch
            # patch = Patch(label="aoi", facecolor='None', edgecolor='r')
            # ax.legend(handles=handles, labels=labels)
            # TODO: Overlay quicklooks on geometry.
        ax.set_axis_off()
        plt.show()

    def plot_quicklook(
        self, figsize: Tuple[int, int] = (8, 8), filepaths: List = None
    ) -> None:
        """
        Plots the downloaded quicklooks (filepaths saved to self.quicklooks of the
        respective object, e.g. job, catalog).

        Args:
            figsize: matplotlib figure size.
        """
        if filepaths is None:
            if not hasattr(self, "quicklook") or self.quicklook is None:
                raise ValueError(
                    "You first need to download the quicklooks via .download_quicklook()."
                )
            filepaths = self.quicklook  # pylint: disable=no-member
        if is_notebook():
            get_ipython().run_line_magic("matplotlib", "inline")
        else:
            raise ValueError("Only works in Jupyter notebook.")

        if len(filepaths) < 2:
            nrows, ncols = 1, 1
        else:
            ncols = 2
            nrows = int(math.ceil(len(filepaths) / float(ncols)))

        fig, axs = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize)
        if len(filepaths) > 1:
            axs = axs.ravel()
        else:
            axs = [axs]
        for idx, fp in enumerate(filepaths):
            with rasterio.open(fp) as src:
                show(
                    src.read(),
                    transform=src.transform,
                    title=Path(fp).stem,
                    ax=axs[idx],
                )
        plt.tight_layout()
        plt.show()

    def plot_result(
        self,
        figsize: Tuple[int, int] = (8, 8),
        filepaths: List[str] = None,
        titles: List[str] = None,
    ) -> None:
        """
        Plots the downloaded data.

        Args:
            figsize: matplotlib figure size.
            filepaths: Paths to images to plot. Optional, by default picks up the downloaded results.
        """
        # TODO: Add other fileformats.
        # TODO: Handle more bands.
        # TODO: add histogram equalization? But requires skimage dependency.
        if filepaths is None:
            if (
                not hasattr(self, "result") or self.result is None
            ):  # pylint: disable=no-member
                raise ValueError("You first need to download the results.")
            filepaths = self.result  # pylint: disable=no-member
        if not titles:
            titles = [Path(fp).stem for fp in filepaths]

        if is_notebook():
            get_ipython().run_line_magic("matplotlib", "inline")
        else:
            raise ValueError("Only works in Jupyter notebook.")

        if len(filepaths) < 2:
            nrows, ncols = 1, 1
        else:
            ncols = 3
            nrows = int(math.ceil(len(filepaths) / float(ncols)))

        fig, axs = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize)
        if len(filepaths) > 1:
            axs = axs.ravel()
        else:
            axs = [axs]
        for idx, (fp, title) in enumerate(zip(filepaths, titles)):
            with rasterio.open(fp) as src:
                img_array = src.read()
                show(
                    img_array, transform=src.transform, title=title, ax=axs[idx],
                )
            axs[idx].set_axis_off()
        plt.tight_layout()
        plt.show()
