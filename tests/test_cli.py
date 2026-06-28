import json

from generator.cli import main


def test_cli_generate_json(capsys):
    assert main(["generate", "family-divorce-cumberland", "--seed", "1"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["provenance"]["scenario_id"] == "family-divorce-cumberland"


def test_cli_catalog_verify(capsys):
    assert main(["catalog", "verify"]) == 0
    assert json.loads(capsys.readouterr().out)["ok"] is True
