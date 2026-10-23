"""Adapt already acquired UTF-8 BOE page/body text, without fetching a source."""
import json
import os
from pathlib import Path
import stat
from .core import MARKER,canonical,make_record,sha256


def read_utf8_input(text_file):
    source=Path(text_file)
    if not stat.S_ISREG(source.stat().st_mode):
        raise ValueError('Input must be a regular UTF-8 file')
    limit=32*1024*1024
    if source.stat().st_size>limit:
        raise ValueError('Input exceeds 32 MiB; use bounded source captures')
    # Nonblocking open and fstat also reject a file replaced by a FIFO after stat.
    fd=os.open(source,os.O_RDONLY|os.O_NONBLOCK)
    with os.fdopen(fd,'rb') as f:
        if not stat.S_ISREG(os.fstat(f.fileno()).st_mode):
            raise ValueError('Input must be a regular UTF-8 file')
        acquired=f.read(limit+1)
    if len(acquired)>limit:
        raise ValueError('Input exceeds 32 MiB; use bounded source captures')
    acquired.decode('utf-8')  # Reject invalid UTF-8 without rewriting acquired bytes.
    return acquired


def capture_text(text_file,title,source_url,captured_at,output,body_only=False):
    out=Path(output)
    if out.exists() or out.is_symlink():
        raise ValueError('Output must be a new JSON file; existing work is preserved')
    acquired=read_utf8_input(text_file)
    raw=acquired.decode('utf-8')
    text=MARKER+'\n'+raw if body_only else raw
    data={'title':title,'status':None,'full_text':text,
          'source':{'url':source_url,'captured_at_utc':captured_at,'hash_sha256':sha256(text.encode()),
                    'input_method':'user_supplied_utf8_body' if body_only else 'user_supplied_utf8_page',
                    'input_text_sha256':sha256(acquired)}}
    encoded=canonical(data).encode()
    record=make_record(data,sha256(encoded))
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('xb') as f:f.write(encoded)
    return {'source_id':record['source_id'],'source_file_sha256':sha256(encoded),
            'input_method':data['source']['input_method'],'source_fetched':False,'publication_permission_inferred':False}
