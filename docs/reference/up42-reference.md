# up42

::: up42.main
    selection:
        members:
            - "authenticate"
    rendering:
       show_root_toc_entry: False
       show_if_no_docstring: False
       group_by_category: False

::: up42.tools
    rendering:
        show_root_toc_entry: False
        show_if_no_docstring: False
        group_by_category: False

::: up42.viztools
    selection:
        members:
            - "draw_aoi"
    rendering:
        show_root_toc_entry: False
        show_if_no_docstring: False
        group_by_category: False

::: up42.main
    selection:
        filters:
            - "!authenticate"
            - "!^_"
    rendering:
        show_root_toc_entry: False
        show_if_no_docstring: False
        group_by_category: False


::: up42.initialization
    rendering:
        show_root_toc_entry: False
        show_if_no_docstring: False
        group_by_category: False
