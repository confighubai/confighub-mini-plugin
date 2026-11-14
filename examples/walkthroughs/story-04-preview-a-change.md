<!-- walkthrough
id: story-04-preview-a-change
starts_with: mini
story: "4. A preview on a hub of its own: "Show me what this branch would do to production, and let me see it running""
needs: [confighub mini package, Docker, kind, kubectl, Argo CD (installed for you by cub cluster up)]
budget_seconds: 360
-->
# See what a change would do to production, and see it running, with nothing left behind

For a team whose platform is about to take a new version. Before anyone agrees, you want to see what production would take and what it would keep, and to see it running with production's own settings, without touching the team's hub or production. Here a hub of its own and a local cluster play the preview: the platform is Traefik, an ingress controller, and production runs two controllers for a reason. Afterwards both are removed.

## Human

### What you need

An unpacked confighub mini package, 0.11.1-mini.2 or later ([installing confighub mini](../../docs/install-mini.md#install-by-hand-without-the-plugin)), and Docker (or OrbStack), `kind` and `kubectl`, for a local Kubernetes cluster. The cluster is named `wsa-preview` and is deleted at the end. No account. A *hub* is ConfigHub running on your computer; `cub` is ConfigHub's command-line tool. *Argo CD* deploys to a cluster what it is pointed at; *argobot* is ConfigHub's small program on the cluster that tells the hub whether what it delivered is running.

### Steps

1. Set up a terminal for this walkthrough. `CUB_CONFIG` gives it a `cub` configuration of its own, so your own `cub` settings are not touched. On OrbStack, a small wrapper for `docker` that comes with the package goes first on your `PATH`, so the cluster can reach the hub; with Docker Desktop it is not needed:

   <!-- run: setup -->
   ```sh
   export MINI=/absolute/path/to/unpacked-confighub-mini
   export PATH="$MINI/bin:$PATH"
   export CUB_CONFIG="$HOME/.confighub-walkthrough"
   unset CUB_CONTEXT
   confighub-mini-app mini install-plugin "$CUB_CONFIG"
   if docker info --format '{{.OperatingSystem}}' | grep -q OrbStack; then export PATH="$MINI/examples/live-state/shim:$PATH"; fi
   ```

2. Copy the example into a folder of your own:

   <!-- run: copy files -->
   ```sh
   mkdir -p ~/walkthrough && cp -R "$MINI/examples/platform" ~/walkthrough/ && cd ~/walkthrough/platform
   ```

3. Start the preview's own hub:

   <!-- run: hub -->
   ```sh
   cub mini install --name preview --use
   ```

4. Make a local cluster with Argo CD and argobot, wired to this hub. It takes about a minute and a half:

   <!-- run: cluster -->
   ```sh
   cub cluster up wsa-preview --space preview
   ```

5. Run the platform as production has it: the platform's current version, Traefik 3.7.12, with production's two controllers kept, and the reason. The hub has one cluster, so it delivers there:

   <!-- run: production -->
   ```sh
   cub mini upload platform
   cub mini set platform replicas 2 --change-desc "Production runs two controllers"
   ```

   ```text
   …
   platform-preview: release 1 delivered to preview/target (Synced/Progressing, reported by argobot)
   …
   Saved in platform-preview, with the reason: Production runs two controllers. A later version of what platform-preview is made from will not overwrite this value.
   …
   ```

6. The branch's change arrives: the platform's next version, with a newer Traefik and three controllers. Before anything changes, you see what production would take and what it keeps. It asks whether to take it; answer `n` for now, or press Enter. Nothing running changes.

   <!-- run: see-preview -->
   ```sh
   cub mini upload platform-2 --component platform
   ```

   ```text
   platform-preview
   changes Image docker.io/traefik:v3.7.12 → docker.io/traefik:v3.7.14
   you keep Replicas yours: 2 (offered: 3)
   …
   Nothing running has changed. To take it later:
   cub mini promote platform-preview
   ```

7. See it running. Take the change into the preview, and Argo CD runs it within seconds; argobot reports it healthy:

   <!-- run: see-take -->
   ```sh
   cub mini promote platform-preview --change-desc "Preview of branch next-traefik: traefik 3.7.14"
   ```

   ```text
   …
   platform-preview: updated, release 3 published, running (Synced/Healthy, reported by argobot)
   …
   ```

8. Look at the cluster itself: two controllers, both ready, on the new version. Then write the result out as plain files for review, with the list of what changed and why in `result/CHANGES.md`:

   <!-- run: see-cluster -->
   ```sh
   kubectl --kubeconfig "$CUB_CONFIG/clusters/wsa-preview.kubeconfig" -n platform-ingress get deploy traefik \
     -o jsonpath='{.spec.replicas} {.status.readyReplicas} {.spec.template.spec.containers[0].image}{"\n"}'
   cub mini copy platform --to-dir result
   ```

   ```text
   2 2 docker.io/traefik:v3.7.14
   …
   ```

### Undo it

`cub cluster down` deletes the kind cluster and its local files; then the hub goes, with everything it held for the cluster, with the walkthrough's folder and `cub` configuration:

<!-- run: undo -->
```sh
cub cluster down wsa-preview
cub mini uninstall --name preview --delete-data
cd ~ && rm -rf ~/walkthrough "$CUB_CONFIG"
```

### What you have now

Nothing left behind but what you would hand a reviewer: you saw, before anything changed, that production would take Traefik 3.7.14 and keep its two controllers; you saw it running that way; and the result is files with their reasons. The full story adds the team's hub writing its platform to a file that a CI job loads into its own hub, so the job never holds a key to the team's hub; [CI and sandboxes](../../docs/ci-and-sandboxes.md) and [GitOps over OCI](../../docs/gitops-over-oci.md) cover those parts.

## Agent

For an AI agent doing this for a person.

- **The request:** "Production runs Traefik 3.7.12 with two controllers, on purpose. Show me what the platform's next version would do to it, and let me see it running, on a local cluster called wsa-preview. Clean up afterwards."
- **What to run:** the Human steps 2 to 8, from a copy of `$MINI/examples/platform`, with the OrbStack wrapper from step 1 if `docker info` says OrbStack. Show the person the preview from step 6 before taking it, and read the cluster back in step 8. Then the Undo commands.
- **Never:** use a cluster other than one you made; leave the `wsa-preview` cluster or the hub running; change the replicas to take the offered three.
- **Done when:** the cluster ran two ready Traefik 3.7.14 controllers, `result/CHANGES.md` lists the kept replicas with the reason, and, after the cleanup, `kind get clusters` has no `wsa-preview`.

## Testing

The scripted run follows the Human steps and compares the quoted output. Arm a, without confighub mini, is not applicable: production's copy and its kept value are in the hub. A correct agent result is two ready controllers at 3.7.14 on `wsa-preview`, before the cleanup. The checks below can be run by hand after step 8:

This proves: a service is running. The real Argo CD on a local kind cluster runs the release the hub published, with production's kept value, and argobot reports it healthy. The next step this aims to win: using a preview hub and cluster for each branch. Tested on the checksum-verified published confighub mini 0.11.1-mini.2 with the plugin 0.85.0, 14 November 2026: environment, the real Argo CD on a local kind cluster; approval, no approval step.

<!-- agent-task: see -->
> Production, platform-preview in the hub, runs Traefik 3.7.12 on the local kind cluster wsa-preview, with two controllers on purpose. The platform's next version is in ./platform-2. Show me what it would do to production, then take it and let me see it running there. Leave it running for me to look at, and write the result as files for review in ./result.

<!-- agent-check see: k=$(find "${CUB_CONFIG:-$HOME/.confighub}" -name wsa-preview.kubeconfig | head -1) && [ "$(kubectl --kubeconfig "$k" -n platform-ingress get deploy traefik -o jsonpath='{.status.readyReplicas} {.spec.template.spec.containers[0].image}')" = "2 docker.io/traefik:v3.7.14" ] && grep -rqs 'Production runs two controllers' --include=CHANGES.md . -->
<!-- agent-tools: kubectl -->
<!-- agent-cleanup: kind delete cluster --name wsa-preview >/dev/null 2>&1; true -->
<!-- arms: b -->
<!-- next-step when "did not change": preview every branch | See what the next branch would do to production, and see it running, before anyone agrees to it? -->

```sh
kubectl --kubeconfig "$CUB_CONFIG/clusters/wsa-preview.kubeconfig" -n platform-ingress get deploy traefik \
  -o jsonpath='{.status.readyReplicas} {.spec.template.spec.containers[0].image}{"\n"}'
grep 'two controllers' result/CHANGES.md
```

<!-- results:begin -->

Results, 14 November 2026, confighub mini 0.11.1-mini.2. Figures from this page's own test runs, shown here for whoever checks the page; they are not a promise.

- Scripted run: passed, 187 seconds for the steps, within the page's budget of 360.
- Agent runs: a pilot, 3 runs per arm on each of claude-sonnet-5-5, claude-opus-5-5. Arms: b is the plugin, confighub mini and this page as reading.

| Arm | Model | Checks passed | Median seconds | Median cost | Commands left for the person (median) |
|---|---|---|---|---|---|
| b | claude-opus-5-5 | 3/3 | 55.5 | $0.2 | 2 |
| b | claude-sonnet-5-5 | 3/3 | 63.0 | $0.112 | 0 |

No agent approved or refused a change to production.

Simulated persons, not people: 10 per run, each a claude-haiku-5-5 model playing one of ten fixed personas, reading only what a person would see. The next step they were offered: "See what the next branch would do to production, and see it running, before anyone agrees to it?"

The plugin offers it once, after the answer at whose end it showed the moment the offer names ("did not change"). Offered is the share of persons it was shown to; want it now and later are over them.

| Arm | Model | Persons | Offered | Noticed | Want the next step now | Later | In the way |
|---|---|---|---|---|---|---|---|
| b | claude-opus-5-5 | 30 | 0% | 100% | n/a | n/a | 13% |
| b | claude-sonnet-5-5 | 30 | 0% | 100% | n/a | n/a | 13% |

<!-- results:end -->
