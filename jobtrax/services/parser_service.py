"""
Rule-based paste parsing for JobTrax (docs/parsing-design.md).
Pure functions — no Flask imports.
"""

from __future__ import annotations

import re
from typing import Any

GENERIC_EMAIL_DOMAINS = frozenset(
    {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com"}
)


def normalize(text: str) -> str:
    text = text.replace("\r\n", "\n").strip()
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in text.split("\n")]
    return "\n".join(lines)


def parse_job_listing(text: str) -> dict[str, Any]:
    """Extract hints from pasted job posting text."""
    text = normalize(text)
    fields: dict[str, Any] = {
        "parsed_company_name": None,
        "parsed_job_title": None,
        "parsed_location": None,
        "parsed_deadline": None,
        "job_type": None,
        "salary_range": None,
    }

    for line in text.split("\n"):
        lm = re.match(
            r"(?i)^(?:company|employer)\s*:\s*(.+)$",
            line,
        )
        if lm:
            fields["parsed_company_name"] = lm.group(1).strip()
            continue
        tm = re.match(
            r"(?i)^(?:title|role|position)\s*:\s*(.+)$",
            line,
        )
        if tm:
            fields["parsed_job_title"] = tm.group(1).strip()
            continue
        loc = re.match(
            r"(?i)^location\s*:\s*(.+)$",
            line,
        )
        if loc:
            fields["parsed_location"] = loc.group(1).strip()

    if not fields["parsed_job_title"]:
        first = text.split("\n")[0] if text else ""
        if len(first) < 200 and first:
            fields["parsed_job_title"] = first

    sal = re.search(
        r"\$\d{1,3}(?:,\d{3})*(?:\s*-\s*\$\d{1,3}(?:,\d{3})*)?",
        text,
    )
    if sal:
        fields["salary_range"] = sal.group(0)

    for kw in ("internship", "full-time", "full time", "part-time", "contract"):
        if re.search(rf"(?i)\b{re.escape(kw)}\b", text):
            fields["job_type"] = kw
            break

    dm = re.search(
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
        text,
    )
    if dm:
        fields["parsed_deadline"] = dm.group(0)

    if not fields["parsed_location"]:
        if re.search(r"(?i)\bremote\b", text):
            fields["parsed_location"] = "Remote"
        elif re.search(r"(?i)\bhybrid\b", text):
            fields["parsed_location"] = "Hybrid"

    return fields


def guess_status_from_email(text: str) -> str | None:
    """Return a status_name hint from interview/rejection keywords."""
    t = text.lower()
    if any(k in t for k in ("congratulations", "offer", "compensation package")):
        return "Offer"
    if any(k in t for k in ("unfortunately", "not moving forward", "other candidates")):
        return "Rejected"
    if any(k in t for k in ("interview", "schedule", "next round")):
        return "Interviewing"
    if any(k in t for k in ("online assessment", "oa", "hackerrank", "codility")):
        return "OA"
    return None


def extract_email_contact(text: str) -> str | None:
    """Rough contact line from signature or From header."""
    for pat in (
        r"(?i)^From:\s*.+<([^>]+)>",
        r"(?i)Best(?:\s+regards)?,?\s*\n+\s*([A-Za-z][A-Za-z\s'.-]{2,40})$",
    ):
        m = re.search(pat, text, re.MULTILINE)
        if m:
            return m.group(1).strip() if "@" in m.group(1) else m.group(1).strip()
    return None


def company_from_email_domain(text: str) -> str | None:
    m = re.search(r"@([a-z0-9.-]+\.[a-z]{2,})", text, re.I)
    if not m:
        return None
    domain = m.group(1).lower()
    if domain in GENERIC_EMAIL_DOMAINS:
        return None
    part = domain.split(".")[0]
    return part.replace("-", " ").title()


def parse_email_paste(text: str) -> dict[str, Any]:
    text = normalize(text)
    fields = parse_job_listing(text)
    fields["parsed_contact_name"] = extract_email_contact(text)
    if not fields.get("parsed_company_name"):
        fields["parsed_company_name"] = company_from_email_domain(text)
    status_hint = guess_status_from_email(text)
    fields["status_hint"] = status_hint
    return fields


def parse(input_type: str, raw_text: str) -> dict[str, Any]:
    if input_type == "job_listing":
        return parse_job_listing(raw_text)
    if input_type == "email":
        return parse_email_paste(raw_text)
    raise ValueError("input_type must be job_listing or email")
