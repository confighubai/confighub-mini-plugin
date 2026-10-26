# The ConfigHub plugin, for Claude Code and Codex

Keeps a record of what the agent changes in configuration, and why. The agent is asked for nothing; when it opens a file that earlier sessions changed, it is given what they changed and why. Nothing in the repository changes unless you turn that on.

- **What it records:** each value the agent changes in Kubernetes files, Helm values, Kustomize, Compose, workflows, settings files, Terraform variables and agent configuration; each `kubectl`, `helm`, `argocd`, `flux`, `terraform` and `cub` command, with where it went, whether it changed something, and the values it set, such as `--replicas=5` or `helm --set`; and what the agent said at the end of each turn.
- **What it never keeps:** a command's output, a copy of a file, or a value that looks like a credential.
- **Where:** in `~/.confighub/agent-changes`, outside the repository.

Read it in a session with `/confighub:changes`, and ask about one value with `/confighub:why replicas`. In a terminal, `bin/confighub mini changes` from this plugin does the same.

## More, when you ask for it

Each is turned on in Claude Code's settings, as `env`:

| Setting | What it adds |
|---|---|
| `CUB_MINI_ASK_REASONS=1` | A reason for each value, in the agent's own answer |
| `CUB_MINI_PULL_REQUEST=1` | The record and its reasons in each pull request the agent opens with `gh` |
| `CUB_MINI_RECORD_IN_REPO=1` | The record in each commit the agent makes, readable from any checkout |
| `CUB_MINI_OTEL=1` | Each value changed, each command that changed something, and each reason, sent at the end of each turn to an OpenTelemetry collector as log events, with Claude Code's `session.id`. Set `CUB_MINI_OTEL_ENDPOINT` to the collector's OTLP/HTTP address, such as `http://localhost:4318` |
| `CUB_MINI_KEEP_IN_HUB=1` | Each change kept in a hub, so that it survives a vendor's next version. This needs the confighub-mini package and a hub; the plugin alone carries none |

## In Codex

Codex keeps the same record, but not by installing this plugin there: Codex runs only the hooks in its own configuration, not those a plugin carries. From a copy of this plugin, the one Claude Code installed or a clone of its repository, run:

```
bin/confighub mini codex-setup
```

It copies the program to `~/.codex/confighub-mini` and adds the plugin's hooks to `~/.codex/hooks.json`, beside any hooks already there. Then open Codex and type `/hooks` to approve them, once. Read the record with `~/.codex/confighub-mini/bin/confighub mini changes`. `codex-setup --dry-run` says what it would do, and `codex-setup --remove` takes it all out again.

## What is in it

One program for each of macOS and Linux, on Intel and ARM, and `bin/confighub-mini`, which runs the one for this machine. The program is the same one that runs `cub mini` in the confighub-mini package. The plugin has no ConfigHub server, no PostgreSQL and no `cub`, and needs no account.
