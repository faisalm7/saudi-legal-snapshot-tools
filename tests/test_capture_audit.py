"""Local processing guards; synthetic inputs do not measure legal accuracy."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

import pytest

from saudi_legal.audit import audit_capture


FIXTURE = Path(__file__).resolve().parents[1] / 'fixtures' / 'synthetic_boe.json'


def inputs(tmp_path):
    js, pdf = tmp_path / 'json', tmp_path / 'pdf'
    js.mkdir(); pdf.mkdir()
    shutil.copyfile(FIXTURE, js / 'invented.json')
    return js, pdf


def test_malformed_capture_does_not_stop_valid_document(tmp_path):
    js, pdf = inputs(tmp_path)
    (js / 'bad.json').write_text('{malformed')
    summary = audit_capture(js, pdf, tmp_path / 'audit', workers=1)
    assert summary['input_json_files'] == 2
    assert summary['parsed_records'] == 1
    assert summary['parse_status'] == {'rejected': 1, 'parsed': 1}
    assert summary['segmentation_status'] == {'not_attempted': 1, 'deferred_missing_pdf': 1}
    row = json.loads((tmp_path / 'audit' / 'records.jsonl').read_text())
    assert row['rights_basis'] is None
    assert row['article_count'] is None


def test_capture_read_timeout_is_logged_without_empty_public_dataset(tmp_path, monkeypatch):
    js, pdf = inputs(tmp_path)
    def blocked(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], kwargs['timeout'])
    monkeypatch.setattr(subprocess, 'run', blocked)
    summary = audit_capture(js, pdf, tmp_path / 'audit', workers=1, timeout=.01)
    assert summary['parsed_records'] == 0
    assert summary['parse_status'] == {'deferred_read_timeout': 1}
    assert not list((tmp_path / 'audit').rglob('*.parquet'))


def test_audit_output_symlink_never_changes_target(tmp_path):
    js, pdf = inputs(tmp_path)
    target = tmp_path / 'target'; target.mkdir()
    sentinel = target / 'sentinel'; sentinel.write_bytes(b'unchanged')
    link = tmp_path / 'link'; link.symlink_to(target, target_is_directory=True)
    with pytest.raises(ValueError, match='symlink'):
        audit_capture(js, pdf, link)
    assert sentinel.read_bytes() == b'unchanged'
    assert list(target.iterdir()) == [sentinel]


def test_mixed_pdf_availability_across_shards_loads_with_one_nullable_schema(tmp_path, monkeypatch):
    from datasets import load_dataset
    js, pdf = inputs(tmp_path)
    (js / 'invented.json').unlink()
    fixture = json.loads(FIXTURE.read_text())
    for n in range(101):
        row = json.loads(json.dumps(fixture))
        row['source']['url'] = ('https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/'
                              f'00000000-0000-4000-8000-{n:012d}/1')
        (js / f'{n:03d}.json').write_text(json.dumps(row, ensure_ascii=False))
    (pdf / '100.pdf').write_bytes(b'Invented PDF bytes; only mocked extraction is tested')
    def local_mock(command, **kwargs):
        p = Path(command[-1])
        if p.suffix == '.json':
            return subprocess.CompletedProcess(command, 0, stdout=p.read_bytes())
        if p.suffix == '.pdf':
            return subprocess.CompletedProcess(command, 0, stdout=hashlib.sha256(p.read_bytes()).hexdigest()+'\n')
        return subprocess.CompletedProcess(command, 0, stdout='سطر اصطناعي بلا عنوان\f')
    out = tmp_path / 'audit'
    with monkeypatch.context() as patch:
        patch.setattr(subprocess, 'run', local_mock)
        audit_capture(js, pdf, out, workers=1)
    ds = load_dataset(str(out), name='laws', split='corpus')
    assert len(ds) == 101
    assert ds.features['source_pdf_sha256'].dtype == 'string'
    assert ds.features['source_pdf_pages'].dtype == 'int32'
    assert ds[0]['source_pdf_sha256'] is None
    assert ds[100]['source_pdf_sha256'] is not None
