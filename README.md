# ChatGPT Memory Repository

This repo hosts structured “memory” artifacts produced from ChatGPT data exports.

## Directory structure
- `runs/<timestamp>/archives/…` : verbatim text transcripts
- `runs/<timestamp>/parsed/<date>/nodes.jsonl` : chunked nodes with tags/topics
- `runs/<timestamp>/vectors/positions_3d.jsonl` : 3D coordinates for each node
- `indexes/memory_catalog.json` : index of all runs and the “latest” pointers

## Programmatic entry point
Read `indexes/memory_catalog.json` (raw URL) to locate the latest files:
- `latest.nodes_jsonl`
- `latest.positions_jsonl`
- `latest.archives`

Then fetch what you need.

## Updating
Use `tools/sync_memory_repo.py` to copy a new local MemoryBuild into this repo and rebuild the index.
