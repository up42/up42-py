from unittest import mock

import pytest
import requests

from up42 import host

from .fixtures import fixtures_globals as constants


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
            workspace_mock.session = requests.session()
            workspace_mock.id = constants.WORKSPACE_ID
            workspace_mock.auth = lambda request: request
            yield
    else:
        yield
