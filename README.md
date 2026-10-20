# minihub plugin for Claude Code

A Claude Code plugin that keeps a record of what an agent changes in configuration, and why. The agent is not told about it and works as it always does. Nothing is shown to it or added to its work.

```
claude plugin marketplace add confighubai/minihub-plugin
claude plugin install minihub@minihub
```

Afterwards, in a session:

```
/minihub:changes              what the agent changed, and why
/minihub:why replicas         every recorded change to one value, and why
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

```
/minihub:why replicas

Deployment/api/spec.replicas, in k8s/api.yaml: now 2
  19 October 17:25  2 → 3                  session d31421b5
      why: third replica for next week's sale, when traffic is expected to triple
  19 October 17:25  3 → 2                  session 08e3720e
      asked: The sale is over: take the api back to two replicas.
```

## What it records, and what it does not

- **Recorded:** each value the agent changes in Kubernetes files, Helm values, Kustomize, Compose, GitHub Actions workflows, settings files, Terraform variables and agent configuration; each `kubectl`, `helm`, `argocd`, `flux`, `terraform` and `cub` command, with where it went and whether it changed something; and what the agent said at the end of each turn.
- **Never kept:** a command's output, a copy of a file, or a value that looks like a credential, even when the request or the agent names it in words.
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
