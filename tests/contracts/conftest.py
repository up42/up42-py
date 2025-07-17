import contextlib
from typing import Callable, Iterator, Protocol, Tuple

import pytest
from pact.v3 import pact


class PactProvider(Protocol):
    def __call__(self, provider: str) -> Tuple[pact.Pact, Callable[[], Iterator[pact.PactServer]]]:
        ...


@pytest.fixture
def create_pact(monkeypatch) -> PactProvider:
    def inner(
        provider: str,
    ) -> Tuple[pact.Pact, Callable[[], Iterator[pact.PactServer]]]:
        pact_mock = pact.Pact(consumer="SDK", provider=provider).with_specification("V4")

        @contextlib.contextmanager
        def mock_server():
            with pact_mock.serve() as srv:
                monkeypatch.setattr("up42.host.endpoint", lambda x: f"{srv.url}{x}")
                yield srv
            pact_mock.write_file("pacts", overwrite=True)

        return (pact_mock, mock_server)  # type: ignore

    return inner
