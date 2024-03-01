import os
from dataclasses import dataclass


@dataclass(eq=True, frozen=True)
class ResilienceSettings:
    total = 10
    backoff_factor = 0.001
    statuses: tuple = tuple(range(500, 600)) + (429,)


@dataclass(eq=True, frozen=True)
class TokenProviderSettings:
    token_url: str
    duration = 5 * 60
    timeout = 120
