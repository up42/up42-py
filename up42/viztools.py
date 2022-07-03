"""
Visualization tools available in various objects
"""

# pylint: disable=dangerous-default-value

from typing import Tuple, List, Union, Optional
import math
from pathlib import Path
import warnings

import numpy as np
from shapely.geometry import box
import geopandas as gpd
from geopandas import GeoDataFrame

try:
    import rasterio
    from rasterio.plot import show
    from rasterio.vrt import WarpedVRT
    import folium
    from folium.plugins import Draw
    import matplotlib.pyplot as plt
except ImportError:
    _viz_installed = False
else:
    _viz_installed = True


from up42.utils import (
    get_logger,
)

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
    def wrapper_func(*args, **kwargs):
        if not _viz_installed:
            raise ImportError(
                "Some dependencies for the optional up42-py visualizations are missing. "
                "You can install them via `install up42py[viz]`."
            )
        return func(*args, **kwargs)

    return wrapper_func


# pylint: disable=no-member, duplicate-code
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
        bands: List[int] = [1, 2, 3],
        titles: Optional[List[str]] = None,
        filepaths: Union[List[Union[str, Path]], dict, None] = None,
        plot_file_format: List[str] = [".tif"],
        **kwargs,
    ) -> None:
        # pylint: disable=line-too-long
        """
        Plots image data (quicklooks or results)

        Args:
            figsize: matplotlib figure size.
            bands: Image bands and order to plot, default [1,2,3]. First band is 1.
            titles: Optional list of titles for the subplots.
            filepaths: Paths to images to plot. Optional, by default picks up the last
                downloaded results.
            plot_file_format: List of accepted image file formats e.g. [".tif"]
            kwargs: Accepts any additional args and kwargs of
                [rasterio.plot.show](https://rasterio.readthedocs.io/en/latest/api/rasterio.plot.html#rasterio.plot.show),
                 e.g. matplotlib cmap etc.
        """
        warnings.filterwarnings(
            "ignore", category=rasterio.errors.NotGeoreferencedWarning
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

        imagepaths = [
            path for path in filepaths if str(path.suffix) in plot_file_format  # type: ignore
        ]
        if not imagepaths:
            raise ValueError(
                f"This function only plots files of format {plot_file_format}."
            )

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

        if len(bands) != 3:
            if len(bands) == 1:
                if "cmap" not in kwargs:
                    kwargs["cmap"] = "gray"
            else:
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
    def plot_quicklooks(
        self,
        figsize: Tuple[int, int] = (8, 8),
        titles: Optional[List[str]] = None,
        filepaths: Optional[list] = None,
    ) -> None:
        """
        Plots the downloaded quicklooks (filepaths saved to self.quicklooks of the
        respective object, e.g. job, catalog).

        Args:
                figsize: matplotlib figure size.
                filepaths: Paths to images to plot. Optional, by default picks up the last
                        downloaded results.
                titles: List of titles for the subplots, optional.

        """
        if filepaths is None:
            if self.quicklooks is None:
                raise ValueError("You first need to download the quicklooks!")
            filepaths = self.quicklooks

        self.plot_results(
            plot_file_format=[".jpg", ".jpeg", ".png"],
            figsize=figsize,
            filepaths=filepaths,
            titles=titles,
        )

    @staticmethod
    def _map_images(
        plot_file_format: List[str],
        result_df: GeoDataFrame,
        filepaths: List[Union[str, Path]],
        bands: List[int] = [1, 2, 3],
        aoi: Optional[GeoDataFrame] = None,
        show_images=True,
        show_features=False,
        name_column: str = "id",
        save_html: Optional[Path] = None,
    ) -> "folium.Map":
        """
        Displays data.json, and if available, one or multiple results geotiffs.
        Args:
            plot_file_format: List of accepted image file formats e.g. [".png"]
            result_df: GeoDataFrame with scene geometries.
            aoi: GeoDataFrame of aoi.
            filepaths: Paths to images to plot. Optional, by default picks up the last
                downloaded results.
            show_images: Shows images if True (default).
            show_features: Show features if True. For quicklooks maps is set to False.
            name_column: Name of the feature property that provides the Feature/Layer name.
            save_html: The path for saving folium map as html file. With default None, no file is saved.
        """
        warnings.filterwarnings(
            "ignore", category=rasterio.errors.NotGeoreferencedWarning
        )

        if result_df.shape[0] > 100:
            result_df = result_df.iloc[:100]
            logger.info(
                "Only the first 100 results will be displayed to avoid memory "
                "issues."
            )

        centroid = box(*result_df.total_bounds).centroid
        m = folium_base_map(
            lat=centroid.y,
            lon=centroid.x,
        )

        df_bounds = result_df.bounds
        list_bounds = df_bounds.values.tolist()
        raster_filepaths = [
            path for path in filepaths if Path(path).suffix in plot_file_format
        ]

        try:
            feature_names = result_df[name_column].to_list()
        except KeyError:
            feature_names = [""] * len(result_df.index)

        if aoi is not None:
            aoi_style = VECTOR_STYLE.copy()
            aoi_style["color"] = "red"
            folium.GeoJson(
                aoi,
                name="aoi",
                style_function=lambda x: aoi_style,
                highlight_function=lambda x: HIGHLIGHT_STYLE,
            ).add_to(m)

        if show_features:
            for idx, row in result_df.iterrows():  # type: ignore
                try:
                    feature_name = row.loc[name_column]
                except KeyError:
                    feature_name = ""
                layer_name = f"Feature {idx + 1} - {feature_name}"
                f = folium.GeoJson(
                    row["geometry"],
                    name=layer_name,
                    style_function=lambda x: VECTOR_STYLE,
                    highlight_function=lambda x: HIGHLIGHT_STYLE,
                )
                folium.Popup(
                    f"{layer_name}: {row.drop('geometry', axis=0).to_json()}"
                ).add_to(f)
                f.add_to(m)

        if show_images and raster_filepaths:
            if len(bands) != 3:
                if len(bands) == 1:
                    bands = bands * 3  # plot as grayband
                else:
                    raise ValueError(
                        "Parameter bands can only contain one or three bands."
                    )

            for idx, (raster_fp, feature_name) in enumerate(
                zip(raster_filepaths, feature_names)
            ):
                with rasterio.open(raster_fp) as src:
                    if src.meta["crs"] is None:
                        dst_array = src.read(bands)
                        minx, miny, maxx, maxy = list_bounds[idx]
                    else:
                        # Folium requires 4326, streaming blocks are 3857
                        with WarpedVRT(src, crs="EPSG:4326") as vrt:
                            dst_array = vrt.read(bands)
                            minx, miny, maxx, maxy = vrt.bounds

                m.add_child(
                    folium.raster_layers.ImageOverlay(
                        np.moveaxis(np.stack(dst_array), 0, 2),
                        bounds=[[miny, minx], [maxy, maxx]],  # different order.
                        name=f"Image {idx + 1} - {feature_name}",
                    )
                )

        # Collapse layer control with too many features.
        collapsed = bool(result_df.shape[0] > 4)
        folium.LayerControl(position="bottomleft", collapsed=collapsed).add_to(m)

        if save_html:
            save_html = Path(save_html)
            if not save_html.exists():
                save_html.mkdir(parents=True, exist_ok=True)
            filepath = save_html / "final_map.html"
            with filepath.open("w") as f:
                f.write(m._repr_html_())
        return m

    @requires_viz
    def map_results(
        self,
        bands=[1, 2, 3],
        aoi: GeoDataFrame = None,
        show_images: bool = True,
        show_features: bool = True,
        name_column: str = "uid",
        save_html: Path = None,
    ) -> "folium.Map":
        """
        Displays data.json, and if available, one or multiple results geotiffs.

        Args:
            bands: Image bands and order to plot, default [1,2,3]. First band is 1.
            aoi: Optional visualization of aoi boundaries when given GeoDataFrame of aoi.
            show_images: Shows images if True (default).
            show_features: Shows features if True (default).
            name_column: Name of the feature property that provides the Feature/Layer name.
            save_html: The path for saving folium map as html file. With default None, no file is saved.
        """
        # TODO: Surface optional filepaths? or remove option alltogether?
        if self.results is None:
            raise ValueError(
                "You first need to download the results via job.download_results()!"
            )

        f_paths = []
        if isinstance(self.results, list):
            # Add features to map.
            # Some blocks store vector results in an additional geojson file.
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

    @requires_viz
    def map_quicklooks(
        self,
        scenes: GeoDataFrame,
        aoi: Optional[GeoDataFrame] = None,
        show_images: bool = True,
        show_features: bool = False,
        filepaths: Optional[list] = None,
        name_column: str = "id",
        save_html: Optional[Path] = None,
    ) -> "folium.Map":
        """
        TODO: Currently only implemented for catalog!

        Plots the downloaded quicklooks (filepaths saved to self.quicklooks of the
        respective object, e.g. job, catalog).

        Args:
                scenes: GeoDataFrame of scenes, results of catalog.search()
                aoi: GeoDataFrame of aoi.
                show_images: Shows images if True (default).
                show_features: Shows no features if False (default).
                filepaths: Paths to images to plot. Optional, by default picks up the last
                        downloaded results.
                name_column: Name of the feature property that provides the Feature/Layer name.
                save_html: The path for saving folium map as html file. With default None, no file is saved.
        """
        if filepaths is None:
            if self.quicklooks is None:
                raise ValueError("You first need to download the quicklooks!")
            filepaths = self.quicklooks

        m = self._map_images(
            plot_file_format=[".jpg", ".jpeg", ".png"],
            result_df=scenes,
            filepaths=filepaths,
            aoi=aoi,
            show_images=show_images,
            show_features=show_features,
            name_column=name_column,
            save_html=save_html,
        )
        return m

    @staticmethod
    @requires_viz
    def plot_coverage(
        scenes: GeoDataFrame,
        aoi: Optional[GeoDataFrame] = None,
        legend_column: str = "sceneId",
        figsize=(12, 16),
    ) -> None:
        """
        Plots a coverage map of a dataframe with geometries e.g. the results of catalog.search())
        Args:
                scenes: GeoDataFrame of scenes, results of catalog.search()
                aoi: GeoDataFrame of aoi.
                legend_column: Dataframe column set to legend, default is "sceneId".
                        Legend entries are sorted and this determines plotting order.
                figsize: Matplotlib figure size.
        """
        if legend_column not in scenes.columns:
            legend_column = None  # type: ignore
            logger.info(
                "Given legend_column name not in scene dataframe, "
                "plotting without legend."
            )

        try:
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
        except AttributeError as e:
            raise TypeError(
                "'scenes' and 'aoi' (optional) have to be a GeoDataFrame."
            ) from e
        ax.set_axis_off()
        plt.show()

    @staticmethod
    @requires_viz
    def draw_aoi() -> "folium.Map":
        """
        Displays an interactive map to draw an aoi by hand, returns the folium object if
        not run in a Jupyter notebook.

        Export the drawn aoi via the export button, then read the geometries via
        read_aoi_file().
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
        return m


if _viz_installed:

    def folium_base_map(
        lat: float = 52.49190032214706,
        lon: float = 13.39117252959244,
        zoom_start: int = 14,
        width_percent: str = "95%",
        layer_control: bool = False,
    ) -> "folium.Map":
        """Provides a folium map with basic features and UP42 logo."""
        mapfigure = folium.Figure(width=width_percent)
        m = folium.Map(
            location=[lat, lon], zoom_start=zoom_start, crs="EPSG3857"
        ).add_to(mapfigure)

        tiles = (
            "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery"
            "/MapServer/tile/{z}/{y}/{x}.png"
        )
        attr = (
            "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, "
            "AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the "
            "GIS User Community"
        )
        folium.TileLayer(tiles=tiles, attr=attr, name="Satellite - ESRI").add_to(m)

        formatter = "function(num) {return L.Util.formatNum(num, 4) + ' ';};"
        folium.plugins.MousePosition(
            position="bottomright",
            separator=" | ",
            empty_string="NaN",
            lng_first=True,
            num_digits=20,
            prefix="lon/lat:",
            lat_formatter=formatter,
            lng_formatter=formatter,
        ).add_to(m)

        folium.plugins.MiniMap(
            tile_layer="OpenStreetMap", position="bottomright", zoom_level_offset=-6
        ).add_to(m)
        folium.plugins.Fullscreen().add_to(m)
        folium.plugins.FloatImage(
            image="https://cdn-images-1.medium.com/max/140/1*XJ_B7ur_c8bYKniXpKVpWg@2x.png",
            bottom=90,
            left=88,
        ).add_to(m)

        if layer_control:
            folium.LayerControl(
                position="bottomleft", collapsed=False, zindex=100
            ).add_to(m)
            # If adding additional layers outside of the folium base map function, don't
            # use this one here. Causes an empty map.
        return m

    class DrawFoliumOverride(Draw):
        def render(self, **kwargs):
            # pylint: disable=import-outside-toplevel
            from branca.element import CssLink, Element, Figure, JavascriptLink

            super().render(**kwargs)

            figure = self.get_root()
            assert isinstance(figure, Figure), (
                "You cannot render this Element " "if it is not in a Figure."
            )

            figure.header.add_child(
                JavascriptLink(
                    "https://cdnjs.cloudflare.com/ajax/libs/leaflet.draw/1.0.2/"
                    "leaflet.draw.js"
                )
            )  # noqa
            figure.header.add_child(
                CssLink(
                    "https://cdnjs.cloudflare.com/ajax/libs/leaflet.draw/1.0.2/"
                    "leaflet.draw.css"
                )
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
            # TODO: How to change hover color?
            export_button = """<a href='#' id='export'>Export as<br/>GeoJson</a>"""
            if self.export:
                figure.header.add_child(Element(export_style), name="export")
                figure.html.add_child(Element(export_button), name="export_button")
