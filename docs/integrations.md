# Working with the tools you already have

This page is for someone who wants to know what the ConfigHub plugin does with a tool they already use, and how far that has been tested. The plugin hands each job to the tool made for it, and does not try to replace it.

| Your tool | What you get | How to set it up | How far it has been run |
|---|---|---|---|
| Git and GitHub | The reason for a change kept with the commit and shown in the pull request | [Git, GitHub and a hub](git-and-github.md) | In the checks made before each release |
| Any MCP server | Each call in the record, and as much checking as you choose | [How closely MCP calls are watched](how-it-works.md#how-closely-mcp-calls-are-watched) | Claude Code stand-ins; Codex MCP stdio and explicit refusals checked on two models against a local SQLite fixture ([record](runs/2026-11-09/codex-mcp/README.md)). No payments or hosted database provider yet |
| A sandbox or container | The record, and the stop before an undo, across sandboxes that share only the repository | [In CI or a sandbox](ci-and-sandboxes.md) | `sandbox-exec` and Linux containers |
| nono | An agent working inside nono, with its changes recorded | No guide yet | Once, by us |
| Entire | The reason for a value, with the checkpoint of each session | [If you use Entire](entire.md) | By us; no outside use yet |
| Vercel | Recorded reasons beside current project settings and local env files | `confighub mini changes --why NAME --vercel production`, with a linked project and signed-in CLI | Ten scripted CLI-contract checks; no authenticated project or running deployment checked ([record and reproduction](runs/2026-11-09/vercel-readback/README.md)) |
| OpenTelemetry | Each change sent separately to your collector | `CUB_MINI_OTEL=1`: [settings](how-it-works.md#settings) | Real Collector Contrib 0.111.0: ten checks for delivery, redaction, no duplicate export and outage retry, with scripted hooks; remote IAM and retention not tested ([record and reproduction](runs/2026-11-09/otel-collector/README.md)) |
| Vault | Owner supplies a Vault value through standard input; the runtime key reads it, the proposal key cannot | [Handoff and reproduction](runs/2026-11-09/vault-secrets/README.md) | Real Vault 2.2.1 dev server, twelve scripted checks including rotation; explicit copy/fetch, not a live provider or production policy |
| A monitor or alert | Agents stopped when it fires | Have it run `touch ~/.confighub/halt` on the machine | By hand only: no monitor has fired it yet |
| Sigstore | Checking the record with `cosign` | [Signed records](signed-records.md) | By us |
| SPIFFE | The record signed with the agent's own workload identity | [Signed records](signed-records.md#signing-with-the-agents-own-identity) | By us |
| Argo CD and Flux | Clusters deploy what a hub approved | [GitOps over OCI](gitops-over-oci.md) | On a local cluster and on hosted ConfigHub, by us |

Nobody outside has run any of these yet. If you try one, we would like to hear how it went.

Not here because other tools do them: running agents at scale, and hardening kernels, browsers and libraries.
