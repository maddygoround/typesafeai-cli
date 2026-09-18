Samples for the TypeSafe **agent CLI**. How to run them, install, and what agents should do lives in the [project README](../README.md).

| Directory | What it is |
| --- | --- |
| [ticket/](ticket/) | Support message → refund / intent / frustration |
| [code-change/](code-change/) | A skill hunk → whether agents must attach real code |

Copy these into a temp dir before a live call (agents use `${TMPDIR:-/tmp}/codex/<project>/`, not the git tree):

```bash
WORKDIR="${TMPDIR:-/tmp}/codex/typesafeai-cli"
mkdir -p "$WORKDIR"
cp examples/ticket/*.json "$WORKDIR/"
typesafe ask --state-file "$WORKDIR/state.json" --questions-file "$WORKDIR/questions.json"
```
