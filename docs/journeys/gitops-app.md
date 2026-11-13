# An app that Argo CD or Flux deploys from Git: a hub beside it, as its source, and back

Let your agents propose changes to an app that Argo CD or Flux deploys, keep your values, and have production take only what you approve, with the same controller and the same pods. This page is for a team whose app is deployed from a Git repository. It helps you choose one of three ways to set it up, from the hub beside Git to the hub as the app's source, and says where each is shown step by step. Until you move an app, Argo CD or Flux still deploys whatever reaches the branch it watches.

The steps, with every command and what it prints, are in the walkthroughs [a Kustomize app that Argo CD deploys](../../examples/walkthroughs/starter-kustomize-argocd.md) and [a Kustomize app that Flux deploys](../../examples/walkthroughs/starter-kustomize-flux.md): each connects the app, moves its delivery to the hub with no pod restarted, changes it, undoes the change, moves it to a shared hub and deletes it. How deploying from the hub works, self-heal and your own cluster are in [GitOps over OCI](../gitops-over-oci.md).

The words on this page, such as *hub*, *base* and *change order*, are explained in [the glossary](../README.md#words).

## Three ways to set it up

| Way | What deploys | Where your approval holds | To go back |
|---|---|---|---|
| 1. The hub beside Git | Git, as today | In the hub only. A merge to the branch still changes production | Stop the hub. Git is untouched |
| 2. The hub beside Git, with a check on each pull request | Git, as today | A pull request whose files differ from the approved copy fails, and branch protection requires the check | Remove the required check, stop the hub |
| 3. The hub as the source for one app | The hub, over OCI, through the same Argo CD or Flux | Only an approved change reaches the cluster. A change made on the cluster by hand is put back | Write the app back to Git, point the controller at Git again, stop the hub ([below](#hand-it-back-to-git)) |

Each step is one app at a time, and each can be undone. Start with the first.

## 1. Attach the app, beside Git

In Claude Code, in the repository, ask the agent to *"attach ConfigHub to this existing app: keep my staging and production values exactly as they are, and make sure an agent cannot change production without my say"*. The agent adopts the Kustomize repository as it is: the base as `kustomize` renders it, staging's own values from `overlays/staging`, and live's own from the prod overlay, or from the overlay an Argo CD Application in the repository deploys. An overlay whose changes a copy cannot hold, such as one that adds a resource, is refused by name, and nothing is written ([what adopt refuses](existing-app.md#what-adopt-refuses-in-a-kustomize-repository)). What the agent runs and what you approve are in [an app you already have](existing-app.md).

The agent then says what this does not cover: Argo CD or Flux still syncs production from Git, so a merge to the branch still changes production without your approval. That is way 1. Agents propose in the hub, and you approve there. Close the Git route with way 2 or way 3.

## 2. Keep Git deploying, and check each pull request against the hub

The person who approves a change writes the approved copy out for Git, as plain files and a `CHANGES.md` that says why each value is set. A GitHub workflow compares each pull request's files with the hub's approved copy, value by value, and sets a status that branch protection requires. A pull request with a value nobody approved fails, and names it, for example "Deployment/api/spec.replicas: 5 here, 2 in the hub".

GitHub's runners cannot reach a confighub mini on a laptop. Use hosted ConfigHub or a server of your own for the workflow, or run the same check from your laptop. The steps: [when a cluster deploys from Git](../approvals.md#when-a-cluster-deploys-from-git-a-check-on-each-pull-request).

## 3. Make the hub the source for one app

Here the app moves from Git to the hub under the same controller, with no pod restarted. One command does each move, for an app adopted from a Kustomize repository or uploaded with `cub mini upload FOLDER --variant live --target none`:

- `cub mini deploy-from-hub APP --variant live --repo DIR` finds the one Argo CD Application or Flux Kustomization that deploys the copy, and points it at the hub. It refuses, and says what it found, when none or several deploy it, when the copy holds other objects than Git deploys, or when its pod templates differ from what runs. It checks that the same pods run before and after. `--dry-run` says what it would change. A person runs it: on an agent's key it refuses.
- From then on, the agent proposes on its key and you approve. Only an approved change is released to the cluster, and a change made on the cluster by hand is put back. What runs keeps running when the hub is down: the controller holds the last release it pulled.

To try it on your laptop, the starter walkthroughs make a kind cluster with `cub cluster up`. For your own cluster, use hosted ConfigHub or a server of your own, with `cub cluster attach` ([your own cluster](../gitops-over-oci.md#your-own-cluster-with-hosted-confighub)).

**By hand, under Flux.** For a Kustomization `shop` that syncs the folder `./api` from Git, the same move is three commands. Pause the Kustomization, which changes nothing on the cluster: `kubectl -n flux-system patch kustomization shop -p '{"spec":{"suspend":true}}'`. Put the folder in the hub as its live copy, with a reason: `cub mini upload shop/api --variant live --namespace shop --change-desc "WHY"`; Flux then applies the same Deployment from the hub's registry, and no pod is recreated. Then put live behind your approval: `cub mini require-approval api --variant live --agent shop-agent`.

## Hand it back to Git

`cub mini back-to-git APP --variant live --repo DIR` writes the copy into the folder the controller deployed from, with a `CHANGES.md` that says why each value is set, commits it, and once the controller's Git source has the commit, puts the controller back as it found it. `--push` pushes the commit; `--stop-hub` stops the hub once no copy deploys from it. The same Deployment and the same pods run on.

It waits for the Git source on purpose: a Flux Kustomization resumed on the commit from before the hub sets the old values back, and removes and remakes pods.

**By hand.** Write the live copy out with `cub mini copy api --variant live --to-dir for-git`, copy `for-git/api-live/` and its `CHANGES.md` into the folder your Kustomization reads, then commit and push. Wait until `flux get sources git` shows that commit. Remove the hub's Flux objects, which do not prune, so the app keeps running: `kubectl -n flux-system delete kustomization,ocirepository confighub-root api-live`. Resume your own Kustomization (`"suspend":false`), and stop the hub with `cub mini stop`.

## If something goes wrong

- **You want pods to restart when a ConfigMap changes.** `cub mini upload` keeps pod templates as your files have them, so taking a running app over restarts nothing; it takes out the hash annotation ConfigHub would add, and says so. `cub mini upload --roll-on-configmap` keeps that annotation instead, so a ConfigMap change restarts the pods that use it. Check `kubectl get pods` before and after, on a kind cluster first.
- **The hand-back set old values for a moment.** The Kustomization was resumed before its GitRepository had the new commit. Wait until `flux get sources git` shows the hand-back commit; `cub mini back-to-git` waits for it.
- **The cluster cannot reach a hub on your laptop.** confighub mini listens on your machine only. A cluster elsewhere needs hosted ConfigHub or a server of your own.
- **A merge to Git still changed production.** In way 1, Git still deploys. Use way 2 or way 3.

## What it takes

- **Way 1:** what [attaching the app](existing-app.md#what-it-takes) takes, including the confighub mini download ([its size](../install-mini.md#the-current-release)).
- **Way 2:** a GitHub workflow, a service account that may only view, and branch protection. A hub GitHub's runners can reach, or the check run from your laptop.
- **Way 3, on your laptop:** Docker, `kind`, `kubectl`, and a kind cluster with Flux or Argo CD.

## What you have now

- **After way 1:** your repository and files unchanged; a hub on this machine with the app's base, staging and live copies; agents on a key of their own that can propose and cannot approve. Argo CD or Flux still deploys from Git, so a merge to the branch it watches still changes production.
- **After way 2:** the same, and a required check that fails a pull request whose values differ from the hub's approved copy.
- **After way 3:** for one app, the controller pulls from the hub over OCI, and only an approved change reaches the cluster. The same pods kept running. Every other app still deploys from Git.

Each can be undone: way 3 by [handing the app back to Git](#hand-it-back-to-git), and the hub with `cub mini stop`, or `cub mini uninstall --delete-data` to remove it and its data ([going back](going-back.md)).

## What to try next

After way 1:

1. Ask the agent to raise production's replicas. Its turn ends with one line: a change waits for you. Run `cub mini waiting`, then the `cub mini approve` command it prints.
2. In Claude Code, type `/confighub:inventory`: what the repository deploys, and what deploys each part.
3. Run `cub mini drift --dir DIR` on the checkout the controller deploys: each field on the cluster that Git does not set, with who set it. It only reads.

Then try way 3 on a kind cluster, with a starter walkthrough, before you move an app your team relies on.
