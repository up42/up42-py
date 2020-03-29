import json
from pathlib import Path

import pytest
import requests_mock

from .fixtures import auth_mock, catalog_mock
import up42


def test_catalog(catalog_mock):
    assert isinstance(catalog_mock, up42.Catalog)
