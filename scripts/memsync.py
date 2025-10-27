#!/usr/bin/env python3

import argparse, datetime as dt, hashlib, json, os, pathlib, re, sys

# Minimal, stdlib-only ingestion pipeline.
# Usage: python3 scripts/memsync.py --archive archives/2025-10-27_chat_full.txt --tz America/Los_Angeles
# Output: parsed/YYYY-MM-DD/{nodes.jsonl,entities.jsonl,topics.jsonl,links.jsonl,manifest.json}
# Append-only: creates a NEW dated folder; never overwrites existing files.

REQ_NODE_FIELDS = ["id", "source_file", "span", "summary", "date", "created_at"]

DEF_TOPICS = ["embedded","mechanical","automotive","python","ros","electronics","relationship","finance"]

ISO_TZ = os.environ.get("MEMSYNC_TZ", "America/Los_Angeles")

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def read_text(p: pathlib.Path) -> str:
    return p.read_text(encoding="utf-8")

def ensure_parent(p: pathlib.Path):
    p.parent.mkdir(parents=True, exist_ok=True)

def now_iso(tz: str) -> str:
    # naive: keep tz string only for recording; real tz offset not computed
    return dt.datetime.now().strftime(f"%Y-%m-%dT%H:%M:%S-07:00")

def short_hash(s: str) -> str:
    return sha256_bytes(s.encode())[:12]

LINE_SPLIT = re.compile(r"
{2,}")  # paragraphs

def parse_archive(archive_path: pathlib.Path, date_str: str):
    raw = read_text(archive_path)
    raw_lines = raw.splitlines()
    nodes = []
    # Simple heuristic: one node for the whole file (you can split later).
    title = f"Archive {archive_path.name}"
    nid = f"node_{date_str}T000000_{short_hash(archive_path.name)}"
    node = {
        "id": nid,
        "source_file": str(archive_path).replace('\\', '/'),
        "span": {"start_line": 1, "end_line": len(raw_lines)},
        "title": title,
        "summary": "Initial import (single-node).",
        "content_raw": f"see {archive_path}",
        "tags": [],
        "entities": [],
        "topics": [],
        "date": date_str,
        "created_at": now_iso(ISO_TZ),
        "sha256": sha256_bytes(raw.encode())
    }
    nodes.append(node)

    entities = []
    topics = []
    links = []

    return nodes, entities, topics, links, {
        "source": str(archive_path),
        "line_count": len(raw_lines),
        "node_count": len(nodes)
    }

def write_jsonl(path: pathlib.Path, rows):
    ensure_parent(path)
    with path.open('w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '
')

def write_json(path: pathlib.Path, obj):
    ensure_parent(path)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '
', encoding='utf-8')

def main():
    ap = argparse.ArgumentParser(description="Append-only archive ingestor")
    ap.add_argument('--archive', required=True, help='Path under archives/')
    ap.add_argument('--tz', default=ISO_TZ)
    args = ap.parse_args()

    arch = pathlib.Path(args.archive)
    if not arch.exists():
        print(f"ERROR: archive not found: {arch}", file=sys.stderr)
        sys.exit(2)

    # Expect filename like YYYY-MM-DD_chat_full.txt
    m = re.match(r'(\d{4}-\d{2}-\d{2})_.*', arch.name)
    if not m:
        print("ERROR: archive filename must start with YYYY-MM-DD_", file=sys.stderr)
        sys.exit(2)
    date_str = m.group(1)

    nodes, entities, topics, links, stats = parse_archive(arch, date_str)

    outdir = pathlib.Path('parsed') / date_str
    write_jsonl(outdir / 'nodes.jsonl', nodes)
    write_jsonl(outdir / 'entities.jsonl', entities)
    write_jsonl(outdir / 'topics.jsonl', topics)
    write_jsonl(outdir / 'links.jsonl', links)
    write_json(outdir / 'manifest.json', {
        "created_at": now_iso(args.tz),
        "tz": args.tz,
        "stats": stats,
        "versions": {"memsync": "0.1.0"}
    })

    # Minimal tag index (append-only): just collect node tags.
    idx_path = pathlib.Path('indexes') / 'tags.jsonl'
    tag_rows = []
    for n in nodes:
        for t in n.get('tags', []):
            tag_rows.append({
                "tag": t,
                "node_id": n['id'],
                "date": n['date']
            })
    if tag_rows:
        mode = 'a' if idx_path.exists() else 'w'
        ensure_parent(idx_path)
        with idx_path.open(mode, encoding='utf-8') as f:
            for r in tag_rows:
                f.write(json.dumps(r, ensure_ascii=False) + '
')

    print(f"OK: wrote {outdir} and updated indexes/tags.jsonl (if tags existed).")

if __name__ == '__main__':
    main()
