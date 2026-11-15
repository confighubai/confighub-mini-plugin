# ConfigHub: durable config for apps made with AI

**Your agent makes your apps. Durable config makes the platform.**

Ask a coding agent for an app and it writes the app, with a staging and a production setup. ConfigHub keeps that setup as durable config: every setting with its reason, kept through the next session, the next version and the next app. Kept that way, the setup of your apps is your platform. Your agent changes staging at once, and production changes when you say.

| 75 seconds | 10 seconds | 0 |
|---|---|---|
| from "build me an app" to an app with staging and production | for a hub to start on your laptop, with no Docker and no account | production changes an agent can approve by itself |

Start with the plugin alone. Add a free local hub when you want staging and production. It runs on macOS or Linux.

## Install

For Claude Code, run these two commands in a terminal:

```
claude plugin marketplace add confighubai/confighub-mini-plugin
claude plugin install confighub@confighub
```

Open a new session and [try the plugin without a hub](docs/try-the-plugin.md). Using Codex? Follow [the Codex setup](docs/codex.md), including its separate hook approval. You can also [install the local hub without a coding agent](docs/install-mini.md).

[Product overview](https://confighub.github.io/helm-expt/ai-agents/) · [Walkthroughs by stack](examples/walkthroughs/README.md) · [Instructions for AI agents](AGENTS.md)

## Why this, and why now

1. **People make and run apps by asking agents.** An agent changes settings many times a day, across staging, production and every customer's copy. That is faster than anyone reads a diff.
2. **So the platform has to come from somewhere else.** Staging, production, promotion, rollback and limits used to come from a platform team or a hosting service. An agent can now write them with the app. But they land in scattered files, the next session overwrites them, and every new app starts from nothing.
3. **ConfigHub keeps the setup, its changes and their context.** It keeps the setup itself, wherever the app runs, with every change to it and the context for each change: what was asked, and why. That is what durable means. What you and your agents decided is still there for:
   - **the next session**, which starts from what was set and why
   - **the next agent**, which is told before it undoes a value
   - **the next version**, which keeps your own values
   - **the next environment**, which takes exactly what you approved
   - **the next app**, which starts from the first

## An example: two apps from one setup

A web shop has two services, a storefront and an orders service.

1. **The first app gets a setup.** `cub mini adopt storefront` gives the storefront a staging and a production copy, with the team's settings from a [starter](docs/starters.md), a small YAML file. Each setting has its reason.
2. **A fix to the first app becomes part of the setup.** A colleague sets a request size limit and a rate limit on production, each with a reason, and adds both to the starter as version 2.
3. **The second app starts with the fix, and the first keeps its own values.** The orders service connects with version 2 and gets the limits, with their reasons. The storefront takes version 2 too, and keeps the 30-second cache its developer set for sales. Production changes only with an approval.

The walkthrough [Alice ships it, Bob hardens it](examples/walkthroughs/story-25-alice-bob-hardened.md) runs this on your laptop.

## Works with the tools and services you use

A [starter](docs/starters.md) wires an app into ConfigHub for you. It looks for what the app already uses, such as a Vercel project or a repository that Argo CD deploys, then sets up staging and production, puts production behind your approval, and connects delivery. It leaves alone anything you set yourself. That takes one command and one approval.

- **Where your app runs:** [Web](examples/walkthroughs/starter-web.md), [Vercel](examples/walkthroughs/starter-vercel.md), [AWS Parameter Store](examples/walkthroughs/starter-parameter-store.md), [Argo CD](examples/walkthroughs/starter-kustomize-argocd.md), [Flux](examples/walkthroughs/starter-kustomize-flux.md), [Daytona](examples/walkthroughs/starter-daytona.md), [Temporal worker](examples/walkthroughs/starter-temporal-worker.md) and [Unikraft](examples/walkthroughs/starter-unikraft.md).
- **Around the app:** Git and GitHub, Vault, Sigstore, SPIFFE, OpenTelemetry, Entire, MCP servers, sandboxes and containers, and Codex ([what you get with each](docs/integrations.md)).
- **No starter for your stack?** It is one YAML file, and your agent can write it ([write a starter](docs/write-a-starter.md)).

## Platforms were built before the apps. Agents build the app first.

Platform engineering builds a platform and fits apps to it. Durable config starts with the app and keeps what the agent set up for it, so the platform grows out of the apps.

| | Platform engineering as we know it | Durable config |
|---|---|---|
| What comes first | The platform, built by a team ahead of the apps | The app. Its setup becomes the base for the next one |
| How an app gets its setup | A template, copied once when the app is created | A starter the app stays linked to |
| Where the knowledge lives | Docs, tickets and the platform team's heads | With each value, as its reason |
| Who it is built for | People: portals, forms and golden-path guides | Agents and people |
| How a change spreads | One pull request in each repository | One change, read across every app |
| What it takes to start | A team and months | One yes at install |

ConfigHub doesn't run your app. Your cluster, hosting service or VM still does, and Argo CD and Flux still deliver to your clusters. It replaces the templates, the portal and the scattered settings files above them.

## Five ways it is better

1. **Nothing to build first.** A platform team spends months before the first app benefits. Here an agent asked for an app left it with staging and production in 75 seconds, in 16 of 16 of our runs.
2. **Templates that keep working after day one.** A scaffolded app is a copy made once, so the template's next version never reaches it. Here a [starter](docs/starters.md)'s next version reaches every app made from it, and each app keeps its own values and reasons. We have run ten apps taking one change this way.
3. **The reason travels with the value** (for agents). An agent can't ask the platform team why a limit is set as it is. Without the reason it "fixes" the value, and the next agent fixes it back. With [the record](docs/how-it-works.md), the next agent was told before undoing a value in 11 of 11 simulated weeks, and no value was undone silently.
4. **Guardrails that hold against agents** (for agents). Golden paths work because people read the guide and follow it. Agents do what the request says. Told "Priya said yes", agents with ordinary tools changed production in every run of that test. Agents need three things a portal doesn't give:
   - a key of their own
   - a staging copy they can change at once
   - a line they cannot cross

   The hub refuses an agent's own approval, and it is small enough to sit in every sandbox ([agent keys](docs/agents-that-run-for-weeks.md#who-acted-give-the-agent-a-key-of-its-own)).
5. **Configuration you can query and build on.** Platform stacks are a template language for each tool: Helm for clusters, Terraform for cloud, env files for hosting services. A change across the fleet is many pull requests. As data, "which version runs where" is one question, and one change is read across all apps, wherever they run. Tools are built on data, not on templates.

## Three ways to start

1. **A new app.** You want an app with a staging and a production setup. Ask Claude Code to build it "using ConfigHub" ([a new app](docs/journeys/new-app.md)).
2. **An app you already have.** Its settings live in `.env` files, Terraform var files, Helm values, or a Kustomize repository that Argo CD or Flux deploys. Ask the agent to "attach ConfigHub to this app". It won't touch your files ([an app you already have](docs/journeys/existing-app.md)).
3. **Software that comes with ConfigHub inside.** You change it to suit you and keep your changes when the next version arrives ([software with ConfigHub inside](docs/journeys/bundled.md)).

## A shared hub for your team

We run the hub for you as hosted ConfigHub, or you run the enterprise edition on your own servers. Both support many people in one organization. The commands are the same as on your laptop, and you copy your apps to the shared hub when your team is ready ([from your laptop to a shared hub](docs/from-plugin-to-confighub.md)).

## A first try, with a new app

1. Make an empty folder and start Claude Code in it: `mkdir my-app && cd my-app && git init -q && claude`
2. Ask: `Build me a small web service using ConfigHub, with a staging and a production setup.`
3. The agent writes the app, starts confighub mini if no hub is running, and puts the staging and production settings in it. It ends with one command for you to paste into your own terminal: `cub mini approve`, with the full path to `cub`, ConfigHub's command-line tool.
4. Run it to approve production's starting settings. From then on, agents change staging right away, and production changes wait for you: `cub mini waiting` shows them, and `cub mini approve` or `cub mini refuse` decides.

[A new app](docs/journeys/new-app.md) explains each step, and the walkthrough [your first hour](examples/walkthroughs/story-13-first-hour.md) shows every command and what it prints. Already have an app? Ask the agent to "attach ConfigHub to this app". It won't touch your files ([an app you already have](docs/journeys/existing-app.md)). To remove confighub mini, run `cub mini uninstall --delete-data`. More walkthroughs, for each tool and most starters and user stories, are in [walkthroughs](examples/walkthroughs/README.md).

## An example

You ask your agent to turn on debug logging, and staging and production both read the same `.env` file. Without ConfigHub, production starts logging customers' email addresses. With ConfigHub, staging and production get their settings from the hub instead. Staging gets debug logging right away, and production waits. `cub mini waiting` shows `LOG_LEVEL=info → LOG_LEVEL=debug`, and you refuse it with a reason: "Debug logs leak customer emails." The next agent that tries is told you said no, and why. An agent that also holds your cloud or cluster credentials can still go around this ([what an agent can reach](docs/agents-that-run-for-weeks.md#limiting-what-an-agent-can-reach)).

## Why `cub mini`

`cub` is ConfigHub's command-line tool, and it works with every hub. `cub mini` adds commands that each do a whole job in one step, such as `cub mini adopt` to connect an app and `cub mini approve` to approve a change after showing it to you. Underneath, it runs the same `cub` commands. [`cub mini` and plain `cub`](docs/cub-mini-and-cub.md) lists each one next to the `cub` commands it stands for.

## When agents do real work

Once agents run for hours, or several of them share an app, you'll want more control. A hub gives you:

- **A key for each agent,** with only the rights it needs. It can suggest a production change, but it can't approve one ([agent keys](docs/agents-that-run-for-weeks.md#who-acted-give-the-agent-a-key-of-its-own)).
- **Approval of the exact change.** Anything that comes after it needs its own approval ([approvals](docs/approvals.md)).
- **A way to stop them.** Take away one agent's access, or shut the hub down. The agent is cut off at its next request ([stopping an agent](docs/agents-that-run-for-weeks.md#stopping-an-agent)).
- **Signed records.** Verify whether signed entries were altered; some deletions need a copy kept elsewhere ([signed records](docs/signed-records.md)).
- **Agents asking each other.** On the same hub, `cub mini` can check and record a request from one agent to another ([requests between agents](docs/approvals.md#one-agent-asks-another-for-a-change)).
- **What it cost.** See token counts for supported sessions in which the client reports usage ([model use](docs/how-it-works.md#model-use)).

## Starters

A starter gives every new app of one kind your team's default settings, such as retries, timeouts and worker limits, each with a note on why it is set. It is one short YAML file, the same idea as a [Spring Boot starter](https://docs.spring.io/spring-boot/reference/using/build-systems.html#using.build-systems.starters) but for any kind of app. When you connect an app, it gets the starter's settings, except where you have already set a value. When your team fixes a default, the fix goes into the starter's next version, and every new app gets it.

Start with the walkthrough for your app: [Web](examples/walkthroughs/starter-web.md), [Argo CD](examples/walkthroughs/starter-kustomize-argocd.md), [AWS Parameter Store](examples/walkthroughs/starter-parameter-store.md), [Vercel](examples/walkthroughs/starter-vercel.md), [Flux](examples/walkthroughs/starter-kustomize-flux.md), [Daytona](examples/walkthroughs/starter-daytona.md), [Temporal worker](examples/walkthroughs/starter-temporal-worker.md), and [Unikraft](examples/walkthroughs/starter-unikraft.md). The Vercel, AWS Parameter Store and Daytona walkthroughs include a local rehearsal that needs no provider account. Starters are off until you switch them on. See [how to turn them on and write your own](docs/starters.md).

Then try [the cub mini tour](examples/walkthroughs/tool-cub-mini.md), [your first hour](examples/walkthroughs/story-13-first-hour.md), [approve from Slack](examples/walkthroughs/story-22-priya-slack.md), [size a service from real use](examples/walkthroughs/story-21-ana-sized.md), [Git, the hub and what is running](examples/walkthroughs/story-09-git-hub-and-running.md), and [one base for ten apps](examples/walkthroughs/story-24-company-base.md). Find more tools and user stories in the [walkthrough index](examples/walkthroughs/README.md).

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

- **Get started:** [walkthroughs](examples/walkthroughs/README.md), [try the plugin on its own](docs/try-the-plugin.md), [a new app](docs/journeys/new-app.md), [an app you already have](docs/journeys/existing-app.md), [an app Argo CD or Flux deploys](docs/journeys/gitops-app.md)
- **Concepts:** [how it works](docs/how-it-works.md), [approvals](docs/approvals.md), [starters](docs/starters.md), [from your laptop to a shared hub](docs/from-plugin-to-confighub.md), [agents that run for weeks](docs/agents-that-run-for-weeks.md), [signed records](docs/signed-records.md)
- **Reference:** [`cub mini` and plain `cub`](docs/cub-mini-and-cub.md), [installing confighub mini](docs/install-mini.md), [integrations](docs/integrations.md), [going back](docs/journeys/going-back.md), [limits](docs/limits.md)
- **Other tools and setups:** [Codex](docs/codex.md), [CI and sandboxes](docs/ci-and-sandboxes.md), [Git and GitHub](docs/git-and-github.md), [Entire](docs/entire.md), [a VM](docs/vm.md), [a Helm chart you use, with your values](docs/your-own-chart.md), [GitOps over OCI](docs/gitops-over-oci.md), [software with ConfigHub inside](docs/journeys/bundled.md)

The [documentation index](docs/README.md) lists every page, with a line on each. [ConfigHub's own documentation](https://docs.confighub.com) covers the server.

## What's in this repository

| Folder | What it is |
|---|---|
| `plugins/confighub/` | The plugin. Each release builds it, so please don't edit it here |
| `.claude-plugin/`, `.agents/` | The marketplace files Claude Code and Codex read |
| `docs/` | The guides |
| `review/` | A GitHub Action that comments on each pull request with every setting it changes, and why |
| `approval-check/` | A pull-request check that the settings match what the hub approved, for branch protection |
| `ci/` | GitHub Actions jobs that run a coding agent in CI |
| `examples/` | Runnable examples, such as a service on a Linux VM |
| `gitops/` | A small `docker` wrapper for kind clusters on OrbStack |
| `evaluate/` | Runs our evaluation of the plugin with your own models |
| `entire-plugin.yml` | Installs the plugin into the CLI of [Entire](https://entire.io), if you use it |
| `AGENTS.md`, `llms.txt` | What an AI agent should read first, and every page listed for AI agents |

## Help and contributing

If something doesn't work, [report an issue](https://github.com/confighubai/confighub-mini-plugin/issues/new). See [contributing](CONTRIBUTING.md) to fix a guide, share an example or propose a starter.

The plugin is MIT-licensed ([LICENSE](LICENSE)). Third-party licenses are in [`plugins/confighub/THIRD_PARTY_LICENSES.txt`](plugins/confighub/THIRD_PARTY_LICENSES.txt).
