# What this directory is

Configuration written out of a ConfigHub hub (soft-snout) as plain files, one directory for each Space. It is what the hub held when this was written. Nothing here needs the hub.

To run from these files, point Argo CD or Flux at the directory of the Space you run.

If your repository makes its files from something else, Helm values or Kustomize overlays, those do not know about the changes below. The files here do. To keep working from values or overlays, put the changes you care about back there.

## Changed in the hub

| Space | Resource | Value | Now | Why | Who, when | Protected |
|---|---|---|---|---|---|---|
| shop-prod | Deployment shop/api | `spec.replicas` | `4` | Four in production for Friday's sale | admin@local.confighub.dev, 2026-10-26 | yes |
