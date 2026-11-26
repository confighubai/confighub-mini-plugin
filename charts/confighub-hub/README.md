# ConfigHub Hub Helm Chart (`confighub-hub`)

Self-host a ConfigHub hub inside your own Kubernetes cluster with persistent PostgreSQL storage (`PersistentVolumeClaim`), optional Ingress/TLS, and corporate OIDC/SAML single sign-on (Dex, Okta, Microsoft Entra ID, or Keycloak).

## Quick start

```sh
helm install confighub ./charts/confighub-hub \
  --namespace confighub --create-namespace \
  --set oidc.issuer=https://idp.internal.example.com/dex \
  --set oidc.audience=confighub-cli \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=confighub.internal.example.com
```

## Key values

| Value | Default | Purpose |
|---|---|---|
| `image.repository` / `image.tag` | `confighub-selfhosted` / `v0.11.1` | ConfigHub server image |
| `persistence.enabled` / `persistence.size` | `true` / `10Gi` | PVC mounted at `/var/lib/confighub` (PostgreSQL data and hub state) |
| `oidc.issuer` | `""` | Corporate OIDC issuer URL (`CONFIGHUB_AUTH_ISSUER`) |
| `oidc.audience` | `""` | Expected OIDC audience (`CONFIGHUB_TOKEN_EXCHANGE_AUDIENCE`) |
| `oidc.jwksUrl` | `""` | Optional internal JWKS URL when split-horizon DNS is used |
| `ingress.enabled` | `false` | Expose behind your cluster Ingress controller and TLS termination |

## Upgrades and backups

- **Upgrade in place (preserves PVC and PostgreSQL history):**
  ```sh
  helm upgrade confighub ./charts/confighub-hub -n confighub --reuse-values --set image.tag=<NEW_TAG>
  ```
  The Deployment uses `strategy.type: Recreate` so the old pod releases the single-writer PostgreSQL PVC cleanly before the new pod starts and runs any schema migrations.
- **Export / backup:** Snapshot the PVC, run `pg_dump` inside the pod, or export any app to plain files with `cub mini copy APP --variant live --to-dir DIR`.
- **Full teardown:** `helm uninstall confighub -n confighub && kubectl -n confighub delete pvc confighub-confighub-hub-data`.
