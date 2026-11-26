# An app on Heroku

If your app runs on Heroku, ConfigHub gives you what a Heroku pipeline gives you, with your coding agent doing the work: a staging copy of the app's config vars that your agent changes at once, and a production copy that changes only when you approve. Approving puts the change live on your Heroku app.

**Moving off Heroku to Fly or Vercel right now? Run a read-only compare first with no hub installed:**

```sh
cub mini deliver --compare --heroku HEROKU_APP --fly FLY_APP
# or, after vercel link in the app's folder:
cub mini deliver --compare --heroku HEROKU_APP --vercel PROJECT
```

That writes nothing to Heroku, Fly, or Vercel, installs no hub, never prints credential values, and prints the missing/differing non-secret vars plus a safe one-line credential copy command.

To try the full staging + approval flow on your computer first, with a stand-in for Heroku and no account, follow [the Heroku walkthrough](../examples/walkthroughs/starter-heroku.md).

## Connect and approve with two commands

You need Claude Code or Codex CLI with the [ConfigHub plugin](../README.md#install), the Heroku CLI signed in (`heroku login`), and your app's folder with a Git remote to the Heroku app, as `heroku git:remote -a APP` makes.

1. **Connect.** In the app's folder, type `/confighub:staging` in Claude Code. The first time, it downloads and starts the local hub (~65 MB, two local processes on `127.0.0.1` only; remove everything anytime with `cub mini uninstall --delete-data`). It reads the production app's config vars into the hub. If the app is in a pipeline, staging starts from the staging app's config vars. Nothing on Heroku changes. If the folder has no Heroku remote, name the app once: `/confighub:staging --heroku APP`.
2. **Ask for a change.** Open a fresh Claude Code session in the folder, so your agent works on a key of its own, and ask for the change you want, for example: `Raise WEB_CONCURRENCY to 8 in production. Checkout times out under load.` Your agent can change staging at once. A production change waits for you.
3. **Approve it.** In your own terminal, run `cub mini approve APP`. `cub` is ConfigHub's command-line tool. `/confighub:staging` downloads it with the hub, and the last lines it prints give this command with the full path to `cub`, so you can paste it as it is. It shows the change and asks. The first time, it also asks once whether approved settings should go to your Heroku app from now on. It then sets the change on the app. Heroku restarts the app whenever its config vars change.

From then on, each production change your agent proposes is one command and one decision for you: `cub mini approve APP`.

## Send staging to your staging app

Staging changes can reach the staging app in your pipeline too. In your own terminal, run `cub mini deliver APP --staging` once. It asks whether staging's settings should go to your staging app from now on, names that app, and says it never sends to production. Answer `y`, and staging is sent at once.

From then on, each staging change your agent makes is sent to the staging app in the same command, with no step for you. Staging needs no approval. It is sent by the same rules as production: only the settings your app set, never a credential or an add-on's setting, and nothing when the staging app already holds it, so Heroku does not restart the app for nothing. Before writing, ConfigHub checks with Heroku that the app is the staging app of your production app's pipeline. It refuses any other app, production included.

## What stays on Heroku

- **Credentials.** A setting that holds a password, token or key is never read into the hub and never sent.
- **Add-on settings.** Settings an add-on sets, such as `DATABASE_URL` or `REDIS_URL`, stay as Heroku keeps them.
- **Heroku's own settings.**

The first step says how many settings it left on Heroku.

## Moving production to Fly or Vercel

### Read-only compare first (no hub installed)

To see what is missing or different on Fly or Vercel before installing any hub or changing either host, run the standalone read-only compare from the plugin:

```sh
cub mini deliver --compare --heroku HEROKU_APP --fly FLY_APP
```

For Vercel, run `vercel link` in the app's folder first, then:

```sh
cub mini deliver --compare --heroku HEROKU_APP --vercel PROJECT
```

This needs no hub, writes nothing to Heroku, Fly, or Vercel, never prints credential values, and prints the exact missing/differing non-secret vars plus the safe one-line credential copy command below.

### Managed move with approvals (with the hub)

When you are ready for ConfigHub to send production's approved settings to Fly or Vercel and gate future changes behind approval, first preview the plan from your connected app (`APP`). It writes nothing:

```sh
cub mini deliver APP --fly FLYAPP --compare
```

For Vercel, first run `vercel link` in the app's folder, choosing the project, because Vercel deploys the code in that folder. Then:

```sh
cub mini deliver APP --vercel PROJECT --compare
```

The plan says:

1. which settings the hub sends there, and which of them are missing or different there;
2. what stays on Heroku and the hub never sends, by name only: credentials, add-on settings and Heroku's own;
3. one line to run in your own terminal before production moves, which copies the credentials straight from Heroku to the new host, so the hub never sees them. Each value is read with `heroku config:get` and passed to `fly secrets set` or `vercel env add`, and the line stops if a read fails, so no credential is set empty. Add-on settings such as `DATABASE_URL` are left out, because the new host needs its own database;
4. that the Heroku app keeps running until you remove it.

Then run the same command without `--compare`, in your own terminal. It asks your yes. On Fly, it sends production's settings to every Machine of the app, one at a time, and a stopped standby Machine stays stopped. On Vercel, it sets them on the project's production and deploys the folder's code to production. From then on, each production change you approve goes to the new host. Your agent cannot name the new host or say yes. Staging still goes to the Heroku staging app.

## Other commands

- `cub mini deliver APP --compare` writes nothing and says whether the Heroku app holds what you approved, naming any setting that differs.
- `cub mini deliver APP` sends what was last approved again. When nothing differs, it writes nothing, and Heroku does not restart the app.
- `cub mini deliver APP --staging --compare` writes nothing and says whether the staging app holds what staging has.
- `cub mini rollback APP --reason "Why"` proposes undoing the last approved change. Once you approve it, it goes live the same way.

## What it does not do yet

- An app in no pipeline has no staging app, so its staging stays in the hub.
- A setting removed in the hub is not removed from Heroku.

## Testing

Each release runs this path against a stand-in for the `heroku` command: connecting from an app in a pipeline, a staging change, a production change that waits, approval, a second delivery that writes nothing, a setting changed on Heroku by hand, and a rollback. Sending staging to the staging app, the agent's key being refused the first yes for it, and a staging change carried on in the same command ran the same way. The move to Fly ran the same way, against stand-ins for `heroku` and `flyctl`, with a Fly app of two Machines. None of it has run against a real Heroku or Fly account.
