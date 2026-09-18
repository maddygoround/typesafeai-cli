# typesafeai-cli

Command-line client for [TypeSafe](https://typesafe.ai) **Jev**.

Jev is a System One model: you send a document (`state`) and typed questions (`noul`, `choice`, `score`). You get probabilities back. It does not write text and it does not choose the next tool.

```
typesafe ask --state-file "$WORKDIR/state.json" --questions-file "$WORKDIR/questions.json"
```

The HTTP surface is `POST /v1/systemone` (and `GET /v1/models`). This binary is that API, with validation, JSON on stdout, and an agent skill that tells callers how to build `state` before they call.

## Requirements

- Python 3.10+
- A key from the [TypeSafe console](https://console.typesafe.ai/settings/keys)

Set `TYPESAFE_API_KEY`. Do not put the key in chat, in the repo, or in `state.json`. Agents should run `typesafe auth status` and look at `has_key` only — they must not read `TYPESAFE_*` or key files.

```bash
export TYPESAFE_API_KEY=apikey_…
typesafe auth status
typesafe smoke
```

`smoke` hits Jev. `data.model` will look like `jev-1.13.0`. If that field is missing, you did not reach TypeSafe.

## Install

Until the package is on PyPI, install a [GitHub release](https://github.com/maddygoround/typesafeai-cli/releases) wheel or this repo:

```bash
pip install https://github.com/maddygoround/typesafeai-cli/releases/download/v0.2.0/typesafeai_cli-0.2.0-py3-none-any.whl

# from a clone
git clone https://github.com/maddygoround/typesafeai-cli.git
cd typesafeai-cli
uv sync
uv run typesafe --help
```

`install.sh` on the repo and on each release downloads that wheel and installs it with pipx, uv, or `pip --user`.

Optional env: `TYPESAFE_BASE_URL` (default `https://api.typesafe.ai`), `TYPESAFE_DEFAULT_MODEL` (default `jev-latest`). Flags `--key` and `--creds` exist for scripts; agents should not pass a key they scraped.

## Commands

| | |
| --- | --- |
| `typesafe ask` | Main path: state file + questions file |
| `typesafe noul` / `choice` / `score` | One question, no files needed |
| `typesafe models` | Model aliases |
| `typesafe smoke` | Docs quickstart against the live API |
| `typesafe auth status` | `has_key` true/false; never prints the secret |
| `typesafe agent schema` | JSON command tree for agents |
| `typesafe skills install` | Official TypeSafe skill plus **typesafe-cli** (how to collect state and call this binary) |

Exit `0` if Jev answered, `1` if the request failed (including no key on `ask`), `2` if the flags or questions are invalid (no HTTP).

A noul near `0.5` is uncertainty, not “medium.” You apply thresholds in the caller.

## How an agent should call it

Jev cannot see the repository, the diff, skills, or memory. The **typesafe-cli** skill is the adapter: write the questions first (they backtick the state paths they need), then fill **only** those fields — including code hunks when the path is code. Put JSON under `${TMPDIR:-/tmp}/codex/<project>/`, not in git.

```bash
typesafe skills install --offline --project   # or --global
typesafe agent schema
```

`--agent` forces JSON `--help`. `--no-agent` turns that off. Several coding-agent env vars enable it automatically.

## Releases

Bump `version` in `pyproject.toml` and `__version__` in `src/typesafe_cli/__init__.py` so they match. Tag `vX.Y.Z` and push it, or run the **Prepare Release** workflow (patch / minor / major).

That tag runs tests, attaches the wheel, sdist, checksums, and `install.sh` to a GitHub release, and publishes to PyPI if [trusted publishing](https://docs.pypi.org/trusted-publishers/) is configured for `release.yml` and environment `pypi`.
