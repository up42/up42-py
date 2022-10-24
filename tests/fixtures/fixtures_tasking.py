import pytest

from ..context import (
    Tasking,
)


@pytest.fixture()
def tasking_mock(auth_mock):
    return Tasking(auth=auth_mock)
