# Jev CLI Plan

> Review copy: `jev-cli/PLAN.md` (2026-09-18, decisions locked)
>
> Phase 1 implementation plan: `docs/superpowers/plans/2026-09-18-phase-1.md`

**Goal:** Make the TypeSafe skill's interaction model executable: agents design typed judgments, call Jev, and compose answers in code. This CLI is the experiment / harness runner, not a chat interface and not a replacement for the skill or SDK.

**Not the goal:** A chat agent. Jev does not generate prose, pick the next tool, or own control flow.

**Spec for agent behavior:** the official `typesafe-ai` skill plus live docs at https://docs.typesafe.ai/llms.txt. Do not invent a second interaction model.

---

## Locked decisions

| Decision | Lock |
| --- | --- |
| Language | **Python 3.10+**, official `typesafe_sdk`. Not Rust. Not Java/JVM. |
| Binary | **`jev`**. Env vars stay `TYPESAFE_*` (vendor contract). |
| Package | `jev-cli` on disk; import package `jev_cli` |
| Auth | API key only (`TYPESAFE_API_KEY`, `--key`, `--creds`). No OAuth. |
| Backend | TypeSafe HTTP via `TypeSafeClient`. Adapter is Phase 3 only. |
| Skill | Install TypeSafe’s official skill in Phase 2. Do not fork it. |
| First ship | **Phase 1 only** (table below). Then stop for review. |

If “go with Java” was meant as the JVM language, stop before coding — this plan is Python, binary name `jev`.

---

## Phase 1 vs Phase 2 (read this first)

**We build Phase 1 next. We do not start Phase 2 until Phase 1 has been reviewed.**

### Phase 1 — Judgment CLI (first ship)

A working `jev` that an agent or human can run today. JSON out by default, so stdout is parseable without Pup’s full agent-mode stack.

| In Phase 1 | Command / behavior |
| --- | --- |
| Config | `TYPESAFE_API_KEY`, `TYPESAFE_BASE_URL`, `TYPESAFE_DEFAULT_MODEL`, `--key`, `--creds` |
| Auth check | `jev auth status` (does not print the key) |
| Models | `jev models` |
| Evaluate | `jev ask --state-file s.json --questions-file q.json` |
| One-question sugar | `jev noul`, `jev choice`, `jev score` |
| Local validation | Missing instructions / one-option choice / one-level score → exit 2, no HTTP |
| Output | **JSON default.** Envelope `{ "status", "data", "metadata" }`. Answers in `data`. |
| Errors | Structured JSON on stderr; answers only on stdout |
| Retries | SDK default for 429/529 |
| Smoke | `jev smoke` (docs quickstart example) |

Phase 1 success: `jev ask --state-file s.json --questions-file q.json` prints the System One response inside the envelope, same answer shape as `POST /v1/systemone`.

**Not in Phase 1:** agent-env auto-detect, `jev agent schema`, `jev skills install`, `--backend llm`, `--min-confidence` as a CLI policy (callers threshold themselves).

### Phase 2 — Agent operability (after Phase 1 review)

Pup-style discovery so an agent with no extra docs can find commands. Does not change how Jev is called.

| In Phase 2 | Command / behavior |
| --- | --- |
| Agent detection | Env table (`CLAUDECODE`, `CURSOR_AGENT`, `CODEX`, …) plus `--agent` / `--no-agent` |
| Schema | `jev agent schema` and agent-mode `--help` as JSON command tree |
| Skills | `jev skills install` copies the **official** TypeSafe skill |
| Prompts | No confirmation prompts in agent mode (none in Phase 1 anyway) |

Phase 2 success: an agent can discover commands from `jev agent schema`, call `jev ask`, and parse the same envelope as Phase 1.

### Phase 3 — LLM comparison (optional, later)

`system-one-adapter` behind `--backend llm` / `jev compare`. Default path remains Jev. Not in the first two ships.

```
Phase 1 (now)          Phase 2 (next)           Phase 3 (maybe)
─────────────────      ──────────────────       ────────────────
jev ask / noul /       agent schema             --backend llm
choice / score         skills install           jev compare
jev models / smoke     env auto-detect
JSON envelope
```

---

## How Jev works with coding agents (Codex, Grok, Claude, …)

Jev is not another chat model those agents talk to. It is a **typed judgment function** they call: state + questions in, probabilities out. The agent (Grok, Codex, Claude, Cursor) still owns the conversation, tools, and control flow.

TypeSafe’s docs and skill already describe this. Coding agents default to one question per call and invent request fields; the skill exists to stop that. This CLI is the cheap way for those agents to obey the skill without writing a throwaway script.

### Two jobs in day-to-day work

**1. Authoring (most days)** — the agent is building *your* software.

1. User asks for a feature that needs semantic judgment (route a ticket, pick a skill, check a citation).
2. Agent loads the official `typesafe-ai` skill and the live docs (`llms.txt`).
3. Agent writes `state.json` + `questions.json` (Choice / Score / Noul, batched).
4. Agent runs `jev ask --state-file state.json --questions-file questions.json` and reads the JSON envelope.
5. Agent adjusts questions and thresholds from the numbers, not from prose.
6. Agent copies the same questions into application code as constants (`TypeSafeClient.system_one(...)`).
7. Human reviews that one file of questions and thresholds.

Without `jev`, the agent either chats (wrong) or pastes curl/Python that drifts from the API. With `jev`, the wire shape is the CLI’s job; the agent’s job is designing judgments.

**2. Harness (the agent runtime itself)** — Jev sits *in front of* Grok/Codex, not beside them.

Examples TypeSafe already published: skill suggestion (rank 182 skills, then verify the top 3), model routing, LLM guardrails, tool-call checks. The chat model never “asks Jev what to do next.” The harness calls `system_one`, then maybe adds one line to the prompt or blocks a tool.

Phase 1 CLI is enough for a harness to shell out. Phase 2 only makes discovery easier (`jev agent schema`, `skills install`).

### What Codex / Grok actually see

| Layer | Who | What they do |
| --- | --- | --- |
| Skill (`typesafe-ai`) | Agent | When and how to design questions; read live docs |
| `jev` CLI | Agent via shell | Run an evaluation now; stdout is JSON they can parse |
| `typesafe_sdk` | Application code the agent writes | Production path in the user’s app |
| Jev (`POST /v1/systemone`) | Neither chats with it | Returns `noul` / `choice` / `score` + confidence |

Pup’s lesson that we copy: JSON on stdout, no confirmation prompts, errors as JSON. Pup’s lesson that we do not copy: OAuth, 200 commands, the agent *operating a whole platform*. Jev’s surface is two endpoints. The agent’s daily win is **faster, cheaper, typed judgments** they can threshold in code, not a Datadog-sized command tree.

### What this does *not* do

- It does not make Jev a coworker that plans the next tool call.
- It does not replace Grok/Codex for writing code or talking to you.
- It does not generate text. If the agent needs prose, that is still the chat model.

---

## 0. How agents should interact with Jev (from the TypeSafe skill)

TypeSafe already defined this. The skill is not "call a TypeSafe CLI." Its stated purpose is: design TypeSafe workflows, read current docs and cookbooks, and compose typed judgments **in code**.

Official skill: https://github.com/typesafe-ai/skills/blob/main/skills/typesafe-ai/SKILL.md
Agent skill docs: https://docs.typesafe.ai/agent-skill.md

### The contract

1. **Read live docs as part of the task.** The skill is direction; `llms.txt` is source of truth for API, primitives, models, and cookbooks.
2. **Work backward from application behavior.** What will the app show, select, change, or hand off? Those become judgments. Keep rules, lookups, and side effects in code.
3. **Call Jev as a typed judgment service.** Provide named JSON `state`. Ask narrow questions (`choice` / `score` / `noul`) with instructions and criteria. Question IDs are for code; they are not sent to the model. Point at fields with backticked paths such as `` `ticket.messages[0].text` ``.
4. **Batch independent questions in one request.** Speculative questions are cheap. A second request is only for when the first answer is required to fetch evidence, build new state, or choose the next options.
5. **Compose answers in code.** Probabilities and confidence gate automation vs review. A Noul near 0.5 is unsure, not "medium." Do not let Jev decide the next agent action.
6. **Write SDK or HTTP code in the user's stack.** The skill's "Write API code" table is Python SDK, JavaScript SDK, or HTTP API. There is no first-party CLI in that table.
7. **Run cheap live queries when a key is present.** The agent-skill docs tell the agent to experiment with `TYPESAFE_API_KEY`, then propose changes from the results. Questions and thresholds live in one file so a human can review them. Agents are not trusted to write questions unsupervised.

### Two agent jobs, one model

| Job | Who | How they touch Jev |
| --- | --- | --- |
| **Author** | Coding agent building an app | Skill → docs → SDK calls embedded in the app. Live API is for experiments, not production chat. |
| **Harness** | Runtime that hosts an agent | Jev is a subroutine inside the harness: skill suggestion, model routing, guardrails, tool-call checks. The chat model never "talks to Jev." |

TypeSafe names the second job **harness engineering** on the [use-case map](https://docs.typesafe.ai/concepts/use-case-map.md). The [skill suggestion cookbook](https://docs.typesafe.ai/cookbooks/skill_suggestion.md) is the canonical example: two `system_one` calls rank/verify which skill to load; the chat model only sees a one-line hint.

### What this means for a CLI

Pup is a useful *operational* analog (JSON out, no prompts, discoverable commands). It is the wrong *product* analog.

- Pup: agents operate Datadog through a CLI.
- TypeSafe skill: agents **author** TypeSafe into software, and harnesses **call** Jev as a function.

A CLI still earns its keep as the skill's "run experiments" path:

```bash
jev ask --state-file state.json --questions-file questions.json --model jev-latest
```

That is how an agent with a key validates a question file before writing SDK code, and how a harness can shell out if it does not want to vendor the SDK. It is not how production app logic should call Jev, and it is not how an agent should converse with Jev.

Do not fork or replace the official skill. Phase 2’s `jev skills install` installs TypeSafe’s skill and notes: “for live evaluations, prefer `jev ask` over ad-hoc curl.”

---

## 0.1 Pup’s actual code shape (the operational analog)

Repo: [DataDog/pup](https://github.com/DataDog/pup). Local checkout: `/Users/m.rathod/Documents/Projects/pup` (Rust, currently `0.54.0`).

Pup is not a chat wrapper. It is a thin CLI over the official Datadog API client, built so **agents can operate the API without inventing HTTP**.

What the code actually does:

| Piece | Where | Behavior |
| --- | --- | --- |
| Entry / clap tree | `src/main.rs` | `pup <domain> <action>`; global `--output` (default **json**), `--agent`, `--no-agent`, `--yes`, `--read-only` |
| Domain commands | `src/commands/*.rs` | Thin: parse flags, call client, print. One module per product domain |
| HTTP | `src/client.rs` | Wraps `datadog-api-client`, not ad-hoc curl |
| Agent detection | `src/useragent.rs` | Env table (`CLAUDECODE`, `CURSOR_AGENT`, `CODEX`, …) or `--agent` |
| Output | `src/formatter.rs` | Human: json/table/yaml/csv. Agent mode: `{ status, data, metadata }` envelope, no confirmation prompts |
| Discovery | `pup agent schema` / agent-mode `--help` | Machine-readable command tree |
| Skills | `src/skills.rs` + `skills/` + `agents/` | Markdown **embedded in the binary** (`include_str!`); `pup skills install` writes them into Claude/Cursor/Codex/… |
| Auth | `src/auth/` | OAuth2 + PKCE preferred; API keys fallback |

Copy from Pup for a TypeSafe CLI: agent-mode, JSON default, schema command, skills install, official SDK as the HTTP layer, thin commands.

Do not copy: OAuth/PKCE (TypeSafe is API-key only), 200+ domain commands (TypeSafe has two HTTP endpoints), runbooks, ACP, WASM, tunnels, extensions.

Pup’s skills tell agents **how to run `pup`**. TypeSafe’s official skill tells agents **how to design judgments and write SDK code**. A TypeSafe CLI should install TypeSafe’s skill, not invent a Pup-sized skill pack.

---

## 1. What we are trying to build

TypeSafe currently ships:

| Layer | Exists? | Role |
| --- | --- | --- |
| Skill (`typesafe-ai`) | Yes | **The agent contract:** design judgments, read docs, compose in code |
| HTTP API | Yes | `POST /v1/systemone`, `GET /v1/models` |
| Python SDK (`typesafe_sdk`) | Yes | Production client for authoring agents |
| JavaScript SDK (`@typesafe-ai/sdk`) | Yes | Production client for authoring agents |
| First-party CLI | **No** | Missing *experiment / harness* runner |

The CLI fills the gap the skill already points at: cheap, typed, non-chat evaluations. It should:

1. Read `TYPESAFE_API_KEY` (or a creds file).
2. Call TypeSafe, not a chat model.
3. Return typed JSON: answers, probabilities, confidence, usage.
4. Keep composition, routing, and side effects in the caller (shell, agent, or code).
5. Refuse chat-shaped usage (no free-text "what should I do next").

That is a **typed judgment service**, not an agent runtime.

---

## 2. Verdict: `system-one-adapter-python` is the wrong primary framework

Repo: [typesafe-ai/system-one-adapter-python](https://github.com/typesafe-ai/system-one-adapter-python) (v0.1.4, MIT, Python ≥ 3.10).

### What it actually is

A drop-in replacement for `TypeSafeClient.system_one()`, backed by OpenAI or Anthropic instead of Jev.

It exists to **compare TypeSafe against an LLM** on cost, speed, and intelligence. It is not a CLI, not an agent harness, and not a TypeSafe API wrapper.

Evidence from the source:

- Public API is `SystemOneAdapterClient` / `AsyncSystemOneAdapterClient`.
- `system_one(state, questions, provider=..., model=...)` prompts an LLM with a System One schema, then maps the JSON back into `typesafe_sdk` answer types.
- It builds a chat transcript (`system` + `<document>…</document>` user message), requests structured JSON, retries malformed output, and optionally rescales invalid probability distributions.
- It depends on `typesafe-sdk`, plus optional `openai` / `anthropic` extras.
- There is no console script, no `ask` command, no auth flow, no agent schema.

### Why it is a poor core for the CLI

| Need | Adapter | Official TypeSafe path |
| --- | --- | --- |
| Call Jev | No. Talks to GPT/Claude | `POST /v1/systemone` |
| Calibrated probabilities | Approximated / normalized from LLM JSON | Trained for this (RLCD) |
| Fast (~100ms) System One calls | LLM latency | Jev |
| Agent-ready CLI | Library only | We would still have to write the CLI |
| Auth | Provider API keys | `TYPESAFE_API_KEY` |

Building the CLI *on* the adapter would produce a “TypeSafe CLI” that does not talk to TypeSafe unless we add a second backend. That inverts the product.

### Where the adapter *is* a fit

Optional later: a comparison backend.

```bash
typesafe ask --state-file s.json --questions-file q.json --json
typesafe ask ... --backend llm --provider openai --model gpt-4o-mini --json
typesafe compare --state-file s.json --questions-file q.json --against openai:gpt-4o-mini
```

Same questions, two backends, same response shape. That is exactly what the adapter is for. It should sit behind a `--backend llm` flag, not under the default `ask` path.

---

## 3. Landscape (do not reinvent blindly)

TypeSafe’s public surface is small. The HTTP API is two endpoints:

- `POST https://api.typesafe.ai/v1/systemone` — evaluate
- `GET https://api.typesafe.ai/v1/models` — list aliases
- Auth: `Authorization: Bearer $TYPESAFE_API_KEY`

Question types: `noul`, `choice`, `score`. Answers carry probabilities and (for choice/score) confidence.

Community CLIs already cover the thin shell:

| Project | Stack | What it does |
| --- | --- | --- |
| [geilt/typesafe-cli](https://github.com/geilt/typesafe-cli) | Python 3.9+, stdlib only | `info`, `models`, `smoke`, `ask` + agent skill |
| [y0usaf/typesafe-cli](https://github.com/y0usaf/typesafe-cli) | Node 22+, official JS SDK shape | `jev noul/choice/score/ask`, JSON, stdin, retries |
| [shantanugoel/ask-jev-skill](https://github.com/shantanugoel/ask-jev-skill) | Python stdlib | Agent-skill helper, confidence thresholds |

None of these is Pup. Pup’s agent contract is the gap:

- Auto-detect agent mode (`CLAUDECODE=1`, `--agent`, etc.)
- `--help` as JSON schema in agent mode
- Structured errors, no interactive prompts
- `skills install` for the host agent
- JSON/YAML output as the default machine interface
- Self-discoverable command tree

TypeSafe also has no OAuth in the public docs. Auth stays API-key based. Do not copy Pup’s PKCE/DCR flow.

---

## 4. Recommended architecture

**Default backend:** official TypeSafe HTTP API, preferably through `typesafe_sdk` (Python) so retries, env vars, and types stay first-party.

**CLI contract:**

Phase 1:

```
jev auth status              # does not print the key
jev models                   # GET /v1/models
jev ask                      # POST /v1/systemone
jev noul | choice | score    # one-question sugar over ask
jev smoke                    # docs quickstart
```

Phase 2 only:

```
jev agent schema             # machine-readable command tree
jev skills install           # official TypeSafe skill
```

`ask` is the core:

```bash
jev ask \
  --state-file state.json \
  --questions-file questions.json \
  --model jev-latest
```

Also accept:

- `--state '…'` or stdin (`--state-file -`)
- inline `--noul id="…"`, `--choice id=opt,opt`, `--score id=level,level`
- `--probs` to include distributions (always present in JSON envelope; this flag is for any future human table format)

**Control-flow rule:** the CLI returns judgments. Shell/agent code combines them.

### Language decision: Python, not Rust, not Java

Pup is Rust because Datadog’s surface is huge. TypeSafe’s public API is two endpoints. There is no official Rust or Java SDK. Reimplementing the wire protocol would duplicate `typesafe_sdk`.

**Python 3.10+ and `typesafe_sdk`.** Console script `jev`. Install with `uv tool install` / `pipx`.

CLI layer: `typer`. HTTP stays inside `TypeSafeClient`. Do not hand-roll `urllib`.

The JSON envelope is a formatter concern, built in Phase 1. Full agent-mode schema is Phase 2.

Why not the adapter as the framework: see section 2.

---

## 5. File map (when implementation starts)

This folder is the repo root. Suggested layout:

```
jev-cli/
  PLAN.md                        # this review plan
  docs/superpowers/plans/
    2026-09-18-phase-1.md        # Phase 1 TDD implementation plan
  pyproject.toml                 # console script: jev
  src/jev_cli/
    __init__.py
    cli.py                       # typer app; no HTTP
    config.py                    # key, base URL, default model
    client.py                    # TypeSafeClient wrapper
    questions.py                 # question-file parse + validate
    format.py                    # JSON envelope
    commands/
      ask.py                     # Phase 1
      models.py                  # Phase 1
      auth.py                    # Phase 1
      smoke.py                   # Phase 1
      agent.py                   # Phase 2 only
      skills.py                  # Phase 2 only
  tests/
    test_questions.py
    test_format.py
    test_client.py
    test_cli.py
```

`client.py` talks only to TypeSafe. Phase 3 would add `backends/llm.py`. Do not create `commands/agent.py` or `commands/skills.py` in Phase 1.

---

## 6. Implementation phases (detail)

Phase 0 is done (this document). **Build Phase 1. Stop. Review. Then Phase 2.**

The table at the top of this file is the contract. This section is the same split with exit codes and explicit exclusions.

### Phase 1 — Judgment CLI

Exit codes: `0` answered, `1` request failed, `2` usage / invalid questions.

Envelope (`data` is the System One body: `model`, `answers`, `usage`):

```json
{
  "status": "success",
  "data": { "model": "jev-1.13.0", "answers": {}, "usage": {} },
  "metadata": { "command": "ask" }
}
```

On failure, stdout is empty; stderr is `{ "status": "error", "error": { "code", "message" } }`.

See `docs/superpowers/plans/2026-09-18-phase-1.md` for the TDD task list.

### Phase 2 — Agent operability

Do not start until Phase 1 is reviewed. Adds discovery (`jev agent schema`) and `jev skills install` of the official skill. Does not add new Jev APIs.

### Phase 3 — Optional LLM comparison

`system-one-adapter` as `--backend llm`. Default remains Jev.

### Out of scope (all phases unless explicitly pulled in)

- Chat / “what should I do next”
- OAuth (TypeSafe has no public OAuth)
- Fine-tuning, LoRA, or per-account weights (TypeSafe does not support this)
- Image/audio/video state (Jev is text-only)
- Replacing the official skill with a home-grown one
- Wrapping the adapter as if it were TypeSafe

---

## 7. How this maps onto TypeSafe’s programming model

These rules are copied from the official skill. Keep them in CLI docs; do not restate them as a second skill:

1. Provide named JSON state. Point questions at paths like `` `ticket.messages[0].text` ``.
2. One judgment per question. Instructions + criteria in the question body; ids are for code only.
3. Batch independent questions in one `ask`. Do not loop `noul` in a shell `for`.
4. Use probabilities/confidence in the *caller*. High confidence may automate; low confidence should print `needs_review` or exit 3, not invent an action.
5. Jev cannot generate missing options. If the value is not in `criteria`, it cannot be chosen.

---

## 8. Sources

- Official skill: https://github.com/typesafe-ai/skills/blob/main/skills/typesafe-ai/SKILL.md (local copy: `~/.agents/skills/typesafe-ai/SKILL.md`)
- Agent skill install/usage: https://docs.typesafe.ai/agent-skill.md
- TypeSafe docs index: https://docs.typesafe.ai/llms.txt
- How to build: https://docs.typesafe.ai/concepts/how-to-build-with-system-one.md
- Primitives: https://docs.typesafe.ai/primitives.md
- Use-case map (incl. harness engineering): https://docs.typesafe.ai/concepts/use-case-map.md
- Skill suggestion cookbook: https://docs.typesafe.ai/cookbooks/skill_suggestion.md
- HTTP API: https://docs.typesafe.ai/api.md
- Models: https://docs.typesafe.ai/models.md
- Python SDK usage: https://docs.typesafe.ai/sdk/python/usage.md
- Adapter README + `_client.py`: https://github.com/typesafe-ai/system-one-adapter-python
- Pup analog (operational CLI only): `/Users/m.rathod/Documents/Projects/pup`
- Community CLIs: geilt/typesafe-cli, y0usaf/typesafe-cli
