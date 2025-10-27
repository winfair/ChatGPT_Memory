#!/usr/bin/env python3
import argparse, json, pathlib, sys

# Minimal validator without external deps.
# Checks only for required fields per our schemas.

REQUIRED = {
  'nodes.jsonl': ['id','source_file','span','summary','date','created_at'],
  'entities.jsonl': ['name','type'],
  'links.jsonl': ['src','dst','type'],
  'topics.jsonl': ['name']
}

def validate_jsonl(path: pathlib.Path, req_fields):
    ok = True
    if not path.exists():
        print(f'[WARN] Missing {path}')
        return ok
    with path.open('r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception as e:
                print(f'[ERROR] {path}:{i} invalid JSON: {e}')
                ok = False
                continue
            missing = [k for k in req_fields if k not in obj]
            if missing:
                print(f'[ERROR] {path}:{i} missing fields: {missing}')
                ok = False
    return ok

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--date', required=True, help='YYYY-MM-DD under parsed/')
    args = ap.parse_args()

    base = pathlib.Path('parsed') / args.date
    files = ['nodes.jsonl','entities.jsonl','topics.jsonl','links.jsonl']
    overall = True
    for fn in files:
        overall &= validate_jsonl(base / fn, REQUIRED[fn])
    print('OK' if overall else 'FAIL')
    sys.exit(0 if overall else 1)

if __name__ == '__main__':
    main()
