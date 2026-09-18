# Phase 3 — agent workflows from TypeSafe’s own docs

Phase 1 is the pipe (`ask`, noul/choice/score). Phase 2 is discovery (`agent schema`, skills). **Phase 3 is the product:** cookbook-shaped commands so an agent’s search, extraction, classification, and review beat “read it yourself and guess.”

This is **not** an LLM-compare backend. Jev is the model. These verbs encode how TypeSafe says to *use* Jev.

Sources (live [llms.txt](https://docs.typesafe.ai/llms.txt) as of 2026-09-18): [use-case map](https://docs.typesafe.ai/concepts/use-case-map.md), [how to build](https://docs.typesafe.ai/concepts/how-to-build-with-system-one.md), [patterns](https://docs.typesafe.ai/patterns.md), [agent skill](https://docs.typesafe.ai/agent-skill.md), [API](https://docs.typesafe.ai/api.md), [Jev 1.13 jaggedness](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md), every cookbook linked below, [smart-home demo](https://docs.typesafe.ai/demos/smart-home.md).

## Documentation coverage

The HTTP surface is two calls: `POST /v1/systemone` and `GET /v1/models`. Phase 1 already represents **100% of the API**. Phase 3 does not invent new TypeSafe endpoints. It encodes the **recipes** TypeSafe documents on top of those two calls so an agent does not have to rediscover them.

The [use-case map](https://docs.typesafe.ai/concepts/use-case-map.md) is the organizing document. Industry accordion examples (recruiting, insurance, legal, support, …) are **instances of the 10 decision shapes**, not extra CLI commands. A recruiting pack is a questions file, not `typesafe recruit`.

### Five pillars → this CLI

| Pillar | What TypeSafe means | What this CLI does | What it does not |
| --- | --- | --- | --- |
| AI automation software | Code owns control flow; TypeSafe handles semantic decisions | Verbs + `decide` keep control in the agent/CLI; Jev never picks the next tool | Become an agent that loops itself |
| Real-time applications | ~100–150 ms judgments in a UI or game | Session-speed `ask`; same primitives | Embed in a 150 ms game loop (that is SDK-in-app) |
| Map-reduce over big data | Cheap judgments over giant corpora | `find` / `rank` / `extract` over files the agent already has | A Spark/warehouse job runner |
| Universal verification | Check prompts, extractions, citations, tool calls, other-model output | `verify` + `screen` | A second generative model |
| Harness engineering | Model routing, context retrieval, guardrails, skill pick | `suggest-skill`, `screen`, `rank`, `decide` | Own the host’s tool list or MCP |

### Ten decision shapes → verbs

| Shape | Reach for it when | CLI |
| --- | --- | --- |
| Classification | One known category should win | `ask` / `choice`; `decide` on confidence ([classification using confidence](https://docs.typesafe.ai/cookbooks/classification_using_confidence.md)) |
| Detection | Probability a property is present | `noul` / `screen` |
| Scoring | Ordered rubric | `score` / `rank` |
| Routing | A category selects the next code path | `ask` (fan-out) + `decide`; agent applies the route |
| Search | Find items matching a natural-language query | `find` |
| Retrieval | Most relevant context or records | `rank` after a local shortlist |
| Ranking | Order by semantic relevance or quality | `rank` |
| Verification | Check an artifact for failure modes | `verify` (citations, claims); `screen` (messages/tool calls) |
| ML feature extraction | Downstream classical ML needs semantic signals | Compose `ask` over rows; **not** a CatBoost trainer |
| Structured data extraction | Known fields from unstructured input | `extract` (regex spans, later date parts) |

That table is the product. If a Phase 3 command is missing, compose the same sequence with `ask`.

### Every cookbook

| Cookbook | Role of Jev | Role of code | CLI |
| --- | --- | --- | --- |
| [Parallel questions](https://docs.typesafe.ai/cookbooks/parallel_questions.md) | 13 independent answers, same as serial | Batch; 12.2× cheaper / 10× faster in the published run | `ask` (already) |
| [Line-by-line search](https://docs.typesafe.ai/cookbooks/semantic_find.md) | Choice over line ids + Noul “exists?” | Tag lines, rank, threshold | **`find`** |
| [Re-ranking](https://docs.typesafe.ai/cookbooks/rerank_typesafe.md) | One question per query–candidate | BM25/grep first, then sort | **`rank`** |
| [Pre-parsed extraction](https://docs.typesafe.ai/cookbooks/pre_parsed_value_extraction_cookbook.md) | Choice among regex spans (`none` hatch) | Regex over-finds; copy pick verbatim | **`extract`** |
| [Date extraction](https://docs.typesafe.ai/cookbooks/date_extraction_cookbook.md) | Choice over month/day/year/weekday | Calendar math, relative resolve | `extract --kind date` later; until then `ask` |
| [Citation check](https://docs.typesafe.ai/cookbooks/citation_check.md) | Choice: supports / contradicts / says nothing | String-match quote first; confidence gate | **`verify`** |
| [LLM guardrails](https://docs.typesafe.ai/cookbooks/llm_guardrails.md) | Hazard nouls + severity score | Threshold → pass / review / block | **`screen`** |
| [Skill suggestion](https://docs.typesafe.ai/cookbooks/skill_suggestion.md) | Rank all, reread top 3; gate nouls | Two calls; at most one name | **`suggest-skill`** |
| [Self-consistency: nouls](https://docs.typesafe.ai/cookbooks/consistency_noul_cookbook.md) | Raw P(yes) | Map 0.30–0.70 → `uncertain` | **`decide`** |
| [Self-consistency: choices](https://docs.typesafe.ai/cookbooks/consistency_choice_cookbook.md) | Label + probabilities | Top-p &lt; 0.60 → `uncertain` | **`decide`** (same command) |
| [Classification using confidence](https://docs.typesafe.ai/cookbooks/classification_using_confidence.md) | One Choice | Report coarser label when confidence low | `ask` + `decide` |
| [Classifying RAG passages](https://docs.typesafe.ai/cookbooks/classifying_rag_passages.md) | 4 nouls per query–passage | `route()` keep / conflict / drop | Compose `rank` + `screen`; pack later |
| [Entity alignment](https://docs.typesafe.ai/cookbooks/entity_alignment.md) | Score with 3 action levels + field nouls | Round to nearest level; no fitted threshold | Compose `ask`; pack later |
| [Structure recovery](https://docs.typesafe.ai/cookbooks/autoformat.md) | Stitch nouls, then block Choices | Merge + render Markdown; never rewrite words | Compose two `ask`s; pack later |
| [SDE cascade](https://docs.typesafe.ai/cookbooks/sde_cascade.md) | Per-field “is this wrong?” nouls | Cheap LLM extracts; escalate on `max` flag | TypeSafe part is **`verify`**. CLI does not call GPT |
| [Hierarchical classification](https://docs.typesafe.ai/cookbooks/hierarchical_classification.md) | Choice per node; beam K=3 | Geometric-mean path score | Compose with `ask`. CLI is not a taxonomy walker |
| [Function calling](https://docs.typesafe.ai/cookbooks/function_calling.md) | Choice over tools + closed-set args; `stated` noul for optional args | Dispatcher; min confidence of weakest arg | Compose with `ask`. CLI is not a tool router |
| [Autoresearch feature discovery](https://docs.typesafe.ai/cookbooks/autoresearch_feature_discovery.md) | Score/noul features per row | LLM proposes questions; CatBoost trains | **Not this CLI** |

### Patterns and demo

| Doc | CLI |
| --- | --- |
| [Speculative fan-out](https://docs.typesafe.ai/patterns/fan-out.md) | `ask`: all questions in one call; ignore unused in code |
| [Confidence-gated routing](https://docs.typesafe.ai/patterns/confidence-routing.md) | `decide`: answer is *what*; confidence is *whether to act* |
| [Composite scoring](https://docs.typesafe.ai/patterns/composite-scoring.md) | `decide` / local weights; do not hide the mix inside Jev |
| [Intent routing](https://docs.typesafe.ai/patterns/intent-routing.md) | `ask` (choice + score) then the agent selects the handler |
| [Smart-home demo](https://docs.typesafe.ai/demos/smart-home.md) | Fan-out + LLM fallback in the caller, not a `typesafe home` command |

### Jaggedness that the CLI must enforce

From [Jev 1.13 jaggedness](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md):

- Do not generate text. Extraction is Choice over candidates code already found.
- Arithmetic, counts, and calendar math stay in code (`extract` / date assemble / `decide`).
- Filter state first; do not dump the repo (`find` tags lines; Choice max **255**).
- Point questions at named paths. The skill already requires this.
- Do not treat Noul and Choice-yes as interchangeable; `decide` keeps the raw numbers.

### What the documentation is **not** asking this CLI to be

- An SDK replacement (`typesafe-ai` stays the design skill).
- An LLM comparison harness.
- A catalog of Codex/Grok jobs or industry vertical commands.
- A function-calling dispatcher, taxonomy beam searcher, or CatBoost loop.
- A real-time UI/game runtime.
- A generative model.

Coverage of *what is possible*: the API is fully represented; the 10 shapes are fully represented as verbs or compose-with-`ask`; 14 of 18 cookbooks are a verb, a `decide` policy, or an explicit compose recipe; 4 stay out (autoresearch) or later packs (hierarchy / function-calling dispatcher / autoformat / RAG `route()`). That is the right direction: **shapes, not industries**.

## Why agents lose today

TypeSafe questions are independent. Batching does not change answers; it only changes cost and latency ([parallel questions](https://docs.typesafe.ai/cookbooks/parallel_questions.md)). Agents still loop `noul` because the CLI only exposes `ask`.

Search, extract, and verify in the cookbooks are **local code + one or two `system_one` calls**, not chat. The CLI must **require the inputs those recipes need** (file, query, candidates, claim+source). That is how flags drive information without a thousand-job skill. The skill stays: questions name paths; these verbs **are** the paths.

## Commands to add

Scratch files stay under `${TMPDIR:-/tmp}/codex/<project>/`. Agents still must not read `TYPESAFE_*`.

Choice is capped at **255 options** (API). `find` / `rank` chunk above that: window, then lines inside ([semantic find](https://docs.typesafe.ai/cookbooks/semantic_find.md)).

### 1. `typesafe find`

Cookbook: semantic find.

```bash
typesafe find --file path --query "who owns uploaded code?"
```

Local: split file into tagged lines `L000| …`. One request: Choice over line ids + Noul `exists`. Print ranked lines, `exists`, and a verdict (`answered` / `partial` / `absent`) using documented bands (cookbook uses ~0.70 / ~0.35 as a starting point, not gospel).

This is agent **search** over a file they already have, without embeddings.

### 2. `typesafe rank`

Cookbook: re-ranking.

```bash
typesafe rank --query "…" --candidates-file items.json --id-field id --text-field text
```

`items.json` is an array the agent built (grep hits, BM25, files). One Score or Noul per item against the query (batch, chunk if needed). CLI sorts. Agent does not loop `score`.

### 3. `typesafe extract`

Cookbook: pre-parsed extraction. Date parts are the same shape (Choice over closed sets; assemble in code).

```bash
typesafe extract --state-file doc.json --pattern email --question "Which address should receive the receipt?"
```

Local regex (email / phone / money, or `--candidates` JSON). Choice options **are** the spans plus `none`. Return the chosen string **verbatim**. Normalization stays in the caller (E.164, Decimal). Jev must not invent a value.

### 4. `typesafe verify`

Cookbook: citation check. SDE-cascade’s TypeSafe rung is the same idea: per-field “is this unsupported?” nouls.

```bash
typesafe verify --claim "…" --source-file rfc.txt [--quote "…"]
```

Local: if `--quote` is set and not in source → `fabricated` (no API). Else Choice on `{claim, section}`: supports / contradicts / says_nothing. Envelope includes `confidence` and `auto` vs `review` using a default like 0.8.

Agent **review** of its own citations and of other models.

### 5. `typesafe screen`

Cookbook: LLM guardrails.

```bash
typesafe screen --text-file msg.txt
```

Fixed pack in one fan-out: jailbreak noul, injection noul, sensitive-data noul, harm score. CLI prints the nouls **and** a suggested action from thresholds in one place (easy for humans to edit). Not a second personality — a gate.

### 6. `typesafe suggest-skill`

Cookbook: skill suggestion.

```bash
typesafe suggest-skill --task "…" --skills-dir ~/.agents/skills
```

Call 1: Choice over skill names (description as criteria) + gate nouls (act on system? documented procedure? prose suffices?). Call 2: top 3 with SKILL.md excerpts + per-skill `fits` nouls. Output at most one name, or none. Agent still decides whether to load it.

This is the “agents-for-agents” hook: Jev in front of skill load, not instead of the agent.

### 7. `typesafe decide` (no HTTP)

Cookbooks: consistency nouls **and** consistency choices. Patterns: confidence-gated routing.

```bash
typesafe decide --answers-file "$WORKDIR/last.json" --noul-band 0.30:0.70 --choice-min-p 0.60
```

- Each noul → `no` / `uncertain` / `yes` from the band.
- Each choice → winning label, or `uncertain` when top probability is below `--choice-min-p` (cookbook uses 0.60; this is **not** the API `confidence` field).
- Keep raw probabilities and confidence in the envelope.
- Review band is application policy; do not hide it inside Jev.

## What we do **not** add

- LLM `--backend` / compare (dropped).
- A catalog of every Codex activity, or industry commands (recruiting, claims, KYC, …).
- Letting Jev generate missing options or extract strings it was not given as candidates.
- Dumping the whole repo into `find` without tagging lines (Choice max 255).
- A function-calling dispatcher, hierarchical beam walker, CatBoost/autoresearch loop, or GPT extract rung.
- Replacing the official `typesafe-ai` skill.

SDE cascade (verify rung only), hierarchical beam, date parts, RAG passage keep/drop, entity-alignment Score, autoformat: same primitives. Ship the seven verbs above first; those become `examples/packs/` or a later flag if agents actually hit them.

## Skill change (small)

**typesafe-cli** stays questions-first for `ask`. Direct the agent to **compose** verbs, not invent a job catalog:

- Many questions, one state → one `ask` (never a noul loop).
- Search / rank / extract / verify / screen / suggest-skill → that verb’s flags.
- Local prefilter before HTTP (regex, quote match) when the cookbook does.
- Second request only to shrink a shortlist or fetch evidence.
- `decide` on the JSON so 0.49 vs 0.51, or a 0.51/0.49 choice split, does not flip automation.

If a Phase 3 command is missing, compose the same sequence with `ask`.

## Success

An agent reviewing a PR can:

1. `find` a policy or test file for a plain-language question.
2. `verify` a claim against a source hunk.
3. `extract` an identifier from a log without hallucinating digits.
4. `suggest-skill` instead of loading three wrong skills.
5. `decide` so 0.49 vs 0.51 does not flip automation.

Each of those is a documented TypeSafe recipe, with flags that force enough context, JSON in `/tmp/codex/<project>/`, and thresholds in this repo in one file.

Phase 1+2 remain the pipe and the discovery layer. Phase 3 is those verbs, mapped from the use-case map’s 10 shapes rather than from a subset of cookbooks we liked.
