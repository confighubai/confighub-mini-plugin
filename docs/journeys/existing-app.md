# Attach an existing app: try previews while keeping staging and production safe

Connect an app you already have without rewriting its config files or changing how it deploys. ConfigHub keeps separate `base`, `staging`, and `live` (production) copies in a local hub, lets your agent experiment in a preview or staging, and holds production changes for your approval.

---

## Run a preview of my app

Try a setting change in an isolated local preview process over HTTP while your working files, staging, and production stay untouched.

**Prerequisites:** The [Claude Code plugin](../../README.md#install) or [Codex setup](../codex.md#set-it-up). For automatic local HTTP process management, use a Node.js (20.6+) app whose `npm start` runs `node` directly (e.g. `node server.js` listening on `127.0.0.1`) and reads a visible setting from `.env` (plus `lsof` installed). *(Using Next.js, Vite, Python, or Rails? Use [the general attach steps](#what-you-do) and run your usual dev server with `cub mini try` settings, or ask your agent to scaffold a quick sample greeting app first.)*

1. **Attach the app** (downloads and starts the local hub on first use, no account needed). Open the Git folder in your coding agent and ask:
   ```text
   Attach ConfigHub to this app so I can try a preview.
   ```
2. **Reopen on the app’s scoped session:**
   - **Claude Code:** Close and reopen `claude` in the same folder (`.claude/settings.local.json` scopes it automatically).
   - **Codex CLI:** Run the `run-codex` command printed at the end of Step 1.
3. **Start a preview:**
   ```text
   Try a warmer greeting in preview.
   ```
   *(Substitute any visible `.env` setting your app renders.)* Open the local `http://127.0.0.1:...` URL your agent returns—it serves the new value while your original app and files stay unchanged.
4. **Verify across sessions:** Close and reopen the app session, then ask:
   ```text
   Is my preview still running? What does it serve?
   ```
   Your agent locates the running preview (`cub mini preview --status`) and checks its response. Ask to stop the preview (`cub mini preview --stop`) when finished. ([Measured clean-profile Mac run](../evidence.md#the-default-preview-on-plugin-0992-and-mini19))

---

## What you do

Works with any `.env`, Compose, Terraform, or Kustomize repository:

1. **Install the plugin** ([README](../../README.md#install)).
2. **Open Claude Code in your app’s repository** and ask:
   ```text
   Attach ConfigHub to this existing app: keep my staging and production values as they are, and require my approval before production changes.
   ```
3. **Approve production’s starting baseline** in your own terminal using the exact full-path command the agent prints:
   ```sh
   ~/.confighub/mini/.../bin/cub mini approve APP-base/adopt
   ```
   *(Tip: add that `bin` directory to your `PATH` if you want to type `cub mini ...` directly. For Kustomize overlays that already define every production value, nothing waits for approval.)*
4. **Commit `.confighub-app`** (the pointer linking your repo to the hub).

### Supported configuration files

| Your app keeps settings in | Shared `base` | `staging` overrides | `live` (production) overrides |
|---|---|---|---|
| Env / Compose | `.env`, `app.env`, `compose.yaml`, or `.env.example` | `.env.staging` | `.env.production` *(non-secret values only)* |
| Terraform | `common.tfvars` | `staging.tfvars` | `prod.tfvars` |
| Kustomize | `base/` | `overlays/staging` | `overlays/prod`, `production`, `live`, or Argo CD target |
| Helm chart values | Use [`cub helm install`](../your-own-chart.md) instead of `adopt` (see [Helm values](#helm-values)) | — | — |

> **Never put secrets or passwords in `.env.production`.** Values that look like credentials are automatically skipped. Store secrets in your host (Vercel, Fly, Vault) or via `cub mini secret set` in your own terminal so no agent key can read them ([secrets guide](../from-plugin-to-confighub.md#a-secret-for-live-that-no-agent-can-read)).

## What it takes

- **Local hub download:** Downloaded once into `~/.confighub/mini` ([package size](../install-mini.md#the-current-release)); runs ConfigHub and PostgreSQL as two local `127.0.0.1` processes. No Docker, no account.
- **Repository footprint:** Your existing config files are **not modified**. Only `.confighub-app` is tracked in Git; `.claude/settings.local.json` (which scopes Claude sessions to the agent key) is added to `.git/info/exclude`.
- **Kustomize requirement:** Needs `kubectl` or `kustomize` on `PATH` to render overlays.

## Changing the app later

Edit files with your agent as usual. Your agent uploads changes with `cub mini upload APP-FOLDER --component APP --change-desc "WHY"`:
- **`staging`** updates immediately.
- **`live` (production)** stays unchanged and creates a pending change order. Run `cub mini waiting` in your terminal to inspect, then `cub mini approve` or `cub mini refuse APP-base/ORDER --reason "WHY"`.
- **Connected deployment:** Running services read approved `live` values once you connect delivery ([where the app runs](../agent-workflow.md#where-the-app-runs) · [Argo CD / Flux repos](gitops-app.md) · [verify live state](../approvals.md#verify-the-result)).

## What you have now & what to try next

You have unchanged source files, `base` / `staging` / `live` copies in your local hub, a scoped `APP-agent` key that can propose but never approve production, and a local prompt history record.

Try next in the same repo:
1. Ask the agent to raise a limit for production → run `cub mini waiting` in your terminal to approve or refuse it.
2. Type `/confighub:why SETTING_NAME` in Claude Code to see every change and prompt behind it.
3. Run `cub mini receipts APP --setup` to inspect copies, keys, rules, and overrides.

More walkthroughs: [Your first hour](../../examples/walkthroughs/story-13-first-hour.md) · [Staging-only memory bump](../../examples/walkthroughs/story-20-noors-staging.md) · [Web starter](../../examples/walkthroughs/starter-web.md) · [Argo CD](../../examples/walkthroughs/starter-kustomize-argocd.md) · [Flux](../../examples/walkthroughs/starter-kustomize-flux.md) · [Going back / uninstall](going-back.md) · [Glossary](../README.md#words).

---

## Under the hood & edge cases

<details>
<summary><strong>What the agent runs during setup (<code>adopt --dry-run</code> &amp; <code>pattern-web</code>)</strong></summary>

The agent starts the local hub if none is running (auto-start in other folders stays off unless you opt in: [details](../agent-workflow.md#a-hub-that-starts-by-itself-only-if-you-say-yes)). It previews with `cub mini adopt --dry-run` before writing anything:

```text
Nothing was changed. Without --dry-run, ConfigHub would keep app's settings, from common.tfvars, with staging.tfvars for staging and prod.tfvars for production:
  It would keep three copies of them: app-base, the shared settings that staging and production start from; app-staging; and app-live, for production.
  First it would make a starter pattern, pattern-web: default settings for a small web service, and rules that each change must pass (replicas-limit, not-public, log-level, no-secret-values).
  Your settings that differ from the defaults in pattern-web/web-service: cpu=512, log_retention_days=14, memory_mb=2048. A new version of those defaults will not overwrite them.
  Staging would have the shared settings at once, with its own settings from staging.tfvars: desired_count=1, env=staging.
  Production would have its own settings from prod.tfvars at once: desired_count=3, env=prod. It would take the shared settings only after you approve them.
```

It then runs `cub mini adopt` and `cub mini require-approval APP --variant live --agent APP-agent`. `pattern-web` provides baseline rules (like blocking secret-shaped values) without overwriting any value you already set; it is separate from optional [starters](../starters.md).
</details>

## What adopt refuses in a Kustomize repository

<details>
<summary><strong>Supported vs. refused Kustomize overlay fields</strong></summary>

Each hub copy holds `base/` resources with overlay value overrides. Overlays that alter resource structure rather than values are refused cleanly before anything is written:

- **Carried:** `namespace`, labels, annotations, `images`, `replicas`, scalar/element value patches, `namePrefix`/`nameSuffix` (including references), fractional values (`cpu: 0.5`), and type changes.
- **Refused (with exact file and field named):** Adding or omitting resources (`resources`, `components`, `configMapGenerator`), deleting fields, changing list lengths, adding empty maps, `helmCharts`, `generators`, `transformers`, `validators`, and remote URL bases.

`adopt` renders each overlay with `kustomize` and verifies byte-level parity with the hub copy, rolling back cleanly if anything differs.
</details>

## Helm values

<details>
<summary><strong>Managing third-party or custom Helm charts</strong></summary>

`cub mini adopt` does not import Helm `values.yaml` directly. Use [cub-helm](https://github.com/confighub/cub-helm) (`cub helm install NAME CHART --version V --values my-values.yaml`) in your terminal to preserve custom values and reasons across upstream chart upgrades ([your own Helm chart](../your-own-chart.md) · [Story 7 walkthrough](../../examples/walkthroughs/story-07-next-version.md)).
</details>

## If something goes wrong

<details>
<summary><strong>Troubleshooting common messages</strong></summary>

- **`reads no settings adopt can find`:** Your env file uses a custom name (like `api.env`). Either rename it to `.env` or run `cub mini upload FOLDER --variant live --target none`.
- **A secret-looking value was skipped:** Keep secrets out of `.env` and set them with `cub mini secret set` in your own terminal.
- **Values in the hub don't match files:** Re-run `cub mini adopt APP-FOLDER --dry-run` or export hub copies with `cub mini copies APP --to DIR`.
- **Agent asks for production write access or your login:** Say **no**—that would bypass the approval gate. Paste the `CLAUDE.md` / `AGENTS.md` instructions printed by `cub mini require-approval` so the agent proposes via change orders instead.
- **Undo everything:** Your original files were never modified. Follow [going back](going-back.md) and delete `.confighub-app`.
</details>
