# Configuration review

This page is for a team that reviews every configuration change as a pull request, more and more of them written by agents. A diff can show `replicas: 4 → 1` in a Kustomize overlay. It does not show what that becomes in each environment, or that the 4 was set last week for a sale. This GitHub Action adds a comment to each pull request that says what each value becomes where it is deployed, why it was set, and what merging would undo.

You need no hub (ConfigHub server), no account, and nothing installed in the cluster. Nothing leaves the runner but the comment.

## Add the review to a repository

1. In your repository, add a GitHub Actions workflow, under `.github/workflows/`, with this content:

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

   `@v0` follows every 0.x release. To stay on one release, use a version such as `@v0.41.0`.

2. For the "why" of each value, have agents that use the [ConfigHub plugin](../README.md) keep their records in the repository. Turn on `CUB_MINI_RECORD_IN_REPO=1` in the plugin's [settings](../docs/how-it-works.md#settings). Without these records, the review still lists each value changed.

3. Open a pull request. The review comments on it.

## What the comment shows

The comment lists every configuration value the pull request changes, from what to what. Where the ConfigHub plugin's record says why a value was set, the comment says why. The record is the plugin's list of what agents changed, with the reason for each change. A value that no record explains is shown as such.

The review reads Kubernetes files, Helm values, Kustomize, Compose, GitHub Actions workflows, settings files, Terraform variables and agent configuration.

## A comment, from a GitOps repository

Agents set a sale's capacity in a repository with Kustomize overlays and a Flux HelmRelease, and kept their records in it. This is part of the comment on their pull request:

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

The comment then renders each Kustomize overlay and Helm release that the change reaches, before and after. It says what each value becomes where it is deployed. In this example:

- The memory limit is new in the overlay's patch file, but prod already had 256Mi from the base.
- The HelmRelease's `replicaCount` is the StatefulSet's replicas in the bitnami Redis chart.

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

## What the review can render

Overlays are rendered with `kubectl kustomize`, and charts with `helm template`, both on GitHub's runners.

- **A Flux HelmRelease** is rendered when its chart is in the repository, or comes from a HelmRepository or OCIRepository defined in the repository.
- **An Argo CD Application** is rendered when its chart is a folder of the repository or comes from a Helm repository. Its value files, values and parameters are used. Applications are rendered with `helm template` as Argo CD applies those settings. This has been tested on charts made for the tests, not yet on a real Argo CD setup.

Otherwise, the comment says why it was not rendered: for example, a source that needs credentials.

## What merging it would undo

The comment opens with what merging the pull request would undo.

Here is an example. An agent scaled the api to 4 on the cluster for a sale, and its record was kept in the repository. Later, a pull request changes only the api's image, in a file that still says 2 replicas. The comment opens:

> **This change undoes 1 earlier change(s):**
>
> - `deploy.yaml` has `Deployment/api/spec.replicas` at 2; an agent set it to 4 on the cluster with `kubectl -n shop scale deploy api --replicas=4`, 25 October 07:01. Deploying this puts it back. Why it was set: the commit with its record, accf5fd, Note live scale-up of api to 4 replicas for flash sale

The pull request never touches the replicas. But deploying it, by Argo CD or by `kubectl apply`, puts the sale's 4 back to 2.

The review flags a second case the same way: a value put back to what it was before an earlier commit set it.

## What a value was, and why

When a pull request replaces a value, the comment also says:

- what the value was;
- the commit that set it, and who made it;
- why it was set. The reason comes from the record, or from the commit message's Reasons section, or else from the commit's subject line.

For example, weeks after the sale, someone without the plugin scales prod back:

| Value | Change | Why | What it was, and why |
|---|---|---|---|
| `Deployment/api/spec.replicas` | 6 → 2 | no record | 6 since 0f426fd, …, 2026-10-24: Black Friday, ~3x normal traffic |
