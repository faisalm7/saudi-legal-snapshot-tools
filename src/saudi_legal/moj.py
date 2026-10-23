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


def decode_case_response(raw,source_url,captured_at):
    """Project complete native judgment/appeal HTML fields from a local response.

    This supports the observed br/p-only source shape. Additional source fields,
    lists or media require explicit handling instead of silently dropping them.
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
        if re.search(r'<\s*/?\s*(?!br\b|p\b)[A-Za-z][^>]*>',value,re.I):
            raise ValueError('Additional body markup needs separate handling')
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
    return row


def capture_case(response_file,source_url,captured_at,output):
    from .inputs import read_utf8_input
    record=decode_case_response(read_utf8_input(response_file),source_url,captured_at);out=Path(output)
    if out.exists() or out.is_symlink():raise ValueError('Output must be new')
    with out.open('x',encoding='utf-8') as stream:stream.write(canonical(record))
    return {'document_id':record['document_id'],'source_components':record['source_component_count'],
            'source_fetched':False,'publication_permission_inferred':False}
