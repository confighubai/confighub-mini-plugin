# The ConfigHub plugin, for Claude Code and Codex

The plugin keeps a record of what an AI agent changes in your configuration, and why. You don't ask the agent to do anything differently. When the agent opens a file that earlier sessions changed, the plugin tells it what they changed and why, before it makes changes of its own.

## What it records

- **Values the agent changes** in Kubernetes files, Helm values, Kustomize, Compose, GitHub Actions workflows, settings files, Terraform variables and agent configuration.
- **Commands the agent runs** with `kubectl`, `helm`, `argocd`, `flux`, `terraform` or `cub`: where each one went, whether it changed something, and the values it set, such as `--replicas=5` or `helm --set`.
- **What the agent said** at the end of each turn.

It never keeps a command's output, a copy of a file, or anything that looks like a password, key or token. The record is kept in `~/.confighub/agent-changes`, outside your repository. Nothing in the repository changes unless you turn that on.

## Reading the record

In a Claude Code session:

- `/confighub:changes` shows what the agent changed in its latest session, and why.
- `/confighub:why replicas` shows every recorded change to one value, and why.
- `/confighub:install-mini` installs confighub mini, which is ConfigHub made small enough to run on your laptop, and starts it.

In a terminal, `bin/confighub mini changes`, run from this plugin's folder, shows the same record as `/confighub:changes`.

## Settings

Each setting is off unless you turn it on, in Claude Code's settings file under `env`:

| Setting | What it adds |
|---|---|
| `CUB_MINI_ASK_REASONS=1` | The agent gives a reason for each value it changes, in its answer to you. |
| `CUB_MINI_PULL_REQUEST=1` | The record and its reasons are added to each pull request the agent opens with `gh`. |
| `CUB_MINI_RECORD_IN_REPO=1` | The record is added to each commit the agent makes, so anyone with a checkout can read it. |
| `CUB_MINI_OTEL=1` | Each changed value, each command that changed something, and each reason are sent to your OpenTelemetry collector at the end of each turn, as log events tagged with Claude Code's `session.id`. Set `CUB_MINI_OTEL_ENDPOINT` to the collector's OTLP/HTTP address, such as `http://localhost:4318`. |
| `CUB_MINI_KEEP_IN_HUB=1` | Each change is also kept in confighub mini, so that it survives a vendor's next version. This needs confighub mini installed; the plugin on its own does not include it. |

## In Codex

Codex runs only the hooks in its own configuration, so installing this plugin in Codex records nothing. Instead, from a copy of this plugin (the one Claude Code installed, or a clone of its repository), run:

```
bin/confighub mini codex-setup
```

This copies the program into `~/.codex/confighub` and adds the plugin's hooks to `~/.codex/hooks.json`, next to any hooks you already have. Then open Codex and type `/hooks` to approve them. You only need to do this once.

To read the record, run `~/.codex/confighub/bin/confighub mini changes`. To see what `codex-setup` would do without doing it, add `--dry-run`. To remove it, run `codex-setup --remove`.

## What is in it

The plugin contains one program for each of macOS and Linux, on Intel and ARM, and `bin/confighub`, which runs the right one for your machine. It has no server and no database, and needs no account.
