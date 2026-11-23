# An app on Heroku

If your app runs on Heroku, ConfigHub gives you what a Heroku pipeline gives you, with your coding agent doing the work: a staging copy of the app's config vars that your agent changes at once, and a production copy that changes only when you approve. Approving puts the change live on your Heroku app.

## Connect and approve with two commands

You need Claude Code or Codex CLI with the [ConfigHub plugin](../README.md#install), the Heroku CLI signed in (`heroku login`), and your app's folder with a Git remote to the Heroku app, as `heroku git:remote -a APP` makes.

1. **Connect.** In the app's folder, type `/confighub:staging` in Claude Code. It reads the production app's config vars into the hub. If the app is in a pipeline, staging starts from the staging app's config vars. Nothing on Heroku changes. If the folder has no Heroku remote, name the app once: `/confighub:staging --heroku APP`.
2. **Ask for a change.** Open a fresh Claude Code session in the folder, so your agent works on a key of its own, and ask for the change you want, for example: `Raise WEB_CONCURRENCY to 8 in production. Checkout times out under load.` Your agent can change staging at once. A production change waits for you.
3. **Approve it.** In your own terminal, run `cub mini approve APP`. `cub` is ConfigHub's command-line tool. `/confighub:staging` downloads it with the hub, and the last lines it prints give this command with the full path to `cub`, so you can paste it as it is. It shows the change and asks. The first time, it also asks once whether approved settings should go to your Heroku app from now on. It then sets the change on the app. Heroku restarts the app whenever its config vars change.

From then on, each production change your agent proposes is one command and one decision for you: `cub mini approve APP`.

## What stays on Heroku

- **Credentials.** A setting that holds a password, token or key is never read into the hub and never sent.
- **Add-on settings.** Settings an add-on sets, such as `DATABASE_URL` or `REDIS_URL`, stay as Heroku keeps them.
- **Heroku's own settings.**

The first step says how many settings it left on Heroku.

## Other commands

- `cub mini deliver APP --compare` writes nothing and says whether the Heroku app holds what you approved, naming any setting that differs.
- `cub mini deliver APP` sends what was last approved again. When nothing differs, it writes nothing, and Heroku does not restart the app.
- `cub mini rollback APP --reason "Why"` proposes undoing the last approved change. Once you approve it, it goes live the same way.

## What it does not do yet

- Staging changes stay in the hub. They are not sent to the staging app in your pipeline.
- A setting removed in the hub is not removed from Heroku.

## Testing

Each release runs this path against a stand-in for the `heroku` command: connecting from an app in a pipeline, a staging change, a production change that waits, approval, a second delivery that writes nothing, a setting changed on Heroku by hand, and a rollback. It has not been run against a real Heroku account.
