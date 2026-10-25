# GitOps over OCI: Flux and Argo CD deploying from ConfigHub

With a hub, ConfigHub is the source of truth, and Flux or Argo CD pull each approved release from ConfigHub's OCI registry, as they would from any container registry, instead of from a Git repository. This is what Flux calls Gitless GitOps. You can keep writing and reviewing in Git; what the cluster runs is what was approved in ConfigHub.

This page sets it up on confighub mini and a local kind cluster, then shows the four things a GitOps team asks about: a change that waits for a person's approval, self-heal, going back, and the cluster's status in ConfigHub. About 15 minutes. You need confighub mini ([install it](install-mini.md)), Docker, `kind` and `kubectl`, and for Flux, the `flux` CLI.

## 1. The cluster, with Flux and k8sbot

```bash
cub cluster up shop --controller flux
source ~/.confighub/clusters/shop.env
```

`cub cluster up` makes a kind cluster, installs Flux, and connects it to the hub: an `OCIRepository` and `Kustomization` that pull the cluster's apps from ConfigHub, and k8sbot, ConfigHub's small bot in the cluster, which asks Flux to reconcile as soon as a release is published and reports each one's sync and health back. `--controller argo` installs Argo CD in its place. The `source` line sets `KUBECONFIG` and the `cub` context for the cluster.

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

Steps 2 to 6 are the same, without the `flux reconcile`. With Argo CD, the approved change ran about 4 seconds after the promotion, going back about 4 seconds after its promotion, and every release read Synced and Healthy. Argo CD's UI is at the address `cub cluster up` prints.

## 6. What runs, in ConfigHub

```
$ cub release list --space api-live
NUM    TAG                              CHANGEORDER           PUBLISHED    SYNC         HEALTH
3      api-base/back-to-2-co-publish    api-base/back-to-2    true         Synced       Healthy
2      api-base/sale-4-co-publish       api-base/sale-4       true         OutOfSync    Unknown
1      release-1                                              true         OutOfSync    Unknown
```

Each release, the change order that made it, and what k8sbot last reported from the cluster.

## Afterwards

`cub cluster down shop --delete-config` deletes the cluster and its setup in the hub.

All of the above was run as written with confighub mini 0.9.0-mini.3 (ConfigHub v0.9.0), with Flux v2.9.2 and with Argo CD, on a Mac with OrbStack.
