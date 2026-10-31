"""Decode an already acquired official MOJ Supreme Court API response locally.

No source is downloaded, anonymized or cleared for publication by this adapter.
"""
from datetime import datetime
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unicodedata
from urllib.parse import urlparse
from uuid import UUID

from .core import canonical, sha256


class SourceText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True);self.parts=[];self.skip=0;self.nontext=[]

    def handle_starttag(self,tag,attrs):
        if tag in ('script','style'):self.skip+=1
        if tag in ('p','div','li','br','h1','h2','h3','h4','tr'):self.parts.append('\n')
        if tag in ('td','th'):self.parts.append('\t')
        if tag in ('img','object','iframe','canvas','math'):self.nontext.append(tag)

    def handle_endtag(self,tag):
        if tag in ('script','style'):self.skip=max(0,self.skip-1)
        if tag in ('p','div','li','h1','h2','h3','h4','tr'):self.parts.append('\n')

    def handle_data(self,data):
        if not self.skip:self.parts.append(data)


def html_body_text(source):
    if not isinstance(source,str):raise ValueError('Official body HTML must be a string')
    p=SourceText();p.feed(source);p.close()
    if p.nontext:raise ValueError('Embedded nontext source content needs separate review')
    text=''.join(p.parts).replace('\r\n','\n').replace('\r','\n').replace('\xa0',' ')
    return unicodedata.normalize('NFC',re.sub(r'\n[ \t]*\n+','\n\n',text).strip())


def decode_supreme_response(raw,source_url,captured_at):
    parsed=urlparse(source_url)
    if parsed.scheme!='https' or parsed.netloc!='laws.moj.gov.sa' or parsed.query or parsed.fragment or not re.fullmatch(r'/ar/JudicialDecisionsList/3/[A-Za-z0-9_=-]+',parsed.path):
        raise ValueError('Supply a canonical public MOJ Supreme Court citation')
    dt=datetime.fromisoformat(captured_at.replace('Z','+00:00'))
    if dt.tzinfo is None or dt.utcoffset().total_seconds()!=0:raise ValueError('Supply an explicit UTC capture time')
    response=json.loads(raw);model=response.get('model') or {}
    if response.get('success') is not True or not model.get('hasJudgment') or model.get('hasAppeal') or 'العليا' not in (model.get('judgmentCourtName') or ''):
        raise ValueError('Only the reviewed Supreme Court ruling-body shape is supported')
    if any(model.get(k) for k in ('judgmentFacts','judgmentReasons','judgmentRuling','appealFacts','appealReasons','appealRuling','appealTextofRulling','judgmentNarrationList')):
        raise ValueError('Additional substantive source sections need a separate adapter/review')
    sid=str(UUID(model['id']));body=model.get('judgmentTextofRulling')
    if not isinstance(body,str) or re.search(r'<\s*/?\s*(?!br\b|p\b)[A-Za-z][^>]*>',body,re.I):
        raise ValueError('Additional body markup needs separate handling')
    text=html_body_text(body)
    if not text or '\ufffd' in text or '\x00' in text:raise ValueError('Missing or corrupted official body')
    digest=sha256(text.encode());doc=f'sa-moj-{sid}-ar'
    return {'document_id':doc,'version_id':doc+'-'+digest[:16],'source_id':sid,'source_url':source_url,
            'source_family':'moj_judgments','document_type':'supreme_court_decision','language':'ar',
            'title':model.get('title'),'judgment_number':model.get('judgmentNumber'),
            'judgment_hijri_date_raw':model.get('judgmentHijriiDate'),'judgment_gregorian_date_raw':model.get('judgmentDate'),
            'court_name':model.get('judgmentCourtName'),'city':model.get('judgmentCityName'),
            'capture_timestamp_utc':captured_at,'source_file_sha256':sha256(raw),
            'source_body_html_sha256':sha256(body.encode()),'text_ar':text,'text_sha256':digest,
            'extraction_method':'official_api_html_text_nodes_v1','rights_basis':None,
            'privacy_review':None,'quality_flags':['current_capture_not_a_reconstruction_of_a_historical_pdf',
                                                       'publisher_masking_is_not_an_anonymity_certificate']}


def capture_supreme(response_file,source_url,captured_at,output):
    out=Path(output)
    if out.exists() or out.is_symlink():raise ValueError('Output must be new; existing work is preserved')
    source=Path(response_file)
    from .inputs import read_utf8_input
    raw=read_utf8_input(source)
    record=decode_supreme_response(raw,source_url,captured_at)
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('xb') as f:f.write(canonical(record).encode())
    return {'document_id':record['document_id'],'source_file_sha256':record['source_file_sha256'],
            'text_sha256':record['text_sha256'],'publication_permission_inferred':False,'source_fetched':False}



class CaseFormatting(HTMLParser):
    """Recognize only observed inline formatting with no substantive attributes."""
    def handle_starttag(self,tag,attrs):
        if tag not in ('p','br','span','ul','li','strong'):
            raise ValueError('Additional body markup needs separate handling')
        if tag=='strong' and attrs:
            raise ValueError('Additional emphasis attributes need separate handling')
        if tag in ('ul','li') and attrs:
            raise ValueError('Additional list attributes need separate handling')
        if tag=='br' and attrs:
            raise ValueError('Additional line-break attributes need separate handling')
        if tag=='p' and attrs not in ([], [('style','text-align: justify;')], [('style','text-align: right;')],
                                     [('style','direction: ltr; text-align: right;')], [('style','direction: ltr;')]):
            raise ValueError('Additional paragraph attributes need separate handling')
        observed_styles=('vertical-align: inherit;','font-size: ١٤pt;','font-size: 14pt;','color: rgb(0, 0, 0);')
        if tag=='span' and not (len(attrs)==1 and attrs[0][0]=='style' and attrs[0][1] in observed_styles):
            raise ValueError('Additional span attributes need separate handling')

    def handle_endtag(self,tag):
        if tag not in ('p','br','span','ul','li','strong'):
            raise ValueError('Additional body markup needs separate handling')


def decode_case_response(raw,source_url,captured_at):
    """Project complete native judgment/appeal HTML fields from a local response.

    This supports observed br/p, attribute-free emphasis/unordered lists and transparent
    vertical-align or 14pt spans. Other fields or media require explicit handling.
    A publication record can contain two judicial bodies; it is not two rows.
    """
    parsed=urlparse(source_url)
    if (parsed.scheme!='https' or parsed.netloc!='laws.moj.gov.sa' or parsed.query or parsed.fragment
        or not re.fullmatch(r'/ar/JudicialDecisionsList/[0123]/[A-Za-z0-9_=-]+',parsed.path)):
        raise ValueError('Supply a canonical public MOJ judicial citation')
    if not isinstance(raw,bytes) or len(raw)>16_777_216:raise ValueError('Supply bounded response bytes')
    dt=datetime.fromisoformat(captured_at.replace('Z','+00:00'))
    if dt.tzinfo is None or dt.utcoffset().total_seconds()!=0:raise ValueError('Supply an explicit UTC capture time')
    response=json.loads(raw);model=response.get('model')
    if response.get('success') is not True or not isinstance(model,dict):raise ValueError('Invalid official response')
    if any(model.get(k) for k in ('judgmentFacts','judgmentReasons','judgmentRuling','appealFacts','appealReasons','appealRuling','judgmentNarrationList','appealNarrationList')):
        raise ValueError('Additional substantive source sections need separate handling')
    components=[];parts=[];offset=0
    for level,field in (('judgment','judgmentTextofRulling'),('appeal','appealTextofRulling')):
        value=model.get(field)
        has=model.get('hasJudgment' if level=='judgment' else 'hasAppeal')
        if type(has) is not bool:raise ValueError('Source component state must be explicit')
        if not has:
            if value:raise ValueError('Body conflicts with source component state')
            continue
        if not isinstance(value,str) or not value.strip():raise ValueError('Missing complete source body')
        formatting=CaseFormatting();formatting.feed(value);formatting.close()
        text=html_body_text(value)
        if not text or '\ufffd' in text or '\x00' in text:raise ValueError('Missing or corrupted source body')
        if parts:offset+=2
        start=offset;parts.append(text);offset+=len(text)
        components.append({'source_field':field,'decision_level':level,
            'source_html_sha256':sha256(value.encode()),'text_sha256':sha256(text.encode()),
            'start_char':start,'end_char':offset,'text_characters':len(text),
            'court_name':model.get(level+'CourtName'),'city':model.get(level+'CityName'),
            'number':model.get(level+'Number'),'hijri_date_raw':model.get(level+'HijriiDate'),
            'gregorian_date_raw':model.get(level+'Date')})
    if not parts:raise ValueError('No published judicial body')
    sid=str(UUID(model['id']));doc=f'sa-moj-{sid}-ar';text='\n\n'.join(parts);digest=sha256(text.encode())
    row={'document_id':doc,'version_id':doc+'-'+digest[:16],'source_id':sid,'source_url':source_url,
         'source_family':'moj_judgments','document_type':'judgment_and_appeal_publication_record' if len(parts)==2
              else 'judgment_publication_record' if model['hasJudgment'] else 'appeal_publication_record',
         'language':'ar','title':model.get('title'),'capture_timestamp_utc':captured_at,
         'source_file_sha256':sha256(raw),'source_body_html_sha256':components[0]['source_html_sha256'] if len(components)==1 else None,
         'source_components_json':json.dumps(components,ensure_ascii=False,sort_keys=True,separators=(',',':')),
         'source_component_count':len(components),'has_judgment':model['hasJudgment'],'has_appeal':model['hasAppeal'],
         'text_ar':text,'text_sha256':digest,'extraction_method':'official_api_complete_html_fields_v1',
         'rights_basis':None,'privacy_review':None}
    for level in ('judgment','appeal'):
        row[level+'_number']=model.get(level+'Number')
        row[level+'_hijri_date_raw']=model.get(level+'HijriiDate')
        row[level+'_gregorian_date_raw']=model.get(level+'Date')
    row.update(court_name=model.get('judgmentCourtName'),city=model.get('judgmentCityName'),
               appeal_court_name=model.get('appealCourtName'),appeal_city=model.get('appealCityName'))
    row['quality_flags']=[]
    if any('direction: ltr;' in model[c['source_field']] for c in components):
        row['quality_flags'].append('publisher_ltr_paragraph_direction_plaintext_keeps_logical_text_node_order')
    if any(re.search(r'<\s*(?:ul|li)\b',model[c['source_field']],re.I) for c in components):
        row['quality_flags'].append('unordered_list_boundaries_preserved_as_line_breaks')
    if any('vertical-align: inherit;' in model[c['source_field']] for c in components):
        row['quality_flags'].append('transparent_inline_vertical_align_span_removed')
    if any('color: rgb(0, 0, 0);' in model[c['source_field']] for c in components):
        row['quality_flags'].append('publisher_black_text_colour_style_removed_text_nodes_unchanged')
    if any('font-size:' in model[c['source_field']] for c in components):
        row['quality_flags'].append('transparent_inline_14pt_font_size_span_removed')
    if row['title'] in ('--','-',''):
        row['title']=None
        row['quality_flags'].append('publisher_title_placeholder_retained_as_null')
    for present,fields in (
        (row['has_judgment'],('judgment_number','judgment_hijri_date_raw','judgment_gregorian_date_raw','court_name','city')),
        (row['has_appeal'],('appeal_number','appeal_hijri_date_raw','appeal_gregorian_date_raw','appeal_court_name','appeal_city'))):
        if present:continue
        if any(row.get(k) not in (None,'') for k in fields):
            row['quality_flags'].append('inactive_component_metadata_not_promoted')
        for key in fields:row[key]=None
    return row


def capture_case(response_file,source_url,captured_at,output):
    from .inputs import read_utf8_input
    record=decode_case_response(read_utf8_input(response_file),source_url,captured_at);out=Path(output)
    if out.exists() or out.is_symlink():raise ValueError('Output must be new')
    with out.open('x',encoding='utf-8') as stream:stream.write(canonical(record))
    return {'document_id':record['document_id'],'source_components':record['source_component_count'],
            'source_fetched':False,'publication_permission_inferred':False}


def validate_case_components(row):
    """Check reviewed body boundaries and the declared source evidence shape.

    Historical PDF page inspections are hash-bound review claims, not a fresh
    verification of private PDF bytes. They never stand in for source HTML.
    """
    encoded=row.get('source_components_json')
    # Earlier reviewed PDF editions have no nested component representation.
    # Keep that existing path; the new opaque-route/page-claim shape is explicit.
    historical=(row.get('extraction_method')=='official_historical_pdf_complete_visual_transcription_v1'
                and (bool(encoded) or row.get('source_identity_kind')==
                     'frozen_official_opaque_route_and_exact_historical_PDF_no_model_UUID'))
    if not encoded and not historical:return
    try:components=json.loads(encoded)
    except (TypeError,ValueError) as exc:raise ValueError('Invalid judicial source components') from exc
    if not isinstance(components,list) or len(components)!=row.get('source_component_count'):
        raise ValueError('Judicial source component count mismatch')
    allowed={'source_field','decision_level','source_html_sha256','text_sha256','start_char','end_char',
             'text_characters','court_name','city','number','hijri_date_raw','gregorian_date_raw'}
    if historical:
        allowed=(allowed-{'source_field','source_html_sha256'})|{'source_pdf_pages','complete_document_pages_inspected'}
        _validate_historical_pdf_identity(row,components)
    parts=[]
    for c in components:
        if not isinstance(c,dict) or set(c)-allowed:
            raise ValueError('Unreviewed nested judicial component fields')
        start,end=c.get('start_char'),c.get('end_char')
        if type(start) is not int or type(end) is not int or not 0<=start<end<=len(row['text_ar']):
            raise ValueError('Invalid judicial component offsets')
        text=row['text_ar'][start:end];parts.append(text)
        if sha256(text.encode())!=c.get('text_sha256'):
            raise ValueError('Judicial component source/body hash mismatch')
        if historical:
            if type(c.get('text_characters')) is not int or c['text_characters']!=len(text):
                raise ValueError('Historical PDF component character count mismatch')
        elif not isinstance(c.get('source_html_sha256'),str) or len(c['source_html_sha256'])!=64:
            raise ValueError('Judicial component source/body hash mismatch')
    if '\n\n'.join(parts)!=row['text_ar']:
        raise ValueError('Judicial body has unbound or overlapping component content')


def _validate_historical_pdf_identity(row,components):
    """Check one complete first-instance, appeal-only, or combined PDF edition."""
    digest=row.get('source_pdf_sha256');pages=row.get('source_pdf_pages')
    appeal=row.get('document_type')=='commercial_court_historical_appeal'
    combined=row.get('document_type')=='commercial_court_historical_judgment_and_appeal'
    if (not isinstance(digest,str) or not re.fullmatch('[0-9a-f]{64}',digest)
        or row.get('source_file_sha256')!=digest or type(pages) is not int or pages<1):
        raise ValueError('Historical PDF requires exact source hashes and page count')
    if (row.get('source_identity_kind')!='frozen_official_opaque_route_and_exact_historical_PDF_no_model_UUID'
        or row.get('source_capture_kind')!='historical_official_PDF_capture_date_unknown'
        or row.get('document_type') not in ('commercial_court_historical_judgment','commercial_court_historical_appeal',
                'commercial_court_historical_judgment_and_appeal')
        or row.get('source_family')!='moj_judgments'
        or row.get('capture_timestamp_utc') is not None or row.get('source_api_url') is not None
        or row.get('judgment_gregorian_date_raw') is not None or row.get('source_body_html_sha256') is not None):
        raise ValueError('Unsupported historical PDF identity or capture claim')
    parsed=urlparse(row.get('source_url') or '')
    route=row.get('opaque_route_id')
    route_kind='0' if appeal else '1'
    if (parsed.scheme!='https' or parsed.netloc!='laws.moj.gov.sa' or parsed.query or parsed.fragment
        or not isinstance(route,str) or not re.fullmatch('[A-Za-z0-9_=-]+',route)
        or parsed.path!='/ar/JudicialDecisionsList/'+route_kind+'/'+route or row.get('source_id')!=route):
        raise ValueError('Historical PDF requires the exact observed official opaque route')
    text=row.get('text_ar');text_hash=row.get('text_sha256');doc='sa-moj-historical-pdf-'+digest
    if (not isinstance(text,str) or not text.strip() or sha256(text.encode())!=text_hash
        or row.get('document_id')!=doc or row.get('version_id')!=doc+'-'+text_hash[:16]):
        raise ValueError('Historical PDF text or version hash mismatch')
    levels=['judgment','appeal'] if combined else ['appeal'] if appeal else ['judgment']
    if (type(row.get('source_component_count')) is not int or len(components)!=len(levels)
        or any(not isinstance(c,dict) for c in components)
        or row.get('has_judgment') is not (not appeal)
        or row.get('has_appeal') is not (appeal or combined)):
        raise ValueError('Historical PDF needs the declared complete judicial components')
    if appeal:
        if (any(row.get(k) is not None for k in ('judgment_number','judgment_hijri_date_raw',
                'judgment_gregorian_date_raw','court_name','city','appeal_gregorian_date_raw'))
            or any(not isinstance(row.get(k),str) or not row[k].strip() for k in (
                'appeal_number','appeal_hijri_date_raw','appeal_court_name','appeal_city'))):
            raise ValueError('Historical appeal needs active appeal metadata and null inactive judgment metadata')
    if combined and (row.get('appeal_gregorian_date_raw') is not None
        or any(not isinstance(row.get(k),str) or not row[k].strip() for k in (
            'judgment_number','judgment_hijri_date_raw','court_name','city',
            'appeal_number','appeal_hijri_date_raw','appeal_court_name','appeal_city'))):
        raise ValueError('Combined historical PDF needs both active metadata sets and null Gregorian dates')
    for component,level in zip(components,levels):
        metadata=(('number','appeal_number'),('court_name','appeal_court_name'),('city','appeal_city'),
                  ('hijri_date_raw','appeal_hijri_date_raw'),('gregorian_date_raw','appeal_gregorian_date_raw')) if level=='appeal' else (
                  ('number','judgment_number'),('court_name','court_name'),('city','city'),
                  ('hijri_date_raw','judgment_hijri_date_raw'),('gregorian_date_raw','judgment_gregorian_date_raw'))
        if (component.get('decision_level')!=level
            or any(component.get(c)!=row.get(r) for c,r in metadata)):
            raise ValueError('Historical PDF component metadata mismatch')
    try:corrections=json.loads(row.get('source_corrections_json'))
    except (TypeError,ValueError) as exc:raise ValueError('Historical PDF needs transcription provenance') from exc
    if (not isinstance(corrections,dict) or corrections.get('source_pdf_sha256')!=digest
        or corrections.get('transcription_sha256')!=text_hash
        or not isinstance(row.get('native_body_text_sha256'),str)
        or not re.fullmatch('[0-9a-f]{64}',row['native_body_text_sha256'])
        or corrections.get('stored_native_body_sha256')!=row['native_body_text_sha256']
        or type(corrections.get('complete_source_pages_reviewed')) is not int
        or corrections['complete_source_pages_reviewed']!=pages):
        raise ValueError('Historical PDF transcription/page provenance mismatch')
    whole=list(range(1,pages+1));blank=corrections.get('blank_pages')
    def page_list(value):
        return (isinstance(value,list) and all(type(p) is int and 1<=p<=pages for p in value)
                and value==sorted(set(value)))
    if not page_list(blank):
        raise ValueError('Historical PDF requires exact component pages and whole-document inspection')
    used=set()
    for component in components:
        component_pages=component.get('source_pdf_pages')
        if (not page_list(component_pages) or not component_pages
            or component.get('complete_document_pages_inspected')!=whole
            or not page_list(component['complete_document_pages_inspected'])):
            raise ValueError('Historical PDF requires exact component pages and whole-document inspection')
        used.update(component_pages)
    if used & set(blank) or sorted(used | set(blank))!=whole:
        raise ValueError('Historical PDF requires exact component pages and whole-document inspection')
    if combined:
        derivations=corrections.get('active_component_body_derivations')
        natives=corrections.get('stored_native_body_components')
        offsets=corrections.get('stored_native_body_offsets')
        if any(not isinstance(v,list) or len(v)!=2 for v in (derivations,natives,offsets)):
            raise ValueError('Combined historical PDF needs both bound native body derivations')
        def offset_pair(value):
            return (isinstance(value,list) and len(value)==2
                    and all(type(v) is int for v in value) and 0<=value[0]<value[1])
        previous_end=0
        for c,d,n,pair in zip(components,derivations,natives,offsets):
            if (not isinstance(d,dict) or not isinstance(n,dict)
                or not offset_pair(pair) or pair[0]<previous_end
                or not offset_pair(d.get('native_offsets')) or d['native_offsets']!=pair
                or not offset_pair([n.get('source_native_start_char'),n.get('source_native_end_char')])
                or n.get('source_native_start_char')!=pair[0] or n.get('source_native_end_char')!=pair[1]
                or type(n.get('raw_body_characters')) is not int
                or n['raw_body_characters']!=pair[1]-pair[0]
                or d.get('decision_level')!=c.get('decision_level') or n.get('decision_level')!=c.get('decision_level')
                or not isinstance(d.get('raw_body_sha256'),str)
                or not re.fullmatch('[0-9a-f]{64}',d['raw_body_sha256'])
                or n.get('raw_body_sha256')!=d['raw_body_sha256']
                or d.get('proposed_body_sha256')!=c.get('text_sha256')
                or not offset_pair(d.get('proposed_offsets'))
                or d['proposed_offsets']!=[c.get('start_char'),c.get('end_char')]
                or not page_list(d.get('source_pdf_pages'))
                or d['source_pdf_pages']!=c.get('source_pdf_pages')):
                raise ValueError('Combined historical PDF native/component derivation mismatch')
            previous_end=pair[1]
