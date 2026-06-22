import json
from email import policy
from email.parser import BytesParser

import pytest

pytest.importorskip("PIL")

from generator import COMMUNICATION_TYPES, generate_communication_pack, generate_matter


def test_text_screenshot_and_ground_truth(tmp_path):
    matter = generate_matter("commercial-contract-dispute", 4)
    pack = generate_communication_pack(
        matter, tmp_path, seed=3, communication_types=["client_other_party_texts"]
    )
    artifact = pack["artifacts"][0]
    assert artifact["files"]["screenshot"].endswith(".iphone.png")
    truth = json.loads(open(artifact["files"]["ground_truth"], encoding="utf-8").read())
    assert len(truth["messages"]) >= 4
    assert truth["legal_context"]["pre_litigation"] is True
    timestamps = [item["timestamp"] for item in truth["messages"]]
    assert timestamps == sorted(timestamps)


def test_eml_is_real_rfc_message(tmp_path):
    matter = generate_matter("commercial-contract-dispute", 4)
    pack = generate_communication_pack(
        matter, tmp_path, seed=2, communication_types=["opposing_counsel_email"]
    )
    path = pack["artifacts"][0]["files"]["eml"]
    parsed = BytesParser(policy=policy.default).parse(open(path, "rb"))
    assert parsed["Message-ID"].endswith("@example.com>")
    assert "SYNTHETIC TEST" in parsed["Subject"]
    assert "preserve" in parsed.get_content().lower()


def test_all_communication_recipes_generate(tmp_path):
    matter = generate_matter("commercial-contract-dispute", 1)
    pack = generate_communication_pack(matter, tmp_path, 1)
    assert {a["communication_type"] for a in pack["artifacts"]} == set(COMMUNICATION_TYPES)
