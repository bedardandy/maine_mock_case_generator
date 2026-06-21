"""Versioned contracts shared by repository adapters and ecosystem reports."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Protocol, runtime_checkable

CONTRACT_VERSION = "1.0"


@dataclass(frozen=True)
class RepositoryCapability:
    repository: str
    mapping_dialect: str
    fill_strategy: str
    case_namespace: str
    trust_model: str
    required_artifacts: tuple[str, ...]
    operations: tuple[str, ...]


@dataclass
class AdapterResult:
    ok: bool
    case: dict[str, Any]
    errors: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[dict[str, Any]] = field(default_factory=list)
    profile: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@runtime_checkable
class CaseAdapter(Protocol):
    profile: str

    def supports(self, form: dict[str, Any]) -> bool: ...
    def adapt(self, matter: dict[str, Any], form: dict[str, Any]) -> dict[str, Any]: ...
    def validate(self, case: dict[str, Any], form: dict[str, Any]) -> AdapterResult: ...


@dataclass
class EcosystemReport:
    contract_version: str = CONTRACT_VERSION
    ok: bool = True
    started_at: str = ""
    duration_ms: int = 0
    source_shas: dict[str, str] = field(default_factory=dict)
    runs: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[dict[str, Any]] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
