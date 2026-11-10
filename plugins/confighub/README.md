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
- `/confighub:why replicas` shows every recorded change to one value, and why. An explicit `confighub mini changes --why NAME --vercel production` also reads the linked Vercel project's setting and compares local env files; it requires an installed, signed-in Vercel CLI.
- `/confighub:permissions` shows what your settings files allow agents to run, which rules were used, and a narrower set you can apply and undo. A line tells you when permissions, hooks or instructions change.
- `/confighub:checks` sets how much is done about MCP tool calls in this folder: `off`, `log` (where you start), `warn`, `repeats` or `ask`. At `repeats`, an agent about to repeat an earlier change is held back once and told of it. At `ask`, you are asked first, and also before an edit that undoes a value an earlier session set for a reason.


- `/confighub:inventory` shows what the repository deploys: each Kustomize overlay, Helm release and Argo CD Application, and what deploys it; the values that differ between environments; and the values agents changed. It reads only the repository's files.
- `/confighub:install-mini` installs confighub mini, which is ConfigHub made small enough to run on your laptop, and starts it.
- `/confighub:to-hub` copies what agents changed here, and why, into the ConfigHub your `cub` is signed in to: your organization's, with no confighub mini, or your own. It names the hub and lists what it would write; `/confighub:to-hub --yes` writes it.

In a terminal, `bin/confighub mini changes`, run from this plugin's folder, shows the same record as `/confighub:changes`.

## Asking for an app with ConfigHub

Ask for an app "using ConfigHub", or ask the agent to attach ConfigHub to the app you have. The plugin's skill tells the agent what to run. It writes the app and its settings file, starts a hub on your machine if none answers (the plugin's own `confighub mini get`: no account, no sign-in), and makes three copies of the settings with `cub mini adopt`: a base, a staging copy that takes changes at once, and a live copy, your production, which changes only when you run the `cub mini approve` command it prints. If you keep `.env.staging` or `.env.production`, each becomes that copy's own values from the start. With `cub mini require-approval --agent`, the agent gets a key that can propose and cannot approve.

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

For the tested Codex CLI 0.163, configure the hooks explicitly. From a copy of this plugin (the one Claude Code installed, or a clone of its repository), run:

```
bin/confighub mini codex-setup
```

This copies the program into `~/.codex/confighub` and adds the plugin's hooks to `~/.codex/hooks.json`, next to any hooks you already have. Then open Codex and type `/hooks` to review them. Run setup again after upgrading; changed hook definitions need a fresh review.

To read the record, run `~/.codex/confighub/bin/confighub mini changes`. To see what `codex-setup` would do without doing it, add `--dry-run`. To remove it, run `codex-setup --remove`.

In Codex, completed MCP calls are also recorded after `codex-setup`. At `ask`, changing MCP calls and supported shell-file undos are refused with an explanation: the hook cannot request an approval prompt there. A refused undo is refused again on retry. Codex `apply_patch` edits are recorded afterwards but are not held before an undo; failed MCP calls can be missing because Codex 0.163 emits no completion callback for them. Read Codex's session transcript for those attempts. This is not approval in the coding-agent chat.

## What is in it

The plugin contains one program for each of macOS and Linux, on Intel and ARM, and `bin/confighub`, which runs the right one for your machine. It has no server and no database, and needs no account.
