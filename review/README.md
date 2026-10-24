# Configuration review

On each pull request, a comment with every configuration value the pull request changes, from what to what, and why, where the record the ConfigHub plugin keeps of what agents change says. A value no record explains is shown as such. It reads Kubernetes files, Helm values, Kustomize, Compose, GitHub Actions workflows, settings files, Terraform variables and agent configuration. No hub, no account, nothing leaves the runner but the comment.

```yaml
name: Configuration review
on: pull_request
permissions:
  contents: read
  pull-requests: write
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: confighubai/confighub-mini-plugin/review@v0
```

`@v0` follows every 0.x release; a version such as `@v0.41.0` stays on one.

The "why" comes from the records agents with the plugin keep in the repository (`CUB_MINI_RECORD_IN_REPO=1`). Without them, the review still lists each value changed.

## A comment, from a GitOps repository

Agents set a sale's capacity in a repository with Kustomize overlays and a Flux HelmRelease, keeping records in it. The comment on their pull request, in part:

`apps/api/overlays/prod/replicas.yaml` (Kubernetes)

| Value | Change | Why |
|---|---|---|
| `Deployment/api/spec.replicas` | 3 → 6 | Black Friday, ~3x normal traffic |

`apps/api/overlays/prod/resources.yaml` (Kubernetes)

| Value | Change | Why |
|---|---|---|
| `Deployment/api/spec.template.spec.containers[api].resources.limits.memory` | (none) → 512Mi | Black Friday, ~3x normal traffic |

`infra/redis/helmrelease.yaml` (Kubernetes)

| Value | Change | Why |
|---|---|---|
| `HelmRelease/redis/spec.values.replica.replicaCount` | 1 → 2 | Black Friday, ~3x normal traffic |

It says what each file holds as written. What a value becomes on each cluster, after the overlays are rendered, it does not yet say.
