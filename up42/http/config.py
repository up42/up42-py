from dataclasses import dataclass
from typing import Union

from up42 import host  # TODO: host to be moved to http package to avoid circular dependencies


@dataclass(eq=True, frozen=True)
class ResilienceSettings:
    total: int = 10
    backoff_factor: float = 0.001
    statuses: tuple = tuple(range(500, 600)) + (429,)


@dataclass(eq=True, frozen=True)
class TokenProviderSettings:
    token_url: str = host.endpoint("/oauth/token")
    duration: int = 5 * 60
    timeout: int = 120


@dataclass(eq=True, frozen=True)
class ProjectCredentialsSettings:
    project_id: str
    project_api_key: str


@dataclass(eq=True, frozen=True)
class AccountCredentialsSettings:
    username: str
    password: str


CredentialsSettings = Union[AccountCredentialsSettings, ProjectCredentialsSettings]
