"""Export reviewed MOJ projections with explicit schemas and exact span checks.

This local gate verifies the supplied decisions and hashes. It cannot make the
underlying legal, fidelity or contextual privacy judgment for the publisher.
"""
import json
from pathlib import Path

from .core import canonical, sha256
from .rights_gate import select_supported


LAW_STRINGS = """document_id document_type title language source_family source_id source_url
capture_timestamp_utc issued_hijri_raw issued_gregorian_raw published_hijri_raw
published_gregorian_raw source_reported_status_at_capture text_ar text_search_ar
source_file_sha256 source_text_sha256 text_sha256 extraction_method processing_version
rights_basis source_pdf_sha256 source_document_id source_version_id source_sections_json
source_html_sha256 historical_original_pdf_sha256 historical_capture_export_hijri
historical_current_body_equivalence current_pdf_capture_timestamp_utc current_pdf_export_url
source_legal_status source_current_api_url official_material_kind formal_issuance_instrument
source_pdf_relationship pdf_printed_export_hijri_raw pdf_bytes_equal_historical_original
normative_classification_note privacy_review source_valid_from_raw source_gregorian_valid_from_raw
related_official_source_url""".split()
LAW_INTS = "removed_amendment_control_count article_count source_pdf_pages source_unit_count table_count".split()
COURT_STRINGS = """document_id version_id source_id source_url source_api_url opaque_route_id
source_family document_type language title judgment_number judgment_hijri_date_raw
judgment_gregorian_date_raw court_name city capture_timestamp_utc source_file_sha256
source_body_html_sha256 source_pdf_sha256 text_ar text_search_ar text_sha256 extraction_method
privacy_review rights_basis rights_source_url attribution source_components_json
appeal_number appeal_hijri_date_raw appeal_gregorian_date_raw appeal_court_name appeal_city source_pdf_url
source_pdf_creation_date_raw source_version_notice native_body_text_sha256 source_corrections_json
source_identity_kind source_capture_kind""".split()
SPAN_STRINGS = """source_section_id source_section_path source_sequence source_section_name
source_legal_status_name text_ar text_html unit_kind document_id source_id source_version_id
source_url source_document_url capture_timestamp_utc source_file_sha256 source_text_sha256
source_html_sha256 text_sha256 span_id""".split()
SPAN_INTS = "source_section_type heading_start start end source_ordinal source_legal_status_code".split()
SPAN_BOOLS = "source_is_published source_is_cancelled source_is_parent_cancelled".split()


def schemas():
    import pyarrow as pa
    from .core import document_arrow_schema
    strings=lambda names:[(k,pa.string()) for k in names]
    lists=lambda names:[(k,pa.list_(pa.string())) for k in names]
    laws=pa.schema(strings(LAW_STRINGS)+[(k,pa.int32()) for k in LAW_INTS]+[("source_is_temporary_save",pa.bool_())]
        +lists(["transformations","quality_flags","rights_evidence_urls"])
        +[("provenance",pa.list_(pa.struct(strings(["source_url","capture_timestamp_utc","source_file_sha256","source_text_sha256"]))))])
    courts=pa.schema(strings(COURT_STRINGS)+[("source_pdf_pages",pa.int32()),("source_component_count",pa.int32()),
        ("has_judgment",pa.bool_()),("has_appeal",pa.bool_())]
        +lists(["historical_source_pdf_sha256","transformations","quality_flags","rights_evidence_urls"]))
    spans=pa.schema(strings(SPAN_STRINGS)+[(k,pa.int32()) for k in SPAN_INTS]
        +[(k,pa.bool_()) for k in SPAN_BOOLS]+lists(["source_parent_ids"]))
    boe=document_arrow_schema(public=True).append(pa.field("privacy_review",pa.string()))
    boe_spans=pa.schema(strings("document_id span_id source_id source_url capture_timestamp_utc heading_raw text_ar text_sha256 evidence_pdf_sha256 evidence_heading_raw boundary_method".split())
        +[(k,pa.int32()) for k in "article_position start_char body_start_char end_char evidence_pdf_page evidence_pdf_line".split()])
    return {"laws":laws,"judgments":courts,"article_spans":spans,"source_sections":spans,
            "boe_documents":boe,"boe_article_spans":boe_spans}


def _read_rows(path):
    if path is None:return []
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def projection_sha256(row):
    """Review binding for source metadata and structure as well as body text.

    Decision-populated fields and the private triage helper are excluded. Only
    non-null fields are hashed so nullable Parquet columns remain reproducible.
    """
    excluded={"rights_basis","rights_evidence_urls","privacy_review","candidate_eligible"}
    return sha256(canonical({k:v for k,v in row.items() if k not in excluded and v is not None}).encode())


def _allowlisted(row,schema):
    unknown=set(row)-set(schema.names)-{"candidate_eligible"}
    if unknown:raise ValueError("Unreviewed export fields: "+", ".join(sorted(unknown)))
    return {k:row.get(k) for k in schema.names}


def _expected_native_units(parent):
    """Bind labels, hierarchy, HTML, offsets and citations to the captured tree."""
    from .moj_legislation import legislation_html_text
    native=json.loads(parent["source_sections_json"]);parts=[];offset=0;expected={}
    cancelled={n["id"] for n in native if n.get("isCancelled") is True}
    for ordinal,node in enumerate(native,1):
        sid=node["id"]
        if sid in expected:raise ValueError("Duplicate native source section ID")
        text,_=legislation_html_text(node.get("text") or "");kind=node["type"]
        label=(node.get("name") if node.get("name") and kind==4
            else " ".join(v for v in (node.get("sequence"),node.get("name")) if v))
        if parts:parts.append("\n\n");offset+=2
        heading_start=offset;parts.append(label);offset+=len(label)
        if label and text:parts.append("\n");offset+=1
        start=offset;parts.append(text);offset+=len(text)
        import re
        unit_kind=("article" if kind==1 and re.match(r"^الم[ـ]*ادة(?:\s|$)",node.get("sequence") or "")
            else "source_section" if kind==1 else "structural")
        unit={"source_section_id":sid,"source_section_path":node["source_path"],
            "source_parent_ids":node["parent_ids"],"source_section_type":kind,
            "source_sequence":node.get("sequence"),"source_section_name":node.get("name"),
            "source_is_published":node.get("isPublished"),"source_is_cancelled":node.get("isCancelled"),
            "source_is_parent_cancelled":any(p in cancelled for p in node["parent_ids"]),
            "source_legal_status_name":node.get("legalStatusName"),"source_legal_status_code":node.get("legalStatus"),
            "heading_start":heading_start,"start":start,"end":offset,"text_ar":text,"text_html":node.get("text") or "",
            "unit_kind":unit_kind,"source_ordinal":ordinal,"span_id":parent["document_id"]+":"+sid,
            "source_url":parent["source_url"]+"#content-card-"+sid,"source_document_url":parent["source_url"],
            "source_html_sha256":sha256((node.get("text") or "").encode()),"text_sha256":sha256(text.encode())}
        for key in ("document_id","source_id","source_version_id","capture_timestamp_utc","source_file_sha256","source_text_sha256"):
            unit[key]=parent[key]
        expected[sid]=unit
    if "".join(parts)!=parent["text_ar"]:raise ValueError("Native source hierarchy does not reconstruct the document body")
    return expected


def prepare_moj_text(laws_path,spans_path,judgments_path,decisions_path,output,boe_path=None,boe_spans_path=None):
    """Write a new, data-only candidate; never fetch, redact, rewrite or publish."""
    import pyarrow as pa
    import pyarrow.parquet as pq
    import yaml
    output=Path(output)
    if output.exists() or output.is_symlink():raise ValueError("Public output must be new")
    laws=_read_rows(laws_path);judgments=_read_rows(judgments_path);spans=_read_rows(spans_path);boe=_read_rows(boe_path)
    registry_bytes=Path(decisions_path).read_bytes();registry=json.loads(registry_bytes)
    decisions={d["document_id"]:d for d in registry.get("decisions",[])}
    supported=select_supported(laws+judgments+boe,registry)
    if not supported:raise ValueError("No supported nonempty text release")
    allowed_ids={r["document_id"] for r in supported}
    law_ids={r["document_id"] for r in laws};court_ids={r["document_id"] for r in judgments};boe_ids={r["document_id"] for r in boe}
    if law_ids&court_ids or law_ids&boe_ids or court_ids&boe_ids:raise ValueError("Source identities overlap")
    schema=schemas();groups={k:[] for k in schema};parents={};native_units={}
    for row in supported:
        if decisions[row["document_id"]].get("projection_sha256")!=projection_sha256(row):
            raise ValueError("Reviewed projection hash mismatch; metadata and structure need exact review binding")
        config="laws" if row["document_id"] in law_ids else "boe_documents" if row["document_id"] in boe_ids else "judgments"
        row["privacy_review"]=decisions[row["document_id"]]["privacy_review"]
        if not row.get("text_ar","").strip():raise ValueError("Empty document body")
        if config=="laws":
            native=row.get("source_sections_json")
            if not isinstance(native,str) or sha256(native.encode())!=row["source_text_sha256"]:
                raise ValueError("Native hierarchy hash mismatch")
            if not isinstance(json.loads(native),list):raise ValueError("Invalid native hierarchy")
            parents[row["document_id"]]=row
            native_units[row["document_id"]]=_expected_native_units(row)
        elif config=="judgments" and row.get("source_components_json"):
            components=json.loads(row["source_components_json"])
            if not isinstance(components,list) or len(components)!=row.get("source_component_count"):
                raise ValueError("Judicial source component count mismatch")
            slices=[]
            for c in components:
                allowed={"source_field","decision_level","source_html_sha256","text_sha256","start_char","end_char",
                    "text_characters","court_name","city","number","hijri_date_raw","gregorian_date_raw"}
                if set(c)-allowed:raise ValueError("Unreviewed nested judicial component fields")
                start,end=c["start_char"],c["end_char"]
                if type(start) is not int or type(end) is not int or not 0<=start<end<=len(row["text_ar"]):
                    raise ValueError("Invalid judicial component offsets")
                text=row["text_ar"][start:end];slices.append(text)
                if sha256(text.encode())!=c["text_sha256"] or not isinstance(c.get("source_html_sha256"),str) or len(c["source_html_sha256"])!=64:
                    raise ValueError("Judicial component source/body hash mismatch")
            if "\n\n".join(slices)!=row["text_ar"]:raise ValueError("Judicial body has unbound or overlapping component content")
        groups[config].append(_allowlisted(row,schema[config]))
    seen=set();counts={k:0 for k in parents};all_counts={k:0 for k in parents};empty=0;placeholders=0
    for unit in spans:
        if unit.get("document_id") not in allowed_ids:continue
        parent=parents.get(unit["document_id"])
        if parent is None:raise ValueError("Span must reference an instrument")
        key=unit.get("span_id")
        if not isinstance(key,str) or key in seen:raise ValueError("Duplicate or missing span ID")
        seen.add(key);all_counts[parent["document_id"]]+=1
        expected=native_units[parent["document_id"]].get(unit.get("source_section_id"))
        if expected is None or any(unit.get(k)!=v for k,v in expected.items()):
            raise ValueError("Source span metadata/HTML/citation differs from the native hierarchy")
        start,end=unit.get("start"),unit.get("end")
        if (type(start) is not int or type(end) is not int or not 0<=start<=end<=len(parent["text_ar"])
            or parent["text_ar"][start:end]!=unit.get("text_ar")):
            raise ValueError("Source span does not exactly slice its parent")
        for key in ("source_file_sha256","source_text_sha256","source_version_id","source_id"):
            if unit.get(key)!=parent.get(key):raise ValueError("Span source/version mismatch")
        if (sha256(unit["text_ar"].encode())!=unit.get("text_sha256")
            or sha256(unit["text_html"].encode())!=unit.get("source_html_sha256")):
            raise ValueError("Span text/HTML hash mismatch")
        kind=unit.get("unit_kind")
        if kind not in ("article","source_section","structural"):raise ValueError("Unknown source unit kind")
        if not unit["text_ar"].strip():
            if kind=="article":raise ValueError("Empty article cannot be published")
            empty+=1;continue
        if kind=="structural" and not any(c.isalnum() for c in unit["text_ar"]):
            placeholders+=1;continue
        config="article_spans" if kind=="article" else "source_sections"
        if kind=="article":counts[parent["document_id"]]+=1
        groups[config].append(_allowlisted(unit,schema[config]))
    for did,parent in parents.items():
        if counts[did]!=parent.get("article_count") or all_counts[did]!=parent.get("source_unit_count"):
            raise ValueError("Instrument source-unit/article count mismatch")
    boe_parents={r["document_id"]:r for r in groups["boe_documents"]};boe_counts={k:0 for k in boe_parents}
    boe_reviewed={k:[] for k in boe_parents}
    for original in _read_rows(boe_spans_path):
        did=original.get("document_id")
        if did not in allowed_ids:continue
        parent=boe_parents.get(did)
        if parent is None:raise ValueError("BOE span must have a BOE parent")
        row=original.copy();boe_counts[did]+=1
        if row.get("article_position")!=boe_counts[did]:raise ValueError("BOE article positions must be contiguous and ordered")
        start,body,end=row.get("start_char"),row.get("body_start_char"),row.get("end_char")
        if (any(type(v) is not int for v in (start,body,end)) or not 0<=start<body<end<=len(parent["text_ar"])
            or parent["text_ar"][start:end]!=row.get("text_ar") or parent["text_ar"][start:body]!=row.get("heading_raw")
            or sha256(row["text_ar"].encode())!=row.get("text_sha256")
            or row.get("evidence_pdf_sha256")!=parent["source_pdf_sha256"]):
            raise ValueError("BOE article source/heading/offset/hash mismatch")
        boe_reviewed[did].append(original)
        row.update(span_id=did+":article:"+str(row["article_position"]),source_id=parent["source_id"],
            source_url=parent["source_url"],capture_timestamp_utc=parent["capture_timestamp_utc"])
        groups["boe_article_spans"].append(_allowlisted(row,schema["boe_article_spans"]))
    for did,parent in boe_parents.items():
        count=parent["article_count"]
        if (count is None and boe_counts[did]) or (count is not None and count!=boe_counts[did]):
            raise ValueError("BOE article count mismatch")
        if decisions[did].get("article_spans_sha256")!=sha256("".join(canonical(u) for u in boe_reviewed[did]).encode()):
            raise ValueError("BOE heading evidence and article labels must bind to the reviewed span projection")
    output.mkdir(parents=True)
    configs=[];inventory=[]
    for config,rows in groups.items():
        if not rows:continue
        rows.sort(key=lambda r:(r["document_id"],r.get("source_ordinal",r.get("article_position",0))))
        shard_size=100 if config in ("laws","judgments","boe_documents") else 2000
        for n,start in enumerate(range(0,len(rows),shard_size)):
            target=output/f"{config}-{n:05d}.parquet"
            table=pa.Table.from_pylist(rows[start:start+shard_size],schema=schema[config])
            pq.write_table(table,target,compression="zstd",row_group_size=32,write_page_index=True)
            inventory.append({"path":target.name,"rows":len(table),"bytes":target.stat().st_size,"sha256":sha256(target.read_bytes())})
        configs.append({"config_name":config,"data_files":[{"split":"corpus","path":f"{config}-*.parquet"}]})
    configs[0]["default"]=True
    card={"language":["ar"],"license":"other","license_name":"saudi-official-text-source-terms","license_link":"RIGHTS.md","configs":configs}
    (output/"README.md").write_text("---\n"+yaml.safe_dump(card,allow_unicode=True,sort_keys=False)+"---\n# Reviewed MOJ text candidate\n\nAdd the source-specific rights, quality and reproduction documentation before publishing.\n")
    summary={"configuration_rows":{k:len(v) for k,v in groups.items() if v},"documents":len(supported),
             "empty_structural_units_omitted_from_rows":empty,"punctuation_only_structural_units_omitted_from_rows":placeholders,
             "rights_registry_sha256":sha256(registry_bytes),
             "parquet_files":inventory,"remote_publication":False}
    (output/"metrics.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
    safe=[{k:d[k] for k in ("document_id","text_sha256","source_file_sha256","projection_sha256","article_spans_sha256","decision","quality_review","privacy_review","rights_basis","evidence_urls","reason") if k in d}
          for d in registry["decisions"] if d["document_id"] in allowed_ids]
    (output/"record-reviews.jsonl").write_text("".join(canonical(d) for d in sorted(safe,key=lambda d:d["document_id"])))
    (output/"schema.json").write_text(json.dumps({k:[{"name":f.name,"type":str(f.type),"nullable":f.nullable} for f in schema[k]] for k,v in groups.items() if v},indent=2)+"\n")
    return summary
