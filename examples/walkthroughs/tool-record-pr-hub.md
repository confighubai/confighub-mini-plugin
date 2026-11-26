<!-- walkthrough
id: tool-record-pr-hub
starts_with: both
needs: [Git, cub with cub mini, a local or self-hosted ConfigHub hub]
budget_seconds: 180
-->
# Record your existing pull-request flow in a self-hosted hub with SSO

For a platform team that runs Kubernetes with GitOps (Argo CD or Flux) and reviews every configuration change in pull requests. You keep Git, branch protection, CODEOWNERS, and your GitOps controllers exactly as they are. Adding `cub mini record-pr` (or three optional inputs on the [PR review GitHub Action](../../review/README.md)) records each pull request's rendered configuration diff, reasons, and GitHub approvers as an immutable `PullRequestReview` attestation in a ConfigHub hub — self-hosted in your own cluster behind your company's OIDC or SAML single sign-on (SSO), or tried first on a local hub on your laptop.

A **hub** is a ConfigHub server and database that stores configuration, the reason for each value, and an immutable record of who approved each change.

## Quick start

You need: a GitOps repository on GitHub, and a ConfigHub hub (self-hosted in your cluster behind corporate SSO, or a local hub to try first).

| | By hand | Ask your agent |
|---|---|---|
| Sign in (humans) | `cub auth login --server https://confighub.internal.example.com` (via corporate OIDC/SAML SSO) | You sign in yourself; CI uses a scoped service account token (`CONFIGHUB_PR_RECORDER_TOKEN`) granted write access only to the audit Space |
| Create audit Space | `cub space create platform-audit` | "Create a `platform-audit` Space for recording pull request reviews." |
| Record a PR | `cub mini record-pr --space platform-audit --repo ORG/REPO --pr 412 --base $BASE --head $HEAD --from-github` (pulls verified `APPROVED` reviewers from GitHub API via `GITHUB_TOKEN`) | "Add `hub-url`, `hub-space`, and `hub-token` inputs to our `confighubai/confighub-mini-plugin/review@v0` workflow so each PR is recorded in `platform-audit` with GitHub API approvers." |
| Backfill recent PRs | `cub mini record-pr --space platform-audit --repo ORG/REPO --backfill 20` | "Backfill the last 20 merged configuration commits into Space `platform-audit` so audit queries work on day one." |
| Query the audit trail | `cub mini record-pr --space platform-audit --list` | "List the pull request configuration reviews recorded in Space `platform-audit`." |

Credentials never leave the runner: secret values in changed files or commit messages are redacted before writing to the hub. Code-only pull requests write nothing, and re-running on the same pull request and commit writes no duplicate attestation. For a security review of the hub server itself (network surface, PostgreSQL storage, upgrades, and teardown), see [For a security review: the ConfigHub hub](../../docs/security-hub.md).

Without ConfigHub: audit questions ("which PR raised `ingress` replicas in `us-east`, why, and who approved it?") mean searching GitHub comments and commit logs across repositories by hand, where comments can be edited or deleted.

## Deeper dive

The rest of this page shows the full steps to test `cub mini record-pr` on a local hub, wire it into GitHub Actions against a self-hosted hub with SSO, and verify that credentials stay out of the hub.

<details>
<summary>Show the full walkthrough</summary>

## Human

For a platform engineer testing the pull-request audit trail locally before pointing it at a self-hosted hub.

### What you need

Git, and `cub` with the local hub ([install the local hub](../../docs/install-mini.md)) or a self-hosted ConfigHub hub behind your company's SSO.

### Steps

1. Sign in to your self-hosted ConfigHub hub with your company's SSO (or install a local hub with `cub mini install` to test locally) and create an audit Space:
   <!-- run: setup -->
   ```sh
   cub space create platform-audit
   ```

2. In a GitOps repository checkout, preview what would be recorded for a pull request without writing anything to the hub:
   <!-- run: dry-run -->
   ```sh
   cub mini record-pr --space platform-audit --repo acme/gitops-fleet --pr 412 \
     --base main --head HEAD --author platform-bot --approved-by sec-lead,sre-oncall --dry-run
   ```

3. Record the pull request review into the hub as an immutable `PullRequestReview` attestation:
   <!-- run: record -->
   ```sh
   cub mini record-pr --space platform-audit --repo acme/gitops-fleet --pr 412 \
     --base main --head HEAD --author platform-bot --approved-by sec-lead,sre-oncall
   ```

   Running the same command again for the same PR and head commit prints `already recorded in Space platform-audit; nothing was written.`

4. Query the recorded pull requests in that Space:
   <!-- run: list -->
   ```sh
   cub mini record-pr --space platform-audit --list
   ```

5. In GitHub Actions, pass the three optional inputs to the [configuration review Action](../../review/README.md). The Action passes `GITHUB_TOKEN` and `--from-github` so `cub mini record-pr` fetches verified `APPROVED` reviewers directly from the GitHub API (ignoring comment-only or superseded reviews):
   ```yaml
   - uses: confighubai/confighub-mini-plugin/review@v0
     with:
       hub-url: https://confighub.internal.example.com
       hub-space: platform-audit
       hub-token: ${{ secrets.CONFIGHUB_PR_RECORDER_TOKEN }}
   ```

   To deploy the hub in your own Kubernetes cluster behind your OIDC IdP (such as Dex, Okta, or Entra ID), run the ConfigHub hub `Deployment` and `Service` in a dedicated `confighub` namespace behind your ingress/TLS termination, point `CONFIGHUB_AUTH_ISSUER` and `CONFIGHUB_TOKEN_EXCHANGE_AUDIENCE` at your IdP, and issue a scoped service account token for the audit Space.

   To undo: remove those three inputs from your workflow file. Git, branch protection, and Argo CD or Flux keep working unchanged.

## Agent

Never pass or print `CUB_TOKEN` or any secret value. When asked to check what pull requests were recorded, run `cub mini record-pr --space SPACE --list` or `cub mini record-pr ... --dry-run`. Do not create or modify audit Spaces or service accounts in a production hub unless the person explicitly asks and approves.

## Testing

The command was run end to end in a Kubernetes `kind` cluster hosting both a self-hosted ConfigHub v0.11.1 hub (`confighub` namespace) and a live Dex OIDC provider (`oidc` namespace, verifying live OIDC discovery, JWKS, and RS256 ID token issuance). Against a GitOps repository PR changing `Deployment/ingress/spec.replicas` and rotating `API_TOKEN`, `cub mini record-pr --from-github` fetched verified `APPROVED` reviewers (`sec-lead,sre-oncall`) from the GitHub API while excluding a `COMMENTED` reviewer, recorded one `PullRequestReview` attestation with `API_TOKEN (redacted)` and no secret value, skipped idempotently on re-run, backfilled an earlier PR with `--backfill 3`, and listed both PRs with `--list`. Unit tests (`TestRecordPRToHubAndIdempotency`, `TestRecordPRRedactsCredentials`, `TestRecordPRSkipsNonConfigAndDryRunWritesNothing`, `TestRecordPRBackfillRespectsLimitAndIdempotency`, `TestRecordPRApproversFromGitHubAPI`) verify all planted faults (`record-pr-duplicate`, `review-record-credential`, `backfill-ignores-limit`, and `record-pr-unapproved-reviewer`).

<!-- agent-task: dry-run -->
> Show what `cub mini record-pr --dry-run` would record for the latest commit on this branch without writing anything to the hub.
<!-- agent-check dry-run: cub mini record-pr --space platform-audit --repo acme/gitops-fleet --pr 412 --base HEAD~1 --head HEAD --dry-run | grep -q "Would record" -->
<!-- agent-task: record -->
> Record this pull request review into Space `platform-audit` and list the recorded pull requests.
<!-- agent-check record: cub mini record-pr --space platform-audit --list | grep -q "acme/gitops-fleet#412" -->
<!-- next-step boundary=same-tier: check pull requests against the hub | Want branch protection to block a PR whose files differ from the hub's approved copy? -->
<!-- arms: a -->

This proves: a platform team can record every pull request's rendered configuration changes, reasons, and GitHub-API-verified approvers as immutable attestations in a self-hosted Kubernetes hub alongside an OIDC provider without replacing Git or Argo CD/Flux, and without sending credentials.

<!-- results:begin -->

<details><summary>Test results</summary>

26 November 2026, in a Kubernetes `kind` cluster running a self-hosted ConfigHub v0.11.1 hub (`confighub` namespace) alongside a live Dex `v2.41.1` OIDC IdP (`oidc` namespace, verified OIDC discovery, JWKS `kid`, and RS256 ID token for `priya@acme.example.com`). Running `cub mini record-pr --from-github` against the in-cluster hub recorded `acme/gitops-fleet#412` with GitHub-API-verified approvers `sec-lead,sre-oncall` (excluding `COMMENTED` reviewer `commenter`) and `API_TOKEN` redacted; re-running wrote nothing; `--backfill 3` imported `#411` and skipped `#412`; `--list` returned both PRs with zero credentials.

</details>

<!-- results:end -->

</details>
