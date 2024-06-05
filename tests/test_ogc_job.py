from unittest import mock

import pytest
import requests


@pytest.fixture(autouse=True)
def workspace():
    with mock.patch("up42.base.workspace") as workspace_mock:
        session = requests.Session()
        session.hooks = {"response": lambda response, *args, **kwargs: response.raise_for_status()}
        workspace_mock.auth.session = session
        yield
