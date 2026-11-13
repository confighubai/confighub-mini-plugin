# A new app in Claude Code, with a staging copy and a live copy

Ask Claude Code for an app in one sentence, and end with the app, staging configuration that takes your agent's changes at once, and live configuration that changes only when you approve. A second app can start from the first. This page is for someone who makes apps with Claude Code and wants production to change only with their say: an agent can change production settings as easily as staging ones, and a rule in `CLAUDE.md` is only a request.

To see a new app fit a team's pattern and its rules from a terminal, follow the walkthrough [a new app that fits the team's pattern](../../examples/walkthroughs/story-18-dev-intent.md).

The app might run on your own machine, on another machine, in CI, on one or many sandbox nodes, in a shared development cluster, or eventually in production. This walkthrough creates staging and live configuration in the hub. Connect the running copies to that configuration using the deployment path for your target ([where the app runs](../agent-workflow.md#where-the-app-runs)).

The words on this page, such as *hub*, *base* and *change order*, are explained in [the glossary](../README.md#words).

## What it costs

- **Time.** One to two minutes for the first app, including the download, and about a minute for a second one.
- **The download.** The first time, the agent downloads confighub mini ([its size](../install-mini.md#the-current-release)) into `~/.confighub/mini`, and starts a hub. The hub listens on this machine only. Nothing else is installed.
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

3. Ask for the app, in your own words. For example:

   ```
   vibe code me a baseline app using ConfigHub: a small web service with a health endpoint,
   a configurable greeting, a request limit per minute, and a staging and a production setup
   ```

   You do not need special prompts for later app work. The [current workflow](../agent-workflow.md) first checks your existing setup. If you have not chosen ConfigHub, the agent explains the relevant benefit and setup cost before offering a hub. The walkthrough below records the earlier explicit ConfigHub setup.

4. Let the agent work. It writes the app and its settings files (`.env`, `.env.staging`, `.env.production`). If no hub answers, it runs the plugin's own `confighub mini get`, which downloads confighub mini and starts a hub. On a machine without it, it printed:

   ```
   Downloading confighub mini 0.10.7-mini.23 for darwin-arm64...
   Checked against SHA256SUMS: bcda6262cb7cc10fcee287c61193632957c158317e1d8781af726244f1088839
   ==> Signed in as context "growl-cub"
       It is the current context.

   ConfigHub: one setting only you can turn on. With it on, when an agent works in a folder that holds an app's settings files, a hub (a ConfigHub server on this machine) starts by itself and keeps those settings. It is off. To turn it on, run this in your own terminal: ~/.confighub/mini/confighub-mini-0.10.7-mini.23-darwin-arm64/bin/cub mini install --arrival yes. To keep it off and stop this line, run it with --arrival no instead.

   confighub mini 0.10.7-mini.23 is running on this machine. Next, ask here, in your own words, for example:
     "Put what the agents changed in this repository into the hub."
     "Make changes to production wait for my approval; agents may only propose them."

   To run its cub in a terminal of your own, with nothing added to your PATH: ~/.confighub/mini/confighub-mini-0.10.7-mini.23-darwin-arm64/bin/cub
   …
   ```

   A hub is now running on your machine, and the last line says where its `cub` is. The hub signed your `cub` in to itself, as a *context*: a named hub and sign-in that `cub` uses. You were asked for nothing. The setting the output names, whether a hub may start by itself in other folders, is yours alone, and it stays off. This walkthrough does not need it, because you asked for this hub. To decide it, read [a hub that starts by itself](../agent-workflow.md#a-hub-that-starts-by-itself-only-if-you-say-yes).

   Then the agent runs `cub mini adopt greeter`, which makes the three copies from what the app reads at start:

   ```
   Made a starter pattern, pattern-web: default settings for a small web service (pattern-web/web-service), and rules that each change must pass (replicas-limit, not-public, log-level, no-secret-values). You can change it or ignore it.
   ConfigHub now keeps greeter's settings, from .env, with .env.staging for staging and .env.production for production. Your files are unchanged.
     It keeps three copies of them: greeter-base, the shared settings that staging and production start from; greeter-staging; and greeter-live, for production.
     Your settings that differ from the defaults in pattern-web/web-service: APP_ENV=base, GREETING=Hello, RATE_LIMIT_PER_MINUTE=60. A new version of those defaults will not overwrite them.
     Defaults from pattern-web/web-service, for settings greeter does not set: LOG_LEVEL=info, PORT=8080, PUBLIC=false, RELEASE=none, REPLICAS=2.
     Staging has the shared settings now, with its own settings from .env.staging: APP_ENV=staging, GREETING=Hello (staging), RATE_LIMIT_PER_MINUTE=600.
     Production has its own settings from .env.production: APP_ENV=production, GREETING=Welcome, RATE_LIMIT_PER_MINUTE=120. The shared settings reach production only after you approve them: run cub mini waiting.
     Commit greeter/.confighub-app with the app. It records what your files matched in ConfigHub, so that cub mini upload from any clone proposes only that clone's changes.
   …
   ```

   Your values are in the hub as your files have them, and your files are unchanged. `pattern-web` is the set of defaults every small web service starts from, with four rules, such as one that refuses a value named like a password. It is yours to change or ignore. (It is not one of the optional [starters](../starters.md), which are switched off unless you switch them on.)

   Last, the agent runs `cub mini require-approval greeter --variant live --agent greeter-agent`. It makes the live copy (`--variant live`) wait for your approval, and gives the agent a key of its own. Its output ends with lines for you, which the agent passes on as they are:

   ```
   Tell the person this, in these words:
     Staging and production now have their own settings. When an agent changes something that production uses, production waits for your yes.
     Claude Code sessions you start in ~/baseline/greeter from now on change staging at once, and ask you before they change production.
     One change waits for you now: production's starting settings, from this setup. To see it and approve it, run this in a terminal of your own:
       ~/.confighub/mini/confighub-mini-0.10.7-mini.23-darwin-arm64/bin/cub mini approve greeter-base/adopt
   ```

   The approve command is the one ConfigHub command you need to type.

5. Read the agent's summary. It ends something like this:

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

6. Approve production's starting settings. Adopt left a change order for live, which waits for you. Run the approve command the agent gave you, in a terminal of your own. It names confighub mini's own `cub` by its full path, so it runs as printed, and nothing needs to go on your PATH. With your version and platform, it is:

   ```
   ~/.confighub/mini/confighub-mini-0.10.7-mini.23-darwin-arm64/bin/cub mini approve greeter-base/adopt
   ```

   `cub mini approve` shows what the change would do and asks you first:

   ```
   A change to production waits for your approval: greeter's settings, from .env, with .env.staging for staging and .env.production for production. It was made just now; its name is greeter-base/adopt.
     Approving it changes no value in production; it only records your approval.
     Production keeps its own value for these, so approving does not change them there:
       APP_ENV=production
       GREETING=Welcome
       RATE_LIMIT_PER_MINUTE=120
   Approved greeter-base/adopt.
   …
   greeter-live: updated. No cluster or service takes its settings from ConfigHub yet
   …
   Done. Each copy kept its own values.
   ```

   Here, production already had its own value for each setting the base holds, from `.env.production`, so approving changed no value there. It recorded that you read and approved production's settings. Where the agent wrote those files, this approval also approves them as production's starting values, and you see `Approved revision N of greeter-live/app too, its starting values, as shown above.` Until then nothing delivers live: `cub mini pull`, `pull-key` and `deploy-from-hub` refuse, and name this command.

7. Commit the app with `.confighub-app`:

   ```
   git add -A && git commit -m "greeter, with its staging and live copies"
   ```

## Changing the app later

Ask for a change as you would. The agent edits `.env`, then proposes it with `cub mini upload`. Staging takes it at once, unless staging has its own value. Live waits for you. When an agent on its key changed the greeting, the upload printed:

```
Changed the shared settings (greeter-base), with the reason: A warmer greeting
  GREETING: Hello → howdy
Staging keeps its own GREETING=Hello (staging), so this change does not reach it.

Production keeps its current settings until you approve this change. To see the change and approve it:
  ~/.confighub/mini/confighub-mini-0.10.7-mini.23-darwin-arm64/bin/cub mini approve greeter-base/upload-20261112-054905-acvw
```

The change is in the shared settings, and staging keeps its own greeting. The agent's turn ends with one line that a change waits for you, with the command that approves it. `cub mini waiting` lists every change that waits:

```
A change to production waits for your approval: A warmer greeting. It was made just now; its name is greeter-base/upload-20261112-054905-acvw.
  It proposes for production, from the app's files:
    GREETING: Hello → howdy
  Production keeps its own value for these, so approving does not change them there:
    APP_ENV=production
    GREETING=Welcome (not the howdy this change proposes)
    RATE_LIMIT_PER_MINUTE=120
  To approve it, which puts it in production: cub mini approve greeter-base/upload-20261112-054905-acvw
  To refuse it: cub mini refuse greeter-base/upload-20261112-054905-acvw --reason WHY
```

Here production has its own greeting, `Welcome`, from `.env.production`. Approving this change would record it for production, but production would keep `Welcome`: a change to the shared settings does not overwrite a copy's own value. To change production's greeting, change `.env.production`. The agent cannot approve its own change. When it tried, on its key, ConfigHub answered:

```
cub mini: ConfigHub did not take your approval: only a person named as an approver for production can approve this change, and greeter-agent is not one. Nothing was changed
```

Later an agent lowered the shared request limit to 5. You refused it with `cub mini refuse`, giving a reason the agent can read. Refusing keeps the change out of production; the value stays in the shared settings until someone changes it back:

```
Refused greeter-base/upload-20261112-054911-yipf, with your reason: Five a minute is too few for the launch
The refused value stays in the shared settings (greeter-base) until someone changes it back, so the next change proposed from them includes it too. cub mini waiting and cub mini approve will show it as a value you refused, with your reason.
With the ConfigHub plugin, the next agent on this machine that finds or sets RATE_LIMIT_PER_MINUTE=5 where production would take it is told your reason.
```

## A second app from the first

Start Claude Code in a new folder, outside the first app's Git repository, and ask:

```
make me a second app like the first: a notes service with a health endpoint, the same staging and production setup
```

The agent writes the second app and runs `cub mini adopt notes --pattern greeter`. The second app's base is made from the first's. It keeps its own values, and takes what the first changes next. Adopt prints something like this:

```
ConfigHub now keeps notes's settings, from .env, with .env.staging for staging and .env.production for production. Your files are unchanged.
  It keeps three copies of them: notes-base, the shared settings that staging and production start from; notes-staging; and notes-live, for production.
  Your settings that differ from the defaults in greeter-base/app: ENVIRONMENT=base, GREETING=Hello from notes, RATE_LIMIT_PER_MINUTE=60. A new version of those defaults will not overwrite them.
  Defaults from greeter-base/app, for settings notes does not set: APP_ENV=base, LOG_LEVEL=info, PORT=8080, PUBLIC=false, RELEASE=none, REPLICAS=2.
  When greeter's settings change, notes can take the change and keep its own values: cub mini upgrade greeter-base/app --change-desc WHY
…
```

The second app took the first app's settings as its defaults, and kept its own.

Approve its live copy as in step 6, with `cub mini approve notes-base/adopt`.

## If something goes wrong

- **`cub: command not found`.** Use the command as the agent printed it, with `cub`'s full path. To type `cub` yourself, first run `export PATH="$HOME/.confighub/mini/confighub-mini-VERSION-OS-ARCH/bin:$PATH"`, with the folder name the agent's command shows.
- **No hub answers after a restart.** Type `/confighub:install-mini` in Claude Code, or ask the agent to start the hub. It starts the hub you had, with everything in it.
- **The agent wrote a setup script for you to run, or asked you to sign in.** The plugin's skill was not used. Check that the plugin is installed with `claude plugin list`, and ask again with the words "using ConfigHub".
- **Adopt found no settings.** It prints `reads no settings adopt can find` when the app has no `.env`, compose file, `.env.example` or `.tfvars` file, and its code reads no setting. Ask the agent to put the app's settings in `.env`, then adopt again. If the folder has an env file by another name, such as `api.env`, the message names it and gives the two ways on: rename it to `.env`, or keep it with `cub mini upload APP --variant live --target none`.
- **Live does not have a production value you asked for.** The agent wrote it in `.env`, which the copies share, and not in `.env.production`. Live takes a shared value only when you approve it: `cub mini waiting` shows it, and `cub mini approve APP-base/adopt` gives it to live. To make it live's own from the start, ask the agent to put it in `.env.production` too.
- **A value was left out and named.** A value that looks like a password or a token never goes into the hub. Keep it out of the file, and set it in a terminal with `cub mini secret set APP KEY --variant live --change-desc "WHY"` ([a secret for live](../from-plugin-to-confighub.md#a-secret-for-live-that-no-agent-can-read)).
- **The second app did not start from the first.** This happens when the second app is asked for inside the first app's repository. Sessions there run on the first app's agent key, which may not make a new app. Ask from a folder of its own.
- **Alpine Linux.** confighub mini does not run on it. Use a distribution with glibc ([install](../install-mini.md)).

## How to go back

- **Refuse a change that waits:** `cub mini refuse APP-base/ORDER --reason "WHY"`. The agent can read your reason. The refused value stays in the base until someone changes it back, so the next change that waits would carry it; `cub mini waiting` and `cub mini approve` mark it as a value you refused, with your reason, so you do not approve it by accident.
- **Undo a change live already has:** going back is a change like any other. Ask the agent to set the value back. It proposes it, and you approve it.
- **Run sessions as yourself again:** `cub mini revoke-agent APP-agent` takes the agent's rights away at once. Then delete `.claude/settings.local.json`, or take out what the agent setup added to it if you keep other settings there.
- **Leave the hub:** your app's files were never changed by the hub, so they are still yours as they are. To take the hub's copies out as plain files, with a `CHANGES.md` that says why each value is set, run `cub mini copy APP --to-dir DIR`. Then `cub mini stop` stops the hub, and `cub mini uninstall --delete-data` removes it and its data.

Every way out, step by step: [going back](going-back.md).

## What you have now

- The app, with its files as the agent wrote them, and `.confighub-app` committed beside them.
- A hub on this machine with three copies of its settings: `greeter-base`; `greeter-staging`, which takes each change at once; and `greeter-live`, which takes a change only when you approve it.
- A key of the agent's own, `greeter-agent`. Claude Code sessions in the folder run on it: they can propose a change to live, and cannot approve it.
- The plugin's record of what each agent changed, with the request and, where the agent said it, what it chose and why. `CUB_MINI_DECISIONS=0` in Claude Code's settings stops keeping what the agent said.

What you do not have yet is a running service that reads live's values. To check one:

1. Check the base, staging and live values in the hub. Live's recorded revision should stay unchanged while a change order waits; the agent must be unable to approve it.
2. If you only wanted managed configuration, that is the result of this walkthrough. To run services from it, connect the [deployment path for your target](../agent-workflow.md#where-the-app-runs).
3. Check that the service answers, then compare its loaded settings or release with the approved live revision, before and after your approval. A configuration copy alone does not prove a service is running ([verification](../approvals.md#verify-the-result)).

## What to try next

In five minutes, in the same folder:

1. Ask the agent for a change, such as *"make the greeting warmer"*. Its turn ends with one line: a change waits for you. Run `cub mini waiting`, then the `cub mini approve` command it prints.
2. In Claude Code, type `/confighub:why GREETING`: each change to the greeting, the request behind it, and the agent's own words about it.
3. Run `cub mini receipts greeter-live` for everything the hub keeps about live's latest revision: who made it, why, and who approved it. `cub mini receipts greeter --setup` shows the app's setup: its copies, approval, agent keys, own values and delivery, each with why, and the `cub` command that changes it.

Then, each a sentence to the agent: [try a change in a copy first](../from-plugin-to-confighub.md#try-a-change-in-a-copy-first), [a Postgres, a Redis, an S3 bucket or a mail sender](../from-plugin-to-confighub.md#a-service-the-app-needs), or [a password for live that no agent can read](../from-plugin-to-confighub.md#a-secret-for-live-that-no-agent-can-read). Later: [your team on one hub](../from-plugin-to-confighub.md#step-3-your-organizations-confighub), [a service on a VM](../vm.md) fed only approved values, or [a cluster](../gitops-over-oci.md) that deploys what the hub approved.
