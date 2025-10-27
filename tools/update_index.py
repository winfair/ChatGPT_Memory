#!/usr/bin/env python3
import json, hashlib, pathlib, time

REPO = pathlib.Path(__file__).resolve().parents[1]
RUNS = REPO / "runs"
INDEXES = REPO / "indexes"
INDEXES.mkdir(parents=True, exist_ok=True)

def sha256_file(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1<<20), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    runs = []
    for r in sorted(RUNS.glob("*")):
        if not r.is_dir(): continue
        vec = r / "vectors" / "positions_3d.jsonl"
        parsed_parent = r / "parsed"
        nodes = None
        if parsed_parent.exists():
            date_dirs = sorted([d for d in parsed_parent.glob("*") if d.is_dir()])
            if date_dirs:
                cand = date_dirs[-1] / "nodes.jsonl"
                if cand.exists(): nodes = cand
        archives = r / "archives"
        if vec.exists() and nodes and archives.exists():
            runs.append({
                "run": r.name,
                "vectors": str(vec.as_posix()),
                "nodes": str(nodes.as_posix()),
                "archives_dir": str(archives.as_posix()),
                "vectors_sha256": sha256_file(vec),
                "nodes_sha256": sha256_file(nodes),
            })

    if not runs:
        raise SystemExit("No valid runs found under /runs")

    latest = runs[-1]
    catalog = {
        "generated_at": int(time.time()),
        "runs": runs,
        "latest": {
            "run": latest["run"],
            "positions_jsonl": latest["vectors"],
            "nodes_jsonl": latest["nodes"],
            "archives_dir": latest["archives_dir"],
            "positions_sha256": latest["vectors_sha256"],
            "nodes_sha256": latest["nodes_sha256"],
        }
    }
    out = INDEXES / "memory_catalog.json"
    out.write_text(json.dumps(catalog, indent=2), encoding="utf-8")
    print(f"Wrote {out} with {len(runs)} runs. Latest = {latest['run']}")

if __name__ == "__main__":
    main()
