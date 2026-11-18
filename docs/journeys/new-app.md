# Build a new app in Claude Code (with staging, preview, and gated production)

Describe the app you want, and let Claude Code set up both the code and a local ConfigHub with separate `staging`, `preview`, and `live` (production) configurations.

## Quick start (4 steps)

1. **Install the plugin** ([README](../../README.md#install)) and open a fresh `claude` session in an empty Git folder:
   ```sh
   mkdir greeter && cd greeter && git init -q && claude
   ```
2. **Ask for your app with “using ConfigHub”:**
   ```text
   Build me a small web service using ConfigHub, with a health endpoint, a configurable greeting, and a staging and a production setup.
   ```
3. **Approve production’s starting settings** in your own terminal using the exact full-path command Claude prints:
   ```sh
   ~/.confighub/mini/.../bin/cub mini approve greeter-base/adopt
   ```
   *(Add that `bin` directory to your `PATH` if you want to run `cub` directly without the full path.)*
4. **Commit your app** along with `.confighub-app`.

From the next session onward, you don’t need to say “using ConfigHub”—sessions in this folder automatically run on the app’s scoped agent key ([how ordinary requests work](../agent-workflow.md)).

---

## Try a preview & change settings later

### Changing the app later

Ask Claude for changes in plain words:

1. **Test in a running preview first:**
   ```text
   Try a warmer greeting in preview and show me what the running app serves.
   ```
   `staging` and `live` stay untouched while you inspect the local preview URL.
2. **Promote to staging & propose for production:**
   Ask Claude to make the change the shared default (or edit files normally—Claude uploads via `cub mini upload`).
   - **`staging`** takes shared changes immediately (unless `.env.staging` overrides that key).
   - **`live` (production)** waits until you run `cub mini approve` in your own terminal (`cub mini waiting` lists pending orders).
   - **Overrides win:** Any key set explicitly in `.env.production` stays production’s own unless `.env.production` itself is updated.
   - **Refusals are remembered:** `cub mini refuse APP-base/ORDER --reason "WHY"` blocks the change and warns future agent sessions why that value was rejected.

## A second app from the first

Open a **new folder outside the first app’s repo** (the first app’s scoped session key cannot create new apps) and start Claude Code:

```sh
mkdir catalog && cd catalog && git init -q && claude
```

Type `/confighub:start-from greeter` or ask: **“Build a second app like `greeter`.”**
- Claude runs `cub mini adopt catalog --pattern greeter`.
- `catalog` inherits `greeter`’s shared settings and reasons immediately in staging, keeps its own app-specific settings separate, and requires its own production approval.
- Later improvements on `greeter` can flow to `catalog` via `cub mini upgrade greeter-base/app` ([walkthrough with every command](../../examples/walkthroughs/story-18-dev-intent.md)).

## What it takes & what you have

- **Download:** First use downloads the local hub ([size](../install-mini.md#the-current-release)) into `~/.confighub/mini` and runs ConfigHub + PostgreSQL on `127.0.0.1` only. **No Docker, no account.**
- **Files added:** `.confighub-app` (commit this) and `.claude/settings.local.json` (auto-excluded via `.git/info/exclude` so Claude sessions in this repo use the scoped agent key).
- **Connecting real deployment:** Local setup prepares hub copies and local runs; connect delivery when deploying to a cloud host, VM, or cluster ([where the app runs](../agent-workflow.md#where-the-app-runs) · [verify live state](../approvals.md#verify-the-result)).

**Inspect anytime:**
- In Claude Code: `/confighub:why GREETING` (every change, prompt, and agent rationale).
- In Terminal: `cub mini receipts APP-live` (who changed, why, who approved) or `cub mini receipts APP --setup`.

Next steps: [Your first hour](../../examples/walkthroughs/story-13-first-hour.md) · [`cub mini` tour](../../examples/walkthroughs/tool-cub-mini.md) · [Add Postgres/Redis/S3](../from-plugin-to-confighub.md#a-service-the-app-needs) · [Live secrets agents can't read](../from-plugin-to-confighub.md#a-secret-for-live-that-no-agent-can-read) · [Move to a shared team hub](../from-plugin-to-confighub.md#step-3-your-organizations-confighub) · [Going back / recovery](going-back.md) · [Glossary](../README.md#words).

---

<details>
<summary><strong>Under the hood: what the agent runs during Step 2</strong></summary>

1. Writes the app and `.env` (shared), `.env.staging`, and `.env.production`.
2. Runs `confighub mini get` if no local hub is running (verifies release checksums, starts the hub on loopback, signs `cub` in; auto-start in other folders stays off unless you enable it).
3. Runs `cub mini adopt`, creating `APP-base`, `APP-staging`, and `APP-live` plus baseline `pattern-web` rules (such as rejecting secret-shaped values in plain settings; separate from optional [starters](../starters.md)).
4. Runs `cub mini require-approval APP --variant live --agent APP-agent --try preview`, creating the preview slot and scoping the folder's agent key.
5. Prints the exact `cub mini approve APP-base/adopt` command for your terminal. Until you approve, `cub mini pull`, `pull-key`, and `deploy-from-hub` refuse production delivery.
</details>

<details>
<summary><strong>Troubleshooting (<code>cub: command not found</code>, restarts, secrets, Linux)</strong></summary>

- **`cub: command not found`:** Paste the full binary path printed by the agent, or add it to your shell: `export PATH="$HOME/.confighub/mini/confighub-mini-VERSION-OS-ARCH/bin:$PATH"`.
- **Hub stopped after reboot:** Type `/confighub:staging` in Claude Code in the app folder (or ask the agent to start the hub); all data and pending orders persist.
- **Agent wrote a bash setup script or asked for login:** Confirm the plugin is active with `claude plugin list`, start a fresh session, and include `"using ConfigHub"` in your prompt.
- **`reads no settings adopt can find`:** Ask the agent to move configurable values into `.env` (or rename custom env files like `api.env` to `.env`).
- **Missing value in `live`:** Shared `.env` values reach `live` only after `cub mini approve APP-base/adopt` (check `cub mini waiting`).
- **Passwords / tokens skipped:** Use `cub mini secret set APP KEY --variant live --change-desc "WHY"` in your own terminal.
- **Alpine Linux:** Requires glibc; Alpine (`musl`) is unsupported ([install details](../install-mini.md)).
</details>
