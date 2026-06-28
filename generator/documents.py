"""Deterministic synthetic client documents and scan-only PDF derivatives."""
from __future__ import annotations

import hashlib
import io
import json
import os
import random
import textwrap
from email.message import EmailMessage
from email.policy import SMTP
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

DOCUMENT_TYPES = (
    "death_certificate", "signed_deed", "bank_statement", "pay_stub",
    "federal_tax_statement", "maine_tax_statement", "stock_certificate",
    "appraisal", "property_tax_bill", "credit_card_statement", "payment_app_statement",
    "signed_will", "signed_power_of_attorney", "retail_receipt", "contract",
    "court_cover_letter", "opposing_counsel_letter",
    "medical_record", "medical_bill", "insurance_declarations", "insurance_eob",
    "mortgage_statement", "loan_statement", "brokerage_statement", "retirement_statement",
    "utility_bill", "lease", "rent_ledger", "security_deposit_accounting",
    "employment_offer", "termination_letter", "timesheet", "wage_history",
    "invoice", "repair_estimate", "work_order", "purchase_order",
    "business_profit_loss", "business_balance_sheet", "general_ledger",
    "trust_instrument", "beneficiary_designation", "funeral_invoice",
    "title_commitment", "closing_statement", "lien_release",
    "incident_report", "demand_letter", "settlement_offer", "affidavit",
)

COMMUNICATION_TYPES = (
    "client_other_party_texts", "client_counsel_email", "opposing_counsel_email",
    "witness_email", "expert_email",
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
        "appraisal": {
            "title": "Synthetic Appraisal Summary",
            "property": facts.get("property_address", "100 Example Lane"),
            "owner": signer.get("full_name", base["name"]),
            "effective_date": meta.get("event_date", "2025-01-15"),
            "appraised_value": _money(facts.get("real_property_value", rng.randint(180000, 900000))),
            "approach": "Sales comparison and cost approach",
            "appraiser": "Morgan Q. Example, TEST-MAI",
        },
        "property_tax_bill": {
            "title": "Synthetic Municipal Property Tax Bill",
            "taxpayer": signer.get("full_name", base["name"]),
            "property": facts.get("property_address", "100 Example Lane"),
            "account_number": f"TEST-{rng.randint(100000,999999)}",
            "assessed_value": _money(facts.get("adjusted_assessed_value", rng.randint(150000, 800000))),
            "tax_due": _money(rng.randint(1800, 12000)),
            "due_date": meta.get("filing_date", "2026-04-01"),
        },
        "credit_card_statement": {
            "title": "Synthetic Credit Card Statement",
            "cardholder": signer.get("full_name", base["name"]),
            "account_number": account,
            "previous_balance": _money(rng.randint(500, 12000)),
            "purchases": _money(rng.randint(300, 7000)),
            "payments": _money(rng.randint(200, 6000)),
            "new_balance": _money(rng.randint(500, 14000)),
            "minimum_due": _money(rng.randint(35, 500)),
        },
        "payment_app_statement": {
            "title": "Synthetic Peer-to-Peer Payment Statement",
            "account_holder": signer.get("full_name", base["name"]),
            "handle": f"@test-{rng.randint(1000,9999)}",
            "payment_1": f"{_money(rng.randint(50,1200))} to Alex Q. Example - shared expense",
            "payment_2": f"{_money(rng.randint(50,1200))} from Casey Q. Example - reimbursement",
            "payment_3": f"{_money(rng.randint(50,1200))} to Jordan Q. Example - materials",
        },
        "signed_will": {
            "title": "Synthetic Last Will and Testament",
            "testator": _party(matter, "decedent").get("full_name", base["name"]),
            "execution_date": facts.get("will_date", facts.get("contested_will_date", "2024-03-15")),
            "personal_representative": signer.get("full_name", base["name"]),
            "beneficiary_clause": "Equal shares to the testator's descendants, per stirpes",
            "testator_signature": _party(matter, "decedent").get("full_name", base["name"]),
            "witnesses": "Alex Q. Example and Casey Q. Example",
        },
        "signed_power_of_attorney": {
            "title": "Synthetic Durable Power of Attorney",
            "principal": person.get("full_name", base["name"]),
            "agent": signer.get("full_name", "Jordan Q. Example"),
            "execution_date": "2024-06-15",
            "powers": "Banking, real property, taxes, and claims",
            "principal_signature": person.get("full_name", base["name"]),
            "notary": "Taylor Q. Example, Test Notary",
        },
        "retail_receipt": {
            "title": "Synthetic Retail Receipt",
            "store": "Example Home Supply",
            "receipt_number": f"TEST-{rng.randint(100000,999999)}",
            "item_1": f"Building materials - {_money(rng.randint(100,1200))}",
            "item_2": f"Equipment rental - {_money(rng.randint(50,600))}",
            "sales_tax": _money(rng.randint(10, 130)),
            "total": _money(rng.randint(200, 1900)),
            "payment": f"Test card ending {rng.randint(1000,9999)}",
        },
        "contract": {
            "title": "Synthetic Services Contract",
            "client": signer.get("full_name", base["name"]),
            "contractor": company.get("full_name", "Example Services LLC"),
            "effective_date": facts.get("contract_date", "2025-04-15"),
            "scope": facts.get("contract_type", "Professional and project services"),
            "contract_price": _money(facts.get("contract_value", rng.randint(5000, 150000))),
            "signature_client": signer.get("full_name", base["name"]),
            "signature_contractor": "Alex Q. Example",
        },
        "court_cover_letter": {
            "title": "Synthetic Court Filing Cover Letter",
            "from": matter.get("parties", {}).get("attorney", {}).get("full_name", "Counsel Q. Example"),
            "to": f"Clerk, {meta.get('jurisdiction', {}).get('court_location', 'Portland')} Court",
            "re": meta.get("title", "Synthetic Matter"),
            "enclosures": "Original filing, service copies, and test filing fee",
            "signature": matter.get("parties", {}).get("attorney", {}).get("full_name", "Counsel Q. Example"),
        },
        "opposing_counsel_letter": {
            "title": "Synthetic Pre-Litigation Counsel Letter",
            "from": matter.get("parties", {}).get("attorney", {}).get("full_name", "Counsel Q. Example"),
            "to": "Opposing Counsel Q. Example",
            "re": meta.get("title", "Synthetic Matter"),
            "position": "Demand to preserve evidence and discuss resolution before filing",
            "response_deadline": meta.get("filing_date", "2026-04-01"),
            "signature": matter.get("parties", {}).get("attorney", {}).get("full_name", "Counsel Q. Example"),
        },
        "medical_record": {
            "title": "Synthetic Clinical Visit Summary",
            "patient": person.get("full_name", base["name"]),
            "provider": "Example Medical Group",
            "visit_date": meta.get("event_date", "2025-03-15"),
            "chief_complaint": facts.get("injury_type", facts.get("alleged_condition", "Pain and functional limitation")),
            "assessment": "Synthetic diagnosis for ingestion testing only",
            "plan": "Follow-up, conservative care, and records review",
        },
        "medical_bill": {
            "title": "Synthetic Medical Billing Statement",
            "patient": person.get("full_name", base["name"]),
            "provider": "Example Medical Group",
            "account_number": f"MED-TEST-{rng.randint(100000,999999)}",
            "service_date": meta.get("event_date", "2025-03-15"),
            "charges": _money(facts.get("medical_specials", rng.randint(500, 35000))),
            "insurance_adjustment": _money(rng.randint(100, 5000)),
            "patient_balance": _money(rng.randint(50, 9000)),
        },
        "insurance_declarations": {
            "title": "Synthetic Insurance Declarations",
            "named_insured": signer.get("full_name", base["name"]),
            "carrier": "Example Mutual Insurance",
            "policy_number": f"TEST-POL-{rng.randint(100000,999999)}",
            "policy_period": "2025-01-01 through 2026-01-01",
            "coverage": "Liability and property coverage",
            "limit": _money(facts.get("policy_limits", rng.randint(100000, 1000000))),
        },
        "insurance_eob": {
            "title": "Synthetic Explanation of Benefits",
            "member": person.get("full_name", base["name"]),
            "plan": "Example Health Plan",
            "claim_number": f"TEST-CLM-{rng.randint(100000,999999)}",
            "provider_charge": _money(rng.randint(500, 18000)),
            "plan_paid": _money(rng.randint(300, 15000)),
            "member_responsibility": _money(rng.randint(25, 3500)),
        },
        "mortgage_statement": {
            "title": "Synthetic Mortgage Statement",
            "borrower": signer.get("full_name", base["name"]),
            "servicer": "Example Home Lending",
            "loan_number": account,
            "principal_balance": _money(rng.randint(80000, 700000)),
            "monthly_payment": _money(rng.randint(700, 5200)),
            "escrow_balance": _money(rng.randint(500, 9000)),
            "due_date": meta.get("filing_date", "2026-04-01"),
        },
        "loan_statement": {
            "title": "Synthetic Loan Statement",
            "borrower": signer.get("full_name", base["name"]),
            "lender": "Example Community Lending",
            "loan_number": account,
            "original_principal": _money(rng.randint(5000, 250000)),
            "current_balance": _money(rng.randint(1000, 220000)),
            "interest_rate": f"{rng.uniform(3.5, 12.5):.2f}%",
            "payment_due": _money(rng.randint(100, 3000)),
        },
        "brokerage_statement": {
            "title": "Synthetic Brokerage Account Statement",
            "account_owner": signer.get("full_name", base["name"]),
            "firm": "Example Securities",
            "account_number": account,
            "stocks": _money(rng.randint(10000, 400000)),
            "bonds": _money(rng.randint(0, 180000)),
            "cash": _money(rng.randint(500, 40000)),
            "total_value": _money(rng.randint(15000, 600000)),
        },
        "retirement_statement": {
            "title": "Synthetic Retirement Plan Statement",
            "participant": signer.get("full_name", base["name"]),
            "plan": "Example Employer 401(k) Plan",
            "account_number": account,
            "employee_contributions": _money(rng.randint(5000, 180000)),
            "employer_contributions": _money(rng.randint(1000, 90000)),
            "vested_balance": _money(rng.randint(10000, 500000)),
        },
        "utility_bill": {
            "title": "Synthetic Utility Bill",
            "customer": signer.get("full_name", base["name"]),
            "service_address": facts.get("premises_address", facts.get("property_address", "100 Example Lane")),
            "account_number": account,
            "billing_period": "2026-03-01 through 2026-03-31",
            "usage": f"{rng.randint(300, 1800)} kWh",
            "amount_due": _money(rng.randint(75, 650)),
        },
        "lease": {
            "title": "Synthetic Residential Lease",
            "landlord": _party(matter, "plaintiff").get("full_name", "Landlord Q. Example"),
            "tenant": _party(matter, "defendant").get("full_name", signer.get("full_name", base["name"])),
            "premises": facts.get("premises_address", "100 Example Lane"),
            "term": "January 1, 2025 through December 31, 2025",
            "monthly_rent": _money(facts.get("monthly_rent", rng.randint(900, 3200))),
            "signatures": "Landlord Q. Example / Tenant Q. Example",
        },
        "rent_ledger": {
            "title": "Synthetic Rent Ledger",
            "tenant": _party(matter, "defendant").get("full_name", signer.get("full_name", base["name"])),
            "premises": facts.get("premises_address", "100 Example Lane"),
            "monthly_rent": _money(facts.get("monthly_rent", rng.randint(900, 3200))),
            "charges": _money(rng.randint(3000, 12000)),
            "payments": _money(rng.randint(1000, 9000)),
            "balance": _money(facts.get("total_rent_owed", rng.randint(500, 7000))),
        },
        "security_deposit_accounting": {
            "title": "Synthetic Security Deposit Accounting",
            "tenant": _party(matter, "defendant").get("full_name", base["name"]),
            "deposit_received": _money(rng.randint(800, 3500)),
            "cleaning": _money(rng.randint(0, 700)),
            "repairs": _money(rng.randint(0, 1800)),
            "refund": _money(rng.randint(0, 2500)),
            "mailing_date": meta.get("filing_date", "2026-04-01"),
        },
        "employment_offer": {
            "title": "Synthetic Employment Offer",
            "employer": company.get("full_name", "Example Employer LLC"),
            "employee": person.get("full_name", base["name"]),
            "position": "Operations Manager",
            "start_date": facts.get("hire_date", "2024-01-15"),
            "salary": _money(facts.get("annual_salary", rng.randint(45000, 145000))),
            "signature": "Hiring Manager Q. Example",
        },
        "termination_letter": {
            "title": "Synthetic Employment Termination Letter",
            "employer": company.get("full_name", "Example Employer LLC"),
            "employee": person.get("full_name", base["name"]),
            "termination_date": facts.get("termination_date", meta.get("event_date", "2025-06-30")),
            "stated_reason": facts.get("adverse_action", "Position eliminated"),
            "final_pay": "Regular wages plus accrued paid leave",
            "signature": "Human Resources Q. Example",
        },
        "timesheet": {
            "title": "Synthetic Employee Timesheet",
            "employee": person.get("full_name", base["name"]),
            "employer": company.get("full_name", "Example Employer LLC"),
            "regular_hours": str(rng.randint(35, 40)),
            "overtime_hours": str(rng.randint(0, 18)),
            "hourly_rate": _money(facts.get("hourly_wage", rng.randint(18, 65))),
            "supervisor_approval": "Supervisor Q. Example",
        },
        "wage_history": {
            "title": "Synthetic Wage History",
            "employee": person.get("full_name", base["name"]),
            "employer": company.get("full_name", "Example Employer LLC"),
            "prior_year_wages": _money(facts.get("last_year_earnings", rng.randint(35000, 150000))),
            "current_ytd_wages": _money(facts.get("expected_year_earnings", rng.randint(25000, 130000))),
            "bonuses": _money(facts.get("bonuses_income", rng.randint(0, 25000))),
        },
        "invoice": {
            "title": "Synthetic Commercial Invoice",
            "vendor": company.get("full_name", "Example Services LLC"),
            "customer": signer.get("full_name", base["name"]),
            "invoice_number": f"TEST-INV-{rng.randint(10000,99999)}",
            "description": facts.get("goods", "Services and materials"),
            "amount": _money(facts.get("invoice_amount", rng.randint(500, 50000))),
            "due_date": meta.get("filing_date", "2026-04-01"),
        },
        "repair_estimate": {
            "title": "Synthetic Repair Estimate",
            "customer": signer.get("full_name", base["name"]),
            "contractor": "Example Repair Company",
            "property_or_item": facts.get("project", facts.get("property_address", "Disputed property")),
            "scope": facts.get("primary_defect", "Repair documented damage"),
            "labor": _money(rng.randint(500, 18000)),
            "materials": _money(rng.randint(300, 25000)),
            "estimate_total": _money(facts.get("repair_cost_estimate", rng.randint(1000, 42000))),
        },
        "work_order": {
            "title": "Synthetic Work Order",
            "customer": signer.get("full_name", base["name"]),
            "vendor": company.get("full_name", "Example Service Company"),
            "work_order_number": f"TEST-WO-{rng.randint(10000,99999)}",
            "requested_work": facts.get("project", "Inspection and repair work"),
            "status": "Completed with customer dispute noted",
            "authorized_by": signer.get("full_name", base["name"]),
        },
        "purchase_order": {
            "title": "Synthetic Purchase Order",
            "buyer": signer.get("full_name", base["name"]),
            "supplier": company.get("full_name", "Example Supply Company"),
            "po_number": f"TEST-PO-{rng.randint(10000,99999)}",
            "items": facts.get("goods", "Materials and equipment"),
            "total": _money(facts.get("contract_value", rng.randint(1000, 75000))),
            "approval": "Authorized Purchaser Q. Example",
        },
        "business_profit_loss": {
            "title": "Synthetic Profit and Loss Statement",
            "business": company.get("full_name", "Example Business LLC"),
            "period": "Year ended December 31, 2025",
            "revenue": _money(facts.get("expected_first_year_revenue", rng.randint(100000, 1200000))),
            "cost_of_sales": _money(rng.randint(30000, 500000)),
            "operating_expenses": _money(rng.randint(25000, 450000)),
            "net_income": _money(rng.randint(-50000, 300000)),
        },
        "business_balance_sheet": {
            "title": "Synthetic Balance Sheet",
            "business": company.get("full_name", "Example Business LLC"),
            "cash": _money(rng.randint(5000, 300000)),
            "receivables": _money(rng.randint(0, 250000)),
            "fixed_assets": _money(rng.randint(10000, 600000)),
            "liabilities": _money(rng.randint(5000, 500000)),
            "equity": _money(rng.randint(-50000, 650000)),
        },
        "general_ledger": {
            "title": "Synthetic General Ledger Extract",
            "business": company.get("full_name", "Example Business LLC"),
            "entry_1": f"1000 Cash - debit {_money(rng.randint(1000,20000))}",
            "entry_2": f"4000 Revenue - credit {_money(rng.randint(1000,30000))}",
            "entry_3": f"6100 Legal expense - debit {_money(rng.randint(500,10000))}",
            "period": "Synthetic test period 2025",
        },
        "trust_instrument": {
            "title": "Synthetic Revocable Trust",
            "settlor": person.get("full_name", base["name"]),
            "trustee": signer.get("full_name", base["name"]),
            "trust_date": "2023-05-01",
            "beneficiaries": "The settlor during life, then descendants",
            "trustee_signature": signer.get("full_name", base["name"]),
            "notary": "Taylor Q. Example, Test Notary",
        },
        "beneficiary_designation": {
            "title": "Synthetic Beneficiary Designation",
            "owner": person.get("full_name", base["name"]),
            "account": account,
            "primary_beneficiary": signer.get("full_name", "Jordan Q. Example"),
            "share": "100%",
            "effective_date": "2024-05-15",
            "owner_signature": person.get("full_name", base["name"]),
        },
        "funeral_invoice": {
            "title": "Synthetic Funeral Home Invoice",
            "decedent": _party(matter, "decedent").get("full_name", person.get("full_name", base["name"])),
            "customer": signer.get("full_name", base["name"]),
            "services": "Professional services, transportation, and burial arrangements",
            "invoice_number": f"TEST-FH-{rng.randint(10000,99999)}",
            "total": _money(rng.randint(3500, 18000)),
            "balance_due": _money(rng.randint(500, 18000)),
        },
        "title_commitment": {
            "title": "Synthetic Title Commitment",
            "proposed_insured": _party(matter, "transferee").get("full_name", signer.get("full_name", base["name"])),
            "property": facts.get("property_address", "100 Example Lane"),
            "commitment_number": f"TEST-TITLE-{rng.randint(10000,99999)}",
            "estate": "Fee simple",
            "exceptions": "Taxes, utility easements, and recorded restrictions",
            "proposed_policy": _money(facts.get("purchase_price", rng.randint(180000, 900000))),
        },
        "closing_statement": {
            "title": "Synthetic Real Estate Closing Statement",
            "seller": _party(matter, "transferor").get("full_name", signer.get("full_name", base["name"])),
            "buyer": _party(matter, "transferee").get("full_name", "Buyer Q. Example"),
            "property": facts.get("property_address", "100 Example Lane"),
            "purchase_price": _money(facts.get("purchase_price", rng.randint(180000, 900000))),
            "seller_proceeds": _money(rng.randint(50000, 700000)),
            "buyer_cash_due": _money(rng.randint(5000, 180000)),
        },
        "lien_release": {
            "title": "Synthetic Lien Release",
            "creditor": company.get("full_name", "Example Creditor LLC"),
            "debtor": signer.get("full_name", base["name"]),
            "property": facts.get("property_address", "100 Example Lane"),
            "original_amount": _money(rng.randint(5000, 250000)),
            "release_date": meta.get("filing_date", "2026-04-01"),
            "authorized_signature": "Creditor Representative Q. Example",
        },
        "incident_report": {
            "title": "Synthetic Incident Report",
            "report_number": f"TEST-IR-{rng.randint(100000,999999)}",
            "reporting_person": person.get("full_name", base["name"]),
            "incident_date": meta.get("event_date", "2025-03-15"),
            "location": facts.get("collision_location", facts.get("incident_location", "Example location")),
            "summary": meta.get("summary", "Synthetic incident narrative"),
            "prepared_by": "Reporting Officer Q. Example",
        },
        "demand_letter": {
            "title": "Synthetic Pre-Litigation Demand Letter",
            "from": matter.get("parties", {}).get("attorney", {}).get("full_name", "Counsel Q. Example"),
            "to": _party(matter, "defendant", "respondent").get("full_name", "Other Party Q. Example"),
            "matter": meta.get("title", "Synthetic dispute"),
            "demand": _money(facts.get("amount_owed", facts.get("repair_cost_estimate", rng.randint(5000, 150000)))),
            "response_deadline": meta.get("filing_date", "2026-04-01"),
            "preservation_notice": "Preserve communications, account records, and electronically stored information",
        },
        "settlement_offer": {
            "title": "Synthetic Settlement Offer",
            "offeror": _party(matter, "defendant", "respondent").get("full_name", "Other Party Q. Example"),
            "offeree": signer.get("full_name", base["name"]),
            "matter": meta.get("title", "Synthetic dispute"),
            "offer_amount": _money(rng.randint(1000, 120000)),
            "terms": "Mutual release, no admission, and confidentiality subject to law",
            "expiration": meta.get("filing_date", "2026-04-01"),
        },
        "affidavit": {
            "title": "Synthetic Affidavit",
            "affiant": signer.get("full_name", base["name"]),
            "matter": meta.get("title", "Synthetic matter"),
            "statement_1": "I have personal knowledge of the facts stated here.",
            "statement_2": meta.get("summary", "This is a fictional statement for testing."),
            "affiant_signature": signer.get("full_name", base["name"]),
            "notary": "Taylor Q. Example, Test Notary",
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
        c.setFont("Helvetica", 9)
        lines = textwrap.wrap(str(value), width=65) or [""]
        for index, line in enumerate(lines):
            c.drawString(210, y - index * 12, line)
        bottom = y - (len(lines) - 1) * 12
        c.line(205, bottom - 3, width - 55, bottom - 3)
        y = bottom - 27
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
        words, lines, line = str(value).split(), [], ""
        for word in words:
            trial = f"{line} {word}".strip()
            if draw.textlength(trial, font=regular) > width - 530:
                lines.append(line); line = word
            else:
                line = trial
        lines.append(line)
        for index, text in enumerate(lines):
            draw.text((410, y + index * 25), text, fill=(0, 0, 0), font=regular)
        bottom = y + (len(lines) - 1) * 25
        draw.line((400, bottom + 25, width - 100, bottom + 25), fill=(90, 90, 90), width=1)
        y = bottom + 52
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


def _communication_participants(matter: dict, kind: str) -> tuple[dict, dict]:
    client = _party(matter, "client", "plaintiff", "personal_representative", "petitioner")
    attorney = matter.get("parties", {}).get("attorney", {})
    other = _party(matter, "defendant", "respondent", "transferee")
    third = (matter.get("third_parties") or [{}])[0]
    expert = (matter.get("expert_opinions") or [{}])[0].get("expert", {})
    pairs = {
        "client_other_party_texts": (client, other),
        "client_counsel_email": (client, attorney),
        "opposing_counsel_email": (attorney, {"full_name": "Opposing Counsel Q. Example"}),
        "witness_email": (attorney, {"full_name": third.get("name", "Witness Q. Example")}),
        "expert_email": (attorney, {"full_name": expert.get("name", "Expert Q. Example")}),
    }
    return pairs[kind]


def _comm_address(person: dict, fallback: str) -> str:
    if person.get("email"):
        return person["email"]
    name = person.get("full_name", fallback).lower().replace(" ", ".")
    return "".join(ch for ch in name if ch.isalnum() or ch == ".") + "@example.com"


def _comm_messages(matter: dict, kind: str, seed: int) -> list[dict]:
    rng = random.Random(f"{matter.get('provenance', {}).get('fixture_id')}:{kind}:{seed}")
    left, right = _communication_participants(matter, kind)
    left_name = left.get("full_name", "Jordan Q. Example")
    right_name = right.get("full_name", "Alex Q. Example")
    summary = matter.get("matter", {}).get("summary", "the disputed matter")
    base_time = datetime(2026, 1, 15, 14, 30, tzinfo=timezone.utc) + timedelta(days=rng.randint(0, 100))
    if kind == "client_other_party_texts":
        texts = [
            "I found the documents we discussed. The numbers do not match what you told me.",
            "You're missing the context. I paid several expenses directly.",
            "Please send the receipts and the account statements by Friday.",
            "I can send what I have, but I disagree that I owe the amount you're claiming.",
        ]
    elif kind == "client_counsel_email":
        texts = [
            f"I need advice about {summary}. I attached the records I have.",
            "Thank you. Please do not contact the other side directly while we review the evidence.",
        ]
    elif kind == "opposing_counsel_email":
        texts = [
            "Our client disputes liability but is willing to discuss preservation and an early exchange of records.",
            "We agree to preserve relevant communications. Please identify the categories you believe are missing.",
        ]
    elif kind == "witness_email":
        texts = [
            "I witnessed the meeting and can describe who was present and what was said.",
            "Please preserve your original messages and do not edit or annotate them. We will follow up about an interview.",
        ]
    else:
        texts = [
            "I have completed a preliminary review. My opinions may change after I receive the missing source records.",
            "Understood. Please identify each missing item and keep draft work product separate from the final report.",
        ]
    participants = [left_name, right_name]
    messages = []
    current = base_time
    for i, body in enumerate(texts):
        if i:
            current += timedelta(minutes=rng.randint(3, 18))
        messages.append({
            "from": participants[i % 2], "to": participants[(i + 1) % 2],
            "timestamp": current.isoformat(), "body": body,
        })
    return messages


def _draw_text_screenshot(path: Path, messages: list[dict], platform: str) -> None:
    Image, _, _, _, _, _ = _deps()
    from PIL import ImageDraw, ImageFont
    width, height = 720, 1280
    bg = (245, 245, 247) if platform == "iphone" else (250, 250, 250)
    image = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(image)
    regular = ImageFont.truetype("arial.ttf", 24)
    bold = ImageFont.truetype("arialbd.ttf", 25)
    draw.rectangle((0, 0, width, 90), fill=(235, 235, 238))
    draw.text((25, 25), "SYNTHETIC TEST CONVERSATION", fill=(170, 0, 0), font=bold)
    first_sender = messages[0]["from"]
    y = 125
    for message in messages:
        outgoing = message["from"] == first_sender
        x1, x2 = (250, 690) if outgoing else (30, 470)
        color = (45, 125, 245) if outgoing and platform == "iphone" else (
            (45, 145, 95) if outgoing else (225, 225, 230)
        )
        body = message["body"]
        words, lines, line = body.split(), [], ""
        for word in words:
            trial = f"{line} {word}".strip()
            if draw.textlength(trial, font=regular) > 390:
                lines.append(line); line = word
            else:
                line = trial
        lines.append(line)
        box_height = 38 * len(lines) + 45
        draw.rounded_rectangle((x1, y, x2, y + box_height), radius=25, fill=color)
        text_color = (255, 255, 255) if outgoing else (20, 20, 20)
        for idx, text in enumerate(lines):
            draw.text((x1 + 20, y + 15 + idx * 36), text, fill=text_color, font=regular)
        draw.text((x1, y + box_height + 5), message["timestamp"][11:16],
                  fill=(100, 100, 100), font=regular)
        y += box_height + 55
    image.save(path, "PNG")


def _write_eml(path: Path, messages: list[dict], kind: str) -> None:
    first = messages[0]
    msg = EmailMessage()
    msg["From"] = f"{first['from']} <sender@example.com>"
    msg["To"] = f"{first['to']} <recipient@example.com>"
    msg["Date"] = first["timestamp"]
    msg["Message-ID"] = f"<synthetic-{kind}@example.com>"
    msg["Subject"] = f"SYNTHETIC TEST - {kind.replace('_', ' ').title()}"
    body = [
        "SYNTHETIC TEST COMMUNICATION - NOT A REAL MESSAGE",
        "",
    ]
    for item in messages:
        body.extend([f"{item['timestamp']} - {item['from']} to {item['to']}:", item["body"], ""])
    msg.set_content("\n".join(body))
    path.write_bytes(msg.as_bytes(policy=SMTP))


def _export_outlook_msg(eml_path: Path, msg_path: Path) -> bool:
    """Best-effort true Outlook MSG export; unavailable on CI/non-Outlook systems."""
    if os.environ.get("MMCG_EXPORT_MSG") != "1":
        return False
    try:
        import win32com.client
        outlook = win32com.client.Dispatch("Outlook.Application")
        item = outlook.Session.OpenSharedItem(str(eml_path.resolve()))
        item.SaveAs(str(msg_path.resolve()), 3)
        return msg_path.exists()
    except Exception:
        return False


def generate_communication_pack(
    matter: dict, out_dir: str | Path, seed: int = 0, communication_types=None
) -> dict:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    kinds = communication_types or COMMUNICATION_TYPES
    artifacts = []
    for index, kind in enumerate(kinds):
        if kind not in COMMUNICATION_TYPES:
            raise ValueError(f"Unknown communication type '{kind}'")
        folder = out / kind
        folder.mkdir(parents=True, exist_ok=True)
        messages = _comm_messages(matter, kind, seed)
        truth = folder / f"{kind}.ground-truth.json"
        truth.write_text(json.dumps({
            "synthetic": True, "communication_type": kind, "messages": messages,
            "expected_classification": kind,
            "legal_context": {
                "privileged_expected": kind in {"client_counsel_email", "expert_email"},
                "third_party": kind in {"witness_email", "expert_email"},
                "pre_litigation": True,
            },
        }, indent=2) + "\n", encoding="utf-8")
        files = {"ground_truth": str(truth)}
        if kind == "client_other_party_texts":
            platform = "iphone" if seed % 2 else "android"
            screenshot = folder / f"{kind}.{platform}.png"
            _draw_text_screenshot(screenshot, messages, platform)
            files["screenshot"] = str(screenshot)
        else:
            eml = folder / f"{kind}.eml"
            msg = folder / f"{kind}.msg"
            _write_eml(eml, messages, kind)
            files["eml"] = str(eml)
            files["msg"] = str(msg) if _export_outlook_msg(eml, msg) else None
            files["msg_export_status"] = "created" if files["msg"] else "outlook-unavailable"
        artifacts.append({"communication_type": kind, "files": files})
    manifest = {
        "schema_version": "1.0", "synthetic": True,
        "fixture_id": matter.get("provenance", {}).get("fixture_id"),
        "artifacts": artifacts,
    }
    (out / "communication-pack.manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return manifest
