# A new app in Claude Code, with a staging copy and a live copy

Ask Claude Code for an app in one sentence, and end with the app, staging configuration that takes your agent's changes at once, and live configuration that changes only when you approve. A second app can start from the first. This page is for someone who makes apps with Claude Code and wants production to change only with their say: an agent can change production settings as easily as staging ones, and a rule in `CLAUDE.md` is only a request.

This page explains what happens and why. To see every command and what it prints, follow a walkthrough:

- [Your first hour](../../examples/walkthroughs/story-13-first-hour.md): the plugin and a hub on your laptop, production behind your approval, and an agent's own approval refused.
- [A new app that fits the team's pattern](../../examples/walkthroughs/story-18-dev-intent.md): a new app on a pattern, with rules that keep a bad value from production, and a second app made from the first.
- [The `cub mini` commands](../../examples/walkthroughs/tool-cub-mini.md): each command the agent runs here, on one small app.

The app might run on your own machine, on another machine, in CI, on one or many sandbox nodes, in a shared development cluster, or eventually in production. This page makes the staging and live configuration in the hub. Connect the running copies to it with the deployment path for your target ([where the app runs](../agent-workflow.md#where-the-app-runs)).

The words on this page, such as *hub*, *base* and *change order*, are explained in [the glossary](../README.md#words).

## What it takes

- **The download.** The first time, the agent downloads confighub mini ([its size](../install-mini.md#the-current-release)) into `~/.confighub/mini`, and starts a hub. The hub listens on this machine only. Nothing else is installed.
- **Your folder.** Besides the app's own files, two files appear: `.confighub-app`, a note of what the files match in the hub, which you commit; and `.claude/settings.local.json`, which runs later Claude Code sessions in the repository on the agent's key. That second file holds paths on your machine, so the agent's setup adds it to `.git/info/exclude`, and Git leaves it out.
- **An account.** None. No sign-in is asked of you.

## What you do

1. Install the plugin ([the README](../../README.md#install)).
2. In an empty folder with Git, start Claude Code and ask for the app in your own words, with "using ConfigHub". For example: *"Build me a small web service using ConfigHub, with a health endpoint, a configurable greeting, and a staging and a production setup."*
3. When the agent is done, run the one command it gives you, in a terminal of your own: `cub mini approve APP-base/adopt`, with `cub`'s full path. It shows production's starting settings and asks you first.
4. Commit the app with its `.confighub-app`.

You do not need special words for later work. For an ordinary request, the [current workflow](../agent-workflow.md) checks your setup first, and offers a hub only with the benefit and the cost.

## What the agent does, and why

1. **It writes the app and its settings files**: `.env` for what every copy shares, `.env.staging` and `.env.production` for what each sets itself.
2. **It starts a hub, if none answers.** It runs the plugin's own `confighub mini get`, which downloads confighub mini, checks it against the release's checksums, starts a hub and signs `cub` in to it. You are asked nothing. The one setting it names, whether a hub may start by itself in other folders, stays off until you turn it on ([a hub that starts by itself](../agent-workflow.md#a-hub-that-starts-by-itself-only-if-you-say-yes)).
3. **It runs `cub mini adopt`**, which keeps three copies of the settings in the hub: the base, staging and live, each named after the app, such as `greeter-base`. Your files are not changed. The values your files set are kept as your own; settings your app does not set come from `pattern-web`, the defaults every small web service starts from, with four rules, such as one that refuses a value named like a password. The pattern is yours to change or ignore. It is not one of the optional [starters](../starters.md).
4. **It runs `cub mini require-approval APP --variant live --agent APP-agent`.** Live now takes a change only when you approve it, and the agent gets a key of its own that can propose a change to live and cannot approve one. Claude Code sessions started in the folder from then on run on that key.
5. **It tells you, in plain words,** what you now have and the one command to type: the approval of production's starting settings.

When you approve, production keeps every value `.env.production` sets: a change to the shared settings never overwrites a copy's own value. Approving also records that you read production's settings. Until you approve, nothing delivers live: `cub mini pull`, `pull-key` and `deploy-from-hub` refuse, and name the command.

## Changing the app later

Ask for a change as you would. The agent edits the files, then proposes the change with `cub mini upload`. Staging takes it at once, unless staging has its own value for that setting. Live waits for you. The agent's turn ends with one line that a change waits for you, and the command that approves it; `cub mini waiting` lists every change that waits.

- **A copy's own value wins.** If production sets its own greeting in `.env.production`, a new greeting in the shared settings is recorded for production when you approve, and production keeps its own. To change production's value, change `.env.production`.
- **The agent cannot approve.** On its key, `cub mini approve` is refused: only a person named as an approver for production can approve the change.
- **A refusal keeps its reason.** `cub mini refuse APP-base/ORDER --reason "WHY"` keeps the change out of production. The refused value stays in the shared settings until someone changes it back, and `cub mini waiting` and `cub mini approve` mark it, with your reason, so you do not approve it by accident inside a later change. With the plugin, the next agent that tries the same value is told your reason.

## A second app from the first

Start Claude Code in a new folder, outside the first app's repository, and ask for *"a second app like the first"*. The agent runs `cub mini adopt notes --pattern greeter`: the second app's base is made from the first's. It keeps its own values, and can take what the first changes next, with `cub mini upgrade greeter-base/app`. Approve its live copy as for the first app. [A new app that fits the team's pattern](../../examples/walkthroughs/story-18-dev-intent.md) shows it with every command.

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

Each way out, from refusing one change to removing the hub, is on [going back](going-back.md). If an agent has already done damage, [Sam's bad afternoon](../../examples/walkthroughs/story-19-recovery.md) stops every agent at once, finds the change and puts it back.

## What you have now

- The app, with its files as the agent wrote them, and `.confighub-app` committed beside them.
- A hub on this machine with three copies of its settings: the base; staging, which takes each change at once; and live, which takes a change only when you approve it.
- A key of the agent's own. Claude Code sessions in the folder run on it: they can propose a change to live, and cannot approve it.
- The plugin's record of what each agent changed, with the request and, where the agent said it, what it chose and why. `CUB_MINI_DECISIONS=0` in Claude Code's settings stops keeping what the agent said.

What you do not have yet is a running service that reads live's values. Connect the [deployment path for your target](../agent-workflow.md#where-the-app-runs), then check that the service answers and that what it loaded matches the approved live revision ([verification](../approvals.md#verify-the-result)).

## What to try next

In the same folder:

1. Ask the agent for a change, such as *"make the greeting warmer"*. Run `cub mini waiting`, then the `cub mini approve` command it prints.
2. In Claude Code, type `/confighub:why GREETING`: each change to the greeting, the request behind it, and the agent's own words about it.
3. Run `cub mini receipts APP-live` for everything the hub keeps about live's latest revision: who made it, why, and who approved it. `cub mini receipts APP --setup` shows the app's setup: its copies, approval, agent keys, own values and delivery, each with why, and the `cub` command that changes it.

Then, each a sentence to the agent: [try a change in a copy first](../from-plugin-to-confighub.md#try-a-change-in-a-copy-first), [a Postgres, a Redis, an S3 bucket or a mail sender](../from-plugin-to-confighub.md#a-service-the-app-needs), or [a password for live that no agent can read](../from-plugin-to-confighub.md#a-secret-for-live-that-no-agent-can-read). Later: [your team on one hub](../from-plugin-to-confighub.md#step-3-your-organizations-confighub), [a service on a VM](../vm.md) fed only approved values, or [a cluster](../gitops-over-oci.md) that deploys what the hub approved.
