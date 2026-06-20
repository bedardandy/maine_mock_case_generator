"""Schema sanity checks."""
from jsonschema import Draft202012Validator

from generator.schema import canonical_case_schema, mock_matter_schema


def test_mock_matter_schema_is_valid_metaschema():
    Draft202012Validator.check_schema(mock_matter_schema())


def test_canonical_case_schema_is_valid_metaschema():
    Draft202012Validator.check_schema(canonical_case_schema())


def test_mock_matter_schema_requires_core_sections():
    schema = mock_matter_schema()
    required = set(schema["required"])
    assert {"schema_version", "provenance", "matter", "parties", "fact_pattern"} <= required


def test_provenance_enforces_mock_and_fictional():
    props = mock_matter_schema()["properties"]["provenance"]["properties"]
    assert props["mock"]["const"] is True
    assert props["fictional"]["const"] is True
