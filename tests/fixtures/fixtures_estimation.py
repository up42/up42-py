from typing import Any, Dict, List

import pytest

from up42 import estimation

from . import fixtures_globals as constants


@pytest.fixture()
def estimation_mock(auth_mock):
    input_parameters = {
        "esa-s2-l2a-gtiff-visual:1": {
            "time": "2018-01-01T00:00:00+00:00/2020-12-31T23:59:59+00:00",
            "limit": 1,
            "bbox": [13.33409, 52.474922, 13.38547, 52.500398],
        },
        "tiling:1": {"tile_width": 768},
    }
    input_tasks: List[Dict[str, Any]] = [
        {
            "name": "esa-s2-l2a-gtiff-visual:1",
            "parentName": None,
            "blockId": "c4cb8913-2ef3-4e82-a426-65ea8faacd9a",
            "blockVersionTag": "1.0.1",
        },
        {
            "name": "tiling:1",
            "parentName": "esa-s2-l2a-gtiff-visual:1",
            "blockId": "3e146dd6-2b67-4d6e-a422-bb3d973e32ff",
            "blockVersionTag": "2.2.3",
        },
    ]

    return estimation.Estimation(
        auth=auth_mock,
        project_id=constants.PROJECT_ID,
        input_parameters=input_parameters,
        input_tasks=input_tasks,
    )
