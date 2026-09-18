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

Jev judges only the `state` and `questions` you send. It cannot see the repo, the diff, AGENTS.md, skills, MCP, memory, or prior tool results. A label like "the code change" or a file path with no body is not context. If the decision is about code, you must copy the relevant slices into `state`.

You are the context adapter. The CLI is the pipe.

## Scratch files

Never write `state.json`, `questions.json`, or other TypeSafe payloads into the git working tree.

Put them in a **private temp directory** scoped to this project:

```bash
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
WORKDIR="${TMPDIR:-/tmp}/codex/$(basename "$ROOT")"
mkdir -p "$WORKDIR"
```

Then `$WORKDIR/state.json` and `$WORKDIR/questions.json`. For a one-line state, prefer `--state "…"` and skip files.

Deleting those files after the call is good. Leaving them is fine. Do not commit them.

## Secrets

The CLI loads credentials. You never do.

Run `typesafe auth status`. Read `data.has_key` only. If it is false, ask the human. Do not open `~/.config/typesafe/env`, `.env.local`, or print `TYPESAFE_*`.

## Procedure

### 1. Confirm the binary and a key

```bash
typesafe auth status
```

Done when `has_key` is true. If the command is missing, tell the human to install typesafeai-cli.

### 2. Name the decision, then write the questions

Do not start by dumping context. Pup gets enough information because **the command flags are the contract**. TypeSafe's contract is the questions: they name the fields Jev is allowed to look at.

One sentence: what you will **do** with the answer. If that is not a noul / choice / score, decide locally.

Then write `$WORKDIR/questions.json`. Each question's `instructions` must point at named paths with backticks (`` `task` ``, `` `files[0].hunk` ``, `` `tools` ``). Those paths **are** the collection list. There is no catalog of agent jobs to encode in this skill.

- `noul` — is this statement true?
- `choice` — pick one; **≥2** options; include `other` / `none` / `abstain`
- `score` — ordered rubric; **≥2** levels

Batch independent questions. One judgment each. Meaning lives in `instructions`, not in the id.

Done when every question names the fields it needs.

### 3. Fill only those fields

Read the repo, diff, tests, or tool list **here**. Put into `$WORKDIR/state.json` **only** the paths the questions reference.

Completeness: a stranger could answer the questions from `state.json` alone.

If a path is code (`` `files[0].hunk` ``), the value must be the slice (path + line range + body), not a filename and not "see the PR." Prefer under ~8k tokens of code. Do not send the tree.

Redact secrets. If a required slice cannot be redacted, **do not call TypeSafe**.

### 4. Call the CLI

```bash
typesafe ask --state-file "$WORKDIR/state.json" --questions-file "$WORKDIR/questions.json"
```

One-shot: `typesafe noul "…" --state "…"` / `choice` / `score`. Prefer `ask` for more than one question.

Read stdout JSON: `data.model` should be a Jev id (`jev-1.13.0`). `data.answers` is the result. Do not parse prose; there is none.

### 5. Apply the answer here

Thresholds are yours, not Jev's.

- Noul near 0.5 is **unsure**, not medium. Do not automate.
- Choice/score `confidence` low → abstain or ask the human.
- Then you pick the skill, run the tool, or stop. Jev does not choose the next action.

## Commands

```bash
typesafe auth status
typesafe agent schema
typesafe ask --state-file "$WORKDIR/state.json" --questions-file "$WORKDIR/questions.json"
typesafe noul "…" --state "…"
typesafe choice "…" --option a --option b --state "…"
typesafe score "…" --level low --level high --state "…"
```

Discover flags with `typesafe agent schema`. Do not invent request fields.

## Official TypeSafe skill

`typesafe-ai` is for **designing** TypeSafe into application code (SDK). This skill is for **running** Jev now through the CLI. Live evaluations in a coding session use this skill.
