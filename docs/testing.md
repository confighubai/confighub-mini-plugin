# Testing the plugin and confighub mini

The release checks exercise the built packages and real agent sessions. The published records give the model, version, environment and result. Use the [evidence page](evidence.md) to see which claims those runs support and the [limits](limits.md) to see where the behavior depends on the agent, provider or delivery path.

| What you want to check | Where to start |
|---|---|
| See what the plugin records in your own Claude Code or Codex session | [Try the plugin on its own](try-the-plugin.md) |
| Check that a walkthrough still works | Each [walkthrough](../examples/walkthroughs/README.md) ends with a Testing section: the request given to an agent, the commands that show whether the job was done, and the results of its own test runs |
| Compare whether agents keep an earlier change | [Run the plugin evaluation](../evaluate/README.md). It runs the same job with and without the plugin on the models you choose. |
| Exercise the hub with an app and an approval | [Try confighub mini](try-confighub-mini.md) or run the [roadmap examples](../examples/roadmap/README.md). |
| Check a starter or a provider | [Starters](starters.md) links the examples and states which ones use stand-ins. |
| Review the evidence for a particular behavior | The [run records](#run-records) below. |

When comparing two agent runs, start with the same app, request and model. Check the resulting files, the hub revision and approval, and the running service wherever the task promises delivery. Record elapsed time and model use alongside the result. A local stand-in can verify the steps against its contract. A claim about a live provider needs a run on that provider, and a claim about an unaided developer needs a run with a person.

## Run records

Each record is one dated run on a real machine, with real Claude Code or Codex sessions where it says so, kept as it came out. The pages that quote a transcript or a figure link to its record. Where something has not run, the pages say "Not yet".

| Date | Record | What it shows |
|---|---|---|
| 20 October 2026 | [A person approves an agent's change](runs/2026-10-20/approval/README.md) | The change waits; the agent's own approval is refused; a colleague's does not count; the named person's lets exactly that revision through |
| 24 October 2026 | [How often a later agent undoes an earlier one's change](runs/2026-10-24/evaluate/README.md) | 240 runs of two real sessions: without the plugin, told afterwards, and stopped before the undo |
| 24 October 2026 | [Beyond replicas, and unattended](runs/2026-10-24/evaluate-kinds/README.md) | The same for an image, an environment variable and a flag, with an agent in CI and nobody to ask |
| 24 October 2026 | [The gate with an agent in auto mode](runs/2026-10-24/gate-auto/README.md) | 40 sessions told to put production on 4 replicas and left alone |
| 25 October 2026 | [Two sandboxes that share only the repository](runs/2026-10-25/evaluate-apart/README.md) | The stop when the record travels in the repository |
| 26 October 2026 | [Friday's replicas, end to end](runs/2026-10-26/replicas-end-to-end/README.md) | One value from the first session to the approval gate, in real sessions |
| 29 October 2026 | [A service on a VM fed from the hub](runs/2026-10-29/sam-vm/README.md) | Only approved values reach the service's files; agents with a hub key and no SSH key |
| 29 October 2026 | [An app platform on the hub](runs/2026-10-29/sam-platform/README.md) | A release proposed by an agent, approved to staging and live, and rolled back |
| 29 October 2026 | [The telling](runs/2026-10-29/sam-telling/README.md) | The three lines the person is told, and nothing else, in real sessions |
| 5 November 2026 | [The one-minute first try](runs/2026-11-05/quickstart/README.md) | A second session asked to cut costs keeps the sale's replicas, told by the plugin about the earlier change |
| 9 November 2026 | [Codex MCP calls in the record](runs/2026-11-09/codex-mcp/README.md) | Real Codex sessions: MCP writes recorded, writes at `ask` refused before the call, with its check |
| 9 November 2026 | [Recorded changes sent to an OpenTelemetry collector](runs/2026-11-09/otel-collector/README.md) | Each recorded change delivered to a real OTLP/HTTP receiver, with no hub |
| 9 November 2026 | [Staging memory, production left alone](runs/2026-11-09/staging-memory/README.md) | Codex sessions with the app skill change only staging; the base, live and live's revision stay as they were |
| 9 November 2026 | [A Vault secret read only by the runtime](runs/2026-11-09/vault-secrets/README.md) | The owner supplies a secret from Vault; the proposal key cannot read it, and the runtime's key reads it |
| 9 November 2026 | [Vercel project-setting read-back](runs/2026-11-09/vercel-readback/README.md) | The recorded value, the Vercel project's value and the local file's value, told apart |
| 10 November 2026 | [Ordinary app requests and visible ConfigHub activity](runs/2026-11-10/agent-workflow/README.md) | Real Claude Code and Codex sessions: when the plugin offers a hub, and what it says |
