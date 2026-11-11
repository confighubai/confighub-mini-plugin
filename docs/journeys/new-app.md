# A new app in Claude Code, with a staging copy and a live copy

Ask Claude Code for an app in one sentence, and end with the app, staging configuration that takes your agent's changes at once, and live configuration that changes only when you approve. A second app can start from the first. This page is for someone who makes apps with Claude Code and wants production to change only with their say: an agent can change production settings as easily as staging ones, and a rule in `CLAUDE.md` is only a request.

The app might run on your own machine, on another machine, in CI, on one or many sandbox nodes, in a shared development cluster, or eventually in production. This walkthrough creates staging and live configuration in the hub. Connect the running copies to that configuration using the deployment path for your target ([where the app runs](../README.md#where-the-app-runs)).

## Words used on this page

- **A hub** is one running ConfigHub: a server that keeps your app's settings, with every change, who made it and why.
- **confighub mini** is ConfigHub made small enough to run on your laptop, as two processes: the server and its PostgreSQL database. It needs no Docker, no cluster and no account.
- **`cub`** is ConfigHub's command-line tool. It comes with confighub mini.
- **The base** is the version of the app's settings that changes first. **The staging copy** is made from the base and takes each change at once. **The live copy** holds the settings intended for production. It takes a change only when you approve it. A running service uses those settings once its deployment path is connected.
- **A Space** is where a hub keeps one copy. The app `greeter` has three: `greeter-base`, `greeter-staging` and `greeter-live`.
- **A change order** is a request for a change to reach the live copy. It waits until you **approve** it, or **refuse** it.
- **The agent's key** is a sign-in of the agent's own, for a **service account**: an account for a program rather than a person. On it, the agent can change the base and staging, and propose changes to live. It cannot approve them.

## What it costs

- **Time.** About 75 seconds for the first session on Sonnet, and about two minutes on Opus, including the download. A second app took about 55 seconds.
- **The download.** The first time, the agent downloads confighub mini, 48 to 73 MB, into `~/.confighub/mini`, and starts a hub. The hub listens on this machine only. Nothing else is installed.
- **Your folder.** Besides the app's own files, two files appear: `.confighub-app`, a note of what the files match in the hub, which you commit; and `.claude/settings.local.json`, which runs later Claude Code sessions in the repository on the agent's key. That second file holds paths on your machine, so the agent's setup adds it to `.git/info/exclude`, and Git leaves it out.
- **An account.** None. No sign-in is asked of you.

## The steps

1. Install the plugin, in a terminal:

   ```
   claude plugin marketplace add confighubai/confighub-mini-plugin
   claude plugin install confighub@confighub
   ```

2. Make an empty folder with Git, and start Claude Code in it:

   ```
   mkdir baseline && cd baseline && git init -q && claude
   ```

3. Ask for the app, in your own words. This is the request we measured:

   ```
   vibe code me a baseline app using ConfigHub: a small web service with a health endpoint,
   a configurable greeting, a request limit per minute, and a staging and a production setup
   ```

   You do not need special prompts for later app work. The [current workflow](../agent-workflow.md) first checks your existing setup. If you have not chosen ConfigHub, the agent explains the relevant benefit and setup cost before offering a hub. The walkthrough below records the earlier explicit ConfigHub setup.

4. Let the agent work. It writes the app and its settings files (`.env`, `.env.staging`, `.env.production`). If no hub answers, it runs the plugin's own `confighub mini get`, which downloads confighub mini and starts a hub. On a machine without it, this took 22 seconds and printed:

   ```
   Downloading confighub mini 0.10.7-mini.9 for darwin-arm64...
   Checked against SHA256SUMS: 4179dcad…
   ==> Signed in as context "shadow-bear"
       It is the current context.

   confighub mini 0.10.7-mini.9 is running on this machine. Next, ask here, in your own words, for example:
     "Put what the agents changed in this repository into the hub."
     "Make changes to production wait for my approval; agents may only propose them."

   In a terminal, its cub is at: export PATH="…/confighub-mini-0.10.7-mini.9-darwin-arm64/bin:$PATH"
   To stop the hub: cub mini stop. To remove it and its data: cub mini uninstall --delete-data.
   ```

   From plugin 0.81.0, the output also has one line about a setting that is yours alone, `ConfigHub: one setting is yours alone: whether a hub may start by itself …`. It is off, and this walkthrough does not need it: you asked for this hub. To decide it, read [a hub that starts by itself](../agent-workflow.md#a-hub-that-starts-by-itself-only-if-you-say-yes).

   Then it runs `cub mini adopt greeter`, which makes the three copies from what the app reads at start:

   ```
   Adopted greeter from what greeter reads at start (.env, app.py, .env.staging for staging, .env.production for live), as an app made from pattern-web/web-service.
     Commit greeter/.confighub-app with the app: it notes what the files match in the hub, so that cub mini upload from any clone proposes only what that clone changed.
     Its own values, kept through pattern-web/web-service's next version: APP_ENV=base, ENV_FILE=.env, GREETING=Hello, RATE_LIMIT_PER_MINUTE=60
     From pattern-web/web-service, as greeter does not set them: LOG_LEVEL=info, PUBLIC=false, RELEASE=none, REPLICAS=2
     Staging: greeter-staging, with them now, and its own from .env.staging: APP_ENV=staging, GREETING=Hello (staging), RATE_LIMIT_PER_MINUTE=600.
     Live: greeter-live, with its own from .env.production: APP_ENV=production, GREETING=Welcome, RATE_LIMIT_PER_MINUTE=120; the rest unchanged until you approve. cub mini waiting shows what it would take, and the commands that approve it.
   ```

   `pattern-web` is a starter pattern the first adopt makes: the defaults every small web service starts from, and four rules, such as one that refuses a value named like a password. It is yours to change or ignore. Last, the agent runs `cub mini require-approval greeter --variant live --agent greeter-agent`, which gives the agent its own key.

5. Read the agent's summary. In our run it ended:

   > **The three copies in the hub:**
   >
   > | Copy | `GREETING` | `RATE_LIMIT_PER_MINUTE` | `APP_ENV` |
   > |---|---|---|---|
   > | `greeter-base` | Hello | 60 | base |
   > | `greeter-staging` | Hello (staging) | 600 | staging |
   > | `greeter-live` | Welcome | 120 | production |
   >
   > …
   > - **Agent rights:** I set up a `greeter-agent` key that can change the base and propose changes, but can't approve or write live. Claude Code sessions started in this folder now run as that agent. …
   >
   > Nothing is committed yet. Commit `greeter/`, including `.confighub-app`, so later uploads from any clone propose only that clone's changes.

6. In your own terminal, run the `export PATH=...` line the agent gave you. `cub` comes with confighub mini and is not on your path until you do. Each new terminal needs it again.

7. Let live take the base's values. Adopt left a change order for live, which waits for you. See it, then approve it:

   ```
   cub mini waiting
   cub mini approve greeter-base/adopt
   ```

   `cub mini approve` shows what the change would do and asks you first. When it worked, you see `Approved greeter-base/adopt.` In a run of an app with other values in its files, it showed:

   ```
   greeter-base/adopt, for greeter-live: greeter adopted from what greeter reads at start (.env, .env.staging for staging, .env.production for live) (made just now)
     what it would change on greeter-live:
       app: LOG_LEVEL=warn stays, kept as this copy's own
       app: RATE_LIMIT=500 stays, kept as this copy's own
       …
       app: GREETING=Hello added
   Approved greeter-base/adopt.
   …
   ```

   Live's own values, from `.env.production`, stay as they are. From plugin 0.82.0, where the agent wrote those files, this approval also approves them as production's starting values, and you see `Approved revision N of greeter-live/app too, its starting values, as shown above.` Until then nothing delivers live: `cub mini pull`, `pull-key` and `deploy-from-hub` refuse, and name this command.

8. Commit the app with `.confighub-app`:

   ```
   git add -A && git commit -m "greeter, with its staging and live copies"
   ```

## Changing the app later

Ask for a change as you would. The agent edits `.env`, then proposes it with `cub mini upload`. Staging takes it at once. Live waits for you. When an agent on its key changed the greeting, the upload printed:

```
greeter-staging has GREETING = howdy now, from .env.

greeter-live takes it only once approved: it waits for that, as greeter-base/upload-20261107-153104-r2jx.
  To see it and approve it: cub mini approve greeter-base/upload-20261107-153104-r2jx
```

The agent's turn ends with one line that a change is waiting for you, with the command that approves it. `cub mini waiting` lists every change that waits:

```
greeter-base/upload-20261107-153104-r2jx, for greeter-live: A warmer greeting (made just now)
  what it proposes for greeter-live, from its files:
    app: GREETING=hello → GREETING=howdy
  promoting it would also carry what greeter-base took from other uploads before it was made:
    app: LOG_LEVEL=warn stays, kept as this copy's own
  to approve and promote it: cub mini approve greeter-base/upload-20261107-153104-r2jx
  to refuse it: cub mini refuse greeter-base/upload-20261107-153104-r2jx --reason WHY
```

The agent cannot approve its own change. When it tried, on its key (named `g-agent` in that run), the hub answered:

```
cub mini: the hub did not take your approval: only someone its workflow for greeter-live names may approve, and g-agent is not one of them. Nothing was approved or promoted
```

## A second app from the first

Start Claude Code in a new folder, outside the first app's Git repository, and ask:

```
make me a second app like the first: a notes service with a health endpoint, the same staging and production setup
```

The agent writes the second app and runs `cub mini adopt notes --pattern greeter`. The second app's base is made from the first's. It keeps its own values, and takes what the first changes next. In our run, adopt printed:

```
Adopted notes from what notes reads at start (.env, .env.staging for staging, .env.production for live), as an app made from greeter-base/app.
  Commit notes/.confighub-app with the app: it notes what the files match in the hub, so that cub mini upload from any clone proposes only what that clone changed.
  What greeter changes next reaches notes, keeping its own, by: cub mini upgrade greeter-base/app --change-desc WHY
  Staging: notes-staging, with them now, and its own from .env.staging: ENVIRONMENT=staging, GREETING=Hello from staging, RATE_LIMIT_PER_MINUTE=600.
  Live: notes-live, with its own from .env.production: ENVIRONMENT=production, GREETING=Welcome, PORT=8080; the rest unchanged until you approve. …
```

Approve its live copy as in step 7, with `cub mini approve notes-base/adopt`.

## If something goes wrong

- **`cub: command not found`.** Run the `export PATH=...` line from step 6 in this terminal. To see it again, type `/confighub:install-mini` in Claude Code.
- **No hub answers after a restart.** Type `/confighub:install-mini` in Claude Code, or ask the agent to start the hub. It starts the hub you had, with everything in it.
- **The agent wrote a setup script for you to run, or asked you to sign in.** The plugin's skill was not used. Check that the plugin is installed with `claude plugin list`, and ask again with the words "using ConfigHub".
- **Adopt found no settings.** It prints `reads no settings adopt can find` when the app has no `.env`, compose file, `.env.example` or `.tfvars` file, and its code reads no setting. Ask the agent to put the app's settings in `.env`, then adopt again. From plugin 0.82.0, if the folder has an env file by another name, such as `api.env`, the message names it and gives the two ways on: rename it to `.env`, or keep it with `cub mini upload APP --variant live --target none`.
- **Live does not have a production value you asked for.** The agent wrote it in `.env`, which the copies share, and not in `.env.production`. Live takes a shared value only when you approve it: `cub mini waiting` shows it, and `cub mini approve APP-base/adopt` gives it to live. To make it live's own from the start, ask the agent to put it in `.env.production` too.
- **A value was left out and named.** A value that looks like a password or a token never goes into the hub. Keep it out of the file, and set it in a terminal with `cub mini secret set APP KEY --variant live --change-desc "WHY"` ([a secret for live](../from-plugin-to-confighub.md#a-secret-for-live-that-no-agent-can-read)).
- **The second app did not start from the first.** In one measured session of eight, the second app was asked for inside the first app's repository. Sessions there run on the first app's agent key, which may not make a new app. Ask from a folder of its own.
- **Alpine Linux.** confighub mini does not run on it. Use a distribution with glibc ([install](../install-mini.md)).

## How to go back

- **Refuse a change that waits:** `cub mini refuse APP-base/ORDER --reason "WHY"`. The agent can read your reason. The refused value stays in the base until someone changes it back, so the next change that waits would carry it; from plugin 0.82.0, `cub mini waiting` and `cub mini approve` mark it `refused before`, with your reason, so you do not approve it by accident.
- **Undo a change live already has:** going back is a change like any other. Ask the agent to set the value back. It proposes it, and you approve it.
- **Run sessions as yourself again:** `cub mini revoke-agent APP-agent` takes the agent's rights away at once. Then delete `.claude/settings.local.json`, or take out what the agent setup added to it if you keep other settings there.
- **Leave the hub:** your app's files were never changed by the hub, so they are still yours as they are. To take the hub's copies out as plain files, with a `CHANGES.md` that says why each value is set, run `cub mini copy APP --to-dir DIR`. Then `cub mini stop` stops the hub, and `cub mini uninstall --delete-data` removes it and its data.

Every way out, step by step: [going back](going-back.md).

## How this was tested

Each step ran in non-interactive Claude Code sessions (`claude -p`) in empty Git repositories, with no `cub` on the path, on 7 November 2026, with the plugin 0.78.0 and confighub mini 0.10.7-mini.9; a program read the hub and the files afterwards, not what the session said. The app came out with its three copies in 16 of 16 sessions, and a second app started from the first's base in 7 of 8 ([the evidence](../evidence.md#the-app-in-one-request)). The agent's upload, `cub mini waiting` and the refused approval are from a run the same day of the change that went out in confighub mini 0.10.7-mini.11, where an agent's key changes staging at once. The wording of a line may differ slightly in the current release.

## What you have now

- The app, with its files as the agent wrote them, and `.confighub-app` committed beside them.
- A hub on this machine with three copies of its settings: `greeter-base`; `greeter-staging`, which takes each change at once; and `greeter-live`, which takes a change only when you approve it.
- A key of the agent's own, `greeter-agent`. Claude Code sessions in the folder run on it: they can propose a change to live, and cannot approve it.
- The plugin's record of what each agent changed, with the request and, where the agent said it, what it chose and why. `CUB_MINI_DECISIONS=0` in Claude Code's settings stops keeping what the agent said.

What you do not have yet is a running service that reads live's values. To check one:

1. Check the base, staging and live values in the hub. Live's recorded revision should stay unchanged while a change order waits; the agent must be unable to approve it.
2. If you only wanted managed configuration, that is the result of this walkthrough. To run services from it, connect the [deployment path for your target](../README.md#where-the-app-runs).
3. Check that the service answers, then compare its loaded settings or release with the approved live revision, before and after your approval. A configuration copy alone does not prove a service is running ([verification](../approvals.md#verify-the-result)).

## What to try next

In five minutes, in the same folder:

1. Ask the agent for a change, such as *"make the greeting warmer"*. Its turn ends with one line: a change waits for you. Run `cub mini waiting`, then the `cub mini approve` command it prints.
2. In Claude Code, type `/confighub:why GREETING`: each change to the greeting, the request behind it, and the agent's own words about it.
3. Run `cub mini receipts greeter-live` for everything the hub keeps about live's latest revision: who made it, why, and who approved it. `cub mini receipts greeter --setup` shows the app's setup: its copies, approval, agent keys, own values and delivery, each with why, and the `cub` command that changes it.

Then, each a sentence to the agent: [try a change in a copy first](../from-plugin-to-confighub.md#try-a-change-in-a-copy-first), [a Postgres, a Redis, an S3 bucket or a mail sender](../from-plugin-to-confighub.md#a-service-the-app-needs), or [a password for live that no agent can read](../from-plugin-to-confighub.md#a-secret-for-live-that-no-agent-can-read). Later: [your team on one hub](../from-plugin-to-confighub.md#step-3-your-organizations-confighub), [a service on a VM](../vm.md) fed only approved values, or [a cluster](../gitops-over-oci.md) that deploys what the hub approved.
