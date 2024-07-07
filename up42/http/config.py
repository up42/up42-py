import dataclasses as dc


@dc.dataclass(eq=True, frozen=True)
class ResilienceSettings:
    total: int = 5
    backoff_factor: float = 1
    statuses: tuple = tuple(range(500, 600))


@dc.dataclass(eq=True, frozen=True)
class TokenProviderSettings:
    token_url: str
    expiry_offset: int = 30
    timeout: int = 120


@dc.dataclass(eq=True, frozen=True)
class AccountCredentialsSettings:
    username: str
    password: str


CredentialsSettings = AccountCredentialsSettings
