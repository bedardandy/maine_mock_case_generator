"""Deterministic synthetic client documents and scan-only PDF derivatives."""
from __future__ import annotations

import hashlib
import io
import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable

DOCUMENT_TYPES = (
    "death_certificate", "signed_deed", "bank_statement", "pay_stub",
    "federal_tax_statement", "maine_tax_statement", "stock_certificate",
)


@dataclass
class DocumentArtifact:
    document_id: str
    document_type: str
    source_pdf: str
    scanned_pdf: str
    ground_truth: str
    sha256: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _deps():
    try:
        from PIL import Image, ImageEnhance, ImageFilter
        from pypdf import PdfReader
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except ImportError as exc:
        raise RuntimeError(
            "Synthetic documents require the 'documents' extra: "
            "pip install -e \".[documents]\""
        ) from exc
    return Image, ImageEnhance, ImageFilter, PdfReader, letter, canvas


def _party(matter: dict, *roles: str) -> dict:
    parties = matter.get("parties", {})
    for role in roles:
        if role in parties:
            return parties[role]
    return next(iter(parties.values()), {})


def _money(value) -> str:
    return f"${float(value or 0):,.2f}"


def _fixture_fields(matter: dict, document_type: str, rng: random.Random) -> dict:
    facts = matter.get("facts", {})
    meta = matter.get("matter", {})
    person = _party(matter, "decedent", "plaintiff", "client", "personal_representative")
    signer = _party(matter, "personal_representative", "transferor", "client", "plaintiff")
    company = _party(matter, "company")
    account = f"XXXX-{rng.randint(1000, 9999)}"
    base = {
        "synthetic_notice": "SYNTHETIC TEST DOCUMENT - NOT VALID - NOT FOR FILING",
        "fixture_id": matter.get("provenance", {}).get("fixture_id", ""),
        "name": person.get("full_name", "Jane Q. Doe"),
        "address": person.get("address", "100 Example Lane"),
        "city_state_zip": " ".join(filter(None, [
            person.get("city", "Portland") + ",", person.get("state", "ME"), person.get("zip", "04001")
        ])),
        "phone": person.get("phone", "(207) 555-0100"),
    }
    variants = {
        "death_certificate": {
            "title": "Synthetic Record of Death",
            "decedent": _party(matter, "decedent").get("full_name", base["name"]),
            "date_of_death": facts.get("date_of_death", meta.get("event_date", "2025-01-15")),
            "place_of_death": f"{meta.get('jurisdiction', {}).get('county', 'Cumberland')} County, Maine",
            "informant": signer.get("full_name", "John Q. Doe"),
            "certificate_number": f"TEST-{rng.randint(100000, 999999)}",
        },
        "signed_deed": {
            "title": "Synthetic Quitclaim Deed",
            "grantor": _party(matter, "transferor", "personal_representative").get("full_name", base["name"]),
            "grantee": _party(matter, "transferee").get("full_name", "Alex Q. Roe"),
            "property": facts.get("property_address", "100 Example Lane"),
            "consideration": _money(facts.get("purchase_price", 250000)),
            "signature": signer.get("full_name", base["name"]),
            "recording_reference": f"TEST BOOK {rng.randint(1000,9999)} PAGE {rng.randint(100,999)}",
        },
        "bank_statement": {
            "title": "Pine Tree Community Bank - Synthetic Statement",
            "account_holder": signer.get("full_name", base["name"]),
            "account_number": account,
            "opening_balance": _money(rng.randint(12000, 90000)),
            "deposits": _money(rng.randint(1000, 12000)),
            "withdrawals": _money(rng.randint(500, 9000)),
            "closing_balance": _money(rng.randint(12000, 90000)),
        },
        "pay_stub": {
            "title": "Synthetic Earnings Statement",
            "employee": signer.get("full_name", base["name"]),
            "employer": company.get("full_name", "Example Employer LLC"),
            "gross_pay": _money(rng.randint(1800, 6500)),
            "federal_withholding": _money(rng.randint(150, 900)),
            "maine_withholding": _money(rng.randint(50, 350)),
            "net_pay": _money(rng.randint(1200, 5000)),
        },
        "federal_tax_statement": {
            "title": "Synthetic Federal Tax Statement",
            "taxpayer": signer.get("full_name", base["name"]),
            "taxpayer_id": f"900-00-{rng.randint(0,9999):04d}",
            "tax_year": str(int(meta.get("filing_date", "2026")[:4]) - 1),
            "wages": _money(rng.randint(45000, 180000)),
            "federal_tax": _money(rng.randint(4000, 35000)),
        },
        "maine_tax_statement": {
            "title": "Synthetic Maine Tax Statement",
            "taxpayer": signer.get("full_name", base["name"]),
            "account_number": f"ME-TEST-{rng.randint(100000,999999)}",
            "tax_year": str(int(meta.get("filing_date", "2026")[:4]) - 1),
            "maine_income": _money(rng.randint(40000, 175000)),
            "maine_tax": _money(rng.randint(1500, 14000)),
        },
        "stock_certificate": {
            "title": "Synthetic Stock Certificate",
            "corporation": company.get("full_name", "Example Corporation Inc."),
            "shareholder": signer.get("full_name", base["name"]),
            "shares": str(rng.randint(10, 1000)),
            "certificate_number": f"TEST-{rng.randint(1000,9999)}",
            "signature": signer.get("full_name", base["name"]),
        },
    }
    return base | variants[document_type]


def _draw_source_pdf(path: Path, fields: dict) -> None:
    _, _, _, _, letter, canvas = _deps()
    c = canvas.Canvas(str(path), pagesize=letter)
    width, height = letter
    c.setTitle(fields["title"])
    c.setStrokeColorRGB(.12, .2, .3)
    c.setLineWidth(2)
    c.rect(35, 35, width - 70, height - 70)
    c.setFont("Helvetica-Bold", 15)
    c.drawCentredString(width / 2, height - 70, fields["title"])
    c.setFont("Helvetica-Bold", 9)
    c.setFillColorRGB(.75, 0, 0)
    c.drawCentredString(width / 2, height - 90, fields["synthetic_notice"])
    c.setFillColorRGB(0, 0, 0)
    y = height - 125
    for key, value in fields.items():
        if key in {"title", "synthetic_notice"}:
            continue
        label = key.replace("_", " ").title()
        c.setFont("Helvetica-Bold", 9)
        c.drawString(55, y, label)
        c.setFont("Helvetica", 10)
        c.drawString(210, y, str(value))
        c.line(205, y - 3, width - 55, y - 3)
        y -= 27
        if y < 100:
            c.showPage()
            y = height - 70
    c.setFont("Helvetica-Bold", 30)
    c.setFillColorRGB(.9, .9, .9)
    c.saveState()
    c.translate(width / 2, height / 2)
    c.rotate(35)
    c.drawCentredString(0, 0, "SYNTHETIC TEST FIXTURE")
    c.restoreState()
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 7)
    c.drawString(45, 45, "Generated solely for automated testing. All identities and identifiers are fictional.")
    c.save()


def _scan_pdf(fields: dict, scanned_pdf: Path, seed: int, dpi: int = 150) -> None:
    Image, ImageEnhance, ImageFilter, _, _, _ = _deps()
    from PIL import ImageDraw, ImageFont
    rng = random.Random(seed)
    width, height = int(8.5 * dpi), int(11 * dpi)
    image = Image.new("RGB", (width, height), (248, 247, 242))
    draw = ImageDraw.Draw(image)
    regular = ImageFont.truetype("arial.ttf", 19)
    bold = ImageFont.truetype("arialbd.ttf", 19)
    title_font = ImageFont.truetype("arialbd.ttf", 28)
    notice_font = ImageFont.truetype("arialbd.ttf", 17)
    margin = 70
    draw.rectangle((margin, margin, width - margin, height - margin), outline=(30, 50, 75), width=4)
    title_box = draw.textbbox((0, 0), fields["title"], font=title_font)
    draw.text(((width - (title_box[2] - title_box[0])) / 2, 105),
              fields["title"], fill=(10, 10, 10), font=title_font)
    notice = fields["synthetic_notice"]
    notice_box = draw.textbbox((0, 0), notice, font=notice_font)
    draw.text(((width - (notice_box[2] - notice_box[0])) / 2, 150),
              notice, fill=(160, 0, 0), font=notice_font)
    y = 210
    for key, value in fields.items():
        if key in {"title", "synthetic_notice"}:
            continue
        label = key.replace("_", " ").title()
        draw.text((100, y), label, fill=(0, 0, 0), font=bold)
        draw.text((410, y), str(value), fill=(0, 0, 0), font=regular)
        draw.line((400, y + 25, width - 100, y + 25), fill=(90, 90, 90), width=1)
        y += 52
    image = image.rotate(rng.uniform(-0.8, 0.8), resample=Image.Resampling.BICUBIC,
                         expand=True, fillcolor=(244, 242, 236))
    image = ImageEnhance.Contrast(image).enhance(rng.uniform(.9, 1.08))
    image = ImageEnhance.Brightness(image).enhance(rng.uniform(.92, 1.02))
    image = image.filter(ImageFilter.GaussianBlur(radius=rng.uniform(.15, .45)))
    pixels = image.load()
    for _ in range(max(200, image.width * image.height // 7000)):
        x, y = rng.randrange(image.width), rng.randrange(image.height)
        shade = rng.randrange(170, 245)
        pixels[x, y] = (shade, shade, shade)
    image.convert("RGB").save(scanned_pdf, "PDF", resolution=dpi)


def pdf_embedded_text(path: str | Path) -> str:
    _, _, _, PdfReader, _, _ = _deps()
    return "".join(page.extract_text() or "" for page in PdfReader(str(path)).pages)


def _normalize_pdf(path: Path) -> None:
    """Remove producer timestamps/IDs so identical fixtures hash identically."""
    _, _, _, PdfReader, _, _ = _deps()
    from pypdf import PdfWriter
    reader = PdfReader(str(path))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.add_metadata({
        "/Title": "Synthetic test fixture",
        "/Author": "Maine Mock Case Generator",
        "/Subject": "Fictional data for automated testing",
        "/Creator": "MMCG",
        "/Producer": "MMCG deterministic PDF pipeline",
        "/CreationDate": "D:20260101000000Z",
        "/ModDate": "D:20260101000000Z",
    })
    with path.open("wb") as fh:
        writer.write(fh)


def generate_document(
    matter: dict, document_type: str, out_dir: str | Path, seed: int = 0
) -> DocumentArtifact:
    if document_type not in DOCUMENT_TYPES:
        raise ValueError(f"Unknown document type '{document_type}'")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    fixture_id = matter.get("provenance", {}).get("fixture_id", "fixture")
    document_id = f"{fixture_id}-{document_type}-{seed}"
    source = out / f"{document_type}.source.pdf"
    scanned = out / f"{document_type}.scan.pdf"
    truth = out / f"{document_type}.ground-truth.json"
    fields = _fixture_fields(matter, document_type, random.Random(f"{fixture_id}:{seed}"))
    _draw_source_pdf(source, fields)
    _scan_pdf(fields, scanned, seed)
    _normalize_pdf(source)
    _normalize_pdf(scanned)
    if pdf_embedded_text(scanned).strip():
        raise RuntimeError(f"Scan-only invariant failed for {scanned}: embedded text remains")
    truth.write_text(json.dumps({
        "document_id": document_id, "document_type": document_type, "synthetic": True,
        "matter_fixture_id": fixture_id, "fields": fields,
        "expected_classification": document_type,
        "scan": {"embedded_text_expected": False, "ocr_required": True, "seed": seed},
    }, indent=2) + "\n", encoding="utf-8")
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    return DocumentArtifact(document_id, document_type, str(source), str(scanned), str(truth),
                            {"source_pdf": digest(source), "scanned_pdf": digest(scanned),
                             "ground_truth": digest(truth)})


def generate_document_pack(
    matter: dict, out_dir: str | Path, seed: int = 0, document_types=None
) -> dict:
    types = document_types or DOCUMENT_TYPES
    artifacts = [generate_document(matter, kind, Path(out_dir) / kind, seed) for kind in types]
    manifest = {
        "schema_version": "1.0", "synthetic": True,
        "fixture_id": matter.get("provenance", {}).get("fixture_id"),
        "artifacts": [artifact.to_dict() for artifact in artifacts],
    }
    path = Path(out_dir) / "document-pack.manifest.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest
