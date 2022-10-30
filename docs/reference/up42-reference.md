# up42

::: up42.__init__
    rendering:
        show_root_toc_entry: False
        show_if_no_docstring: False
        group_by_category: False

::: up42.main
    selection:
        members:
            - "authenticate"
    rendering:
       show_root_toc_entry: False
       show_if_no_docstring: False
       group_by_category: False

::: up42.initialization
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
