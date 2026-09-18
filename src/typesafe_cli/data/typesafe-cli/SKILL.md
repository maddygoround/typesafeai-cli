---
name: typesafe-cli
description: >
  Drive Jev through the typesafe CLI. Use when you need a typed snap judgment
  (route, yes/no, score) over local task context: a ticket, a diff, a tool list,
  a failing test. Collect privacy-safe state yourself, then run typesafe ask.
  Do not curl TypeSafe, do not write throwaway SDK scripts, do not read TYPESAFE_*
  env vars or key files. Triggers: typesafe CLI, Jev, noul, choice, score,
  typed judgment, which skill, is this urgent, tool routing.
---

# typesafe CLI

Jev judges only the `state` and `questions` you send. It cannot see the repo, the diff, AGENTS.md, skills, MCP, memory, or prior tool results unless you put a summary in `state`.

You are the context adapter. The CLI is the pipe.

## Secrets

The CLI loads credentials. You never do.

Run `typesafe auth status`. Read `data.has_key` only. If it is false, ask the human. Do not open `~/.config/typesafe/env`, `.env.local`, or print `TYPESAFE_*`.

## Procedure

### 1. Confirm the binary and a key

```bash
typesafe auth status
```

Done when `has_key` is true. If the command is missing, tell the human to install typesafeai-cli.

### 2. Name the decision

One sentence: what will you **do** with the answer (pick a skill, gate a tool, label a ticket). If Jev cannot return a type that maps to that action, do not call it — decide locally.

### 3. Collect state locally

Gather only facts that judgment needs. Write `state.json` with **named fields**.

| Job | Collect locally | Put in state |
| --- | --- | --- |
| Route a skill/tool | List names + one-line what each does | `tools` array; `task` string |
| Judge a change | `git diff --stat` and a short summary of hunks, not the whole tree | `diff_stat`, `diff_summary`, `task` |
| Ticket / message | The message text, plus any policy line you actually need | `message`, `policy` |
| Test / CI | Relevant snippet of the failure, not the full log | `failure`, `command` |

Redact secrets, tokens, private customer data, and anything the human did not approve to leave the machine. If the full diff is required and cannot be redacted, **do not call TypeSafe** — decide locally.

Point questions at fields with backticks: `` `message` ``, `` `tools` ``, `` `diff_summary` ``.

Done when a stranger could judge from `state.json` alone.

### 4. Write questions

`questions.json`: map of id → `{type, instructions, criteria?}`.

- `noul` — is this statement true? (probability)
- `choice` — pick one option; **≥2** named options
- `score` — place on an ordered rubric; **≥2** levels

Batch independent questions in one file. One judgment per question. Put the full meaning in `instructions`, not in the id.

Always include an out: `other`, `none`, or `abstain` on choices so Jev is not forced.

Done when every question is answerable from `state.json`.

### 5. Call the CLI

```bash
typesafe ask --state-file state.json --questions-file questions.json
```

One-shot: `typesafe noul "…" --state "…"` / `choice` / `score`. Prefer `ask` for more than one question.

Read stdout JSON: `data.model` should be a Jev id (`jev-1.13.0`). `data.answers` is the result. Do not parse prose; there is none.

### 6. Apply the answer here

Thresholds are yours, not Jev's.

- Noul near 0.5 is **unsure**, not medium. Do not automate.
- Choice/score `confidence` low → abstain or ask the human.
- Then you pick the skill, run the tool, or stop. Jev does not choose the next action.

## Commands

```bash
typesafe auth status
typesafe agent schema
typesafe ask --state-file state.json --questions-file questions.json
typesafe noul "…" --state "…"
typesafe choice "…" --option a --option b --state "…"
typesafe score "…" --level low --level high --state "…"
```

Discover flags with `typesafe agent schema`. Do not invent request fields.

## Official TypeSafe skill

`typesafe-ai` is for **designing** TypeSafe into application code (SDK). This skill is for **running** Jev now through the CLI. Live evaluations in a coding session use this skill.
