"""An adapter is not a source downloader or a publication permission."""
import json
import os
import pytest
from saudi_legal.inputs import capture_text
from saudi_legal.core import make_record,sha256


def test_user_supplied_body_keeps_arabic_and_real_input_method(tmp_path,expected_body):
    inp=tmp_path/'body.txt';out=tmp_path/'capture.json';inp.write_text(expected_body)
    summary=capture_text(inp,'عنوان اصطناعي','https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/00000000-0000-4000-8000-000000000001/1','2025-08-09T12:00:00Z',out,True)
    raw=out.read_bytes();data=json.loads(raw);r=make_record(data,sha256(raw))
    assert r['text_ar']==expected_body
    assert r['extraction_method']=='reuse_user_supplied_utf8_body'
    assert r['rights_basis'] is None
    assert summary['source_fetched'] is False
    assert summary['publication_permission_inferred'] is False
    assert 'upstream_whitespace_flattened' not in r['quality_flags']
    with pytest.raises(ValueError,match='existing work'):
        capture_text(inp,'عنوان','https://example.org','2025-08-09T12:00:00Z',out,True)
    assert out.read_bytes()==raw


def test_invalid_source_or_capture_time_creates_nothing(tmp_path,expected_body):
    inp=tmp_path/'body.txt';inp.write_text(expected_body);out=tmp_path/'invalid.json'
    with pytest.raises(ValueError,match='source_url'):
        capture_text(inp,'عنوان','https://example.org','2025-08-09T12:00:00Z',out,True)
    assert not out.exists()
    with pytest.raises(ValueError,match='capture_timestamp'):
        capture_text(inp,'عنوان','https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/00000000-0000-4000-8000-000000000001/1','unknown',out,True)
    assert not out.exists()


def test_input_bytes_and_crlf_are_preserved_before_declared_cleaning(tmp_path):
    raw=('المادة الأولى\r\nنص اصطناعي\rسطر آخر\n'*12).encode('utf-8')
    inp=tmp_path/'crlf.txt';inp.write_bytes(raw);out=tmp_path/'capture.json'
    capture_text(inp,'عنوان اصطناعي','https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/00000000-0000-4000-8000-000000000001/1','2025-08-09T12:00:00Z',out,True)
    data=json.loads(out.read_bytes())
    assert data['full_text'].endswith(raw.decode('utf-8'))
    assert data['source']['input_text_sha256']==sha256(raw)


def test_nonregular_input_is_rejected_without_opening_or_output(tmp_path):
    inp=tmp_path/'fifo';os.mkfifo(inp);out=tmp_path/'capture.json'
    with pytest.raises(ValueError,match='regular'):
        capture_text(inp,'عنوان','https://example.org','2025-08-09T12:00:00Z',out,True)
    assert not out.exists()
