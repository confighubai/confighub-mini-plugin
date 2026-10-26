# GitOps over OCI: Flux and Argo CD deploying from ConfigHub

**Who.** Dan's platform team runs Flux and Argo CD with self-heal on, and agents now propose changes to what they deploy.

**What goes wrong without it.** What the cluster runs is whatever reaches the branch it watches. A person has to read every agent's diff to know whether it should ship, and nothing in Git says why a value is what it is.

**What they get.** The cluster pulls only releases ConfigHub has approved, from ConfigHub's own registry. An agent's change waits until a named person approves it; then it is running within about 10 seconds. A change made by hand on the cluster is put back, and going back is an approved change like any other. Every release shows, in ConfigHub, what the cluster reported about it.

With a hub, ConfigHub is the source of truth, and Flux or Argo CD pull each approved release from ConfigHub's OCI registry, as they would from any container registry, instead of from a Git repository. This is what Flux calls Gitless GitOps. You can keep writing and reviewing in Git; what the cluster runs is what was approved in ConfigHub.

This page sets it up on confighub mini and a local kind cluster, then shows the four things a GitOps team asks about: a change that waits for a person's approval, self-heal, going back, and the cluster's status in ConfigHub. About 15 minutes. You need confighub mini ([install it](install-mini.md)), Docker, `kind` and `kubectl`, and for Flux, the `flux` CLI.

## 1. The cluster, with Flux and k8sbot

The `cub mini` commands on this page are plain `cub` with the rest filled in ([which](cub-mini-and-cub.md)); on your own cluster with hosted ConfigHub, below, the same is shown with `cub` alone.


```bash
cub cluster up shop --controller flux
source ~/.confighub/clusters/shop.env
```

`cub cluster up` makes a kind cluster, installs Flux, and connects it to the hub: an `OCIRepository` and `Kustomization` that pull the cluster's apps from ConfigHub, and k8sbot, ConfigHub's small bot in the cluster (`cub`'s messages still call it by its old name, argobot), which asks Flux to reconcile as soon as a release is published and reports each one's sync and health back. `--controller argo` installs Argo CD in its place. The `source` line sets `KUBECONFIG` and the `cub` context for the cluster.

**On OrbStack**, put [gitops/docker](../gitops/docker) first on your `PATH` for this step: `cub` otherwise points the cluster at an address that does not reach a hub listening on 127.0.0.1. With Docker Desktop it is not needed.

## 2. An app, deployed from the hub

```bash
mkdir api
cat > api/namespace.yaml <<'EOF2'
apiVersion: v1
kind: Namespace
metadata: {name: shop}
EOF2
cat > api/api.yaml <<'EOF2'
apiVersion: apps/v1
kind: Deployment
metadata: {name: api, namespace: shop}
spec:
  replicas: 2
  selector: {matchLabels: {app: api}}
  template:
    metadata: {labels: {app: api}}
    spec:
      containers:
      - {name: api, image: registry.k8s.io/pause:3.10}
EOF2
cub mini upload api --variant live --namespace shop --yes
```

The Namespace belongs with the app, since Flux creates nothing it is not given. Flux then runs 2 replicas, pulled from the hub. What it pulls from, as `cub cluster up` and `cub mini upload` set it up:

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: OCIRepository
metadata: {name: api-live, namespace: flux-system}
spec:
  url: oci://host.docker.internal:PORT/space/api-live   # the hub's OCI registry, one repository per Space
  ref: {tag: latest}
  secretRef: {name: confighub-oci}                      # the cluster's own key to the hub
  interval: 10m
---
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata: {name: api-live, namespace: flux-system}
spec:
  sourceRef: {kind: OCIRepository, name: api-live}
  path: .
  interval: 10m
  prune: false
  wait: true
```

## 3. A change that waits for a person

```bash
cub mini require-approval api --variant live --agent bot
CUB_CONFIG=~/.confighub-agent-bot CUB_CONTEXT=bot cub function set --space api-base --unit api --change-desc "Four for the sale" set-replicas 4
CUB_CONFIG=~/.confighub-agent-bot CUB_CONTEXT=bot cub changeorder create --space api-base sale-4 --component api --change-workflow workflows/api-live-approval --description "Four for the sale"
```

The agent's change waits: nothing is released, and the cluster still runs 2. When you approve it and promote it, ConfigHub releases it, k8sbot asks Flux to reconcile, and the cluster runs 4, about 10 seconds later:

```bash
cub variant approve api-base --change-order api-base/sale-4 --note "Checked: four is right for the sale"
cub mini promote api-live --change-order api-base/sale-4
```

## 4. Self-heal

```bash
kubectl -n shop scale deploy api --replicas=7
flux reconcile kustomization api-live -n flux-system --with-source
```

Flux applies the approved release again and the cluster is back at 4. Without the `flux reconcile`, it does the same at its next interval, 10 minutes here. Argo CD, with self-heal on as `cub cluster up` sets it, put the approved value back by itself within a second or two.

## 5. Going back

Going back is a change like any other, so it waits for an approval too:

```bash
cub function set --space api-base --unit api --change-desc "The sale is over" set-replicas 2
cub changeorder create --space api-base back-to-2 --component api --change-workflow workflows/api-live-approval --description "The sale is over"
cub variant approve api-base --change-order api-base/back-to-2 --note "Back to two"
cub mini promote api-live --change-order api-base/back-to-2
```

The cluster runs 2 again, about 10 seconds after the promotion. `cub variant demote` restores the earlier revision in the hub, but where approval is required, ConfigHub releases only what a change order with an approval covers, so the way back is the change order above.

## 6. What runs, in ConfigHub

```
$ cub release list --space api-live
NUM    TAG                              CHANGEORDER           PUBLISHED    SYNC         HEALTH
3      api-base/back-to-2-co-publish    api-base/back-to-2    true         Synced       Healthy
2      api-base/sale-4-co-publish       api-base/sale-4       true         OutOfSync    Unknown
1      release-1                                              true         OutOfSync    Unknown
```

Each release, the change order that made it, and what k8sbot last reported from the cluster. Only the release running now reads Synced; earlier ones read OutOfSync once a later one has replaced them.

## With Argo CD

`cub cluster up shop --controller argo` installs Argo CD in place of Flux, with each deployment an Application that reads the hub's OCI registry, auto-sync and self-heal on:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata: {name: api-live, namespace: argocd}
spec:
  project: default
  source:
    repoURL: oci://host.docker.internal:PORT/space/api-live
    targetRevision: latest
    path: .
  destination: {server: https://kubernetes.default.svc}
  syncPolicy:
    automated: {selfHeal: true, allowEmpty: true}
```

The other steps are the same, except that step 4 needs no `flux reconcile`. With Argo CD, the approved change ran about 4 seconds after the promotion, going back about 4 seconds after its promotion, and every release read Synced and Healthy. Argo CD's UI is at the address `cub cluster up` prints.

## Your own cluster, with hosted ConfigHub

The same works with a cluster you already have and hosted ConfigHub, or a ConfigHub server of your own. Signed in to it with `cub auth login`, and with `kubectl` pointed at the cluster:

```bash
cub cluster attach my-cluster
```

`cub cluster attach` wires the cluster your kubeconfig points at into ConfigHub, and creates no cluster. An Argo CD already in the `argocd` namespace is left as it is; otherwise it is installed. Argo CD v3.1 or later is needed, for `oci://` sources. For Flux, `cub cluster attach my-cluster --controller flux`: a Flux already in `flux-system` is left as it is. It adds a credential Argo CD pulls with, a token of a service account made for the cluster, a root Application, and k8sbot. Then the app, its live copy aimed at the cluster, and its first release:

```bash
cub component create api
cub space create api-base --component api --variant base
cub unit create --space api-base namespace api/namespace.yaml
cub unit create --space api-base api api/api.yaml
cub variant create live api-base --target my-cluster/target
cub release publish api-live
```

Argo CD pulls it from `oci://oci.hub.confighub.com:443/space/api-live`. The approval gate is set up with `cub` alone, as in [approvals](approvals.md#on-hosted-confighub-or-your-own-server-with-cub-alone); after the approval, the change is promoted and released by its change order:

```bash
cub variant approve api-base --change-order api-base/sale-4 --note "Checked: four is right for the sale"
cub variant promote api-live --change-order api-base/sale-4
cub release publish api-live --revision ChangeOrder:api-base/sale-4
```

Run against hosted ConfigHub, with a kind cluster on which Argo CD v3.1.9 was installed first: attach left that Argo CD in place; the first release ran 2 replicas; before the approval the promotion was refused ("requires approval: … 0 of 1") and the cluster still ran 2; after it, the cluster ran 4, 9 seconds after the promotion; a hand-made scale to 7 was put back by Argo CD within 3 seconds; and `cub release list` showed the running release Synced and Healthy.

Run the same way with Flux already installed on the cluster (`flux install`): attach left it in place; Flux pulled the release from `oci.hub.confighub.com`; a released change ran 4 seconds later; and a hand-made scale was put back.

To remove it: `cub cluster detach my-cluster` leaves the cluster as it is and unwires it, and the Spaces `my-cluster`, `my-cluster-argo-apps`, `argobot-my-cluster` and `argobot-base`, the Component `argobot` and the service account `argo-my-cluster` are deleted with `cub space delete --recursive`, `cub component delete` and `cub serviceaccount delete`.

## A change made in Git

Dan's team still reviews some changes as pull requests. The hub's copy can live in a repository of its own, written by the hub, and a change merged there comes back into the hub with the pull request's reason:

```bash
cub mini copy api --variant live --to-dir shop-config     # once: the hub's copy, at the root of a new repository
cd shop-config && git init -b main && git add -A && git commit -m "The hub's copy" && cd ..
# ...a pull request changes shop-config/api-live/api.yaml, is reviewed, and merged...
cub mini copy --from-git shop-config --variant live --since FIRST-COMMIT
```

The value is kept in the hub with the commit's message, the commit and its author as its reason, and the cluster runs it. Run on confighub mini with Flux: the merged change, 2 to 3 replicas, was in the hub as "Three for the launch, reviewed in a pull request (Git, commit bb2beb3, by Dan)", and the cluster ran 3 replicas 5 seconds later. The commit is recorded on the copy, so `--since` is needed only the first time. Each top-level folder of the repository is a Space, so the copy must be at its root, not in a subfolder. This was run with no approval required for live.

## When the hub is down

What runs keeps running: the controller holds the last release it pulled. Run on confighub mini with Flux, with the hub stopped: the app kept its 2 replicas; scaled by hand to 7, it was put back to 2 by Flux from its last release; and new releases waited. When the hub started again, Flux fetched from it straight away. This was not run with Argo CD.

## What k8sbot may do in your cluster

Read, and one write. On the cluster `cub cluster up --controller flux` made, its service account had a ClusterRole to get, list and watch pods and their logs, services, endpoints, configmaps, events, namespaces, nodes, volumes and the workload, networking and Flux resources, but not Secrets; and one to get, list, watch and patch Flux `OCIRepository` objects, which is how it asks Flux to reconcile. With Argo CD, k8sbot patches an Application's refresh annotation instead, as [its own README](https://github.com/confighub/k8sbot) describes.

## Afterwards

`cub cluster down shop --delete-config` deletes the cluster and its setup in the hub.

All of the above was run as written with confighub mini 0.9.0-mini.3 (ConfigHub v0.9.0), with Flux v2.9.2 and with Argo CD, on a Mac with OrbStack.
