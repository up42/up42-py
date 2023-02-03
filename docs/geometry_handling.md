# Geometry Handling

The Polygon `geometry` parameter required for some UP42 operations like placing an image order, can be 
provided in multiple formats in the Python SDK. It is automatically transformed to the required formatting. 
Also see [AOI guidelines](https://docs.up42.com/help/aoi-guidelines).

You can also use `up42.read_vector_file()` to read local geojson, shapefiles, kml & wkt files.

=== "GeoJSON Geometry"
    ```python
    {
        "coordinates": [
            [
                [
                    13.382853541948975,
                    52.5185756711692
                ],
                [
                    13.382853541948975,
                    52.512321097987126
                ],
                [
                    13.39586259650261,
                    52.512321097987126
                ],
                [
                    13.39586259650261,
                    52.5185756711692
                ],
                [
                    13.382853541948975,
                    52.5185756711692
                ]
            ]
        ],
        "type": "Polygon"
    }
    ```

=== "FeatureCollection"
    ```python
    {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "coordinates": [
                        [
                            [
                                13.382853541948975,
                                52.5185756711692
                            ],
                            [
                                13.382853541948975,
                                52.512321097987126
                            ],
                            [
                                13.39586259650261,
                                52.512321097987126
                            ],
                            [
                                13.39586259650261,
                                52.5185756711692
                            ],
                            [
                                13.382853541948975,
                                52.5185756711692
                            ]
                        ]
                    ],
                    "type": "Polygon"
                }
            }
        ]
    }
    ```

=== "Feature"
    ```python
        {
        "type": "Feature",
        "properties": {},
        "geometry": {
            "coordinates": [
                [
                    [
                        13.382853541948975,
                        52.5185756711692
                    ],
                    [
                        13.382853541948975,
                        52.512321097987126
                    ],
                    [
                        13.39586259650261,
                        52.512321097987126
                    ],
                    [
                        13.39586259650261,
                        52.5185756711692
                    ],
                    [
                        13.382853541948975,
                        52.5185756711692
                    ]
                ]
            ],
            "type": "Polygon"
        }
    }
    ```

=== "bbox coordinates"
    The `minx, miny, maxx, maxy` bbox outline / bounds coordinates of a geometry.
    ```python
    aoi = [13.382853541948975, 52.512321097987126, 13.39586259650261, 52.5185756711692]
    ```


=== "GeoDataFrame"
    See the geopandas [documentation](https://geopandas.org/en/stable/index.html).
    
    The geopandas dataframe can only have a single row, and requires a Polygon geometry.
    ```python
    aoi = geopandas.read_file("aoi.geojson")
    ```

=== "shapely Polygon"
    See the shapely [documentation](https://shapely.readthedocs.io/en/stable/manual.html).
    ```python
    aoi = Polygon([(0, 0, 0), (0, 0, 1), (1, 1, 1)])
    ```

