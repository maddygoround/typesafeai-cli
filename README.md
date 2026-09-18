# TypeSafe agent CLI

`typesafe` is an **agent CLI** for [TypeSafe](https://typesafe.ai) **Jev**.

It is meant to be invoked by coding agents (Grok, Codex, Claude Code, Cursor, and anything else that can run a shell command). You can run it yourself while you debug; the usual caller is an agent.

Jev does not chat. The agent gathers a small JSON document (`state`) and typed questions (`noul`, `choice`, `score`). This CLI sends that to `POST /v1/systemone` and prints probabilities on stdout. Jev never sees the repo unless the agent copies the relevant slices into `state`.

You do not hand-write production payloads every day. Install the **typesafe-cli** skill, and the agent writes the JSON (in a temp directory, not in git). The files under [`examples/`](examples/) exist so you can see the shape, and so you can run a call without inventing one.

## JSON shape

Two files. Names are yours; types are not.

**`state.json`** — named fields the questions will point at:

```json
{
  "message": "I was charged twice for order A-104. Please refund the duplicate.",
  "policy": "Duplicate charges are eligible for an immediate refund."
}
```

**`questions.json`** — one judgment per id. `instructions` should backtick those fields (`` `message` ``):

```json
{
  "refund_requested": {
    "type": "noul",
    "instructions": "Does `message` request a refund?"
  },
  "intent": {
    "type": "choice",
    "instructions": "What does `message` ask for?",
    "criteria": {
      "refund": "The customer wants money returned",
      "information": "Explanation only",
      "other": "Something else"
    }
  }
}
```

Full copies, including a **code-change** example with `files[].hunk`:

| Sample | Files |
| --- | --- |
| Support ticket | [`examples/ticket/state.json`](examples/ticket/state.json), [`questions.json`](examples/ticket/questions.json) |
| Skill / code slice | [`examples/code-change/state.json`](examples/code-change/state.json), [`questions.json`](examples/code-change/questions.json) |
| How to run them | [`examples/README.md`](examples/README.md) |

```bash
WORKDIR="${TMPDIR:-/tmp}/codex/typesafeai-cli"
mkdir -p "$WORKDIR"
cp examples/ticket/*.json "$WORKDIR/"
typesafe ask --state-file "$WORKDIR/state.json" --questions-file "$WORKDIR/questions.json"
```

One-liners skip files: `typesafe noul "Does this request a refund?" --state "I was charged twice."`

If `data.model` looks like `jev-1.13.0`, the request reached TypeSafe. `auth status` does not.

## What the agent is supposed to do

1. `typesafe skills install` (once) so **typesafe-cli** and the official TypeSafe skill are on disk.
2. `typesafe auth status` — read `has_key` only. Agents must not print or open `TYPESAFE_*` or key files.
3. Write questions first. Each instruction backticks the state paths it needs. That list is what to collect.
4. Fill only those paths. If a path is code, put the hunk body in, not a filename.
5. Write JSON under `${TMPDIR:-/tmp}/codex/<project>/`, never in the git tree.
6. `typesafe ask`. Apply thresholds in the agent (a noul near `0.5` is unsure). Jev does not pick the next tool.

`typesafe agent schema` is the machine-readable command list. `--agent` makes `--help` JSON.

## Install

Python 3.10+ and a key from the [TypeSafe console](https://console.typesafe.ai/settings/keys).

```bash
export TYPESAFE_API_KEY=apikey_…

pip install https://github.com/maddygoround/typesafeai-cli/releases/download/v0.2.0/typesafeai_cli-0.2.0-py3-none-any.whl
# or clone, then: uv sync && uv run typesafe --help
```

`install.sh` on the repo and on each release installs that wheel. Optional: `TYPESAFE_BASE_URL`, `TYPESAFE_DEFAULT_MODEL`. `--key` / `--creds` are for scripts, not for agents scraping secrets.

Until PyPI trusted publishing is set, `pip install typesafeai-cli` from the index will fail; use the release URL above.

## Commands

| | |
| --- | --- |
| `typesafe ask` | State file + questions file |
| `typesafe noul` / `choice` / `score` | One question |
| `typesafe models` | Aliases (`jev-latest`, …) |
| `typesafe smoke` | Live docs quickstart |
| `typesafe auth status` | `has_key`; never prints the key |
| `typesafe agent schema` | JSON command tree |
| `typesafe skills install` | Official TypeSafe skill + **typesafe-cli** |

Exit `0` answered, `1` request failed (including missing key on `ask`), `2` bad flags or questions (no HTTP).

## Releases

Match `version` in `pyproject.toml` to `__version__` in `src/typesafe_cli/__init__.py`. Tag `vX.Y.Z` or run **Prepare Release**. The tag builds the wheel, attaches it to a GitHub release, and publishes to PyPI when trusted publishing is configured (`release.yml`, environment `pypi`).
