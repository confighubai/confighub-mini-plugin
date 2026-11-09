# An app that Argo CD or Flux deploys from Git: a hub beside it, as its source, and back

This page is for a team whose app is deployed by Argo CD or Flux from a Git repository, and whose agents now propose changes to it. Attaching ConfigHub keeps your values and holds production for your approval in the hub, but Argo CD or Flux still deploys whatever reaches the branch it watches. This page shows the three ways to set that up, how to move one app so that the cluster deploys from the hub, and how to hand it back to Git.

## Words used on this page

- **Argo CD** and **Flux** are GitOps controllers. They run in a cluster and keep it matching configuration they pull from a source, usually a Git repository.
- **A hub** is one running ConfigHub, which keeps your configuration with every change, who made it and why. **confighub mini** is ConfigHub made small enough to run on your laptop. `cub` is its command-line tool.
- **The base**, **the staging copy** and **the live copy** are the app's configuration in the hub: the version that changes first, the copy that takes changes at once, and the copy that takes them only when you approve. Each is kept in a **Space**, such as `api-live`.
- **A change order** is a request for a change to reach the live copy. It waits until you approve or refuse it.
- **OCI** is the format and protocol container registries use. Argo CD and Flux can pull configuration from an OCI registry as they pull images. Each hub has one.
- **A release** is a numbered, published version of a copy that a cluster pulls. **argobot** is ConfigHub's small program in the cluster that asks the controller to deploy each release, and reports back whether it is running.

## Three ways to set it up

| Way | What deploys | Where your approval holds | To go back |
|---|---|---|---|
| 1. The hub beside Git | Git, as today | In the hub only. A merge to the branch still changes production | Stop the hub. Git is untouched |
| 2. The hub beside Git, with a check on each pull request | Git, as today | A pull request whose files differ from the approved copy fails, and branch protection requires the check | Remove the required check, stop the hub |
| 3. The hub as the source for one app | The hub, over OCI, through the same Argo CD or Flux | Only an approved change reaches the cluster. A change made on the cluster by hand is put back | Write the app back to Git, point the controller at Git again, stop the hub ([below](#hand-it-back-to-git)) |

Each step is one app at a time, and each can be undone. Start with the first.

## 1. Attach the app, beside Git

In Claude Code, in the repository, ask:

```
attach confighub to this existing app: keep my staging and production values exactly as they are,
and make sure an agent cannot change production without my say
```

The agent adopts the Kustomize repository as it is: the base as `kustomize` renders it, staging's own values from `overlays/staging`, and live's own from the prod overlay, or from the overlay an Argo CD Application in the repository deploys. The steps, outputs and costs are in [an app you already have](existing-app.md). In 15 of 16 measured sessions, the agent then said what this does not cover, as here:

> **Argo CD**
> Argo CD still syncs production from `overlays/prod` on `main`, so a merge to `main` still changes production without your approval. Because of that, ConfigHub only gates the agent's changes to production if the Argo CD route is closed. You could protect `main` or change how Argo CD syncs. I haven't changed either.

That is way 1. Agents propose in the hub, and you approve there. Close the Git route with way 2 or way 3.

## 2. Keep Git deploying, and check each pull request against the hub

The person who approves a change writes the approved copy out for Git, as plain files and a `CHANGES.md` that says why each value is set. A GitHub workflow compares each pull request's files with the hub's approved copy, value by value, and sets a status that branch protection requires. A pull request with a value nobody approved fails, and names it, for example "Deployment/api/spec.replicas: 5 here, 2 in the hub".

GitHub's runners cannot reach a confighub mini on a laptop. Use hosted ConfigHub or a server of your own for the workflow, or run the same check from your laptop. The steps: [when a cluster deploys from Git](../approvals.md#when-a-cluster-deploys-from-git-a-check-on-each-pull-request).

## 3. Make the hub the source for one app

Here the app moves from Git to the hub under the same controller, with no pod restarted. These steps are for trying it on your laptop, with a kind cluster that `cub` makes. For your own cluster, use hosted ConfigHub or a server of your own, with `cub cluster attach` ([your own cluster](../gitops-over-oci.md#your-own-cluster-with-hosted-confighub)).

**You need** confighub mini, Docker, `kind`, `kubectl` and, for Flux, the `flux` CLI. On OrbStack, read [the note in GitOps over OCI](../gitops-over-oci.md#step-1-make-the-cluster-with-flux-and-k8sbot) first.

The example is a shop whose `api` Flux syncs from the folder `./api` of its Git repository, with a Kustomization named `shop`.

1. Make the cluster, with Flux wired to the hub. About two minutes:

   ```bash
   cub cluster up rt-flux --controller flux
   ```

   `--controller argo` installs Argo CD instead.

2. Pause the Kustomization that deploys the app from Git. Nothing on the cluster changes:

   ```bash
   kubectl -n flux-system patch kustomization shop -p '{"spec":{"suspend":true}}'
   ```

3. Put the app's folder in the hub, as its live copy, with a reason:

   ```bash
   cub mini upload shop/api --variant live --namespace shop --change-desc "Taken over from the shop's Git, commit ebc8ad1, as Flux ran it"
   ```

   ```
   api-live: release 1 delivered to rt-flux/target (Synced/Healthy, reported by argobot)
   ```

   Flux now applies the api from the hub's registry. In our run it was the same Deployment and the same 2 pods: nothing was recreated or restarted.

4. Require your approval for live, and give the agent a key of its own:

   ```bash
   cub mini require-approval api --variant live --agent shop-agent
   ```

5. From then on, the agent proposes and you approve. On its key, the agent ran `cub mini upload api --component api --change-desc "Three replicas for the launch on Monday (SHOP-77)"`. The change waited, and the hub refused the agent's own approval. Then the person approved it:

   ```bash
   cub mini approve api-base/upload-20261108-173654-f0mk --note "Launch traffic is expected on Monday"
   ```

   ```
   api-live: updated, release 2 published, running (Synced/Healthy, reported by argobot)
   ```

   The cluster ran 3 replicas, and the 2 pods from before kept running.

What runs keeps running when the hub is down: the controller holds the last release it pulled. Self-heal, going back to an earlier value, and the release list are in [GitOps over OCI](../gitops-over-oci.md).

## Hand it back to Git

To leave, write the app as the hub holds it into your Git repository, with each reason, and point the controller at Git again.

1. Write the live copy out as plain files:

   ```bash
   cub mini copy api --variant live --to-dir for-git
   ```

   This writes a folder for each Space, such as `for-git/api-live/`, and a `CHANGES.md`.

2. Copy the files from `for-git/api-live/` into the folder your Kustomization reads, here `api/`, with `CHANGES.md`. Commit and push. In our run, the shop's Git then held `replicas: 3 # Three replicas for the launch on Monday (SHOP-77)`, and `CHANGES.md` had this row:

   | Space | Resource | Value | Now | Why | Who, when | Protected |
   |---|---|---|---|---|---|---|
   | api-live | Deployment shop/api | `spec.replicas` | `3` | Three replicas for the launch on Monday (SHOP-77) (from api-base, by change order api-base/upload-20261108-173654-f0mk, approved by admin@local.confighub.dev: Launch traffic is expected on Monday) | shop-agent, 2026-11-08 |  |

3. Wait until Flux's GitRepository has fetched that commit. `flux get sources git` shows the revision it has. Do not go on before it has: a Kustomization resumed on the commit from before the hub sets the old values back, and removes and remakes pods.

4. Remove the hub's Flux objects. They do not prune, so the app keeps running:

   ```bash
   kubectl -n flux-system delete kustomization,ocirepository confighub-root api-live
   ```

5. Resume your own Kustomization:

   ```bash
   kubectl -n flux-system patch kustomization shop -p '{"spec":{"suspend":false}}'
   ```

6. Stop the hub:

   ```bash
   cub mini stop
   ```

In our run, Flux's Kustomization `shop` was Ready at the hand-back commit, nothing on the cluster pulled from the hub, and the same Deployment and the same 3 pods ran on. The whole round trip, from making the cluster to the hand-back, took 189 seconds.

With Argo CD, the same round trip ran on an app synced by an Argo CD Application: onto the hub under the same Argo CD, with no pod restarted, and back to Git with the hub stopped and the same Deployment running.

One command each way, for the move to the hub and the hand-back, is coming in the next release.

## If something goes wrong

- **Pods restart once, on an app whose Deployment reads a ConfigMap.** In the current release, the hub's copy of such a pod template gains an annotation, `hash.confighub.com/...`, that your Git does not have. Deployed from the hub, or written back to Git, the pods roll once. In a test of 22 public charts, 9 had such workloads. Try it on a kind cluster first, as above, and check `kubectl get pods` before and after.
- **The hand-back set old values for a moment.** The Kustomization was resumed before its GitRepository had the new commit. Wait for it, as in step 3.
- **The cluster cannot reach a hub on your laptop.** confighub mini listens on your machine only. A cluster elsewhere needs hosted ConfigHub or a server of your own.
- **A merge to Git still changed production.** In way 1, Git still deploys. Use way 2 or way 3.

## What it costs

- **Way 1:** what [attaching the app](existing-app.md#what-it-costs) costs: about two minutes, and a 44 to 67 MB download.
- **Way 2:** a GitHub workflow, a service account that may only view, and branch protection. A hub GitHub's runners can reach, or the check run from your laptop.
- **Way 3, on your laptop:** a kind cluster with Flux or Argo CD, about two minutes to make; seconds to move the app; about 30 seconds to hand it back.

## How this was tested

On 8 November 2026, with the released confighub mini 0.10.7-mini.11, on a Mac with OrbStack and kind: the Flux round trip above, every check passed, in 189 seconds; and an app under Argo CD, moved onto the hub, changed there and on the cluster, and handed back to Git, in 346 seconds. No Claude Code session was needed for these runs: the agent's change was typed as an agent makes it, on its own key. The Argo CD warning quoted in step 1 is from 16 Claude Code sessions on 7 November 2026, with the plugin 0.78.0 and confighub mini 0.10.7-mini.9.
