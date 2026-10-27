# GitOps over OCI: Flux and Argo CD deploying from ConfigHub

This page is for a platform team that runs Flux or Argo CD, and whose agents now propose changes to what those tools deploy. It shows how to make the cluster deploy only changes a named person has approved, with the reason for each value kept. It takes about 15 minutes on your laptop.

## What "deploying from the hub over OCI" means

Today, your cluster's Flux or Argo CD deploys whatever reaches the Git branch it watches. A person has to read every agent's diff to know whether it should ship. Nothing in Git says why a value is what it is.

With this setup, your cluster's Flux or Argo CD pulls the approved configuration from ConfigHub instead of from Git:

1. An agent proposes a change in ConfigHub. The change waits.
2. A person you name approves it.
3. ConfigHub publishes the approved configuration as a *release*.
4. Flux or Argo CD pulls the release from ConfigHub and applies it. The change is running about 10 seconds later.

A change someone makes by hand on the cluster is put back. Going back to an earlier value is an approved change like any other. For every release, ConfigHub shows what the cluster reported about it.

You can keep writing and reviewing changes in Git. What the cluster runs is what was approved in ConfigHub. Flux calls this Gitless GitOps.

## Words used here

- **Flux** and **Argo CD** are GitOps controllers. They run in a cluster and keep it matching configuration they pull from a source, usually a Git repository. *Self-heal* means the controller puts back a change made on the cluster by hand.
- **OCI** is the standard format and protocol that container registries use. Flux and Argo CD can pull configuration from an OCI registry as they pull images. Each hub has an OCI registry of its own.
- **[ConfigHub](https://docs.confighub.com)** keeps your configuration with the reason each value is set. A *hub* is one running ConfigHub server. *confighub mini* runs a hub on your machine. `cub` is ConfigHub's command-line tool.
- A **Space** holds configuration, as **Units**: one Unit per file or resource. A **Component** is one piece of software, here `api`. Its **base**, here `api-base`, is the version you change. A **variant**, here `live`, is a copy made from the base for one place it runs. Its Space is `api-live`.
- A **change order** asks for a change to reach a variant. A **ChangeWorkflow** says what it needs first, here a person's approval.
- A **release** is a numbered, published version of a variant that a cluster pulls. A **target** is the cluster a variant is aimed at.
- **k8sbot** is ConfigHub's small bot in the cluster. It asks Flux or Argo CD to deploy as soon as a release is published, and reports each release's sync and health back to ConfigHub. `cub`'s messages, and some names `cub` creates, still use its old name, argobot.

## What you need

- confighub mini ([install it](install-mini.md)).
- Docker, `kind` (Kubernetes in Docker) and `kubectl`.
- For Flux, the `flux` CLI.

The steps below set this up on confighub mini and a local kind cluster. Then they show the four things a GitOps team asks about: a change that waits for a person's approval, self-heal, going back, and the cluster's status in ConfigHub.

The `cub mini` commands on this page are plain `cub` with the rest of the request filled in ([which commands](cub-mini-and-cub.md)). For your own cluster with hosted ConfigHub, [further down](#your-own-cluster-with-hosted-confighub), the same is shown with `cub` alone.

The example follows Dan's platform team, which runs Flux and Argo CD with self-heal on.

## Step 1: Make the cluster, with Flux and k8sbot

1. Make the cluster:

   ```bash
   cub cluster up shop --controller flux
   ```

   This makes a kind cluster named `shop`, installs Flux in it, and connects it to the hub. It adds:
   - an `OCIRepository` and a `Kustomization`, which pull the cluster's apps from ConfigHub;
   - k8sbot.

   To install Argo CD in place of Flux, use `--controller argo` ([With Argo CD](#with-argo-cd)).

2. Point your shell at the cluster:

   ```bash
   source ~/.confighub/clusters/shop.env
   ```

   This sets `KUBECONFIG`, and the `cub` context for the cluster.

**On OrbStack**, put [gitops/docker](../gitops/docker) first on your `PATH` for this step. Otherwise `cub` points the cluster at an address that does not reach a hub listening on 127.0.0.1. With Docker Desktop you do not need this.

## Step 2: Deploy an app from the hub

1. Make a folder for the app, with its Namespace:

   ```bash
   mkdir api
   cat > api/namespace.yaml <<'EOF2'
   apiVersion: v1
   kind: Namespace
   metadata: {name: shop}
   EOF2
   ```

   The Namespace belongs with the app, since Flux creates nothing it is not given.

2. Add the Deployment:

   ```bash
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
   ```

3. Put the app in the hub, as the Component `api` with a `live` copy:

   ```bash
   cub mini upload api --variant live --namespace shop --yes
   ```

Flux now runs 2 replicas of `api`, pulled from the hub.

This is what Flux pulls from, as `cub cluster up` and `cub mini upload` set it up:

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

## Step 3: A change that waits for a person

1. Require approval for the live copy, and make an agent named `bot`:

   ```bash
   cub mini require-approval api --variant live --agent bot
   ```

   `--agent bot` gives the agent a key of its own, in a `cub` configuration of its own, `~/.confighub-agent-bot`. The next two commands run `cub` as the agent, by pointing `CUB_CONFIG` and `CUB_CONTEXT` at that configuration.

2. As the agent, change the base to 4 replicas:

   ```bash
   CUB_CONFIG=~/.confighub-agent-bot CUB_CONTEXT=bot cub function set --space api-base --unit api --change-desc "Four for the sale" set-replicas 4
   ```

3. As the agent, ask for the change to reach the live copy, with a change order:

   ```bash
   CUB_CONFIG=~/.confighub-agent-bot CUB_CONTEXT=bot cub changeorder create --space api-base sale-4 --component api --change-workflow workflows/api-live-approval --description "Four for the sale"
   ```

   The agent's change waits. Nothing is released, and the cluster still runs 2 replicas.

4. As yourself, approve the change:

   ```bash
   cub variant approve api-base --change-order api-base/sale-4 --note "Checked: four is right for the sale"
   ```

5. Promote it to the live copy:

   ```bash
   cub mini promote api-live --change-order api-base/sale-4
   ```

   ConfigHub releases the change, and k8sbot asks Flux to deploy it. About 10 seconds later, the cluster runs 4 replicas.

## Step 4: Self-heal

1. Change the cluster by hand:

   ```bash
   kubectl -n shop scale deploy api --replicas=7
   ```

2. Ask Flux to apply the release again now:

   ```bash
   flux reconcile kustomization api-live -n flux-system --with-source
   ```

   Flux applies the approved release again, and the cluster is back at 4 replicas.

Without the `flux reconcile`, Flux does the same at its next interval, which is 10 minutes here. Argo CD, with self-heal on as `cub cluster up` sets it, put the approved value back by itself within a second or two.

## Step 5: Go back

Going back is a change like any other, so it waits for an approval too.

1. Change the base back to 2 replicas:

   ```bash
   cub function set --space api-base --unit api --change-desc "The sale is over" set-replicas 2
   ```

2. Ask for it with a change order:

   ```bash
   cub changeorder create --space api-base back-to-2 --component api --change-workflow workflows/api-live-approval --description "The sale is over"
   ```

3. Approve it:

   ```bash
   cub variant approve api-base --change-order api-base/back-to-2 --note "Back to two"
   ```

4. Promote it:

   ```bash
   cub mini promote api-live --change-order api-base/back-to-2
   ```

   About 10 seconds later, the cluster runs 2 replicas again.

`cub variant demote` restores the earlier revision in the hub, but it is not the way back here. Where approval is required, ConfigHub releases only what an approved change order covers. So the way back is a change order, as above.

## Step 6: See what runs, in ConfigHub

```
$ cub release list --space api-live
NUM    TAG                              CHANGEORDER           PUBLISHED    SYNC         HEALTH
3      api-base/back-to-2-co-publish    api-base/back-to-2    true         Synced       Healthy
2      api-base/sale-4-co-publish       api-base/sale-4       true         OutOfSync    Unknown
1      release-1                                              true         OutOfSync    Unknown
```

Each line is one release. It shows the change order that made the release, and what k8sbot last reported from the cluster. Only the release running now reads Synced. Earlier releases read OutOfSync once a later one has replaced them.

## With Argo CD

`cub cluster up shop --controller argo` installs Argo CD in place of Flux. Each deployment is an Argo CD Application that reads the hub's OCI registry, with auto-sync and self-heal on:

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

The other steps are the same, except that step 4 needs no `flux reconcile`. Argo CD's UI is at the address `cub cluster up` prints.

With Argo CD, the approved change ran about 4 seconds after the promotion. Going back ran about 4 seconds after its promotion. Every release read Synced and Healthy.

## Your own cluster, with hosted ConfigHub

The same works with a cluster you already have and hosted ConfigHub, or a ConfigHub server of your own.

1. Sign in to ConfigHub with `cub auth login`, and point `kubectl` at your cluster.

2. Connect the cluster to ConfigHub:

   ```bash
   cub cluster attach my-cluster
   ```

   `cub cluster attach` connects the cluster your kubeconfig points at to ConfigHub. It creates no cluster. It adds:
   - a credential Argo CD pulls with: a token of a service account made for the cluster;
   - a root Application;
   - k8sbot.

   An Argo CD already in the `argocd` namespace is left as it is. Otherwise Argo CD is installed. You need Argo CD v3.1 or later, for `oci://` sources.

   For Flux, run `cub cluster attach my-cluster --controller flux` instead. A Flux already in `flux-system` is left as it is.

3. Put the app in ConfigHub, make its live copy aimed at the cluster, and publish its first release:

   ```bash
   cub component create api
   cub space create api-base --component api --variant base
   cub unit create --space api-base namespace api/namespace.yaml
   cub unit create --space api-base api api/api.yaml
   cub variant create live api-base --target my-cluster/target
   cub release publish api-live
   ```

   Argo CD pulls the release from `oci://oci.hub.confighub.com:443/space/api-live`.

4. Set up the approval gate with `cub` alone, as in [approvals](approvals.md#on-hosted-confighub-or-your-own-server-with-cub-alone).

5. After the approval, promote the change and release it, by its change order:

   ```bash
   cub variant approve api-base --change-order api-base/sale-4 --note "Checked: four is right for the sale"
   cub variant promote api-live --change-order api-base/sale-4
   cub release publish api-live --revision ChangeOrder:api-base/sale-4
   ```

**How this was tested with Argo CD.** We ran it against hosted ConfigHub, with a kind cluster on which Argo CD v3.1.9 was installed first:
- `cub cluster attach` left that Argo CD in place.
- The first release ran 2 replicas.
- Before the approval, the promotion was refused ("requires approval: … 0 of 1"), and the cluster still ran 2.
- After the approval, the cluster ran 4, 9 seconds after the promotion.
- A scale to 7 made by hand was put back by Argo CD within 3 seconds.
- `cub release list` showed the running release Synced and Healthy.

**How this was tested with Flux.** We ran it the same way, with Flux already installed on the cluster (`flux install`):
- `cub cluster attach` left Flux in place.
- Flux pulled the release from `oci.hub.confighub.com`.
- A released change ran 4 seconds later.
- A scale made by hand was put back.

**To remove it:**
- `cub cluster detach my-cluster` disconnects the cluster from ConfigHub, and leaves the cluster as it is.
- Delete the Spaces `my-cluster`, `my-cluster-argo-apps`, `argobot-my-cluster` and `argobot-base` with `cub space delete --recursive`.
- Delete the Component `argobot` with `cub component delete`.
- Delete the service account `argo-my-cluster` with `cub serviceaccount delete`.

## A change made in Git

Dan's team still reviews some changes as pull requests. The hub's copy can live in a Git repository of its own, written by the hub. A change merged there comes back into the hub, with the pull request's reason.

1. Write the hub's copy to the root of a new folder. You do this once:

   ```bash
   cub mini copy api --variant live --to-dir shop-config     # once: the hub's copy, at the root of a new repository
   ```

2. Make the folder a Git repository:

   ```bash
   cd shop-config && git init -b main && git add -A && git commit -m "The hub's copy" && cd ..
   ```

3. A pull request changes `shop-config/api-live/api.yaml`, is reviewed, and is merged.

4. Bring the merged change into the hub:

   ```bash
   cub mini copy --from-git shop-config --variant live --since FIRST-COMMIT
   ```

   The value is kept in the hub. Its reason is the commit's message, the commit, and its author. The cluster then runs it.

Replace `FIRST-COMMIT` with the hash of the commit made in step 2, "The hub's copy" (right after step 2, `git -C shop-config log --format=%h -1` prints it). `--since` takes in every change committed after it. The commit taken in is recorded on the copy, so you need `--since` only the first time.

Each top-level folder of the repository is a Space. So the copy must be at the root of the repository, not in a subfolder.

**How this was tested.** We ran it on confighub mini with Flux, with no approval required for live. The merged change, 2 to 3 replicas, was in the hub as "Three for the launch, reviewed in a pull request (Git, commit bb2beb3, by Dan)". The cluster ran 3 replicas 5 seconds later.

## When the hub is down

What runs keeps running. The controller holds the last release it pulled.

We ran this on confighub mini with Flux, with the hub stopped:
- The app kept its 2 replicas.
- Scaled to 7 by hand, it was put back to 2 by Flux, from its last release.
- New releases waited.
- When the hub started again, Flux fetched from it straight away.

This was not run with Argo CD.

## What k8sbot may do in your cluster

k8sbot reads, and makes one kind of write.

On the cluster `cub cluster up --controller flux` made, k8sbot's service account had two ClusterRoles:
- One to get, list and watch pods and their logs, services, endpoints, configmaps, events, namespaces, nodes, volumes, and the workload, networking and Flux resources. It does not include Secrets.
- One to get, list, watch and patch Flux `OCIRepository` objects. Patching one is how k8sbot asks Flux to deploy.

With Argo CD, k8sbot patches an Application's refresh annotation instead, as [its own README](https://github.com/confighub/k8sbot) describes.

## Remove the cluster

```bash
cub cluster down shop --delete-config
```

This deletes the cluster, and its setup in the hub.

## How this page was tested

All of the above was run as written with confighub mini 0.9.0-mini.3 (ConfigHub v0.9.0), with Flux v2.9.2 and with Argo CD, on a Mac with OrbStack.
