# What a repository deploys: `/confighub:inventory`

This page is for anyone who opens a GitOps repository they did not write, or have not looked at in a while, and needs to know what it deploys before they or an agent change it.

A GitOps repository is a Git repository that a tool such as Flux or Argo CD reads to decide what runs on your clusters. Its folders do not say which of them reach a cluster. A folder can look deployed and be deployed by nothing. Two environments can differ in values nobody wrote down. And an agent's change to production can sit in a file nobody opens.

`/confighub:inventory` reads the repository's files and tells you, in under a second:

- each app and chart, and what in the repository deploys it;
- the folders that nothing in the repository deploys;
- the values that differ between environments;
- the values agents changed, and why.

It needs no cluster and no account, and it changes nothing.

## A story: Amara's first day

Amara joins a platform team and is given the shop's GitOps repository. Her first task is to raise the api's memory in production. Before she asks an agent to do it, she opens Claude Code in the repository and types:

```
/confighub:inventory
```

She reads:

```
What shop-gitops deploys, read from its files

Kustomize overlays
  apps/api/overlays/prod, built on apps/api/base
      deployed by: Flux Kustomization flux-system/api (clusters/prod/api.yaml)
  apps/api/overlays/staging, built on apps/api/base
      deployed by: Flux Kustomization flux-system/api (clusters/staging/api.yaml)

Helm releases
  shop-prod/redis: chart redis 18.1.0 from https://charts.bitnami.com/bitnami (infra/redis/helmrelease.yaml)
      deployed by: nothing in this repository (perhaps kubectl, CI, or something in another repository)

Argo CD
  Application argocd/payments: apps/payments in https://github.com/example/shop-gitops at main, to https://kubernetes.default.svc namespace payments (argocd/payments.yaml)

Plain manifests
  apps/payments/: ConfigMap payments-config
      deployed by: Argo CD Application argocd/payments (argocd/payments.yaml)
  k8s-tools/: CronJob cleanup
      deployed by: nothing in this repository (perhaps kubectl, CI, or something in another repository)

Values that differ between environments
  The overlays built on apps/api/base:
                                                                                prod    staging
    Deployment/api/spec.replicas                                                8       2
    Deployment/api/spec.template.spec.containers[api].resources.limits.memory   512Mi   256Mi

Values agents changed, latest first (from the record)
  apps/api/overlays/prod/replicas.yaml Deployment/api/spec.replicas: 6 → 8, 27 October, asked "Black Friday: production api needs 8 replicas"
```

In one screen she learns four things she did not know:

1. Production's memory is set in `apps/api/overlays/prod`, and Flux deploys it from `clusters/prod/api.yaml`. That is the file her change belongs in.
2. Production already runs 8 replicas against staging's 2. An agent raised it from 6 for Black Friday, so she will not "tidy" it back.
3. Nothing in the repository deploys Redis or the cleanup CronJob. Someone deploys them some other way. She asks her team before she relies on either.
4. Payments is deployed by Argo CD, not Flux, so it follows different rules.

## How to run it

- In Claude Code, with the plugin installed: type `/confighub:inventory` in the repository.
- In a terminal: from the plugin's folder, run `bin/confighub mini inventory DIR`, where `DIR` is the repository. Without `DIR`, it reads the current folder.

To compare environments, it builds each Kustomize overlay with `kubectl kustomize` or `kustomize`. If neither is installed, it lists everything else and says that the comparison needs one of them.

## Reading what it says

**Kustomize overlays.** An overlay is a Kustomize folder that no other folder builds on: usually one environment of one app. Each is listed with the folders it builds on, and with what deploys it.

**Helm releases.** Each Flux `HelmRelease`, with its chart, the chart's version, and where the chart comes from. A release patched in an overlay is listed once, where it is defined.

**Helm charts kept in this repository.** Each folder with a `Chart.yaml`, and what deploys it. A chart's own dependencies, in its `charts/` folder, are not listed.

**Argo CD.** Each Application, with the folder or chart it deploys, the revision, and the cluster and namespace it deploys to. Each ApplicationSet, with what it makes. An ApplicationSet that makes one Application for each folder matching a pattern counts as deploying each of those folders. If it names a branch other than `HEAD`, the line says which, so you can tell one that points at an old or missing branch.

**Plain manifests.** Folders of Kubernetes objects that no Kustomize folder includes.

**Deployed by.** For each folder, what in the repository deploys it:

- a Flux Kustomization or an Argo CD Application or ApplicationSet that names the folder;
- a Flux Kustomization that names a folder above it, since Flux deploys every folder under a path that has no `kustomization.yaml` of its own;
- the overlays that build on it, for a base folder ("deployed through apps/production, apps/staging");
- Flux itself, for the `flux-system` folder that `flux bootstrap` writes.

When nothing in the repository deploys a folder, it says so. That is not always a mistake. An Argo CD Application kept in another repository, a CI job or a person with `kubectl` may deploy it. It is something to ask about before you rely on it.

**Values that differ between environments.** For each base with more than one overlay, the overlays are built and compared value by value. Only values that differ are shown, up to twelve for each base. Values that look like passwords, keys or tokens are shown as `(not shown)`.

**Values agents changed.** The latest changes from the plugin's record in this repository: the value, from what to what, when, and the request or reason behind it. `/confighub:why VALUE` shows every recorded change to one value.

## On Flux's and Argo CD's own examples

We ran the inventory on the two example repositories most teams copy:

- **[fluxcd/flux2-kustomize-helm-example](https://github.com/fluxcd/flux2-kustomize-helm-example).** It found each environment's apps deployed by that cluster's Flux Kustomization, through the `ArtifactGenerator` that copies the repository's folders for Flux. It found the podinfo release in the shared base, deployed through both environments. And it found the three values in which production and staging differ, such as the chart version range `>=1.0.0` against `>=1.0.0-alpha`.
- **[argoproj/argocd-example-apps](https://github.com/argoproj/argocd-example-apps).** In 0.4 seconds it listed twelve ApplicationSets and what each makes, and five charts kept in the repository. It found that nothing in the repository deploys `plugins/kustomized-helm`. It also showed that many folders are matched only by an ApplicationSet named `git-broken`, which points at a branch that does not exist.

## What it does not do

- **It reads one repository.** A folder deployed from another repository, by an Argo CD Application or a Flux source kept there, shows as deployed by nothing.
- **It reads files, not clusters.** It says what the repository asks for, not what is running. To list what was set on a cluster outside Git, and who set it, run `bin/confighub mini drift --dir DIR`, which reads the cluster and changes nothing.
- **Some ApplicationSets are not followed.** Generators other than Git directories, such as list, cluster and matrix generators, are listed but not followed, unless the template names one folder.
- **It does not check sources.** It does not check that a Helm repository, an OCI registry or a branch it names exists.

## When you want more than a list

The inventory tells you what the repository deploys today. It does not keep anything.

- **To keep each environment's values with the reason for each change**, add confighub mini, which is ConfigHub made small enough to run on your laptop. Type `/confighub:install-mini`, then follow [a first run](try-confighub-mini.md).
- **For the whole team to see the same inventory, and for agents to propose changes that a person approves**, use your organization's ConfigHub. [From the plugin to ConfigHub](from-plugin-to-confighub.md) walks through each step.

The last line of the inventory names the first of these steps. `CUB_MINI_TIPS=0` turns that line off.
