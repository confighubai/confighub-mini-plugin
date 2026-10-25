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

It then renders each Kustomize overlay and Helm release the change reaches, before and after, and says what each value becomes where it is deployed: the memory limit is new in the overlay's patch file, but prod had 256Mi from the base, and the HelmRelease's `replicaCount` is the StatefulSet's replicas in the bitnami Redis chart:

`apps/api/overlays/prod`

| Value | Change | Why |
|---|---|---|
| `Deployment/api/spec.replicas` | 3 → 6 | Black Friday, ~3x normal traffic |
| `Deployment/api/spec.template.spec.containers[api].resources.limits.memory` | 256Mi → 512Mi | Black Friday, ~3x normal traffic |

`HelmRelease shop-prod/redis`

| Value | Change | Why |
|---|---|---|
| `StatefulSet/redis-replicas/spec.replicas` | 1 → 2 | Black Friday, ~3x normal traffic |

The chart makes these anew each time it renders, so they are not compared: `Secret/redis/data.redis-password`.

Overlays are rendered with `kubectl kustomize` and charts with `helm template`, both on GitHub's runners. A Flux HelmRelease is rendered when its chart is in the repository or comes from a HelmRepository or OCIRepository defined in it; an Argo CD Application, when its chart is a folder of the repository or comes from a Helm repository, with its value files, values and parameters. Applications are rendered with `helm template` as Argo CD applies those settings, tested on charts made for the tests, not yet on a real Argo CD estate. Otherwise the comment says why it was not rendered, for example a source that needs credentials.

## What merging it would undo

The comment opens with what merging the pull request would undo. A pull request that changes only the api's image, in a file that still says 2 replicas, after an agent scaled the api to 4 on the cluster for a sale with its record kept in the repository:

> **This change undoes 1 earlier change(s):**
>
> - `deploy.yaml` has `Deployment/api/spec.replicas` at 2; an agent set it to 4 on the cluster with `kubectl -n shop scale deploy api --replicas=4`, 25 October 07:01. Deploying this puts it back. Why it was set: the commit with its record, accf5fd, Note live scale-up of api to 4 replicas for flash sale

The pull request never touches the replicas; deploying it, by Argo CD or `kubectl apply`, puts the sale's 4 back to 2. A value put back to what it was before an earlier commit set it is flagged the same way.

## What a value was, and why

When a pull request replaces a value, the comment also says what it was, the commit that set it, by whom, and why: from the record, from the commit message's Reasons section, or else the commit's subject. Weeks after the sale, someone without the plugin scales prod back:

| Value | Change | Why | What it was, and why |
|---|---|---|---|
| `Deployment/api/spec.replicas` | 6 → 2 | no record | 6 since 0f426fd, …, 2026-10-24: Black Friday, ~3x normal traffic |
