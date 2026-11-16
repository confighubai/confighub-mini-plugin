# ConfigHub: durable config for apps made with AI

**One session turns the cache on for next week's sale. The next one turns it off. ConfigHub tells it why first.**

You ask your agent for two things, a few days apart:

```
claude -p "Turn the cache on in .env for next week's sale. Don't commit."
claude -p "We're chasing a memory leak: turn the cache off and set debug logging. Don't commit."
```

Nothing was committed, so `git diff` shows the new value but not why. With ConfigHub's Claude plugin, the second agent is told before it undoes the change, and it says so:

> **This undoes an earlier change.** Before I edited it, `.env` had `CACHE=on`, which wasn't committed yet. The ConfigHub plugin shows it was switched on today at 07:50 by another agent session. The request in that session was to "turn the cache on in .env for next week's sale."

`/confighub:why CACHE` then shows every change to that value, with the request behind each ([the walkthrough](examples/walkthroughs/tool-plugin.md)). On a cluster the same thing looks like this: Git shows replicas 2 → 1, and your agent set 4 in between ([the problem it solves](docs/try-the-plugin.md#the-problem-it-solves)).

That is one of four things that go wrong when agents change configuration:

- **Agents undo each other's changes**, and nobody is told.
- **Nothing stands between an agent and production.** An agent working under your sign-in can approve its own change.
- **A new version overwrites your changes**, such as the values you set in someone else's Helm chart.
- **Nobody knows what a repository deploys** before they, or an agent, change it.

## Install

For Claude Code, run these two commands in a terminal:

```
claude plugin marketplace add confighubai/confighub-mini-plugin
claude plugin install confighub@confighub
```

The Claude plugin works alone, with no hub and no account, and its record stays on your computer. Open a new session, ask your agent to change a setting, then run `/confighub:why SETTING` ([try the plugin without a hub](docs/try-the-plugin.md)). Using Codex? Follow [the Codex setup](docs/codex.md), including its separate hook approval. You can also [install the local hub without a coding agent](docs/install-mini.md).

[Product overview](https://confighub.github.io/helm-expt/ai-agents/) · [Walkthroughs by stack](examples/walkthroughs/README.md) · [Instructions for AI agents](AGENTS.md)

## What ConfigHub keeps

ConfigHub keeps the settings of the apps you make with a coding agent. With each change it keeps what you asked the agent for. Settings kept with their reasons are durable config. It is the part of your agent's context that has to be true: what is running, where, and why. It is still there for the next session, the next version of the app and your next app.

Your next app can start from the same settings instead of from nothing. What your apps share in this way is your platform. It grows from your apps, and nobody has to build it first.

## Why Git, your hosting service and a rules file are not enough

- **Git** keeps a diff once someone commits. It shows nothing for a change nobody committed. If all you want is a reason in each commit message, one line in `CLAUDE.md` asks for that. ConfigHub keeps the reason by value, across sessions, and tells the next agent before it undoes one ([limits](docs/limits.md)).
- **Your hosting service's settings** keep the current value. They don't know what you asked your agent for, and an agent with your sign-in can change production there. ConfigHub sits beside your host: with Vercel, you try a setting in Preview and review the first production delivery when you are ready ([Next.js on Vercel](docs/nextjs-on-vercel.md)).
- **A rule in `CLAUDE.md`** that says "ask first" is only a request. An agent that holds the keys can be talked past it ([an agent that can propose and cannot approve](examples/walkthroughs/story-11-propose-not-approve.md)).
- **Branch protection and CODEOWNERS** approve a commit, and they stay the gate when Argo CD or Flux deploys from Git. ConfigHub adds the reason for each value, and a pull-request check that names any value nobody approved ([an app Argo CD or Flux deploys](docs/journeys/gitops-app.md)).

## When the record is not enough, add a hub

The Claude plugin keeps a record. A hub adds control: a staging and a production copy of each app's settings, approval, a key for each agent, and delivery. A hub is one running ConfigHub server. Add one at the moment you need it, and stop at any step.

| When this happens | What you add | What you get |
|---|---|---|
| A new session undoes a setting | The Claude plugin, alone | Each change kept with the request behind it. The next agent is told before it undoes one ([try it](docs/try-the-plugin.md)) |
| You open a repository you did not write | `/confighub:inventory`, in the Claude plugin | What the repository deploys, and what deploys it, before anyone changes it ([inventory](docs/inventory.md)) |
| A teammate reviews a pull request | The [review action](review/README.md) for GitHub | A comment on each pull request with every setting it changes, and why |
| You want your agent to try things without touching production | A local hub on your computer, free and with no account | A staging copy your agent changes at once, and a production copy that changes only when you approve ([a new app](docs/journeys/new-app.md)) |
| Someone else's next version would overwrite your values | The same local hub | You take the new version and keep the values you changed, each with its reason ([keep your changes](examples/walkthroughs/story-02-keep-your-changes.md), [a Helm chart you use](docs/your-own-chart.md)) |
| You start a second app | A [starter](docs/starters.md), a short file of your settings | The second app starts with your settings. A fix reaches every app made from the starter, and each app keeps its own values |
| An agent works in a sandbox or a CI job | A hub of its own for that run | The agent makes its fix there and writes it out for a person to review, and the hub is deleted with the run ([a hub for each agent run](examples/walkthroughs/story-03-a-hub-per-agent-run.md)) |
| A teammate joins, or agents run for hours | A shared hub, on confighub.com or on your own servers | A key for each agent, which can propose a production change and cannot approve one. A way to cut one agent off. Signed records ([agents that run for weeks](docs/agents-that-run-for-weeks.md)) |
| You run many apps on clusters | The hub as the source Argo CD or Flux pulls from | What you approved is what they deploy, and "which version runs where" is one question ([GitOps over OCI](docs/gitops-over-oci.md)) |

The local hub is the full ConfigHub server, and the commands work the same way on a shared hub. Copy your apps over when your team is ready ([from your laptop to a shared hub](docs/from-plugin-to-confighub.md)).

## One team, many apps, many agents

Priya's platform team looks after ten services, and coding agents change their configuration.

1. **One base for all ten.** The team keeps the settings every service shares in one base, and each service keeps the few values it sets itself. When the team changes the base once, every service takes the change, and no service's own values are touched ([one base for every service](examples/walkthroughs/story-24-company-base.md)).
2. **Agents propose, and a person approves.** Each agent has a key of its own. It proposes Friday's change, it is refused when it tries to approve it, and production changes only when Priya says yes ([propose, not approve](examples/walkthroughs/story-11-propose-not-approve.md)).
3. **A yes in Slack counts only when it is hers.** Priya is told in the thread where the work was asked for, and her Approve there records the approval as hers. An agent relaying "Priya said yes" approves nothing ([approve from Slack](examples/walkthroughs/story-22-priya-slack.md)).
4. **What is running, and why.** For an app Argo CD deploys, the team sees Git, the hub and the cluster side by side, and sorts each difference into deliberate, drift, or Git out of date ([Git, the hub and what is running](examples/walkthroughs/story-09-git-hub-and-running.md)).

More for agents that run for hours is in [agents that run for weeks](docs/agents-that-run-for-weeks.md).

## A first try, with a new app

1. Make an empty folder and start Claude Code in it: `mkdir my-app && cd my-app && git init -q && claude`
2. Ask: `Build me a small web service using ConfigHub, with a staging and a production setup.`
3. The agent writes the app, starts the local hub if no hub is running, and puts the staging and production settings in it. It ends with one command for you to paste into your own terminal: `cub mini approve`, with the full path to `cub`, ConfigHub's command-line tool.
4. Run it to approve production's starting settings. From then on, agents change staging right away, and production changes wait for you: `cub mini waiting` shows them, and `cub mini approve` or `cub mini refuse` decides.

[A new app](docs/journeys/new-app.md) explains each step, and the walkthrough [your first hour](examples/walkthroughs/story-13-first-hour.md) shows every command and what it prints. Already have an app? Ask the agent to "attach ConfigHub to this app". It won't touch your files ([an app you already have](docs/journeys/existing-app.md)). To remove the local hub, run `cub mini uninstall --delete-data`. More walkthroughs, for each tool and most starters and user stories, are in [walkthroughs](examples/walkthroughs/README.md).

## An example: staging takes it, and production waits

You ask your agent to turn on debug logging, and staging and production both read the same `.env` file. Without ConfigHub, production starts logging customers' email addresses. With ConfigHub, staging and production get their settings from the hub instead. Staging gets debug logging right away, and production waits. `cub mini waiting` shows `LOG_LEVEL=info → LOG_LEVEL=debug`, and you refuse it with a reason: "Debug logs leak customer emails." The next agent that tries is told you said no, and why. An agent that also holds your cloud or cluster credentials can still go around this ([what an agent can reach](docs/agents-that-run-for-weeks.md#limiting-what-an-agent-can-reach)).

## What it does not do

- **It doesn't run your app**, and it doesn't watch what your agents do. Your cluster, hosting service or VM still runs it, and Argo CD and Flux still deliver to your clusters.
- **The approval holds against an agent on a key of its own.** An agent that also holds your cloud or cluster credentials can go around it.
- **What the next agent is told goes to your model provider** with the rest of that session. The record itself stays on your machine.

[The full list](docs/limits.md) says more.

## Start from the tools you use

1. **Make a new app.** Ask Claude Code to build it "using ConfigHub". It writes the app and gives it a staging and a production setup ([a new app](docs/journeys/new-app.md)).
2. **Attach an app you already have.** Its settings live in `.env` files, Terraform var files, Helm values, or a Kustomize repository that Argo CD or Flux deploys. Ask the agent to "attach ConfigHub to this app". It won't touch your files ([an app you already have](docs/journeys/existing-app.md)).
3. **Use a starter.** [Pick one for your app](docs/starters.md) to fill in settings and see what it can connect.

Some software comes with a hub inside. You change it to suit you, and keep your changes when its next version arrives ([software with ConfigHub inside](docs/journeys/bundled.md)).

Pick the guide for your app to see what its [starter](docs/starters.md) does and where you’ll be asked to approve a change.

- **Where your app runs:** [Web](examples/walkthroughs/starter-web.md), [Vercel](examples/walkthroughs/starter-vercel.md), [Next.js on Vercel](docs/nextjs-on-vercel.md), [AWS Parameter Store](examples/walkthroughs/starter-parameter-store.md), [Argo CD](examples/walkthroughs/starter-kustomize-argocd.md), [Flux](examples/walkthroughs/starter-kustomize-flux.md), [Daytona](examples/walkthroughs/starter-daytona.md), [Temporal worker](examples/walkthroughs/starter-temporal-worker.md), [Unikraft](examples/walkthroughs/starter-unikraft.md), and [Rails on Fly](docs/rails-on-fly.md).
- **Around the app:** Git and GitHub, Vault, Sigstore, SPIFFE, OpenTelemetry, Entire, MCP servers, sandboxes and containers, and Codex ([Integrations](docs/integrations.md) says what you get with each and how far along it is).

Each walkthrough opens with a quick start: the whole flow in a few rows, by hand and with your agent.

A starter gives every new app of one kind your team's default settings, such as retries, timeouts and worker limits, each with a note on why it is set. It is one short YAML file, the same idea as a [Spring Boot starter](https://docs.spring.io/spring-boot/reference/using/build-systems.html#using.build-systems.starters) but for any kind of app. When you connect an app, it gets the starter's settings, except where you have already set a value. When your team fixes a default, the fix goes into the starter's next version, and every new app gets it.

The Vercel, AWS Parameter Store and Daytona walkthroughs include a local rehearsal that needs no provider account. Starters are off until you switch them on. See [how to turn them on and write your own](docs/starters.md).

[Why durable config, and why now](docs/why-durable-config.md) gives the reasoning: why agents change what a platform is, one setup becoming two apps, and a comparison with platform engineering.

## Why `cub mini`

`cub` is ConfigHub's command-line tool, and it works with every hub. `cub mini` adds commands that each do a whole job in one step, and runs the same `cub` commands underneath ([`cub mini` and plain `cub`](docs/cub-mini-and-cub.md)).

## Commands in Claude Code

```
/confighub:changes        what agents changed, and why
/confighub:why LOG_LEVEL  every change to one setting, and what was asked each time
/confighub:inventory      what this repository deploys, and what deploys it
/confighub:permissions    what your agents may run
/confighub:checks         how closely MCP tool calls are watched
/confighub:install-mini   install confighub mini
/confighub:to-hub         copy the record into a hub
```

## Documentation

- **Get started:** [walkthroughs](examples/walkthroughs/README.md), [try the Claude plugin on its own](docs/try-the-plugin.md), [a new app](docs/journeys/new-app.md), [an app you already have](docs/journeys/existing-app.md), [an app Argo CD or Flux deploys](docs/journeys/gitops-app.md)
- **Concepts:** [how it works](docs/how-it-works.md), [approvals](docs/approvals.md), [starters](docs/starters.md), [from your laptop to a shared hub](docs/from-plugin-to-confighub.md), [agents that run for weeks](docs/agents-that-run-for-weeks.md), [signed records](docs/signed-records.md)
- **Reference:** [`cub mini` and plain `cub`](docs/cub-mini-and-cub.md), [installing the local hub](docs/install-mini.md), [integrations](docs/integrations.md), [going back](docs/journeys/going-back.md), [limits](docs/limits.md)
- **Other tools and setups:** [Codex](docs/codex.md), [CI and sandboxes](docs/ci-and-sandboxes.md), [Git and GitHub](docs/git-and-github.md), [Entire](docs/entire.md), [a VM](docs/vm.md), [a Helm chart you use, with your values](docs/your-own-chart.md), [GitOps over OCI](docs/gitops-over-oci.md), [software with ConfigHub inside](docs/journeys/bundled.md)

The [documentation index](docs/README.md) lists every page, with a line on each. [ConfigHub's own documentation](https://docs.confighub.com) covers the server.

## What's in this repository

The Claude plugin is in `plugins/confighub/`, built by each release, so please don't edit it here. The guides are in `docs/`, and runnable examples in `examples/`. [Contributing](CONTRIBUTING.md#whats-in-this-repository) lists every folder.

## Open, and yours to extend

- **The Claude plugin is MIT-licensed** ([LICENSE](LICENSE)). Third-party licenses are in [`plugins/confighub/THIRD_PARTY_LICENSES.txt`](plugins/confighub/THIRD_PARTY_LICENSES.txt).
- **A starter is a plain YAML file.** Write one, or ask your agent to, and share it ([write a starter](docs/write-a-starter.md)).
- **The UI and the SDKs are MIT-licensed too,** so you can build your own tools on a hub: [the UI](https://github.com/confighub/ui), [the SDK](https://github.com/confighub/sdk) and [the JavaScript SDK](https://github.com/confighub/js-sdk).
- **Contribute:** fix a guide, share an example or propose a starter ([contributing](CONTRIBUTING.md)). If something doesn't work, [report an issue](https://github.com/confighubai/confighub-mini-plugin/issues/new).

The local hub is the full ConfigHub server, free, in one download. **[Click here to download a full ConfigHub binary](docs/install-mini.md#the-current-release).**
