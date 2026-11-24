# What a repository deploys: `/confighub:inventory`

This page is for anyone who opens a GitOps repository they did not write, or have not looked at in a while, and needs to know what it deploys before they or an agent change it.

The walkthrough [what your GitOps repository deploys](../examples/walkthroughs/tool-inventory.md) runs `/confighub:inventory` on a repository shaped like a platform team's, with charts deployed by Argo CD ApplicationSets, and shows how to check that it reads files only. [The Claude plugin](../examples/walkthroughs/tool-plugin.md) runs it with the Claude plugin's other commands.

A GitOps repository is a Git repository that a tool such as Flux or Argo CD reads to decide what runs on your clusters. Its folders do not say which of them reach a cluster. A folder can look deployed and be deployed by nothing. Two environments can differ in values nobody wrote down. And an agent's change to production can sit in a file nobody opens.

`/confighub:inventory` reads the repository's files and tells you:

- each app and chart, what in the repository deploys it, and for which clusters;
- the value files kept for each cluster, and what reads them;
- the folders that nothing in the repository deploys;
- the values that differ between environments;
- the values agents changed, and why.

It needs no cluster, no account and no hub, it changes nothing, and it sends nothing anywhere. [What it reads and what it writes](#what-it-reads-and-what-it-writes) has the details a security reviewer asks for.

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

- In Claude Code, with the Claude plugin installed: type `/confighub:inventory` in the repository.
- In a terminal: from the Claude plugin's folder, run `bin/confighub mini inventory DIR`, where `DIR` is the repository. Without `DIR`, it reads the current folder.
- Without installing the plugin: see the next section.

## Without installing the plugin

A security review may come before anyone installs a plugin with hooks. You can run the inventory first, on its own: one program, downloaded from the plugin's latest release and checked against the checksum published with it. Nothing is installed, and no hook is set up. Pick your computer's program, `confighub-darwin-arm64` for a Mac with Apple silicon, or `confighub-darwin-amd64`, `confighub-linux-arm64` or `confighub-linux-amd64`:

```sh
p=confighub-darwin-arm64
curl -fsSLO https://github.com/confighubai/confighub-mini-plugin/releases/latest/download/$p.gz
curl -fsSLO https://github.com/confighubai/confighub-mini-plugin/releases/latest/download/SHA256SUMS
shasum -a 256 -c SHA256SUMS --ignore-missing
gunzip $p.gz && chmod +x $p
CUB_MINI_COUNT=0 ./$p mini inventory ~/code/your-gitops-repository
```

The checksum line must print `OK`. On Linux, use `sha256sum -c SHA256SUMS --ignore-missing`. On a Mac, download with `curl` as shown: a program downloaded with a browser is blocked, because it is not code-signed. With `CUB_MINI_COUNT=0`, the program writes nothing anywhere. Without it, it notes the day you used it in `~/.confighub/agent-changes`. [For a security review](security.md) says what the full plugin reads, writes and sends.

To compare environments, it builds each Kustomize overlay with `kubectl kustomize` or `kustomize`. If neither is installed, it lists everything else and says that the comparison needs one of them.

## Reading what it says

**Kustomize overlays.** An overlay is a Kustomize folder that no other folder builds on: usually one environment of one app. Each is listed with the folders it builds on, and with what deploys it.

**Helm releases.** Each Flux `HelmRelease`, with its chart, the chart's version, and where the chart comes from. A release patched in an overlay is listed once, where it is defined.

**Helm charts kept in this repository.** Each folder with a `Chart.yaml`, and what deploys it. A chart's own dependencies, in its `charts/` folder, are not listed. A chart that other charts here take as a dependency from a folder, with `file://`, is said to be built into them; a library chart, that Helm never deploys it alone.

**Argo CD.** Each Application, with the folder or chart it deploys, the revision, and the cluster and namespace it deploys to. Each ApplicationSet, with its generators in plain words, such as "one Application for each cluster labeled cert-manager=enabled", and what its template deploys, from its `source` or each of its `sources`. A source counts as this repository's when its `repoURL` is the repository's `origin`, written as ssh or https. List and Git generators of this repository, and combinations of them, are filled into the template for each Application, so `apps/api/{{env}}` deploys only the folders the list names. If it names a branch other than `HEAD`, the line says which, so you can tell one that points at an old or missing branch.

**Helm value files Argo CD reads from this repository.** A value file a source reaches through another source's `ref:`, such as `$values/clusters/{{name}}/ingress/values.yaml`, is matched against the repository's files, and each file found is listed with the ApplicationSet or Application that reads it and what `{{name}}` is for it. With two or more, the values that differ between them are shown, as for environments.

**Plain manifests.** Folders of Kubernetes objects that no Kustomize folder includes.

**Deployed by.** For each folder, what in the repository deploys it:

- a Flux Kustomization or an Argo CD Application or ApplicationSet that names the folder;
- a Flux Kustomization that names a folder above it, since Flux deploys every folder under a path that has no `kustomization.yaml` of its own;
- the overlays that build on it, for a base folder ("deployed through apps/production, apps/staging");
- Flux itself, for the `flux-system` folder that `flux bootstrap` writes.

Where an ApplicationSet's path is filled in from what only Argo CD knows, such as a cluster's labels, a folder that matches it is "perhaps deployed by" that ApplicationSet. When the whole path comes from Argo CD, a folder nothing else deploys is "not known", never "nothing".

When nothing in the repository deploys a folder, it says so. That is not always a mistake. An Argo CD Application kept in another repository, a CI job or a person with `kubectl` may deploy it. It is something to ask about before you rely on it.

**Values that differ between environments.** For each base with more than one overlay, the overlays are built and compared value by value. Only values that differ are shown, up to twelve for each base. Values that look like passwords, keys or tokens are shown as `(not shown)`.

**Values agents changed.** The latest changes from the Claude plugin's record in this repository: the value, from what to what, when, and the request or reason behind it. `/confighub:why VALUE` shows every recorded change to one value.

## On Flux's and Argo CD's own examples

Here's what the inventory finds in the two example repositories most teams copy:

- **[fluxcd/flux2-kustomize-helm-example](https://github.com/fluxcd/flux2-kustomize-helm-example).** It finds each environment's apps deployed by that cluster's Flux Kustomization, through the `ArtifactGenerator` that copies the repository's folders for Flux. It finds the podinfo release in the shared base, deployed through both environments. And it finds the three values in which production and staging differ, such as the chart version range `>=1.0.0` against `>=1.0.0-alpha`.
- **[argoproj/argocd-example-apps](https://github.com/argoproj/argocd-example-apps).** It lists twelve ApplicationSets and what each makes, and five charts kept in the repository. It finds that nothing in the repository deploys `plugins/kustomized-helm`. It also shows that many folders are matched only by an ApplicationSet named `git-broken`, which points at a branch that does not exist.

## What it does not do

- **It reads one repository.** A folder deployed from another repository, by an Argo CD Application or a Flux source kept there, shows as deployed by nothing.
- **It reads files, not clusters.** It says what the repository asks for, not what is running. To list what was set on a cluster outside Git, and who set it, run `bin/confighub mini drift --dir DIR`, which reads the cluster and changes nothing.
- **It does not know which clusters have a label.** For a clusters generator, it says which label picks the clusters; Argo CD keeps the list. Merge generators, and pull request, Git hosting service and plugin generators, are described but not filled in. An ApplicationSet kept inside a chart's templates is not read.
- **It does not check sources.** It does not check that a Helm repository, an OCI registry or a branch it names exists.

## What it reads and what it writes

- **It reads** the repository's YAML and JSON files, up to 1 MB each, and the Claude plugin's own record of what agents changed there, kept on your computer.
- **It runs** `git` on this computer, to find the repository's top folder and its `origin`. When two or more Kustomize overlays build on one base, it runs `kubectl kustomize` or `kustomize build` to compare them. An overlay built on a remote base makes kustomize download that base, as it would if you ran it yourself.
- **It never** contacts a cluster or opens a Kubernetes configuration, signs in anywhere, starts or reaches a hub, or sends anything over the network.
- **It writes** nothing in the repository. On your computer it notes the day you used it, in `~/.confighub/agent-changes`, and never sends that anywhere; `CUB_MINI_COUNT=0` turns it off.
- **It hides** values that look like passwords, keys or tokens: they are shown as `(not shown)`.

## When you want more than a list

The inventory tells you what the repository deploys today. It does not keep anything.

- **For each pull request to show what it changes on each cluster, and wait for a person on your team to approve it**, add [the review](../review/README.md#a-person-approves-and-argo-cd-keeps-reading-git): one workflow file, and GitHub's own code owners. Argo CD or Flux keeps reading Git, and nothing is installed on anyone's computer.
- **To keep each environment's values with the reason for each change**, add the local hub, which is ConfigHub made small enough to run on your laptop. In Claude Code, type `/confighub:staging` in the app's folder: it starts the hub and gives the app a staging and a production copy of its settings ([install the local hub](install-mini.md)).
- **For the whole team to see the same inventory, and for agents to propose changes that a person approves**, use your organization's shared hub. [From the Claude plugin to ConfigHub](from-plugin-to-confighub.md) walks through each step.

The last line of the inventory names the next step: the review, in a repository Argo CD or Flux reads, and otherwise the local hub. `CUB_MINI_TIPS=0` turns that line off.
