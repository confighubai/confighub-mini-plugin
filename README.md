# minihub plugin for Claude Code

A Claude Code plugin that keeps a record of what an agent changes in configuration, and why. The agent is not told about it and works as it always does. Nothing is shown to it or added to its work.

```
claude plugin marketplace add confighubai/minihub-plugin
claude plugin install minihub@minihub
```

Afterwards, in a session:

```
/minihub:changes
```

```
What an agent changed, session ad20e805, 19 October 14:37 to 14:37

Asked: The api is getting more traffic from the sale next week. ...

  k8s/api.yaml (Kubernetes)
    Deployment/api/spec.replicas                 2 → 3
    Deployment/api/spec.template.spec.containers[api].resources.limits.memory 256Mi → 512Mi

  .env (Settings file)
    CACHE                                        off → on

  Looked at:
    kubectl get deploy,pods,cm -A (kind-shop)
```

## What it records, and what it does not

- **Recorded:** each value the agent changes in Kubernetes files, Helm values, Kustomize, Compose, GitHub Actions workflows, settings files, Terraform variables and agent configuration; each `kubectl`, `helm`, `argocd`, `flux`, `terraform` and `cub` command, with where it went and whether it changed something; and what the agent said at the end of each turn.
- **Never kept:** a command's output, a copy of a file, or a value that looks like a credential.
- **Where:** in `~/.confighub/agent-changes` on your machine, outside the repository. Nothing leaves the machine unless you turn on one of the settings below.

Each setting is turned on in Claude Code's settings, as `env`:

| Setting | What it adds |
|---|---|
| `CUB_MINI_ASK_REASONS=1` | A reason for each value, in the agent's own answer |
| `CUB_MINI_PULL_REQUEST=1` | The record and its reasons in each pull request the agent opens with `gh` |
| `CUB_MINI_RECORD_IN_REPO=1` | The record in each commit the agent makes, readable from any checkout |

## What is in it

One program for each of macOS and Linux, on Intel and ARM, about 9 MB each, and a launcher that runs the one for this machine. No server, no database, no account.

## Licence

The licence of the minihub program is not yet decided; until it is, no licence is granted for it. The program is built with Go and open-source modules, whose licences are in [`plugins/minihub/THIRD_PARTY_LICENSES.txt`](plugins/minihub/THIRD_PARTY_LICENSES.txt).
