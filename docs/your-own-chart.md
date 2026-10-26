# Your own Helm chart, step by step: about 10 minutes

**Who.** A platform engineer who runs vendor charts with values of their own: a pinned driver, a scrape path, a replica count for a busy week.

**What goes wrong without it.** The chart's next version changes or drops what your values set, as cert-manager 1.21.2 dropped the setting for the path its ServiceMonitor scrapes, and you find out at upgrade time: Helm refuses the old key, or quietly renders without it. Why each of your values was set lives in someone's head.

**What they get.** Your values kept, each with its reason, through the chart's next version; what that version would change shown before you take it; and plain files that say why each value is set, for Git or a cluster.

Your chart, with your values, kept in confighub mini; a value of your own that the chart's next version does not undo, with why; the next version previewed before you take it; and the result on a cluster. The example uses the public `podinfo` chart; put your own chart and values in its place.

You need confighub mini installed and a hub started ([install it](install-mini.md)), and, for the last step, a cluster and `kubectl`. Helm itself is not needed.

## 1. The chart, with your values

[cub-helm](https://github.com/confighub/cub-helm) renders a chart on your machine and keeps the result in the hub, one Unit per resource, with the chart and values beside it for later versions:

```bash
cub plugin install confighub/cub-helm
cat > my-values.yaml <<'EOF2'
replicaCount: 2
ui:
  message: "Hello from our team"
EOF2
cub helm install podinfo oci://ghcr.io/stefanprodan/charts/podinfo --version 6.5.4 --values my-values.yaml
```

That makes the Component `podinfo`, with `podinfo-base`, what the chart renders, and `podinfo-helm`, the chart and values it came from. `cub helm template` shows the same without writing anything.

## 2. The copy that runs, and a value of your own

The base follows the chart. What runs is a copy of it, which keeps your own changes:

```bash
cub variant create live podinfo-base
cub mini set podinfo replicas 3 --variant live --change-desc "Three for the launch"
```

The 3 is now yours: a later version of the chart does not replace it, and the reason is kept beside it. A field the chart does not expose as a value is set the same way, with the resource's type and the field's path, for example `cub mini set podinfo set-int-path apps/v1/Deployment spec.revisionHistoryLimit 5 --variant live --change-desc "We keep five"`.

## 3. The chart's next version: see it, then take it

```bash
cub helm upgrade podinfo --version 6.6.0
cub mini promote podinfo-live --dry-run
cub mini promote podinfo-live
```

`cub helm upgrade` renders the new version, with the same values, into the base. The dry run lists what the live copy would take, here the image `ghcr.io/stefanprodan/podinfo:6.5.4 → 6.6.0` and the chart's labels, and changes nothing. Taking it keeps your 3 replicas:

```
  replicas: 3 # Three for the launch
        image: "ghcr.io/stefanprodan/podinfo:6.6.0"
```

## 4. Onto a cluster

Write the live copy out as plain files, and apply them:

```bash
cub mini copy podinfo --variant live --to-dir deploy
kubectl create namespace podinfo
kubectl apply -n podinfo -f deploy/podinfo-live/
```

`deploy/podinfo-live/` holds one file per resource, and `deploy/CHANGES.md` says why each of your values is set. Commit `deploy/` instead, and Argo CD or Flux deploys it from Git. This chart writes no namespace into its manifests, so it is given with `-n`; a chart that does keeps its own.

## What is different from Helm

- **No Helm release on the cluster.** `helm list` shows nothing, and `helm rollback` is not used: each change is a revision in ConfigHub, with its reason.
- **Hooks are dropped** unless you install with `--include-hooks`, which keeps them as plain resources, applied with the rest rather than at install or upgrade time.
- **Rendering never contacts a cluster.** The `lookup` template function returns nothing, so a chart that depends on it is out of scope.

All of the above was run as written on a Mac, with confighub mini 0.9.0-mini.3 and cub-helm 0.1.2, onto a kind cluster: the next version of the chart, `podinfo:6.6.0`, ran with both values of our own kept, 3 replicas and a revision history of 5.
