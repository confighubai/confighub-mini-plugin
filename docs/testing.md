# Testing the plugin and confighub mini

The release checks exercise the built packages and real agent sessions. The published records give the model, version, environment and result. Use the [evidence page](evidence.md) to see which claims those runs support and the [limits](limits.md) to see where the behavior depends on the agent, provider or delivery path.

| What you want to check | Where to start |
|---|---|
| See what the plugin records in your own Claude Code or Codex session | [Try the plugin on its own](try-the-plugin.md) |
| Compare whether agents keep an earlier change | [Run the plugin evaluation](../evaluate/README.md). It runs the same job with and without the plugin on the models you choose. |
| Exercise the hub with an app and an approval | [Try confighub mini](try-confighub-mini.md) or run the [roadmap examples](../examples/roadmap/README.md). |
| Check a starter or a provider | [Starters](starters.md) links the examples and states which ones use stand-ins. |
| Review the evidence for a particular behavior | [Dated run records](runs/README.md). |

When comparing two agent runs, start with the same app, request and model. Check the resulting files, the hub revision and approval, and the running service wherever the task promises delivery. Record elapsed time and model use alongside the result. A local stand-in can verify the steps against its contract. A claim about a live provider needs a run on that provider, and a claim about an unaided developer needs a run with a person.
