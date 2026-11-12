# Working with the tools you already have

This page is for someone who wants to know what the ConfigHub plugin does with a tool they already use, and how far along each one is. The plugin hands each job to the tool made for it, and does not try to replace it.

| Your tool | What you get | How to set it up | Status |
|---|---|---|---|
| Git and GitHub | The reason for a change kept with the commit and shown in the pull request | [Git, GitHub and a hub](git-and-github.md) | Works |
| Any MCP server | Each call in the record, and as much checking as you choose | [How closely MCP calls are watched](how-it-works.md#how-closely-mcp-calls-are-watched) | Claude Code, and Codex with a local MCP server. Not yet with a payments or hosted database server |
| A sandbox or container | The record, and the stop before an undo, across sandboxes that share only the repository | [In CI or a sandbox](ci-and-sandboxes.md) | `sandbox-exec` and Linux containers |
| nono | An agent working inside nono, with its changes recorded | No guide yet | Early |
| Entire | The reason for a value, with the checkpoint of each session | [If you use Entire](entire.md) | Works |
| Vercel | Recorded reasons beside current project settings and local env files | `confighub mini changes --why NAME --vercel production`, with a linked project and signed-in CLI | The Vercel CLI calls are checked. Not yet against a signed-in project or a running deployment |
| OpenTelemetry | Each change sent separately to your collector | `CUB_MINI_OTEL=1`: [settings](how-it-works.md#settings) | Works with OpenTelemetry Collector Contrib 0.111.0, including redaction and a retry after the collector is down. Authentication, TLS and retention not tried |
| Vault | Owner supplies a Vault value through standard input; the runtime key reads it, the proposal key cannot | Pipe the value in: `vault kv get -field=KEY PATH \| cub mini secret set APP KEY --variant live --change-desc "WHY"` ([a secret for live](from-plugin-to-confighub.md#a-secret-for-live-that-no-agent-can-read)) | Works with Vault 2.2.1 in development mode, rotation included. You copy each value yourself: it isn't a live Vault provider, and production Vault policies haven't been tried |
| A monitor or alert | Agents stopped when it fires | Have it run `touch ~/.confighub/halt` on the machine | Works when your monitor runs that command |
| Sigstore | Checking the record with `cosign` | [Signed records](signed-records.md) | Works |
| SPIFFE | The record signed with the agent's own workload identity | [Signed records](signed-records.md#signing-with-the-agents-own-identity) | Works |
| Argo CD and Flux | Clusters deploy what a hub approved | [GitOps over OCI](gitops-over-oci.md) | Works, on a local cluster and on hosted ConfigHub |

**Recording and delivery are separate.** The plugin records supported Vercel and AWS changes. Applying approved hub settings to those providers hasn't been tried. Delivery works to files, VM services through file pull, and clusters through Argo CD or Flux; each needs its configured delivery path.

If you try one of these, we'd like to hear how it went: [open an issue](https://github.com/confighubai/confighub-mini-plugin/issues).

Not here because other tools do them: running agents at scale, and hardening kernels, browsers and libraries.
