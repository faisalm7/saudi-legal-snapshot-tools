"""Project already acquired MOJ legislation JSON without fetching or clearing rights.

Only the native statuteStructure body is represented. Source summaries,
translations, relatedSections, workflow identifiers and attachments are excluded.
Exact per-unit HTML and hierarchy are retained alongside readable Arabic text.
"""
from datetime import datetime
from html.parser import HTMLParser
import json
import re
from urllib.parse import urlparse

from .core import normalize_search, sha256
from .inputs import read_utf8_input
from pathlib import Path


def _canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


class _BodyText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts=[];self.tags={};self.lists=[];self.unsupported=[];self.cell_depth=0

    def _sep(self, text="\n"):
        self.parts.append(" " if self.cell_depth and text=="\n" else text)

    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs);self.tags[tag]=self.tags.get(tag,0)+1
        if tag in ("td","th"):self.cell_depth+=1
        if tag in ("script","style","img","svg","canvas","math","object","iframe","video","audio","pre"):
            self.unsupported.append(tag)
        if tag in ("ol","ul"):
            start=attrs.get("start","1")
            self.lists.append([tag,int(start) if start.isdigit() else 1])
        if tag in ("p","div","h1","h2","h3","h4","h5","h6","tr","table","ul","ol","blockquote","br"):
            self._sep()
        if tag=="li":
            self._sep()
            if self.lists and self.lists[-1][0]=="ol":
                value=attrs.get("value")
                number=int(value) if value and value.isdigit() else self.lists[-1][1]
                self.parts.append(str(number)+". ");self.lists[-1][1]=number+1
            else:self.parts.append("• ")

    def handle_endtag(self, tag):
        if tag in ("td","th"):
            self.cell_depth=max(0,self.cell_depth-1);self._sep("\t")
        if tag in ("p","div","h1","h2","h3","h4","h5","h6","tr","table","li","ul","ol","blockquote"):
            self._sep()
        if tag in ("ol","ul") and self.lists:self.lists.pop()

    def handle_data(self, data):
        self.parts.append(re.sub(r"[ \t\r\n\f]+"," ",data))

    def text(self):
        text="".join(self.parts)
        text=re.sub(r" *\n *","\n",text)
        text=re.sub(r" *\t *","\t",text)
        text=re.sub(r"\t+\n","\n",text)
        return re.sub(r"\n{3,}","\n\n",text).strip()


def legislation_html_text(source):
    if not isinstance(source,str) or len(source)>2_000_000:
        raise ValueError("Supply bounded native MOJ body HTML")
    parser=_BodyText();parser.feed(source);parser.close()
    if parser.unsupported:
        raise ValueError("Embedded nontext or unsupported body markup needs separate review")
    text=parser.text()
    if "\ufffd" in text or any(ord(c)<32 and c not in "\n\r\t" for c in text):
        raise ValueError("Corrupted source text needs separate review")
    return text, parser.tags


def _nodes(nodes, path=(), parents=()):
    if not isinstance(nodes,list) or len(path)>30:
        raise ValueError("Unsupported source structure")
    for i,node in enumerate(nodes):
        if not isinstance(node,dict):
            raise ValueError("Source structure entries must be objects")
        position=path+(i,)
        yield position,parents,node
        children=node.get("items")
        if children is not None:
            yield from _nodes(children,position,parents+(node.get("id"),))


def decode_legislation_response(raw, source_url, captured_at):
    """Return document/source_spans/article_spans from one local response.

    source_url is the observed canonical MOJ /ar/legislation/<serial> citation.
    captured_at is its recorded UTC acquisition time. Neither is invented.
    The adapter does not fetch sources, infer permission or make a privacy decision.
    """
    if not isinstance(raw,bytes) or len(raw)>16_777_216:
        raise ValueError("Supply response bytes of at most 16 MiB")
    parsed=urlparse(source_url)
    if (parsed.scheme!="https" or parsed.netloc!="laws.moj.gov.sa" or parsed.query or parsed.fragment
        or not re.fullmatch(r"/ar/legislation/[A-Za-z0-9_=-]{1,256}",parsed.path)):
        raise ValueError("Supply a canonical public MOJ legislation citation")
    if not isinstance(captured_at,str):
        raise ValueError("Supply an explicit UTC capture time")
    stamp=datetime.fromisoformat(captured_at.replace("Z","+00:00"))
    if stamp.tzinfo is None or stamp.utcoffset().total_seconds()!=0:
        raise ValueError("Supply an explicit UTC capture time")
    response=json.loads(raw.decode("utf-8"))
    if not isinstance(response,dict) or response.get("success") is not True:
        raise ValueError("The source response was not successful")
    model=response.get("model")
    if not isinstance(model,dict) or model.get("serial")!=parsed.path.rsplit("/",1)[1]:
        raise ValueError("Source response/citation identity mismatch")
    version=model.get("statuteVersionId")
    if not isinstance(version,str) or not version or len(version)>256:
        raise ValueError("Missing or invalid source version")
    for key in ("name","legalType","legalStatueName"):
        if model.get(key) is not None and not isinstance(model[key],str):
            raise ValueError("Invalid source metadata")
    for key in ("validFromDate","gregorianValidFromDate","bureauOfExpertsAtTheCouncilOfMinistersUrl"):
        if model.get(key) is not None and not isinstance(model[key],str):raise ValueError("Invalid source date/reference metadata")
    if model.get("isTemporarySave") is not None and type(model["isTemporarySave"]) is not bool:
        raise ValueError("Invalid source draft state")
    nodes=list(_nodes(model.get("statuteStructure")))
    if not nodes or len(nodes)>20_000:
        raise ValueError("Missing or oversized source structure")
    parts=[];native=[];spans=[];seen=set();flags=[];table_count=0;body_size=0;position=0
    cancelled={node.get("id") for _,_,node in nodes if node.get("isCancelled") is True}
    for path,parents,node in nodes:
        sid=node.get("id")
        if not isinstance(sid,str) or not sid or len(sid)>256 or sid in seen:
            raise ValueError("Missing, duplicate or invalid source section ID")
        seen.add(sid)
        kind=node.get("type")
        if isinstance(kind,bool) or kind not in (1,2,3,4,5,6):
            raise ValueError("Unsupported source unit type")
        for key in ("sequence","name","text"):
            if node.get(key) is not None and not isinstance(node[key],str):
                raise ValueError("Source body fields must be strings or null")
        for key in ("isPublished","isCancelled"):
            if node.get(key) is not None and not isinstance(node[key],bool):
                raise ValueError("Source state flags must be booleans or null")
        text,tags=legislation_html_text(node.get("text")or"")
        body_size+=len(text)
        if body_size>8_000_000:
            raise ValueError("Oversized source body")
        table_count+=tags.get("table",0)
        if node.get("isPublished") is False:flags.append("source_node_unpublished_flag_rendered_by_frontend")
        if node.get("isCancelled") is True:flags.append("contains_source_cancelled_nodes")
        if node.get("supportedFiles"):flags.append("source_section_has_supporting_files_not_reproduced")
        if node.get("relatedSections"):flags.append("auxiliary_related_sections_excluded")
        label=(node.get("name") if node.get("name") and kind==4
               else " ".join(v for v in (node.get("sequence"),node.get("name")) if v))
        if parts:parts.append("\n\n");position+=2
        heading_start=position;parts.append(label);position+=len(label)
        if label and text:parts.append("\n");position+=1
        start=position;parts.append(text);position+=len(text)
        source_path="/statuteStructure/"+"/items/".join(map(str,path))
        item={key:node.get(key) for key in ("id","type","sequence","name","text","isPublished","isCancelled","legalStatusName","legalStatus")}
        item.update(parent_ids=list(parents),source_path=source_path);native.append(item)
        spans.append({"source_section_id":sid,"source_section_path":source_path,"source_parent_ids":list(parents),
                      "source_section_type":kind,"source_sequence":node.get("sequence"),"source_section_name":node.get("name"),
                      "source_is_published":node.get("isPublished"),"source_is_cancelled":node.get("isCancelled"),
                      "source_is_parent_cancelled":any(p in cancelled for p in parents),
                      "source_legal_status_name":node.get("legalStatusName"),"source_legal_status_code":node.get("legalStatus"),
                      "heading_start":heading_start,"start":start,"end":position,"text_ar":text,"text_html":node.get("text")or"",
                      "unit_kind":"article" if kind==1 and re.match(r"^الم[ـ]*ادة(?:\s|$)",node.get("sequence")or"")
                                  else "source_section" if kind==1 else "structural"})
    text="".join(parts)
    if not body_size:raise ValueError("Missing native source body")
    digest=sha256(text.encode());raw_hash=sha256(raw);source_json=_canonical(native);source_hash=sha256(source_json.encode())
    did="moj-legislation:"+sha256((source_url+"\n"+version+"\n"+digest).encode())
    if table_count:flags.append("tables_retained_in_native_html_and_tabular_plaintext")
    document={"document_id":did,"source_document_id":model.get("statuteId"),"source_version_id":version,
              "source_id":model["serial"],"source_url":source_url,"source_family":"MOJ_legislation",
              "document_type":model.get("legalType"),"title":model.get("name"),"language":"ar",
              "capture_timestamp_utc":captured_at,"issued_hijri_raw":model.get("issuanceDate"),
              "issued_gregorian_raw":model.get("issuanceDateGerogian"),"published_hijri_raw":model.get("publishDate"),
              "published_gregorian_raw":model.get("publishDateGerogian"),
              "source_reported_status_at_capture":model.get("legalStatueName"),"source_legal_status":model.get("legalStatus"),
              "source_file_sha256":raw_hash,"source_text_sha256":source_hash,
              "source_html_sha256":sha256(_canonical([n.get("text")or"" for _,_,n in nodes]).encode()),
              "source_sections_json":source_json,"text_ar":text,"text_search_ar":normalize_search(text),"text_sha256":digest,
              "source_unit_count":len(spans),"article_count":sum(u["unit_kind"]=="article" for u in spans),
              "table_count":table_count,"rights_basis":None,"privacy_review":None,"quality_flags":sorted(set(flags)),
              "extraction_method":"current_MOJ_API_statuteStructure_frontend_order_native_HTML_to_text",
              "formal_issuance_instrument":model.get("issuanceDepartmentTool")}
    document.update(source_valid_from_raw=model.get("validFromDate"),
                    source_gregorian_valid_from_raw=model.get("gregorianValidFromDate"),
                    source_is_temporary_save=model.get("isTemporarySave"),
                    related_official_source_url=model.get("bureauOfExpertsAtTheCouncilOfMinistersUrl"))
    for i,unit in enumerate(spans):
        unit.update(document_id=did,source_id=model["serial"],source_version_id=version,
                    source_url=source_url+"#content-card-"+unit["source_section_id"],source_document_url=source_url,
                    capture_timestamp_utc=captured_at,source_file_sha256=raw_hash,source_text_sha256=source_hash,
                    source_html_sha256=sha256(unit["text_html"].encode()),text_sha256=sha256(unit["text_ar"].encode()),
                    span_id=did+":"+unit["source_section_id"],source_ordinal=i+1)
    return {"document":document,"source_spans":spans,"article_spans":[u for u in spans if u["unit_kind"]=="article"]}


def capture_legislation(response_file, source_url, captured_at, output):
    """Project a user-acquired response into a new local JSON file."""
    raw=read_utf8_input(response_file)
    projected=decode_legislation_response(raw,source_url,captured_at)
    output=Path(output)
    if output.exists() or output.is_symlink():
        raise ValueError("Refusing to overwrite existing output")
    with output.open("x",encoding="utf-8") as stream:
        stream.write(_canonical(projected)+"\n")
    return {"documents":1,"source_units":len(projected["source_spans"]),
            "articles":len(projected["article_spans"]),"source_fetched":False,
            "publication_permission_inferred":False}

