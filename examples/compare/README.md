# Compare `typesafe` vs `typesafe2`

Same `state.json` + `questions.json`. Baseline binary is `typesafe` (PyPI). This branch is `typesafe2`.

```bash
./examples/compare/run.sh examples/ticket
./examples/compare/run.sh examples/code-change
./examples/compare/run.sh examples/compare/fan-out
```

`fan-out` is the coding-agent case that matches the safer policy: one `operation` Choice plus speculative `*_target` heads. `typesafe decide` will treat every head as live. `typesafe2 decide` ignores unused targets and may abstain.

Do not copy these payloads into the git working tree when you run them. The script writes under `${TMPDIR:-/tmp}/codex/typesafe-compare/`.
