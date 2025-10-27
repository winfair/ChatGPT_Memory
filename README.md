# ChatGPT Memory Repo

Append-only personal knowledge base designed for durable retrieval and 3D exploration.

## Layout
```
archives/    # raw, verbatim chat dumps (append-only)
parsed/      # machine-readable nodes/entities/links/topics per archive date
vectors/     # embeddings + 3D coordinates (append-only)
indexes/     # fast tag/text indexes (optional)
schemas/     # JSON Schemas for interchange
```

## Workflow
1) Add a verbatim chat to `archives/YYYY-MM-DD_chat_full.txt`.
2) Run the parser (ChatGPT step) → write `parsed/YYYY-MM-DD/*.jsonl`.
3) Run the vectorizer (Python step) → append to `vectors/*.jsonl`.
4) (Optional) Build `indexes/*` for fast lookup.

**Append-only rule:** never delete or rewrite earlier files; always add new versioned files.

## Querying (from any chat)
Ask: "search my github memory for <thing>".
We search tags, entities, and (if available) approximate nearest neighbors over stored embeddings.
