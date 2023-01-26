# up42

::: up42.main
    selection:
        members:
            - "authenticate"
    rendering:
       group_by_category: False


::: up42.tools
    rendering:
        group_by_category: False


::: up42.viztools
    selection:
        members:
            - "draw_aoi"
    rendering:
        group_by_category: False


::: up42.main
    selection:
        filters:
            - "!authenticate"
            - "!^_"
    rendering:
        group_by_category: False


::: up42.initialization
    rendering:
        group_by_category: False
