<!-- walkthrough
id: story-01-find-the-fault
starts_with: mini
story: "1. Dan: "I don't know what's wrong. Please fix it.""
needs: [confighub mini package, helm, python3, internet access to render the chart]
budget_seconds: 120
-->
# Find the fault in a customer's platform, and keep the changes they meant

For someone called in to fix a platform a customer has changed over the months, where nobody remembers every change. Dan finds three differences from the platform as it was given. The customer explains two; the third is the fault. He rebuilds their installation in a hub with the two changes they meant, each with its reason, leaves the fault out, and writes it back out as plain files for their Git.

## Human

### What you need

An unpacked confighub mini package, 0.11.1-mini.2 or later ([installing confighub mini](../../docs/install-mini.md#install-by-hand-without-the-plugin)), `helm`, `python3`, and internet access to render NVIDIA's published GPU Operator chart. No GPU, no cluster, no Docker and no account. A *hub* is ConfigHub running on your computer; `cub` is ConfigHub's command-line tool, and `cub mini` the commands confighub mini adds to it.

### Steps

1. Say where the unpacked package is:

   <!-- run: package files -->
   ```sh
   export MINI=/absolute/path/to/unpacked-confighub-mini
   ```

2. Set up a terminal for this walkthrough. `CUB_CONFIG` gives it a `cub` configuration of its own, so your own `cub` settings are not touched:

   <!-- run: setup -->
   ```sh
   export PATH="$MINI/bin:$PATH"
   export CUB_CONFIG="$HOME/.confighub-walkthrough"
   unset CUB_CONTEXT
   confighub-mini-app mini install-plugin "$CUB_CONFIG"
   ```

3. Copy the example and render the platform. `given/` is the platform as the customer was given it; `as-found/` is what they run today:

   <!-- run: render files -->
   ```sh
   mkdir -p ~/walkthrough && cp -R "$MINI/examples/gpu-platform" ~/walkthrough/ && cd ~/walkthrough/gpu-platform
   ./render
   ```

   ```text
   given/gpu-operator: GPU Operator 25.10.1, 27 objects
   …
   as-found/gpu-operator: GPU Operator 25.10.1, 27 objects
   ```

4. Compare what they run with what they were given. No hub is needed for this. Three values differ:

   <!-- run: fix-compare may-fail -->
   ```sh
   diff given/gpu-operator/gpu-operator.yaml as-found/gpu-operator/gpu-operator.yaml
   ```

   ```text
   <     repository: nvcr.io/nvidia
   ---
   >     repository: nvcr.io/nvdia
   …
   <     version: "580.105.08"
   ---
   >     version: "580.95.05"
   …
   <     enabled: true
   ---
   >     enabled: false
   ```

   The customer explains two: their nodes are certified with driver 580.95.05, and they collect GPU metrics with their own exporter, so they switched the platform's exporter off. Nobody can explain the third. The driver's registry is spelled `nvcr.io/nvdia`, which does not exist, so the driver can never be downloaded. That is the fault.

5. Start a hub, and put the platform as given into it, as the *base*. Then make the customer's installation, a *variant* (a copy made from the base) named `gpu-operator-customer`:

   <!-- run: fix-hub -->
   ```sh
   cub mini install --name dan --use
   cub mini upload given/gpu-operator --namespace gpu-operator
   cub variant create customer gpu-operator-base
   ```

6. Make the two changes the customer meant, each with their reason. Each one is *kept*: the platform's next version will not overwrite it. The misspelled registry is simply not made again.

   <!-- run: fix-keep -->
   ```sh
   cub mini set gpu-operator set-string-path nvidia.com/v1/ClusterPolicy spec.driver.version 580.95.05 \
     --variant customer --change-desc "Customer: our nodes are certified with driver 580.95.05"
   cub mini set gpu-operator set-bool-path nvidia.com/v1/ClusterPolicy spec.dcgmExporter.enabled false \
     --variant customer --change-desc "Customer: we collect GPU metrics with our own exporter"
   ```

   ```text
   …
   Saved in gpu-operator-customer, with the reason: Customer: our nodes are certified with driver 580.95.05. A later version of what gpu-operator-customer is made from will not overwrite this value.
   …
   Saved in gpu-operator-customer, with the reason: Customer: we collect GPU metrics with our own exporter. A later version of what gpu-operator-customer is made from will not overwrite this value.
   ```

7. Hand it back for their Git: plain files, one folder for each copy, with a list of every change, who made it and why, in `CHANGES.md`:

   <!-- run: fix-handback -->
   ```sh
   cub mini copy gpu-operator --variant customer --to-dir handback
   ```

   ```text
   …
   Wrote 2 Spaces and 54 Units from this hub to handback, with the list in CHANGES.md. Nothing was changed in the hub.
   …
   ```

8. Check the files. Each reason sits beside its value, and the misspelled registry is gone:

   <!-- run: fix-check -->
   ```sh
   grep '# Customer' handback/gpu-operator-customer/cluster-policy-clusterpolicy.yaml
   grep -rq 'nvcr.io/nvdia' handback || echo "The misspelled registry is not in the files."
   ```

   ```text
   version: "580.95.05" # Customer: our nodes are certified with driver 580.95.05
   enabled: false # Customer: we collect GPU metrics with our own exporter
   The misspelled registry is not in the files.
   ```

### Undo it

This removes the hub with everything in it, and the walkthrough's folder and `cub` configuration:

<!-- run: undo -->
```sh
cub mini uninstall --name dan --delete-data
cd ~ && rm -rf ~/walkthrough "$CUB_CONFIG"
```

### What you have now

Nothing left behind but what you would hand the customer: a working installation as files, their two deliberate changes kept with the reasons beside them, and the fault gone. The full story adds the other two ways to leave: handing the hub itself over to the customer's own key, and keeping a copy in Dan's own hub; and the same fix done by an agent in a sandbox. [Going back](../../docs/journeys/going-back.md) covers handing an app back to Git.

## Agent

For an AI agent doing this for a person.

- **The request:** "The customer's GPU nodes stopped showing GPUs. Compare what they run with the platform we gave them and fix it. They changed the driver to 580.95.05 because their nodes are certified with it, and switched our metrics exporter off because they use their own; keep both, with those reasons. Give me files for their Git."
- **What to run:** the Human steps 3 to 8, in order, from a copy of `$MINI/examples/gpu-platform`. Use the customer's own words as each `--change-desc`. Tell the person which difference was the fault and why, and where the files and `CHANGES.md` are.
- **Never:** copy `as-found/` back as the fix, which keeps the fault; make a change without the customer's reason; change anything the customer did not ask for.
- **Done when:** the customer's copy has driver 580.95.05 and the exporter off, each with its reason, the registry is `nvcr.io/nvidia`, and `handback/CHANGES.md` lists both changes.

## Testing

The scripted run follows the Human steps on a hub of its own and compares the quoted output. A correct agent result is the customer's copy, `gpu-operator-customer`, with the two kept values and their reasons and no misspelled registry, written out with `CHANGES.md`. Without a hub, the equivalent is a fixed file with both values and the registry corrected. The checks below can be run by hand after the steps:

This proves: stored. The fix is kept in a hub on this computer and written out as files for Git; nothing is delivered to a cluster. The next step this aims to win: moving the work from a hub on one computer to a shared hub. Tested on the checksum-verified published confighub mini 0.11.1-mini.2 with the plugin 0.85.0, 14 November 2026: environment, local hub and local files (no cluster); approval, no approval step. At the moment this page's next step belongs to, the plugin showed no line in the runs, so the offer was not made: the plugin missed the moment. From the next release, the plugin says one line at this moment, such as "ConfigHub plugin: kept version 580.95.05 and enabled false in gpu-operator-customer, each with its reason, so a later version will not overwrite them. Files with the reasons are in handback/." The next-step line names words from that line. The Results below stay as run on 0.11.1-mini.2 until a release run replaces them.

<!-- agent-task: fix -->
> The customer's GPU nodes stopped showing GPUs. In this folder, given/ is the GPU platform we gave them and as-found/ is what they run. Compare the two and fix it. They changed the driver to 580.95.05 because their nodes are certified with it, and switched our metrics exporter off because they use their own; keep both, with those reasons, in their installation, called "customer". Give me files for their Git.

<!-- agent-check fix: d=$(cub unit data cluster-policy-clusterpolicy --space gpu-operator-customer) && echo "$d" | grep -q 'version: "580.95.05" # Customer' && echo "$d" | grep -q 'enabled: false # Customer' && ! echo "$d" | grep -q 'nvcr.io/nvdia' && grep -rqs 'certified with driver 580.95.05' --include=CHANGES.md . -->
<!-- agent-check-a fix: f=$(grep -rl --include='*.yaml' '580.95.05' . | grep -v -e '/as-found/' -e '/given/' -e '/next/' | head -1) && [ -n "$f" ] && ! grep -q 'nvcr.io/nvdia' "$f" && grep -q 'repository: nvcr.io/nvidia$' "$f" -->
<!-- arms: a,b -->
<!-- next-step when "with its reason, so a later version will not overwrite": copy to the team's hub | Your fix and its reasons are kept on this computer. Copy them to your team's hub, so the next person who looks at this customer starts from them? -->

```sh
cub unit data cluster-policy-clusterpolicy --space gpu-operator-customer | grep -E '# Customer|nvdia'
grep -r 'certified with driver' --include=CHANGES.md .
```

<!-- results:begin -->

Results, 14 November 2026, confighub mini 0.11.1-mini.2. Figures from this page's own test runs, shown here for whoever checks the page; they are not a promise.

- Scripted run: passed, 59 seconds for the steps, within the page's budget of 120.
- Agent runs: a pilot, 3 runs per arm on each of claude-sonnet-5-5, claude-opus-5-5. Arms: a is ordinary tools only; b is the plugin, confighub mini and this page as reading.

| Arm | Model | Checks passed | Median seconds | Median cost | Commands left for the person (median) |
|---|---|---|---|---|---|
| a | claude-opus-5-5 | 3/3 | 81.6 | $0.328 | 5 |
| b | claude-opus-5-5 | 3/3 | 61.9 | $0.215 | 0 |
| a | claude-sonnet-5-5 | 3/3 | 18.0 | $0.095 | 0 |
| b | claude-sonnet-5-5 | 3/3 | 48.9 | $0.089 | 0 |

No agent approved or refused a change to production.

Simulated persons, not people: 10 per run, each a claude-haiku-5-5 model playing one of ten fixed personas, reading only what a person would see. The next step they were offered: "Your fix and its reasons are kept on this computer. Copy them to your team's hub, so the next person who looks at this customer starts from them?"

The plugin offers it once, after the answer at whose end it showed the moment the offer names ("recorded"). Offered is the share of persons it was shown to; want it now and later are over them.

| Arm | Model | Persons | Offered | Noticed | Want the next step now | Later | In the way |
|---|---|---|---|---|---|---|---|
| a | claude-opus-5-5 | 30 | 0% | 100% | n/a | n/a | 100% |
| b | claude-opus-5-5 | 30 | 0% | 100% | n/a | n/a | 50% |
| a | claude-sonnet-5-5 | 30 | 0% | 100% | n/a | n/a | 60% |
| b | claude-sonnet-5-5 | 30 | 0% | 100% | n/a | n/a | 53% |

<!-- results:end -->
