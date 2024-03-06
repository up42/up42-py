from dataclasses import dataclass


@dataclass(eq=True, frozen=True)
class ResilienceSettings:
    total: int = 10
    backoff_factor: float = 0.001
    statuses: tuple = tuple(range(500, 600)) + (429,)


@dataclass(eq=True, frozen=True)
class TokenProviderSettings:
    token_url: str
    duration: int = 5 * 60
    timeout: int = 120


@dataclass(eq=True, frozen=True)
class ProjectCredentialsSettings:
    client_id: str
    client_secret: str
