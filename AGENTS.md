# For AI agents: read this first

This page teaches an AI agent what this project is, so it can help a person use it or explain it. It is written for agents, but people may read it too. Every page it names is listed, with a line on each, in [llms.txt](llms.txt).

## What the project is

ConfigHub keeps an app's settings in a small server called a **hub**. A coding agent can change the app's staging settings at once, but a change to its production settings waits until a person approves it. Every change is kept with who made it and why.

There are three ways to run a hub. They are the same server, and `cub`, ConfigHub's command-line tool, works the same on all three:

- **confighub mini** runs on the person's own computer. It is free and needs no account or Docker.
- **Hosted ConfigHub** is run for the person's organization.
- **The enterprise edition** runs on the organization's own servers.

Hosted ConfigHub and the enterprise edition support many people in one organization. An app made on confighub mini can be copied to a shared hub ([from your laptop to a shared hub](docs/from-plugin-to-confighub.md)).

**The plugin** in this repository, for Claude Code and Codex, is the easy way to start. On its own, with no hub, it records each setting an agent changes, with the request and the reason, and tells the next agent before it undoes an earlier change. When the person asks for an app "using ConfigHub", it sets up confighub mini.

## How an app lives in a hub

An app connected to a hub has three copies of its settings:

- **the base**, the shared settings, where a change is made once;
- **staging**, which takes a change to the base at once;
- **live**, the copy for production, which takes a change only through a **change order** a person approves.

A value one copy keeps as its own, such as production's database address, is never overwritten by a change to the base.

## What you, the agent, may and may not do

- Change staging and the base freely, and always give the reason (`--change-desc`).
- Propose a production change. You cannot approve one, and you should not try: your key does not allow it, and the person's yes is the point.
- When something waits for the person, end with the exact command for them to run in their own terminal, such as `cub mini approve`. `cub mini waiting` lists what waits.
- If the person refused a value, you are told their reason. Do not propose the same value again without new information.
- Never put a password or token in a setting. `cub mini secret set` keeps it where the app can read it and your key cannot.

## The commands

`cub mini` adds a few commands to `cub` that each do a whole job in one step. Plain `cub` can do all of it on any hub; [`cub mini` and plain `cub`](docs/cub-mini-and-cub.md) shows both.

| Command | What it does |
|---|---|
| `cub mini install` | Starts confighub mini on this computer |
| `cub mini adopt FOLDER` | Connects an app from its settings files and makes its three copies. The files are not changed |
| `cub mini upload FOLDER --variant V` | Brings changed files into the hub: staging at once, production as a change order |
| `cub mini set` | Sets one value in one copy, with the reason |
| `cub mini require-approval` | Puts production behind the person's approval and gives an agent a key that can propose but not approve |
| `cub mini waiting`, `approve`, `refuse` | What waits for the person, and their decision. These are the person's commands |
| `cub mini try`, `tries` | A copy of the app for one try, kept or dropped |
| `cub mini secret set` | A secret the app reads and no agent's key can |

In Claude Code, the plugin adds `/confighub:changes`, `/confighub:why NAME`, `/confighub:inventory`, `/confighub:permissions`, `/confighub:checks`, `/confighub:install-mini` and `/confighub:to-hub`.

## Starters

A starter is one short YAML file that gives every new app of one kind a team's default settings, each with a reason. A person's own values always win, and it writes only once, when the app is connected. Starters are off unless `CUB_MINI_STARTERS` names a folder of starter files. The idea comes from Spring Boot's starters. See [starters](docs/starters.md).

## Which page answers which question

| The person asks | Read |
|---|---|
| How do I start? | [README](README.md), then [a new app](docs/journeys/new-app.md) or [an app you already have](docs/journeys/existing-app.md) |
| My app is deployed by Argo CD or Flux | [an app Argo CD or Flux deploys](docs/journeys/gitops-app.md) |
| How do approvals work? | [approvals](docs/approvals.md) |
| What does the plugin record, and where? | [how it works](docs/how-it-works.md) |
| How do I stop or limit an agent? | [agents that run for weeks](docs/agents-that-run-for-weeks.md) |
| How do I undo something, or remove it all? | [going back](docs/journeys/going-back.md) |
| Does it work with my tools? | [integrations](docs/integrations.md) |
| What doesn't it do? | [limits](docs/limits.md) |

The plugin's own instructions for an agent at work are the skill [app-with-confighub](plugins/confighub/skills/app-with-confighub/SKILL.md).

## If you are changing this repository

`plugins/confighub/` is built by each release, so do not edit it here; describe the change in an issue instead. The guides are in `docs/`, and fixes to them and to `examples/` are welcome as pull requests. Commands and output in the guides come from released versions, so run a command before you quote its output.
