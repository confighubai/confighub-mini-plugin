# Your own Helm chart, step by step: about 10 minutes

This walkthrough is for a platform engineer who runs a vendor's Helm chart with values of their own, such as a pinned driver, a scrape path, or a replica count for a busy week. It shows how to keep those values, each with its reason, through the chart's next version. You see what the next version would change before you take it, and you end with plain files you can apply to a cluster or commit to Git.

## The problem this solves

A chart's next version can change or drop a setting your values depend on. For example, cert-manager 1.21.2 dropped the setting for the path its ServiceMonitor scrapes. You find out at upgrade time. Helm either refuses the old key, or quietly renders the chart without it. And the reason each of your values was set is usually in someone's head, not written down.

## Words used here

- [ConfigHub](https://docs.confighub.com) keeps your configuration with the reason each value is set. A *hub* is one running ConfigHub server. *confighub mini* runs a hub on your machine. `cub` is ConfigHub's command-line tool.
- A *Component* is one piece of software, here `podinfo`.
- A Component's *base* is the configuration as the chart renders it. A *variant* is a copy made from the base for one place it runs, here `live`. The variant keeps your own changes when the base changes.
- A *Space* holds configuration, as *Units*: one Unit per Kubernetes resource.

## What you need

- confighub mini installed, and a hub started ([install it](install-mini.md)).
- For the last step only: a Kubernetes cluster, and `kubectl`.

You do not need Helm itself.

The example uses the public `podinfo` chart. To do the same with your own chart, put your chart and values in its place.

## Step 1: Put the chart, with your values, in the hub

[cub-helm](https://github.com/confighub/cub-helm) renders a chart on your machine and keeps the result in the hub, one Unit per resource. It keeps the chart and values beside the result, for later versions.

1. Install cub-helm:

   ```bash
   cub plugin install confighub/cub-helm
   ```

2. Write your values:

   ```bash
   cat > my-values.yaml <<'EOF2'
   replicaCount: 2
   ui:
     message: "Hello from our team"
   EOF2
   ```

3. Render the chart into the hub:

   ```bash
   cub helm install podinfo oci://ghcr.io/stefanprodan/charts/podinfo --version 6.5.4 --values my-values.yaml
   ```

   This makes the Component `podinfo`, with two parts:
   - `podinfo-base` holds what the chart renders.
   - `podinfo-helm` holds the chart and the values it came from.

To see what `cub helm install` would render without writing anything, use `cub helm template` in its place.

## Step 2: Make the copy that runs, and set a value of your own

The base follows the chart. What runs is a copy of the base, which keeps your own changes.

1. Make the copy, `live`:

   ```bash
   cub variant create live podinfo-base
   ```

2. Set 3 replicas in it, with your reason:

   ```bash
   cub mini set podinfo replicas 3 --variant live --change-desc "Three for the launch"
   ```

The 3 is now yours. A later version of the chart does not replace it, and your reason is kept beside it.

To set a field the chart does not expose as a value, give the resource's type and the field's path. For example:

```bash
cub mini set podinfo set-int-path apps/v1/Deployment spec.revisionHistoryLimit 5 --variant live --change-desc "We keep five"
```

## Step 3: See the chart's next version, then take it

1. Render the new version of the chart, with the same values, into the base:

   ```bash
   cub helm upgrade podinfo --version 6.6.0
   ```

2. See what the live copy would take from it:

   ```bash
   cub mini promote podinfo-live --dry-run
   ```

   This lists what would change in the live copy, and changes nothing. Here it lists the new image, `ghcr.io/stefanprodan/podinfo:6.5.4 → 6.6.0`, and the chart's labels.

3. Take it:

   ```bash
   cub mini promote podinfo-live
   ```

   The live copy now has the new image, and still has your 3 replicas:

   ```
     replicas: 3 # Three for the launch
           image: "ghcr.io/stefanprodan/podinfo:6.6.0"
   ```

## Step 4: Apply it to a cluster

1. Write the live copy out as plain files:

   ```bash
   cub mini copy podinfo --variant live --to-dir deploy
   ```

   `deploy/podinfo-live/` now holds one file per resource. `deploy/CHANGES.md` says why each of your values is set.

2. Create the namespace:

   ```bash
   kubectl create namespace podinfo
   ```

   This chart writes no namespace into its manifests, so you give it with `-n` in the next step. A chart that does write one keeps its own.

3. Apply the files:

   ```bash
   kubectl apply -n podinfo -f deploy/podinfo-live/
   ```

If you use Argo CD or Flux, which deploy to a cluster what is in a Git repository, commit `deploy/` instead of applying it. Argo CD or Flux then deploys it from Git.

## The same in plain `cub`

On the company's ConfigHub, you can do the same with plain `cub`:

- `cub mini set podinfo replicas 3 --variant live` is `cub function set --space podinfo-live --unit podinfo set-replicas 3`. `cub mini set` also marks the value as kept, and records the reason.
- `cub mini promote podinfo-live` is `cub variant promote podinfo-live`. `cub mini promote` also shows the values in its preview.
- `cub mini copy --to-dir` has no `cub` equivalent yet.

All of them are in [`cub mini` and plain `cub`](cub-mini-and-cub.md).

## How this differs from Helm

- **There is no Helm release on the cluster.** `helm list` shows nothing, and you do not use `helm rollback`. Each change is a revision in ConfigHub, with its reason.
- **Chart hooks are dropped**, unless you install with `--include-hooks`. That flag keeps them as plain resources. They are then applied with the rest, not at install or upgrade time.
- **Rendering never contacts a cluster.** The `lookup` template function returns nothing, so a chart that depends on it is out of scope.

## How this was tested

All of the above was run as written on a Mac, with confighub mini 0.9.0-mini.3 and cub-helm 0.1.2, onto a kind cluster. The chart's next version, `podinfo:6.6.0`, ran with both of our own values kept: 3 replicas, and a revision history of 5.
