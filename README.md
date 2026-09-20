# typesafe2

Safer decision-maker CLI for [TypeSafe](https://typesafe.ai) Jev. Same primitives as `typesafe` (`noul`, `choice`, `score`). Different policy: invalid answers fail closed, unused speculative heads cannot act, and a ranked line is not evidence when `find` says the document has no answer.

This is the `safer-decide` branch. Install it **beside** the published `typesafe` binary, then run the same questions on both.

## Install beside `typesafe`

Keep `typesafe` from PyPI. From this checkout:

```bash
pipx install -e . --force
```

That installs package `typesafeai-cli2` as `typesafe2`. It does not replace `typesafe`.

```bash
typesafe auth status    # baseline, PyPI
typesafe2 auth status   # this branch
```

API key: [TypeSafe console](https://console.typesafe.ai/settings/keys). Same `TYPESAFE_API_KEY` for both.

## What is stricter

- **Answer integrity.** Invented labels, NaN, missing options, non-argmax choices, and probabilities that do not add up → exit 1, `invalid_answer`. Not a success envelope.
- **`decide` consumes heads.** If questions include `operation` plus `click_target` / `type_text_target` / …, only the matching `*_target` is active. The rest are `ignored` even if they look confident. `data.action` is `act` or `abstain`. `needs_verify` is true when acting; a Choice is not proof.
- **`find` ranking is not evidence.** If every window’s exists noul is absent, `lines` is empty and `usable` is false.
- **State is untrusted data**, never instructions, on find/extract/verify/screen.

## Compare

[`examples/compare`](examples/compare) runs the same payload through `typesafe` and `typesafe2`.

```bash
./examples/compare/run.sh examples/ticket
./examples/compare/run.sh examples/compare/fan-out
```

Scratch JSON still belongs under `${TMPDIR:-/tmp}/codex/<project>/`. `typesafe2 skills install` writes **typesafe2-cli** and does not overwrite **typesafe-cli**.

## Commands

Same verbs as `typesafe`: `ask`, `noul` / `choice` / `score`, `find`, `rank`, `extract`, `verify`, `screen`, `suggest-skill`, `decide`, `models`, `smoke`, `auth status`, `agent schema`, `skills install`.

Exit `0` answered, `1` request failed or invalid answer, `2` bad flags or questions.
