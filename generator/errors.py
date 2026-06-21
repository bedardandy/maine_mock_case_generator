"""Stable public exceptions and diagnostics for MMCG."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


class MMCGError(Exception):
    """Base class for expected generator and ecosystem failures."""

    code = "MMCG_ERROR"


class UnknownScenarioError(MMCGError):
    code = "UNKNOWN_SCENARIO"


class ScenarioFormatError(MMCGError):
    code = "SCENARIO_FORMAT_ERROR"


class ValidationFailure(MMCGError):
    code = "VALIDATION_FAILURE"


class UnresolvedTemplateError(MMCGError):
    code = "UNRESOLVED_TEMPLATE"


class UnsupportedProfileError(MMCGError):
    code = "UNSUPPORTED_PROFILE"


class ContractError(MMCGError):
    code = "CONTRACT_ERROR"


@dataclass(frozen=True)
class Diagnostic:
    code: str
    message: str
    severity: str = "error"
    path: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
