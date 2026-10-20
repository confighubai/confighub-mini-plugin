# minihub, for Claude Code

Keeps a record of what the agent changes in configuration, and why. Nothing is shown to the agent or added to its work, and nothing in the repository changes unless you turn that on.

- **What it records:** each value the agent changes in Kubernetes files, Helm values, Kustomize, Compose, workflows, settings files, Terraform variables and agent configuration; each `kubectl`, `helm`, `argocd`, `flux`, `terraform` and `cub` command, with where it went and whether it changed something; and what the agent said at the end of each turn.
- **What it never keeps:** a command's output, a copy of a file, or a value that looks like a credential.
- **Where:** in `~/.confighub/agent-changes`, outside the repository.

Read it in a session with `/minihub:changes`, and ask about one value with `/minihub:why replicas`. In a terminal, `bin/minihub mini changes` from this plugin does the same.

## More, when you ask for it

Each is turned on in Claude Code's settings, as `env`:

| Setting | What it adds |
|---|---|
| `CUB_MINI_ASK_REASONS=1` | A reason for each value, in the agent's own answer |
| `CUB_MINI_PULL_REQUEST=1` | The record and its reasons in each pull request the agent opens with `gh` |
| `CUB_MINI_RECORD_IN_REPO=1` | The record in each commit the agent makes, readable from any checkout |
| `CUB_MINI_KEEP_IN_HUB=1` | Each change kept in a hub, so that it survives a vendor's next version. This needs the minihub package and a hub; the plugin alone carries none |

## What is in it

It is made for Claude Code. It also carries Codex's files (`plugin.json` and `hooks/codex-hooks.json`), which have not yet been tried in a real Codex session.

One program for each of macOS and Linux, on Intel and ARM, and `bin/minihub`, which runs the one for this machine. The program is the same one that runs `cub mini` in the minihub package. The plugin has no ConfigHub server, no PostgreSQL and no `cub`, and needs no account.
