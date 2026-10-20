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

Deployment/api/spec.replicas, in k8s/api.yaml: 2 in the file now
  19 October 22:10  2 → 3                  session 8622fb51
      why: add a third replica for next week's sale, when traffic is expected to triple
  19 October 22:11  3 → 2                  session e82a40c3
      asked: The sale is over: take the api back to two replicas. Don't commit.
```

## What it records, and what it does not

- **Recorded:** each value the agent changes in Kubernetes files, Helm values, Kustomize, Compose, GitHub Actions workflows, settings files, Terraform variables and agent configuration, whether with its edit tool or with shell commands such as `sed`, including files Git ignores; each `kubectl`, `helm`, `argocd`, `flux`, `terraform` and `cub` command, also when run through `env`, `bash -c`, `xargs`, `make` or a script in the repository, with where it went and whether it changed something; and what the agent said at the end of each turn. `/minihub:why` also lists changes the agent made directly on a cluster to the same resource.
- **Never kept:** a command's output, a copy of a file, or a value that looks like a credential, including a password inside an address such as `postgres://user:password@host`, even when the request or the agent names it in words.
- **Where:** in `~/.confighub/agent-changes` on your machine, outside the repository. Nothing leaves the machine unless you turn on one of the settings below.

Each setting is turned on in Claude Code's settings, as `env`:

| Setting | What it adds |
|---|---|
| `CUB_MINI_ASK_REASONS=1` | A reason for each value, in the agent's own answer |
| `CUB_MINI_PULL_REQUEST=1` | The record and its reasons in each pull request the agent opens with `gh` |
| `CUB_MINI_RECORD_IN_REPO=1` | The record in each commit the agent makes, readable from any checkout; when the agent commits in the same command that changed a file, the record is staged for the next commit |

## What is in it

One program for each of macOS and Linux, on Intel and ARM, about 9 MB each, and a launcher that runs the one for this machine. No server, no database, no account. Tested in real Claude Code sessions on macOS and on Linux.

## Licence

The licence of the minihub program is not yet decided; until it is, no licence is granted for it. The program is built with Go and open-source modules, whose licences are in [`plugins/minihub/THIRD_PARTY_LICENSES.txt`](plugins/minihub/THIRD_PARTY_LICENSES.txt).
