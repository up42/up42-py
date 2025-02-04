from unittest import mock

import pytest
import requests

from tests import constants
from up42 import host


@pytest.fixture(autouse=True)
def restore_default_domain():
    # To avoid breaking urls in other tests when the domain is changed in a test
    default_domain = host.DOMAIN
    yield
    host.DOMAIN = default_domain


@pytest.fixture(autouse=True)
def workspace(request):
    if "no_workspace" not in request.keywords:
        with mock.patch("up42.base.workspace") as workspace_mock:
            session = requests.Session()
            session.hooks = {"response": lambda response, *args, **kwargs: response.raise_for_status()}
            workspace_mock.session = session
            workspace_mock.id = constants.WORKSPACE_ID
            workspace_mock.auth = lambda request: request
            yield
    else:
        yield
