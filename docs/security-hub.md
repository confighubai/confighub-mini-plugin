# For a security review: the ConfigHub hub (local and self-hosted)

This page is for a platform or security team reviewing the ConfigHub hub itself — either the local hub (`confighub mini`) on a developer's laptop or a self-hosted ConfigHub hub in your own Kubernetes cluster. For what the Claude Code plugin does on a developer's computer with no hub, see [For a security review: what the Claude plugin does](security.md).

A **hub** is a ConfigHub server and PostgreSQL database that stores your apps' settings, the reason for each value, and an immutable record of who approved each change.

## Network surface

- **Local hub (`confighub mini`):** The ConfigHub server and its bundled PostgreSQL listen on loopback (`127.0.0.1`) only, on randomly chosen local ports. Nothing listens on external network interfaces, no Docker daemon is required, and no account or outbound cloud connection is needed once downloaded.
- **Self-hosted hub in Kubernetes:** Install with the packaged [Helm chart (`charts/confighub-hub/`)](../charts/confighub-hub/README.md) ([one-page Helm install, upgrade, and backup guide](self-hosted-helm.md)). Runs non-root behind your own ingress and TLS termination with a `PersistentVolumeClaim` for PostgreSQL. People sign in through your company's OIDC or SAML single sign-on (SSO) with `cub auth login --server https://...` (for example, Dex, Okta, or Entra ID; tested end to end with `helm install` and `helm upgrade` in `kind` alongside a live Dex OIDC provider). Automated jobs (such as GitHub Actions running `cub mini record-pr --from-github`) authenticate with scoped service account keys granted access only to the specific Space they write to, and pull verified `APPROVED` reviewers directly from the GitHub API.

## What is stored in PostgreSQL

- **Configuration copies and revisions:** Non-secret settings (`base`, `staging`, `live`), mutation ownership (which values belong to an app vs. a shared starter), and the reason recorded for each change.
- **Immutable attestations:** Server-timestamped records tied to the authenticated user or service account, including:
  - `Approval` attestations recording who approved a change order and revision.
  - `PullRequestReview` attestations (`cub mini record-pr`) recording repository, PR number, base and head commits, author, GitHub approvers, changed file/value counts, redacted summary note, and the SHA-256 digest of the redacted review.
  - `AgentRecord` and `ModelUse` attestations (when turned on) recording signed agent session digests and token counts.
- **Data location (local hub):** All state for a local hub lives under `~/.confighub/servers/<name>/` (PostgreSQL data directory, server logs, PID files, and runtime metadata). Your repository files are not rewritten.

## Credential redaction and boundaries

- **Credentials stay out of the hub by default.** Values whose names or shapes look like credentials (passwords, tokens, API keys, URLs with embedded passwords, Kubernetes `Secret` `data`/`stringData`) are skipped when adopting from files or hosts (`Vercel`, `Fly`, `Heroku`, `Unikraft`), and are redacted before `cub mini record-pr` writes claims or notes.
- **Scoped agent keys:** An agent's service account key can propose changes to `live` and update `staging`, and is refused by the server if it tries to approve `live`, read owner-only secrets, or act outside its Spaces. Revoking the key stops future requests immediately.
- **Host delivery boundaries:** When delivering approved changes to Vercel, Fly, Heroku, or Unikraft, the person's own CLI sign-in is used from their terminal after a one-time confirmation; an agent session cannot give that confirmation or redirect the target host.

## Binaries, upgrades, and backups

- **Verification:** Each local hub release publishes `SHA256SUMS` alongside the platform archives ([current release](install-mini.md#the-current-release)). `bin/confighub mini get` verifies the downloaded archive against its checksum before unpacking. macOS binaries are currently not Apple-notarized (downloaded via `curl`, they run without Gatekeeper prompts).
- **Upgrades (local hub):** Installing a newer `confighub mini` package migrates an existing local hub's PostgreSQL schema in place on the first `cub mini` command, preserving all Spaces, Units, revisions, waiting orders, and attestations.
- **Backups and exit:** Export any app back to plain files with `cub mini copy APP --variant live --to-dir DIR`, or hand a GitOps app back to Git with `cub mini back-to-git APP --variant live --repo DIR` without restarting pods.

## Stopping and removing a local hub

- **Stop processes (keep data):** `cub mini stop`
- **Remove everything (processes, PostgreSQL data, and local hub state):**

  ```sh
  cub mini uninstall --delete-data
  ```

For removing the plugin and its local record as well, see [going back](journeys/going-back.md).
