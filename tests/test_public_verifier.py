import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    'public_verifier', Path(__file__).parents[1]/'scripts/verify_text_release.py')
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


def test_hub_cache_snapshot_symlink_is_read_anonymously_and_revision_pinned(tmp_path, monkeypatch):
    blob = tmp_path/'blob'
    blob.write_bytes(b'\xff\xd8synthetic-test-image')
    snapshot = tmp_path/'page.jpg'
    snapshot.symlink_to(blob)
    calls = []
    def download(*args, **kwargs):
        calls.append((args, kwargs))
        return str(snapshot)
    monkeypatch.setattr(verifier, 'hf_hub_download', download)
    assert verifier.read_annex_asset('owner/dataset', 'page.jpg', 'fixed-revision') == blob.read_bytes()
    assert calls == [(('owner/dataset', 'page.jpg'), {
        'repo_type': 'dataset', 'revision': 'fixed-revision', 'token': False})]


def test_local_export_symlink_and_parent_traversal_are_rejected(tmp_path):
    blob = tmp_path/'blob'
    blob.write_bytes(b'\xff\xd8synthetic-test-image')
    (tmp_path/'page.jpg').symlink_to(blob)
    with pytest.raises(ValueError, match='ordinary file'):
        verifier.read_annex_asset(str(tmp_path), 'page.jpg')
    with pytest.raises(ValueError, match='Unexpected annex'):
        verifier.read_annex_asset(str(tmp_path), '../page.jpg')
