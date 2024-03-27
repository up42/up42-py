import dataclasses as dc
from typing import Union


@dc.dataclass(eq=True, frozen=True)
class ResilienceSettings:
    total: int = 3
    backoff_factor: float = 0.5
    statuses: tuple = tuple(range(500, 600))


@dc.dataclass(eq=True, frozen=True)
class TokenProviderSettings:
    token_url: str
    duration: int = 5 * 60 - 1
    timeout: int = 120


@dc.dataclass(eq=True, frozen=True)
class ProjectCredentialsSettings:
    project_id: str
    project_api_key: str


@dc.dataclass(eq=True, frozen=True)
class AccountCredentialsSettings:
    username: str
    password: str


CredentialsSettings = Union[AccountCredentialsSettings, ProjectCredentialsSettings]
