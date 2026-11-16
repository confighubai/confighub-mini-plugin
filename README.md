# ConfigHub: durable config for apps made with AI

**Your agent makes your apps. Durable config makes the platform.**

ConfigHub keeps the settings of the apps you make with a coding agent, such as a log level, a cache switch or the number of instances. With each change it keeps what you asked the agent for.

A new agent session doesn’t know why the last one set a value. Ask one session to turn a cache on for a sale, and a later session chasing a memory leak turns it off. With ConfigHub, the later session is told the cache is on for the sale before it changes it.

Settings kept with their reasons are durable config. They are still there for the next session and the next version of the app. Your next app can start from the same settings instead of from nothing. What your apps share in this way is your platform: it grows from your apps, and nobody has to build it first.

Start with the Claude plugin alone: it keeps a record of the settings your agent changes and the reason for each, and `/confighub:why` shows them. Add a free local hub, a ConfigHub server that runs on your computer, when you want a staging copy of the app that your agent can change at once and a production copy that changes only when you approve. It runs on macOS or Linux with no ConfigHub account, Docker or Kubernetes.

## Install

For Claude Code, run these two commands in a terminal:

```
claude plugin marketplace add confighubai/confighub-mini-plugin
claude plugin install confighub@confighub
```

Open a new session and [try the plugin without a hub](docs/try-the-plugin.md). Using Codex? Follow [the Codex setup](docs/codex.md), including its separate hook approval. You can also [install the local hub without a coding agent](docs/install-mini.md).

[Product overview](https://confighub.github.io/helm-expt/ai-agents/) · [Walkthroughs by stack](examples/walkthroughs/README.md) · [Instructions for AI agents](AGENTS.md)

## Why this, and why now

1. **People make and run apps by asking agents.** An agent changes settings many times a day, across staging, production and every customer's copy. No one reads diffs that fast.
2. **So the platform has to come from somewhere else.** Staging, production, promotion, rollback and limits used to come from a platform team or a hosting service. An agent can now write them with the app. But they land in scattered files, the next session overwrites them, and every new app starts from nothing.
3. **ConfigHub keeps the setup, its changes and their context.** It keeps the setup itself, wherever the app runs, with every change to it and the context for each change: what was asked, and why. That is what durable means. What you and your agents decided is still there for:
   - **the next session**, which starts from what was set and why
   - **the next agent**, which is told before it undoes a value
   - **the next version**, which keeps your own values
   - **the next environment**, which takes exactly what you approved
   - **the next app**, which starts from the first

## An example: two apps from one setup

A developer builds a web shop with an agent. Their next app is a cart service.

1. **The first app gets a setup.** `cub mini adopt shop` gives the shop a staging and a production copy, with the team's settings from a [starter](docs/starters.md), a small YAML file. Each setting has its reason.
2. **A fix to the first app becomes part of the setup.** A teammate proposes warning-level logs and three instances for the next starter version, with a reason for each setting. The owner approves the version.
3. **The second app starts with the fix, and the first keeps its own values.** The cart service starts with the new settings. The shop takes the update and keeps its production log level. Production changes still go through their own approval.

The walkthrough [Alice ships it, Bob hardens it](examples/walkthroughs/story-25-alice-bob-hardened.md) runs this on your laptop.

## Give your app a starting setup

A [starter](docs/starters.md) recognizes the tools your app already uses and fills in settings you haven’t set. It makes staging and production copies in ConfigHub. Some starters also connect delivery. Pick the guide for your app to see what it does and where you’ll be asked to approve a change.

- **Where your app runs:** [Web](examples/walkthroughs/starter-web.md), [Vercel](examples/walkthroughs/starter-vercel.md), [Next.js on Vercel](docs/nextjs-on-vercel.md), [AWS Parameter Store](examples/walkthroughs/starter-parameter-store.md), [Argo CD](examples/walkthroughs/starter-kustomize-argocd.md), [Flux](examples/walkthroughs/starter-kustomize-flux.md), [Daytona](examples/walkthroughs/starter-daytona.md), [Temporal worker](examples/walkthroughs/starter-temporal-worker.md), [Unikraft](examples/walkthroughs/starter-unikraft.md), and [Rails on Fly](docs/rails-on-fly.md).
- **Around the app:** Git and GitHub, Vault, Sigstore, SPIFFE, OpenTelemetry, Entire, MCP servers, sandboxes and containers, and Codex ([Integrations](docs/integrations.md) says what you get with each and how far along it is).

## How one app’s setup becomes a starting point

Platform engineering builds a platform and fits apps to it. Durable config starts with the app, so the platform grows out of the apps.

| | Platform engineering as we know it | Durable config |
|---|---|---|
| What comes first | The platform, built by a team ahead of the apps | The app. Its setup becomes the base for the next one |
| How an app gets its setup | A template, copied once when the app is created | A starter the app stays linked to |
| Where the knowledge lives | Docs, tickets and the platform team's heads | With each value, as its reason |
| Who it is built for | People: portals, forms and golden-path guides | Agents and people |
| How a change spreads | One pull request in each repository | One change, read across every app |
| Where you can start | With a platform team | With one app on your computer |

ConfigHub doesn't run your app. Your cluster, hosting service or VM still does, and Argo CD and Flux still deliver to your clusters. It replaces the templates, the portal and the scattered settings files above them.

## Five ways it is better

1. **Nothing to build first.** Start with an app. Its staging and production setup can become the starting point for the next app.
2. **Templates that keep working after day one.** A scaffolded app is a copy made once, so the template's next version never reaches it. Here a [starter](docs/starters.md)'s next version reaches every app made from it, and each app keeps its own values and reasons.
3. **The reason travels with the value** (for agents). An agent can't ask the platform team why a limit is set as it is. Without the reason it "fixes" the value, and the next agent fixes it back. With the record, the next agent can see why a value was chosen before changing it. [How the Claude plugin works](docs/how-it-works.md).
4. **Let agents change staging.** Give them what they need to try a change. The owner still decides what reaches production:
   - a key of their own
   - a staging copy they can change at once
   - a line they cannot cross

   The hub refuses an agent's own approval, and it is small enough to sit in every sandbox ([agent keys](docs/agents-that-run-for-weeks.md#who-acted-give-the-agent-a-key-of-its-own)).
5. **Configuration you can query and build on.** Platform stacks are a template language for each tool: Helm for clusters, Terraform for cloud, env files for hosting services. A change across the fleet is many pull requests. As data, "which version runs where" is one question, and one change is read across all apps, wherever they run. Tools are built on data, not on templates.

## Three ways to start

1. **Make a new app.** Ask Claude Code to build it "using ConfigHub". It writes the app and gives it a staging and a production setup ([a new app](docs/journeys/new-app.md)).
2. **Attach an app you already have.** Its settings live in `.env` files, Terraform var files, Helm values, or a Kustomize repository that Argo CD or Flux deploys. Ask the agent to "attach ConfigHub to this app". It won't touch your files ([an app you already have](docs/journeys/existing-app.md)).
3. **Use a starter.** [Pick one for your app](docs/starters.md) to fill in settings and see what it can connect.

Some software comes with a hub inside. You change it to suit you, and keep your changes when its next version arrives ([software with ConfigHub inside](docs/journeys/bundled.md)).

## A shared hub for your team

Use a shared hub on confighub.com or run one on your own servers. The commands work the same way. Copy your apps over when your team is ready ([from your laptop to a shared hub](docs/from-plugin-to-confighub.md)).

## A first try, with a new app

1. Make an empty folder and start Claude Code in it: `mkdir my-app && cd my-app && git init -q && claude`
2. Ask: `Build me a small web service using ConfigHub, with a staging and a production setup.`
3. The agent writes the app, starts the local hub if no hub is running, and puts the staging and production settings in it. It ends with one command for you to paste into your own terminal: `cub mini approve`, with the full path to `cub`, ConfigHub's command-line tool.
4. Run it to approve production's starting settings. From then on, agents change staging right away, and production changes wait for you: `cub mini waiting` shows them, and `cub mini approve` or `cub mini refuse` decides.

[A new app](docs/journeys/new-app.md) explains each step, and the walkthrough [your first hour](examples/walkthroughs/story-13-first-hour.md) shows every command and what it prints. Already have an app? Ask the agent to "attach ConfigHub to this app". It won't touch your files ([an app you already have](docs/journeys/existing-app.md)). To remove the local hub, run `cub mini uninstall --delete-data`. More walkthroughs, for each tool and most starters and user stories, are in [walkthroughs](examples/walkthroughs/README.md).

## An example

You ask your agent to turn on debug logging, and staging and production both read the same `.env` file. Without ConfigHub, production starts logging customers' email addresses. With ConfigHub, staging and production get their settings from the hub instead. Staging gets debug logging right away, and production waits. `cub mini waiting` shows `LOG_LEVEL=info → LOG_LEVEL=debug`, and you refuse it with a reason: "Debug logs leak customer emails." The next agent that tries is told you said no, and why. An agent that also holds your cloud or cluster credentials can still go around this ([what an agent can reach](docs/agents-that-run-for-weeks.md#limiting-what-an-agent-can-reach)).

## Why `cub mini`

`cub` is ConfigHub's command-line tool, and it works with every hub. `cub mini` adds commands that each do a whole job in one step, such as `cub mini adopt` to connect an app and `cub mini approve` to approve a change after showing it to you. Underneath, it runs the same `cub` commands. [`cub mini` and plain `cub`](docs/cub-mini-and-cub.md) lists each one next to the `cub` commands it stands for.

## When more people or agents share an app

Once agents run for hours, or several of them share an app, you'll want more control. A hub gives you:

- **A key for each agent,** with only the rights it needs. It can suggest a production change, but it can't approve one ([agent keys](docs/agents-that-run-for-weeks.md#who-acted-give-the-agent-a-key-of-its-own)).
- **Approval of the exact change.** Anything that comes after it needs its own approval ([approvals](docs/approvals.md)).
- **A way to stop them.** Take away one agent's access, or shut the hub down. The agent is cut off at its next request ([stopping an agent](docs/agents-that-run-for-weeks.md#stopping-an-agent)).
- **Signed records.** Verify whether signed entries were altered; some deletions need a copy kept elsewhere ([signed records](docs/signed-records.md)).
- **Agents asking each other.** On the same hub, `cub mini` can check and record a request from one agent to another ([requests between agents](docs/approvals.md#one-agent-asks-another-for-a-change)).
- **What it cost.** See token counts for supported sessions in which the client reports usage ([model use](docs/how-it-works.md#model-use)).

## Starters

A starter gives every new app of one kind your team's default settings, such as retries, timeouts and worker limits, each with a note on why it is set. It is one short YAML file, the same idea as a [Spring Boot starter](https://docs.spring.io/spring-boot/reference/using/build-systems.html#using.build-systems.starters) but for any kind of app. When you connect an app, it gets the starter's settings, except where you have already set a value. When your team fixes a default, the fix goes into the starter's next version, and every new app gets it.

The Vercel, AWS Parameter Store and Daytona walkthroughs include a local rehearsal that needs no provider account. Starters are off until you switch them on. See [how to turn them on and write your own](docs/starters.md).

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

- **Get started:** [walkthroughs](examples/walkthroughs/README.md), [try the Claude plugin on its own](docs/try-the-plugin.md), [a new app](docs/journeys/new-app.md), [an app you already have](docs/journeys/existing-app.md), [an app Argo CD or Flux deploys](docs/journeys/gitops-app.md)
- **Concepts:** [how it works](docs/how-it-works.md), [approvals](docs/approvals.md), [starters](docs/starters.md), [from your laptop to a shared hub](docs/from-plugin-to-confighub.md), [agents that run for weeks](docs/agents-that-run-for-weeks.md), [signed records](docs/signed-records.md)
- **Reference:** [`cub mini` and plain `cub`](docs/cub-mini-and-cub.md), [installing the local hub](docs/install-mini.md), [integrations](docs/integrations.md), [going back](docs/journeys/going-back.md), [limits](docs/limits.md)
- **Other tools and setups:** [Codex](docs/codex.md), [CI and sandboxes](docs/ci-and-sandboxes.md), [Git and GitHub](docs/git-and-github.md), [Entire](docs/entire.md), [a VM](docs/vm.md), [a Helm chart you use, with your values](docs/your-own-chart.md), [GitOps over OCI](docs/gitops-over-oci.md), [software with ConfigHub inside](docs/journeys/bundled.md)

The [documentation index](docs/README.md) lists every page, with a line on each. [ConfigHub's own documentation](https://docs.confighub.com) covers the server.

## What's in this repository

| Folder | What it is |
|---|---|
| `plugins/confighub/` | The Claude plugin. Each release builds it, so please don't edit it here |
| `.claude-plugin/`, `.agents/` | The marketplace files Claude Code and Codex read |
| `docs/` | The guides |
| `review/` | A GitHub Action that comments on each pull request with every setting it changes, and why |
| `approval-check/` | A pull-request check that the settings match what the hub approved, for branch protection |
| `ci/` | GitHub Actions jobs that run a coding agent in CI |
| `examples/` | Runnable examples, such as a service on a Linux VM |
| `gitops/` | A small `docker` wrapper for kind clusters on OrbStack |
| `evaluate/` | Runs our evaluation of the Claude plugin with your own models |
| `entire-plugin.yml` | Installs the Claude plugin into the CLI of [Entire](https://entire.io), if you use it |
| `AGENTS.md`, `llms.txt` | What an AI agent should read first, and every page listed for AI agents |

## Open, and yours to extend

- **The Claude plugin is MIT-licensed** ([LICENSE](LICENSE)). Third-party licenses are in [`plugins/confighub/THIRD_PARTY_LICENSES.txt`](plugins/confighub/THIRD_PARTY_LICENSES.txt).
- **A starter is a plain YAML file.** Write one, or ask your agent to, and share it ([write a starter](docs/write-a-starter.md)).
- **The UI and the SDKs are MIT-licensed too,** so you can build your own tools on a hub: [the UI](https://github.com/confighub/ui), [the SDK](https://github.com/confighub/sdk) and [the JavaScript SDK](https://github.com/confighub/js-sdk).
- **Contribute:** fix a guide, share an example or propose a starter ([contributing](CONTRIBUTING.md)). If something doesn't work, [report an issue](https://github.com/confighubai/confighub-mini-plugin/issues/new).

The local hub is the full ConfigHub server, free, in one download. **[Click here to download a full ConfigHub binary](docs/install-mini.md#the-current-release).**
