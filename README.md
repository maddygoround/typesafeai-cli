# Give your agent Jev

Coding agents are pretty good at chatting. They are worse at calling a model that does not chat back.

`typesafe` is a small CLI for [TypeSafe](https://typesafe.ai) System One. The model is **Jev**. You hand it state and typed questions (noul, choice, score). It hands back probabilities. No prose, no "here's what you should do next."

If your agent was about to write a curl one-liner or a throwaway Python file, this is that, minus the invented fields.

## What it is

A client for `POST /v1/systemone`. That is almost the whole API. The CLI exists so agents (and you) can run an evaluation without re-learning the wire format every time.

It is not a chatbot wrapper. It is not a bake-off against GPT. Jev is the model. This binary just calls it.

## Why an agent would bother

- Commands are discoverable. `typesafe agent schema` dumps the tree as JSON. In agent mode, `--help` does the same.
- Output is JSON on stdout: `{ "status", "data", "metadata" }`. Errors go to stderr, also JSON.
- Independent questions go in one `ask`. Jev runs them in parallel. Your agent should not loop `noul` in a shell `for`.
- `typesafe skills install` drops TypeSafe's official skill (how to *design* questions) plus a short note that live calls go through this CLI.

Humans can use it too. That is allowed.

## Try it

```bash
export TYPESAFE_API_KEY=apikey_…

typesafe auth status
typesafe models
typesafe smoke
```

A real call looks like this:

```bash
typesafe ask \
  --state-file state.json \
  --questions-file questions.json
```

Or one question with no files:

```bash
typesafe noul "Does this message request a refund?" \
  --state "I was charged twice. Please refund the duplicate."

typesafe choice "What does the message request?" \
  --option refund --option information --option other \
  --state "I was charged twice. Please refund the duplicate."
```

`data.model` should say something like `jev-1.13.0`. If it doesn't, you are not talking to Jev.

## Commands

| Command | What it does |
| --- | --- |
| `typesafe ask` | State + a questions file. The main path. |
| `typesafe noul` / `choice` / `score` | One-question shortcuts over `ask` |
| `typesafe models` | List aliases (`jev-latest`, `jev-preview`, …) |
| `typesafe smoke` | The docs quickstart, as a sanity check |
| `typesafe auth status` | Whether a key is loaded. Does not print the key. |
| `typesafe agent schema` | Machine-readable command tree |
| `typesafe skills install` | Official TypeSafe skill into `.agents/skills` (or `--dir`) |

Exit codes: `0` answered, `1` request failed, `2` bad flags or invalid questions (no HTTP).

A Noul near `0.5` means Jev is unsure, not "medium." Thresholds live in your code, not in this CLI.

## Auth

API key only. TypeSafe does not expose OAuth on this API.

```bash
export TYPESAFE_API_KEY=apikey_…          # required
export TYPESAFE_BASE_URL=https://api.typesafe.ai
export TYPESAFE_DEFAULT_MODEL=jev-latest

# or pass --key / --creds creds.json  ({ "api_key": "…" })
typesafe auth status
```

## Install

Python 3.10+. The Cilium-style one-liner (needs `python3`, plus `pipx` or `uv` if you have them):

```bash
curl -fsSL https://raw.githubusercontent.com/maddygoround/typesafeai-cli/main/install.sh | bash
```

That pulls the latest GitHub release wheel and installs the `typesafe` command. Pin a tag with `TYPESAFE_CLI_VERSION=v0.2.0`. Use PyPI instead of GitHub with `TYPESAFE_CLI_FROM=pypi`.

Or skip the script:

```bash
pipx install typesafeai-cli
# or: pip install typesafeai-cli
# or: uv tool install typesafeai-cli
```

From a clone, for hacking:

```bash
git clone https://github.com/maddygoround/typesafeai-cli.git
cd typesafeai-cli
uv sync
uv run typesafe --help
```

Get a key from the [TypeSafe dashboard](https://console.typesafe.ai/settings/keys).

## Cutting a release

Bump `version` in `pyproject.toml` and `__version__` in `src/typesafe_cli/__init__.py` so they match. Then:

```bash
git tag v0.2.0
git push origin v0.2.0
```

GitHub Actions runs tests, builds the wheel and sdist, attaches them (plus `install.sh` and checksums) to a GitHub release, and publishes to PyPI. PyPI needs a [trusted publisher](https://docs.pypi.org/trusted-publishers/) on this repo, workflow `release.yml`, environment `pypi`. The GitHub release still happens if PyPI is not set up yet.

## Agent mode

If Codex, Claude Code, Cursor, Grok, etc. set their usual env vars, the CLI notices. You can also pass `--agent` or `--no-agent`.

```bash
typesafe agent schema
typesafe --agent --help
typesafe skills install --project
```

For live evaluations, prefer `typesafe ask` over ad-hoc curl. Design the questions with TypeSafe's skill; run them here.

P.S. Jev still will not write your commit message. That is the other model's job.
