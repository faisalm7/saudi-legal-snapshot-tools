"""Map captured PDF heading lines to exact offsets in a captured DOM legal body.

No legal text is rewritten. Ambiguous or unmatched sequences produce no table.
The intentionally lossy heading key is used for alignment only, never for output.
"""
import re
import unicodedata
from .core import sha256

ORDINAL_WORDS = set("الأولى الأول الاولى الاول الثانية الثاني الثالثة الثالث الرابعة الرابع الخامسة الخامس السادسة السادس السابعة السابع الثامنة الثامن التاسعة التاسع العاشرة العاشر الحادية الحادي الواحدة الواحد عشرة عشر والعشرون والعشرين والثلاثون والثلاثين والأربعون والأربعين والخمسون والخمسين والستون والستين والسبعون والسبعين والثمانون والثمانين والتسعون والتسعين العشرون العشرين الثلاثون الثلاثين الأربعون الأربعين الخمسون الخمسين الستون الستين السبعون السبعين الثمانون الثمانين التسعون التسعين المائة المئة والمائة والمئة بعد المائتين المئتين مكرر مكررة الأولى: الثانية: الثالثة: الرابعة: الخامسة: السادسة: السابعة: الثامنة: التاسعة: العاشرة:".split())


def heading_key(text):
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[\u0610-\u061a\u064b-\u065f\u0670ـ\u202a-\u202e\u2066-\u2069]", "", text)
    # PDF font mappings can duplicate or transpose lam/alef in headings.
    # Remove alef/hamza distinctions only in the alignment key.
    text = text.translate(str.maketrans({"أ": "", "إ": "", "آ": "", "ا": "", "ى": "ي", "ة": "ه"}))
    return re.sub(r"[\s:：().،\-]+", "", text)


VOCAB_KEYS = {heading_key(w) for w in ORDINAL_WORDS}


def heading_prefix(text, allowed_keys=None):
    """Return a maximal grammatical article-heading prefix, or None."""
    m = re.match(r"المادة\s+", text)
    if not m:
        return None
    rest = text[m.end():]
    num = re.match(r"\(?[0-9٠-٩]+\)?(?:\s+مكرر)?\s*:?[ \t]*", rest)
    if num:
        return text[:m.end()+num.end()].rstrip()
    end = m.end(); valid_ends=[]
    for token in re.finditer(r"\S+", rest):
        word = token[0].rstrip(":：")
        if heading_key(word) not in VOCAB_KEYS:
            break
        end = m.end()+token.end()
        if allowed_keys is None or heading_key(text[:end]) in allowed_keys:
            valid_ends.append(end)
        if token[0].endswith((":", "：")):
            break
        if token.end() > 100:
            break
    if allowed_keys is not None:
        return text[:valid_ends[-1]] if valid_ends else None
    return text[:end] if end > m.end() else None


def pdf_headings(pdf_text):
    result=[]
    for page_no,page in enumerate(pdf_text.split("\f"),1):
        for line_no,line in enumerate(page.splitlines(),1):
            line = re.sub(r"[\u202a-\u202e\u2066-\u2069]", "", unicodedata.normalize("NFKC",line)).strip()
            prefix=heading_prefix(line)
            # Isolated heading lines are structural source evidence. Inline
            # references or headings sharing a line with body text are deferred.
            if prefix and not line[len(prefix):].strip(" :："):
                result.append({"heading_pdf_raw":line,"key":heading_key(prefix),"page":page_no,"line":line_no})
    return result


def segment_with_pdf_evidence(record, pdf_text, pdf_sha256):
    headings=pdf_headings(pdf_text)
    allowed_keys={h['key'] for h in headings}
    text=record["text_ar"]
    candidates=[]
    for m in re.finditer(r"(?<!\w)المادة\s+",text):
        prefix=heading_prefix(text[m.start():],allowed_keys)
        if prefix:
            candidates.append({"start":m.start(),"end":m.start()+len(prefix),"heading_raw":prefix,"key":heading_key(prefix)})
    evidence={"document_id":record["document_id"],"pdf_sha256":pdf_sha256,"pdf_heading_count":len(headings),"dom_heading_candidate_count":len(candidates),"method":"exact_ordered_heading_key_alignment_v1","alignment_key_only":"NFKC,diacritic/tatweel/bidi/space/punctuation/alef removal; body unchanged"}
    if not headings:
        return [],{**evidence,"status":"deferred_no_isolated_pdf_headings"}
    # Count full ordered alignments, capped at two. Preamble citations can be
    # skipped only when the complete source-heading sequence has ONE mapping.
    ways=[1]+[0]*len(headings)
    for c in candidates:
        for j in range(len(headings)-1,-1,-1):
            if c["key"]==headings[j]["key"]:
                ways[j+1]=min(2,ways[j+1]+ways[j])
    evidence["full_ordered_alignment_count_capped_at_two"]=ways[-1]
    if ways[-1]!=1:
        return [],{**evidence,"status":"deferred_ambiguous_or_mismatched_heading_sequence"}
    chosen=[];cursor=0
    for h in headings:
        while candidates[cursor]["key"]!=h["key"]:
            cursor+=1
        chosen.append(candidates[cursor]);cursor+=1
    candidates=chosen
    if len({c["start"] for c in candidates})!=len(candidates):
        return [],{**evidence,"status":"deferred_duplicate_offsets"}
    rows=[]
    for i,(c,h) in enumerate(zip(candidates,headings)):
        end=candidates[i+1]["start"] if i+1<len(candidates) else len(text)
        body=text[c["end"]:end]
        if not body.strip():
            return [],{**evidence,"status":"deferred_empty_article_body"}
        rows.append({"document_id":record["document_id"],"article_position":i+1,"heading_raw":c["heading_raw"],"start_char":c["start"],"body_start_char":c["end"],"end_char":end,"text_ar":text[c["start"]:end],"text_sha256":sha256(text[c["start"]:end].encode()),"evidence_pdf_sha256":pdf_sha256,"evidence_pdf_page":h["page"],"evidence_pdf_line":h["line"],"evidence_heading_raw":h["heading_pdf_raw"],"boundary_method":"captured_pdf_isolated_heading_and_exact_dom_offset_v1"})
    return rows,{**evidence,"status":"aligned","article_rows":len(rows),"preamble_end_char":candidates[0]["start"]}
