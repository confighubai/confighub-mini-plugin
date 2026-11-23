# Attach an existing app: try previews while keeping staging and production safe

Connect an app you already have without rewriting its config files or changing how it deploys. ConfigHub keeps separate `base`, `staging`, and `live` (production) copies in a local hub, lets your agent experiment in a preview or staging, and holds production changes for your approval.

---

## Run a preview of my app

**You** choose the app, ask for a change and open the address. **Your agent** changes the preview setting, checks the response and leaves it running. Your working files and both staging and production settings stay as they were.

**Prerequisites:** The [Claude Code plugin](../../README.md#install) or [Codex setup](../codex.md#set-it-up), an app that reads a setting from `.env`, `.env.local` or `.env.development`, and `lsof` installed. The preview runs your app the way it already runs: the `dev` or `start` script in `package.json`, the `web:` line of a `Procfile`, or a command you give. Next.js, Vite and Python apps work this way, and your files are not changed. The app has to listen on `127.0.0.1` or take the address and port it is given; a command that listens on every network address is refused, and you can give it after `--` with an option that keeps it on this machine. No app yet? Ask your agent to make a small sample app first.

1. In the app folder, ask for the change you want:
   ```text
   Try “Evening collection” as the heading. Keep the usual board as it is. I’d like to open the preview again tomorrow.
   ```
   Pick a setting your app already reads. Say **yes** when your agent offers to attach the app locally. The first download can take a minute.
2. Open the address your agent gives you in this chat. It has checked the page with the app’s preview settings. Codex may ask for permission to run the setup command or read the local address.
3. Later, open a fresh chat in the same app folder and ask **“Where’s the preview, and what does it say?”** Your agent checks the running process and reads the page. You can ask it to stop the preview when you’re finished.

You can try a change you care about the same way. For example, ask a queue app to try a larger batch before a busy weekend. With 360 sample jobs, our usual app returned three batches of 120. The preview returned one batch of 240 and one of 120. [What we checked](../evidence.md#trying-a-larger-batch-before-shipping-it).

[See what Claude Code and Codex returned](../evidence.md#the-preview-in-the-chat-that-said-yes).

### Compare with last Friday

Once the hub has saved production settings from Friday or earlier, ask **“Open Friday’s production settings as a new preview.”** Your agent runs the current checkout with the settings the hub held for production at the end of the most recent completed Friday in your timezone. If you attached the app on Saturday, its history starts on Saturday. You can still preview a change to today’s settings. Otherwise, open the historical preview and compare it with your usual app. In a fresh chat in the same folder, ask **“Where’s the preview I left running, and what does it show?”** [What the two-starter app served](../evidence.md#opening-fridays-production-settings).

---

## What you do

Works with any `.env`, Compose, Terraform, or Kustomize repository:

1. **Install the plugin** ([README](../../README.md#install)).
2. **Open Claude Code in your app’s repository** and ask:
   ```text
   Attach ConfigHub to this existing app: keep my staging and production values as they are, and require my approval before production changes.
   ```
3. **Review production’s starting settings** when you want to use them. Paste the exact approval command the agent gives you into your own terminal. Check the named order and values before you confirm. With a Kustomize overlay that defines every production value, there may be no pending change.
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
