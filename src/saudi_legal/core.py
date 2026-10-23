"""Conservative, versioned transformations of source JSON; never reverse Arabic."""
import hashlib
import json
import re
import unicodedata
from urllib.parse import urlparse

VERSION = "0.3.0"
MARKER = "ن ص النظ ام"
URL = re.compile(r"^/BoeLaws/Laws/LawDetails/([0-9a-fA-F-]{36})/1/?$")
# Processing eligibility is independent of publication permission. Only a reviewed
# hash-specific rights decision may populate a public release's rights basis.
RIGHTS = None


def document_arrow_schema(public=False):
    """One nullable schema for every shard, including all-null optional fields."""
    import pyarrow as pa
    names = (
        "document_id document_type title language source_family source_id source_url "
        "capture_timestamp_utc issued_hijri_raw issued_gregorian_raw published_hijri_raw "
        "published_gregorian_raw source_reported_status_at_capture text_ar text_search_ar "
        "source_file_sha256 source_text_sha256 text_sha256 extraction_method processing_version "
        "transformations removed_amendment_control_count quality_flags article_count rights_basis "
        "provenance source_pdf_sha256 source_pdf_pages"
    ).split()
    types = {k: pa.string() for k in names}
    for k in ("transformations", "quality_flags"):
        types[k] = pa.list_(pa.string())
    for k in ("article_count", "removed_amendment_control_count", "source_pdf_pages"):
        types[k] = pa.int32()
    types["provenance"] = pa.list_(pa.struct([(k, pa.string()) for k in (
        "source_url", "capture_timestamp_utc", "source_file_sha256", "source_text_sha256")]))
    if public:
        names.append("rights_evidence_urls")
        types["rights_evidence_urls"] = pa.list_(pa.string())
    return pa.schema([(name, types[name]) for name in names])


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def source_id(url):
    if not isinstance(url, str):
        return None
    p = urlparse(url)
    if p.scheme != "https" or p.netloc != "laws.boe.gov.sa" or p.query or p.fragment:
        return None
    m = URL.fullmatch(p.path)
    if not m:
        return None
    import uuid
    try:
        return str(uuid.UUID(m[1]))
    except ValueError:
        return None


def clean_body(raw):
    """Keep the exact suffix after the observed portal label; no inferred articles."""
    if raw.count(MARKER) != 1:
        raise ValueError("missing_or_ambiguous_legal_body_marker")
    prefix, body = raw.split(MARKER, 1)
    # Literal portal control only. Keep amendment text and citations that follow it.
    body, removed = re.subn(r"(?<!\S)تعديلات المادة(?!\S)", "", body)
    body = body.replace("\r\n", "\n").replace("\r", "\n")
    body = re.sub(r"[ \t]{2,}", " ", body).strip()
    body = unicodedata.normalize("NFC", body)
    return prefix, body, removed


def normalize_search(text):
    t = unicodedata.normalize("NFKC", text)
    t = re.sub(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06edـ]", "", t)
    return t.translate(str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا"}))


def date_fields(prefix, label, stop):
    # Preserve both source date strings. No Hijri conversion or guessed date.
    m = re.search(re.escape(label) + r"\s+(.+?)\s+" + re.escape(stop), prefix)
    if not m:
        return None, None
    m2 = re.fullmatch(r"([0-9٠-٩/ ]+)\s*ه\s+الموافق\s*:\s*([0-9٠-٩/ ]+)\s*م", m[1])
    return (m2[1].strip(), m2[2].strip()) if m2 else (None, None)


def make_record(data, file_hash):
    if not isinstance(data, dict):
        raise ValueError("invalid_source_object")
    s = data.get("source") or {}
    if not isinstance(s, dict):
        raise ValueError("unverified_official_source_url")
    sid = source_id(s.get("url"))
    if not sid:
        raise ValueError("unverified_official_source_url")
    raw = data.get("full_text")
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError("empty_source_text")
    if sha256(raw.encode()) != s.get("hash_sha256"):
        raise ValueError("captured_text_hash_mismatch")
    title = data.get("title")
    if not isinstance(title, str) or not title.strip() or title == "بدون عنوان":
        raise ValueError("missing_source_title")
    if data.get("status") is not None and not isinstance(data["status"], str):
        raise ValueError("invalid_source_status_type")
    capture = s.get("captured_at_utc")
    from datetime import datetime
    try:
        dt = datetime.fromisoformat(capture.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            raise ValueError()
    except (AttributeError, TypeError, ValueError):
        raise ValueError("invalid_capture_timestamp") from None
    prefix, text, removed = clean_body(raw)
    if len(text) < 200:
        raise ValueError("insufficient_official_body")
    if "عدد مرات التصفح" in text or "نبذة عن النظام" in text:
        raise ValueError("residual_portal_boilerplate")
    if any(0xfb50 <= ord(c) <= 0xfdff or 0xfe70 <= ord(c) <= 0xfeff for c in text):
        raise ValueError("unreviewed_presentation_forms")
    if "\ufffd" in text or "\x00" in text:
        raise ValueError("replacement_or_null_character")
    if sum("\u0600" <= c <= "\u06ff" for c in text) / len(text) < .35:
        raise ValueError("low_arabic_ratio")
    issue_h, issue_g = date_fields(prefix, "تاريخ الإصدار", "تاريخ النشر")
    pub_h, pub_g = date_fields(prefix, "تاريخ النشر", "الحالة")
    flags = ["historical_snapshot_not_current_law", "article_boundaries_unverified", "layout_and_media_not_preserved"]
    if "\n" not in text:
        flags.append("upstream_whitespace_flattened")
    if not issue_h:
        flags.append("issue_date_unknown")
    if not pub_h:
        flags.append("publication_date_unknown")
    if "أصل الوثيقة" in text:
        flags.append("source_refers_to_omitted_illustration")
    h = sha256(text.encode())
    return {
        "document_id": f"sa-boe-{sid}-ar-{h[:16]}",
        "document_type": "official_legal_instrument",
        "title": unicodedata.normalize("NFC", title.strip()),
        "language": "ar", "source_family": "boe",
        "source_id": sid, "source_url": s["url"],
        "capture_timestamp_utc": capture,
        "issued_hijri_raw": issue_h, "issued_gregorian_raw": issue_g,
        "published_hijri_raw": pub_h, "published_gregorian_raw": pub_g,
        "source_reported_status_at_capture": data.get("status"),
        "text_ar": text, "text_search_ar": normalize_search(text),
        "source_file_sha256": file_hash, "source_text_sha256": s["hash_sha256"],
        "text_sha256": h, "extraction_method": "reuse_" + s["input_method"] if s.get("input_method") in ("user_supplied_utf8_body", "user_supplied_utf8_page") else "reuse_captured_dom_inner_text",
        "processing_version": VERSION,
        "transformations": ["exact_legal_body_suffix", "remove_literal_amendment_ui_control", "CRLF_to_LF", "collapse_repeated_horizontal_spaces", "trim_outer_whitespace", "unicode_NFC", "separate_search_NFKC_diacritics_tatweel_alef"],
        "removed_amendment_control_count": removed,
        "quality_flags": sorted(flags), "article_count": None,
        "rights_basis": RIGHTS,
        "provenance": [{"source_url": s["url"], "capture_timestamp_utc": capture, "source_file_sha256": file_hash, "source_text_sha256": s["hash_sha256"]}],
    }


def deduplicate(records):
    """Exact text only; keep all provenances. Never merge near versions."""
    groups = {}
    for r in sorted(records, key=lambda x: x["document_id"]):
        h = r["text_sha256"]
        if h not in groups:
            groups[h] = r.copy()
            groups[h]["provenance"] = list(r["provenance"])
        else:
            groups[h]["provenance"].extend(r["provenance"])
    for r in groups.values():
        r["provenance"] = sorted({canonical(p): p for p in r["provenance"]}.values(), key=canonical)
    return sorted(groups.values(), key=lambda r: r["document_id"])
