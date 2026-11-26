# Self-hosting the ConfigHub hub in Kubernetes (Helm)

For a platform team that wants to run a ConfigHub hub inside their own Kubernetes cluster behind corporate OIDC/SAML single sign-on (Dex, Okta, Microsoft Entra ID, or Keycloak) with persistent PostgreSQL storage, in-place Helm upgrades, and clean teardown.

A **hub** is a ConfigHub server and PostgreSQL database that stores configuration, the reason for each value, and an immutable record of who approved each change.

## Install with Helm

The Helm chart is packaged in [`charts/confighub-hub/`](../charts/confighub-hub/README.md):

```sh
helm install confighub ./charts/confighub-hub \
  --namespace confighub --create-namespace \
  --set oidc.issuer=https://idp.internal.example.com/dex \
  --set oidc.audience=confighub-cli \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=confighub.internal.example.com
```

Key chart defaults:
- **Storage:** 10 Gi `PersistentVolumeClaim` mounted at `/var/lib/confighub` for PostgreSQL data and hub state (`persistence.enabled: true`).
- **Security:** Runs non-root (`runAsUser: 1000`, `allowPrivilegeEscalation: false`), listens on cluster-internal port `8080` behind your Ingress and TLS termination.
- **SSO:** Sets `CONFIGHUB_AUTH_ISSUER`, `CONFIGHUB_TOKEN_EXCHANGE_AUDIENCE`, and optional `CONFIGHUB_AUTH_JWKS_URL` for corporate OIDC token exchange.

## Upgrade, back up, and remove

- **Upgrade in place (preserves PostgreSQL data and audit history):**
  ```sh
  helm upgrade confighub ./charts/confighub-hub \
    --namespace confighub --reuse-values \
    --set image.tag=<NEW_TAG>
  ```
  The Deployment uses `strategy.type: Recreate` so the old pod releases the single-writer PostgreSQL PVC cleanly before the new pod starts and runs schema migrations.
- **Back up or export:** Snapshot the PVC, run `pg_dump` in the pod, or export any app to plain files with `cub mini copy APP --variant live --to-dir DIR`.
- **Remove everything:**
  ```sh
  helm uninstall confighub -n confighub
  kubectl -n confighub delete pvc confighub-confighub-hub-data
  ```

## Security review and PR audit trail

- For network surface, stored PostgreSQL tables, credential redaction, and binary verification, see [For a security review: the ConfigHub hub](security-hub.md).
- To record every pull request's rendered diff, reasons, and GitHub-API-verified approvers into this self-hosted hub without changing Argo CD or Flux, see [Record your existing pull-request flow in a self-hosted hub with SSO](../examples/walkthroughs/tool-record-pr-hub.md).
- **Where this grows (1:46 video):** Once your team trusts the self-hosted hub for PR audit trails, watch the [ConfigHub Trailer](https://youtu.be/H7xtSqMZrao) to see multi-cluster fleet promotion, field guards, and `cub unit blame` alongside Argo CD, Flux, and Sveltos.
