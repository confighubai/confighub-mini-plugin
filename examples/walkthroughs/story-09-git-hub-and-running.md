<!-- walkthrough
id: story-09-git-hub-and-running
starts_with: mini
story: "9. Dan at ACME: "What is where, and what is running?""
needs: [confighub mini package, Docker, kind, kubectl, git, python3, Argo CD (installed for you), the cub-scout plugin for cub, internet access]
budget_seconds: 600
-->
# What Git says, what the hub holds, and what is running, side by side

For someone who looks after an app that Argo CD deploys from Git, where support staff change things on the cluster and nobody writes it down. Dan takes ACME's app over from their Git without restarting it, sees Git, the hub and the cluster side by side, sorts each difference into *deliberate* (the hub records why), *drift* (on the cluster, with no record) or *Git out of date*, keeps what was meant with a reason, and hands the app back to Git with the hub stopped. The package's `./run` plays the whole story, months of changes included, in about five minutes.

## Human

### What you need

An unpacked confighub mini package, 0.11.1-mini.2 or later ([installing confighub mini](../../docs/install-mini.md#install-by-hand-without-the-plugin)), Docker (or OrbStack), `kind`, `kubectl`, `git`, `python3`, and internet access for Argo CD and the container images. The kind cluster is named `wsa-live-state` and is deleted at the end. No account. A *hub* is ConfigHub running on your computer; *Argo CD* deploys to a cluster what it is pointed at; *argobot* is ConfigHub's small program on the cluster that tells the hub what is running.

### Steps

1. Set up a terminal for this walkthrough. `CUB_CONFIG` gives it a `cub` configuration of its own. The two `LIVESTATE_` settings name the cluster and the folder for ACME's Git:

   <!-- run: setup -->
   ```sh
   export MINI=/absolute/path/to/unpacked-confighub-mini
   export PATH="$MINI/bin:$PATH"
   export CUB_CONFIG="$HOME/.confighub-walkthrough" LIVESTATE_CLUSTER=wsa-live-state LIVESTATE_WORK="$HOME/walkthrough/acme"
   unset CUB_CONTEXT
   confighub-mini-app mini install-plugin "$CUB_CONFIG"
   ```

2. Add cub-scout, ConfigHub's plugin that reads a cluster and says who changed each field, to this `cub` configuration:

   <!-- run: scout -->
   ```sh
   cub plugin install confighub/cub-scout
   ```

3. Copy the example into a folder of your own:

   <!-- run: copy -->
   ```sh
   mkdir -p ~/walkthrough && cp -R "$MINI/examples/live-state" ~/walkthrough/ && cd ~/walkthrough/live-state
   ```

4. Play the story. `./run` starts a hub and a kind cluster with Argo CD; serves ACME's Git to it from this computer; moves ACME's app onto the hub under the same Argo CD; makes months of changes, some in the hub with reasons and some by support on the cluster with none; then shows the three columns:

   <!-- run: dan -->
   ```sh
   ./run
   ```

   ```text
   …
   PASS web/acme is Synced/Healthy, reported by argobot
   …
   field Git hub running what it is
   replicas 2 3 4 deliberate: ACME asked for 3 replicas for their peak season (ticket ACME-4410)
   drift: on the cluster only, no record (changed by kubectl)
   web: env NGINX_ENTRYPOINT_QUIET_LOGS - - 1 drift: on the cluster only, no record (changed by kubectl-set)
   web: image nginx:1.27.3-alpine nginx:1.27.3-alpine nginx:1.27.2-alpine drift: on the cluster only, no record (changed by kubectl-set)
   …
   ```

   It goes on, as Dan: the drift comes into the hub, the hub refuses to overwrite the three replicas ACME asked for, and each finding is decided with a reason. The image pin goes back to Git's version; four replicas and the extra variable are kept, each with its ticket. Then it looks again, and hands the app back:

   ```text
   …
   PASS no drift is left: each difference from Git is a decision with its reason, or a later version
   …
   PASS the hub is stopped
   PASS web-from-git is Synced/Healthy from ACME's Git again
   …
   PASS: every check passed
   ```

5. See ACME's cluster for yourself: it runs from Git again, with four replicas, the declared image and the kept variable, in the same Deployment it had at the start:

   <!-- run: dan-cluster -->
   ```sh
   k="$CUB_CONFIG/clusters/wsa-live-state.kubeconfig"
   kubectl --kubeconfig "$k" -n acme get deploy web -o jsonpath='{.spec.replicas} {.spec.template.spec.containers[0].image}{"\n"}'
   kubectl --kubeconfig "$k" -n argocd get applications.argoproj.io web-from-git -o jsonpath='{.status.sync.status}/{.status.health.status}{"\n"}'
   ```

   ```text
   4 nginx:1.27.3-alpine
   Synced/Healthy
   ```

6. Read what ACME's Git now has: every change made in the hub, who made it and why, in `CHANGES.md`:

   <!-- run: dan-git -->
   ```sh
   grep -E 'ACME-5120|ACME-5133' ~/walkthrough/acme/for-acme-git/CHANGES.md | cut -d'|' -f4,6
   ```

   Each line names a value the hub kept and the reason, with its ticket: four replicas for the October traffic spike, and the variable because ACME pays for log volume.

### Undo it

`./run remove` deletes the cluster, the hub with its data and ACME's Git, and stops the Git server; then the walkthrough's `cub` configuration goes:

<!-- run: undo -->
```sh
./run remove
cd ~ && rm -rf ~/walkthrough "$CUB_CONFIG"
```

### What you have now

Nothing left behind. While it ran, ACME's app was taken over and given back without a restart, every difference was explained, and ACME's Git is up to date and running without the hub, with a list that tells the next support engineer why each value is what it is. The full story adds the case where ACME's cluster cannot reach the hub, and a change made by an agent with `kubectl` while nobody watches. [An app Argo CD or Flux deploys](../../docs/journeys/gitops-app.md) and [going back](../../docs/journeys/going-back.md) cover the same with your own repository.

## Agent

For an AI agent doing this for a person.

- **The request:** "ACME's app runs from their Git under Argo CD, and support changed things on the cluster. Show me what Git says, what the hub holds and what is running, sort each difference, and give ACME back their Git with the hub stopped. Use the cluster wsa-live-state."
- **What to run:** the Human steps 4 and 5, in a copy of `$MINI/examples/live-state`. Report the three columns as the run printed them, each difference with its kind, and what was decided and why. Then tell the person `./run remove` cleans up.
- **Never:** change a cluster other than `wsa-live-state`; leave drift undecided; keep a value without a reason.
- **Done when:** the cluster's `web` runs four replicas of `nginx:1.27.3-alpine` from ACME's Git, Argo CD reports `web-from-git` Synced/Healthy, and the hub is stopped.

## Testing

The scripted run follows the Human steps and compares the quoted output. Arm a, without confighub mini, is not applicable: the takeover and the three columns need the hub. A correct agent result is ACME's cluster as in step 5, before the cleanup. The checks below can be run by hand after step 5:

This proves: a service is running. The real Argo CD on a local kind cluster runs ACME's app from Git, with each kept value and the declared image, after the hub took it over and handed it back. The next step this aims to win: using the takeover for a second app. Tested on the checksum-verified published confighub mini 0.11.1-mini.2 with the plugin 0.85.0, 14 November 2026: environment, the real Argo CD on a local kind cluster, with a local Git server; approval, no approval step. At the moment this page's next step belongs to, the plugin showed no line in the runs, so the offer was not made: the plugin missed the moment. From plugin 0.87.0, the plugin says one line at the end of a turn in which the hub kept a value with its reason. In this story the hub's work happens inside `./run`, which writes its own report, so the plugin says nothing unless the agent runs `cub` itself. The next-step line names words from that line. The Results below stay as run on 0.11.1-mini.2 until a release run replaces them.

<!-- agent-task: dan -->
> ACME's app runs from their Git under Argo CD, and support changed things on the cluster with no record. This folder's ./run plays it on a local kind cluster, wsa-live-state (LIVESTATE_CLUSTER is set). Show me what Git says, what the hub holds and what is running, sort each difference into deliberate, drift or Git out of date, and give ACME back their Git with the hub stopped. Leave the cluster running for me to look at.

<!-- agent-check dan: k=$(find "${CUB_CONFIG:-$HOME/.confighub}" -name wsa-live-state.kubeconfig | head -1) && [ "$(kubectl --kubeconfig "$k" -n acme get deploy web -o jsonpath='{.spec.replicas} {.spec.template.spec.containers[0].image}')" = "4 nginx:1.27.3-alpine" ] && [ "$(kubectl --kubeconfig "$k" -n argocd get applications.argoproj.io web-from-git -o jsonpath='{.status.sync.status}/{.status.health.status}')" = "Synced/Healthy" ] -->
<!-- agent-tools: ./run kubectl -->
<!-- agent-cleanup: kind delete cluster --name wsa-live-state >/dev/null 2>&1; lsof -ti tcp:19419 -sTCP:LISTEN | xargs kill 2>/dev/null; true -->
<!-- arms: b -->
<!-- next-step boundary=same-tier when "with its reason": take over the next app | Do the same for your next app that Argo CD deploys from Git? -->

```sh
k="$CUB_CONFIG/clusters/wsa-live-state.kubeconfig"
kubectl --kubeconfig "$k" -n acme get deploy web -o jsonpath='{.spec.replicas} {.spec.template.spec.containers[0].image}{"\n"}'
kubectl --kubeconfig "$k" -n argocd get applications.argoproj.io web-from-git -o jsonpath='{.status.sync.status}/{.status.health.status}{"\n"}'
```

<!-- results:begin -->

Results, 14 November 2026, confighub mini 0.11.1-mini.2. Figures from this page's own test runs, shown here for whoever checks the page; they are not a promise.

- Scripted run: passed, 293 seconds for the steps, within the page's budget of 480.
- Agent runs: a pilot, 3 runs per arm on each of claude-sonnet-5-5, claude-opus-5-5. Arms: b is the plugin, confighub mini and this page as reading.

| Arm | Model | Checks passed | Median seconds | Median cost | Commands left for the person (median) |
|---|---|---|---|---|---|
| b | claude-opus-5-5 | 3/3 | 331.7 | $0.216 | 0 |
| b | claude-sonnet-5-5 | 3/3 | 329.8 | $0.105 | 0 |

No agent approved or refused a change to production.

Simulated persons, not people: 10 per run, each a claude-haiku-5-5 model playing one of ten fixed personas, reading only what a person would see. The next step they were offered: "Take over your next app that Argo CD deploys from Git, and see Git, the hub and the cluster side by side, without restarting it?"

The plugin offers it once, after the answer at whose end it showed the moment the offer names ("recorded"). Offered is the share of persons it was shown to; want it now and later are over them.

| Arm | Model | Persons | Offered | Noticed | Want the next step now | Later | In the way |
|---|---|---|---|---|---|---|---|
| b | claude-opus-5-5 | 30 | 0% | 100% | n/a | n/a | 53% |
| b | claude-sonnet-5-5 | 30 | 0% | 100% | n/a | n/a | 60% |

<!-- results:end -->
