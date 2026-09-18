# typesafeai-cli

CLI for TypeSafe System One (Jev). Typed judgments, not chat.

```bash
uv sync
export TYPESAFE_API_KEY=apikey_…
uv run typesafe ask --state-file state.json --questions-file questions.json
```

Commands: `ask`, `noul`, `choice`, `score`, `models`, `smoke`, `auth status`, `agent schema`, `skills install`.

Stdout is `{ "status", "data", "metadata" }`. The model is Jev (`jev-latest`).
