# Compare `typesafe` vs `typesafe2`

Same `state.json` + `questions.json` for both binaries. Do not add policy text to the questions.

```bash
./examples/compare/run.sh examples/ticket
./examples/compare/run.sh examples/code-change
./examples/compare/run.sh examples/compare/fan-out
```

`fan-out` is one `operation` Choice plus speculative `*_target` heads, the shape TypeSafe’s fan-out pattern uses. The questions do not tell either CLI what to do with unused heads.

The script writes under `${TMPDIR:-/tmp}/codex/typesafe-compare/<example>/`. Do not copy those payloads into the git working tree.
