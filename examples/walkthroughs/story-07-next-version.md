<!-- walkthrough
id: story-07-next-version
starts_with: mini
story: "7. The customer, months later: "Take the platform's next version, and keep the change we had to make""
needs: [confighub mini package, helm, python3, internet access to render the chart]
budget_seconds: 120
-->
# Take a platform's next version, and keep the one value you set on purpose

For a team that runs a platform someone else gives them and changed one value in it. Here the platform is NVIDIA's GPU Operator. The customer pinned the GPU driver, because a driver change takes every GPU node out in turn. The next version changes about a hundred values and offers a newer driver. You see what you would take and what you keep before anything changes, then take it with the driver and its reason kept.

## Human

### What you need

An unpacked confighub mini package, 0.10.7-mini.24 or later ([installing confighub mini](../../docs/install-mini.md#install-by-hand-without-the-plugin)), `helm`, `python3`, and internet access to render NVIDIA's published chart. No GPU, no cluster, no Docker and no account. A *hub* is ConfigHub running on your computer; `cub` is ConfigHub's command-line tool, and `cub mini` the commands confighub mini adds to it.

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

3. Copy the example and render the platform at two versions: 25.10.1, which the customer was given, into `given/`, and 26.3.3, the next one, into `next/`:

   <!-- run: render files -->
   ```sh
   mkdir -p ~/walkthrough && cp -R "$MINI/examples/gpu-platform" ~/walkthrough/ && cd ~/walkthrough/gpu-platform
   ./render
   ```

   ```text
   given/gpu-operator: GPU Operator 25.10.1, 27 objects
   next/gpu-operator: GPU Operator 26.3.3, 27 objects
   …
   ```

4. Start a hub, and put the platform as given into it. It goes in as the *base*, `gpu-operator-base`: the copy that takes each new version.

   <!-- run: take-hub -->
   ```sh
   cub mini install --name gpu --use
   cub mini upload given/gpu-operator --namespace gpu-operator
   ```

5. Make the customer's installation, a *variant* (a copy made from the base) named `gpu-operator-customer`, and keep its driver with the reason. The value does not change, but from now on a later version will not overwrite it:

   <!-- run: take-keep -->
   ```sh
   cub variant create customer gpu-operator-base --change-desc "The customer's installation"
   cub mini set gpu-operator set-string-path nvidia.com/v1/ClusterPolicy spec.driver.version 580.105.08 \
     --change-desc "A driver change drains every GPU node. We change it only in a maintenance window."
   ```

   ```text
   …
   gpu-operator-customer already has spec.driver.version=580.105.08. A later version of what gpu-operator-customer is made from will not overwrite this value now.
   …
   Reason recorded beside the value: A driver change drains every GPU node. We change it only in a maintenance window.
   ```

6. The next version arrives. Put it into the base. Before anything changes, you see what the customer's installation would take and what it keeps, with the offered value beside it. It asks whether to take it; answer `n` for now, or press Enter.

   <!-- run: take-next -->
   ```sh
   cub mini upload next/gpu-operator --component gpu-operator --namespace gpu-operator
   ```

   ```text
   gpu-operator-customer
   …
   changes Validator version v25.10.1 → v26.3.3
   …
   changes Toolkit version v1.18.1 → v1.19.1
   …
   you keep Driver version yours: "580.105.08" (offered: "580.126.20")
   …
   Nothing running has changed. To take it later:
   cub mini promote gpu-operator-customer
   ```

7. Take it, with a note of what it is:

   <!-- run: take -->
   ```sh
   cub mini promote gpu-operator-customer --change-desc "GPU Operator 26.3.3"
   ```

   ```text
   …
   gpu-operator-customer: updated. No cluster or service takes its settings from ConfigHub yet
   …
   Done. Each copy kept its own values.
   ```

8. Read the result: the operator is at 26.3.3, and the driver is still 580.105.08, with the reason written beside it.

   <!-- run: take-read -->
   ```sh
   cub unit data cluster-policy-clusterpolicy --space gpu-operator-customer | grep -E 'version: "?(v26.3.3|580)'
   ```

   ```text
   …
   version: "580.105.08" # A driver change drains every GPU node. We change it only in a maintenance window.
   …
   ```

### Undo it

This removes the hub with everything in it, and the walkthrough's folder and `cub` configuration:

<!-- run: undo -->
```sh
cub mini uninstall --name gpu --delete-data
cd ~ && rm -rf ~/walkthrough "$CUB_CONFIG"
```

### What you have now

Nothing left behind. While it ran, the customer had the platform's new version, their one change kept, and the reason for it beside the value for the next person who asks. The full story adds three customers taking the same version at once, the platform coming from the provider's own hub, and a refusal when a new version would drop a kept value. [A Helm chart you use, with your values](../../docs/your-own-chart.md) does the same with your own chart.

## Agent

For an AI agent doing this for a person.

- **The request:** "We pinned the GPU driver to 580.105.08 because a driver change drains every GPU node. Take the GPU Operator's next version, 26.3.3, but keep our driver."
- **What to run:** the Human steps 3 to 7, in order, from a copy of `$MINI/examples/gpu-platform`: render, `cub mini install`, upload `given/`, `cub variant create customer gpu-operator-base`, `cub mini set ... spec.driver.version 580.105.08 --change-desc "<the person's reason>"`, upload `next/` with `--component gpu-operator`, show the person the preview, then `cub mini promote gpu-operator-customer`. Tell the person what changed, that the driver was kept, and the offered driver they did not take.
- **Never:** edit the rendered files to put the old driver back by hand; set the driver without the person's reason; take the version before showing the preview.
- **Done when:** step 8 reads `v26.3.3` and `version: "580.105.08"` with the reason beside it.

## Testing

The scripted run follows the Human steps on a hub of its own and compares the quoted output. A correct agent result is the customer's copy, `gpu-operator-customer`, at operator 26.3.3 with driver 580.105.08 and its reason. Without a hub, the equivalent is a file of the merged result with both. The checks below can be run by hand after the steps:

This proves: stored. The new version and the kept driver are in a hub on this computer; nothing is delivered to a cluster.

<!-- agent-task: take -->
> We run NVIDIA's GPU Operator 25.10.1, in given/ in this folder; its next version, 26.3.3, is in next/. Our installation is called "customer", and we pinned the GPU driver to 580.105.08 because "A driver change drains every GPU node. We change it only in a maintenance window." Take the next version, but keep our driver.

<!-- agent-check take: d=$(cub unit data cluster-policy-clusterpolicy --space gpu-operator-customer) && echo "$d" | grep -q 'version: "v26.3.3"' && echo "$d" | grep -q 'version: "580.105.08" # A driver change drains' -->
<!-- agent-check-a take: grep -rl --include='*.yaml' 'gpu-operator:v26.3.3' . | grep -v -e '/next/' -e '/given/' | xargs grep -l '580.105.08' | grep -q . -->
<!-- arms: a,b -->

```sh
cub unit data cluster-policy-clusterpolicy --space gpu-operator-customer | grep -E 'version: "?(v26.3.3|580)'
```
