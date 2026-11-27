# An app on Heroku

If your app runs on Heroku, ConfigHub gives you what a Heroku pipeline gives you, with your coding agent doing the work: a staging copy of the app's config vars that your agent changes at once, and a production copy that changes only when you approve. Approving puts the change live on your Heroku app.

Moving off Heroku to Fly or Vercel right now? Jump straight to the [zero-hub read-only compare](#read-only-compare-first-no-hub-installed). To try staging + approval locally with a stand-in and no account, follow [the Heroku walkthrough](../examples/walkthroughs/starter-heroku.md).

## Connect and approve with two commands

You need Claude Code or Codex CLI with the [ConfigHub plugin](../README.md#install), `heroku login`, and a folder with a Heroku Git remote (`heroku git:remote -a APP`).

1. **Connect:** Run `/confighub:staging` in Claude Code (or `/confighub:staging --heroku APP` if there is no Git remote).
   - First run downloads and starts the local hub (~65 MB, two processes on `127.0.0.1`; remove anytime with `cub mini uninstall --delete-data`).
   - Reads production (and pipeline staging, if present) config vars into the hub. Writes nothing to Heroku.
2. **Propose:** Open a fresh Claude Code session (scoped agent key) and ask for a change, e.g. `Raise WEB_CONCURRENCY to 8 in production. Checkout times out under load.` Staging updates at once; production waits.
3. **Approve:** In your terminal, run `cub mini approve APP` (full path printed by step 1). Confirm once that approved settings go to Heroku; ConfigHub sets the changed vars (Heroku restarts the app on change).

## Send staging to your staging app

Run `cub mini deliver APP --staging` once in your terminal and answer `y`. After that, every staging change your agent makes goes to the pipeline's staging app automatically:

- Needs no approval and never targets production.
- Verifies with Heroku that the target is the staging app of your production app's pipeline (refuses any other app, production included).
- Sends only non-secret app config vars (never credentials or add-on vars).
- Skips writing when staging already matches, avoiding unnecessary restarts.

## What stays on Heroku

- **Credentials:** Passwords, tokens, and keys are never read into the hub or sent.
- **Add-on settings:** Managed add-on vars (`DATABASE_URL`, `REDIS_URL`, etc.) stay on Heroku.
- **Heroku's own settings:** `HEROKU_*` vars stay untouched.

Step 1 reports how many settings it left on Heroku.

## Moving production to Fly or Vercel

### Read-only compare first (no hub installed)

Diff Heroku against Fly or Vercel without installing a hub or changing either host:

```sh
cub mini deliver --compare --heroku HEROKU_APP --fly FLY_APP
# or, after `vercel link` in the app's folder:
cub mini deliver --compare --heroku HEROKU_APP --vercel PROJECT
```

Writes nothing, never prints credential values, and prints missing/differing non-secret vars plus a safe credential copy command.

### Managed move with approvals (with the hub)

From a connected app (`APP`), preview the move plan first (writes nothing):

```sh
cub mini deliver APP --fly FLYAPP --compare
# or, after `vercel link`:
cub mini deliver APP --vercel PROJECT --compare
```

The plan lists:
1. Non-secret settings to send, noting which are missing or differ on the target host.
2. Settings left on Heroku by name only (credentials, add-on vars, `HEROKU_*`).
3. One terminal command to copy credentials directly from Heroku to the new host before cutover:
   - Reads each value via `heroku config:get` and passes it to `fly secrets set` or `vercel env add --sensitive`.
   - Stops immediately if any read fails so no credential is set empty.
   - Excludes add-on vars (`DATABASE_URL`, etc.) since the new host needs its own database.
4. Confirmation that the Heroku app stays running until you remove it.

Run the same command without `--compare` in your terminal and confirm `y`:
- **Fly:** updates every Machine one at a time; stopped standby Machines stay stopped.
- **Vercel:** sets production env vars and deploys the folder's code to production.
- Future approved production changes go to the new host (agents cannot name the new host or confirm); staging stays on the Heroku staging app.

## Other commands

- `cub mini deliver APP --compare` — read-only drift check against Heroku.
- `cub mini deliver APP` — re-apply last approved settings (no-op if unchanged).
- `cub mini deliver APP --staging --compare` — read-only drift check against staging.
- `cub mini rollback APP --reason "Why"` — propose undoing the last approved change.

<details>
<summary><strong>Limits &amp; testing</strong></summary>

### What it does not do yet
- An app outside a pipeline has no staging app, so staging stays in the hub.
- Removing a setting in the hub does not delete it from Heroku.

### Testing
**Never run against a real Heroku or Fly account.** Each release runs the full path against CLI stand-ins:

| Path | Covered against stand-ins |
|---|---|
| Pipeline connect & approval | Read-only connect, staging edit, production wait, approve, idempotent re-deliver, manual drift, rollback |
| Staging delivery | Agent refused first confirmation; auto-delivery on staging edits |
| Move to Fly / Vercel | Heroku + `flyctl` stand-ins with 2-Machine Fly app; read-only `--compare` + safe copy line |
</details>
