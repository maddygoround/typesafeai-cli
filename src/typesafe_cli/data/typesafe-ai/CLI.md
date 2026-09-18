# Using the typesafe CLI

This file is a sidecar to the official TypeSafe skill. It does not replace it.

For live evaluations, prefer `typesafe ask` over ad-hoc curl or a throwaway script.

```bash
typesafe ask --state-file state.json --questions-file questions.json
typesafe noul "Does this request a refund?" --state "..."
typesafe agent schema
```

Stdout is `{ "status", "data", "metadata" }`. Errors go to stderr as JSON. Jev (the model) does not generate prose or decide the next action — compose answers in code.

Discover commands with `typesafe agent schema` (or `typesafe --help` in agent mode).
