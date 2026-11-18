# ConfigHub for your first app

Build your first app with Claude Code or Codex, or open one you already run. The plugin remembers why a setting changed. A local hub adds previews and settings you can reuse.

**[Three things to try first](https://confighub.github.io/helm-expt/ai-agents/first-look.html)** shows what you do, what your agent does and how to check the result.

- **[Remember one setting in five minutes](docs/try-the-plugin.md#try-it-in-five-minutes)**. Ask “Turn the cache on for next week’s sale. Don’t commit.” In a fresh session ask “Why is the cache on?” Your agent should recover the change and the sale reason. No hub needed.
- **[Run a preview of my app](docs/journeys/existing-app.md#run-a-preview-of-my-app)**. In a local Node app, ask “Try a warmer greeting in preview.” Your agent gives you the address. Open it, then ask a fresh app session what’s running.

Reviewing someone’s changes? [See reasons on a pull request](review/README.md) or [compare Git, the hub and the cluster](examples/walkthroughs/story-09-git-hub-and-running.md).

| Where are you starting? | What to try |
| --- | --- |
| **From scratch** | In an empty Git folder, ask: “Build a small greeting app using ConfigHub. Give it a configurable greeting and run it locally.” The local hub keeps separate staging and production settings. [Build your first app](docs/journeys/new-app.md). |
| **Halfway through building** | Install the plugin and reopen the same project. Ask: “Turn the cache on in `.env` for Friday’s sale.” In a fresh Claude Code session, type `/confighub:why CACHE` to find that change and your request. Recording starts when you install and reopen. [Try it on one setting](docs/try-the-plugin.md#try-it-in-five-minutes). |
| **Already running an app** | Ask: “Attach ConfigHub to this app. I want to try a change in staging.” It reads the settings your files already hold without rewriting them or switching your deployment. Connect delivery when you want the running app to use what you approve. [Attach an existing app](docs/journeys/existing-app.md). |

**What did the preview actually show?** In a local macOS run with fresh Codex sessions, the greeter answered these HTTP requests:

| What changed | Staging served | Production served |
| --- | --- | --- |
| Only preview served **Welcome to the neighborhood!** | Hello, world! | Hello, world! |
| The new greeting became the shared default | Welcome to the neighborhood! | Hello, world! |

After approval, production served **Welcome to the neighborhood!** too. Then a fresh session built a catalog in a new folder, linked to the greeter’s setup. The catalog served the same greeting in staging **without a greeting in its own settings file**. Its production copy needed its own approval. This local run used a scripted owner. [Try it in Codex](docs/codex.md#try-a-change-and-start-a-second-app).

## Install

For Claude Code, run these two commands in a terminal:

```
claude plugin marketplace add confighubai/confighub-mini-plugin
claude plugin install confighub@confighub
```

Open a fresh Claude Code session after installing. Ask Claude to change a setting, then type `/confighub:why SETTING` in Claude Code to see the change and the request behind it. The record stays on your computer. [Install the local hub on its own](docs/install-mini.md).

**Using the Codex CLI?** With Git installed, paste this in Terminal to install the released hooks and app workflow:

```sh
git clone --depth 1 --branch v0 https://github.com/confighubai/confighub-mini-plugin.git "$HOME/confighub-mini-plugin" &&
  "$HOME/confighub-mini-plugin/plugins/confighub/bin/confighub" mini codex-setup
```

In the Codex CLI, open `/hooks`, review and approve the ConfigHub hooks, then start a fresh session in your app’s folder. [Codex setup and removal](docs/codex.md#set-it-up).

[Product overview](https://confighub.github.io/helm-expt/ai-agents/) · [Walkthroughs by stack](examples/walkthroughs/README.md) · [Instructions for AI agents](AGENTS.md)

## Why this, and why now

1. **Agents change settings across environments.** A change meant for staging can affect production if both read the same file.
2. **The next session needs context.** When a limit is spread across files, a new agent can miss why you raised it in the first place.
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

## When the record is not enough, add a hub

A hub adds control to the record: a staging and a production copy of each app's settings, approval, a key for each agent, and delivery. Add one when you need it, and stop at any step.

| When this happens | What you add | What you get |
|---|---|---|
| You open a repository you did not write | `/confighub:inventory`, in the Claude plugin | What the repository deploys, and what deploys it, before anyone changes it ([inventory](docs/inventory.md)) |
| A teammate reviews a pull request | The [review action](review/README.md) for GitHub | A comment on each pull request with every setting it changes, and why |
| You want your agent to try things without touching production | `/confighub:staging` in the app's folder: a local hub, free and with no account | A staging copy your agent changes at once, and a production copy that changes only when you approve ([a new app](docs/journeys/new-app.md)) |
| Someone else's next version would overwrite your values | The same local hub | You take the new version and keep the values you changed, each with its reason ([keep your changes](examples/walkthroughs/story-02-keep-your-changes.md), [a Helm chart you use](docs/your-own-chart.md)) |
| Your app runs on Vercel or Fly | The same local hub | When you approve a production change, the same command puts it live on the host, and a change still waiting is not sent ([Next.js on Vercel](docs/nextjs-on-vercel.md), [Rails on Fly](docs/rails-on-fly.md)) |
| You start a second app | `/confighub:start-from APP` in its folder, or a [starter](docs/starters.md) for a team's defaults | The second app starts with the first's settings and keeps its own values. A fix to a starter reaches every app made from it |
| An agent works in a sandbox or a CI job | A hub of its own for that run | The agent makes its fix there and writes it out for a person to review, and the hub is deleted with the run ([a hub for each agent run](examples/walkthroughs/story-03-a-hub-per-agent-run.md)) |
| A teammate joins, or agents run for hours | A shared hub, on confighub.com or on your own servers | A key for each agent, which can propose a production change and cannot approve one. A way to cut one agent off. Signed records ([agents that run for weeks](docs/agents-that-run-for-weeks.md)) |
| You run many apps on clusters | The hub as the source Argo CD or Flux pulls from | What you approved is what they deploy, and "which version runs where" is one question ([GitOps over OCI](docs/gitops-over-oci.md)) |

The local hub is the full ConfigHub server, and the commands work the same way on a shared hub. Copy your apps over when your team is ready ([from your laptop to a shared hub](docs/from-plugin-to-confighub.md)).

## A first try, with a new app

After [installing](#install), start Claude Code in an empty Git folder: `mkdir my-app && cd my-app && git init -q && claude`. Ask for the greeting app above. Review production’s starting settings with the exact command the agent gives you. Then ask: “Try a warmer greeting in preview and show me what it serves.” [New app guide](docs/journeys/new-app.md) · [Your first hour](examples/walkthroughs/story-13-first-hour.md).

## Find your stack

Some software comes with a hub inside. You change it to suit you, and keep your changes when its next version arrives ([software with ConfigHub inside](docs/journeys/bundled.md)).

- **Where your app runs:** [Web](examples/walkthroughs/starter-web.md), [Vercel](examples/walkthroughs/starter-vercel.md), [Next.js on Vercel](docs/nextjs-on-vercel.md), [AWS Parameter Store](examples/walkthroughs/starter-parameter-store.md), [Argo CD](examples/walkthroughs/starter-kustomize-argocd.md), [Flux](examples/walkthroughs/starter-kustomize-flux.md), [Daytona](examples/walkthroughs/starter-daytona.md), [Temporal worker](examples/walkthroughs/starter-temporal-worker.md), [Unikraft](examples/walkthroughs/starter-unikraft.md), and [Rails on Fly](docs/rails-on-fly.md).
- **Around the app:** Git and GitHub, Vault, Sigstore, SPIFFE, OpenTelemetry, Entire, MCP servers, sandboxes and containers, and Codex ([Integrations](docs/integrations.md) says what you get with each and how far along it is).

A starter is one short YAML file of default settings, such as retries, timeouts and worker limits, each with a note on why it is set: the same idea as a [Spring Boot starter](https://docs.spring.io/spring-boot/reference/using/build-systems.html#using.build-systems.starters), for any kind of app. An app you connect gets the starter's settings, except where you already set a value.

The Vercel, AWS Parameter Store and Daytona walkthroughs include a local rehearsal that needs no provider account. Starters are off until you switch them on. See [how to turn them on and write your own](docs/starters.md).

[Why not just Git, your hosting service or a rules file](docs/why-durable-config.md) compares each with ConfigHub, and shows one team running ten services with many agents.

## Why `cub mini`

`cub` is ConfigHub's command-line tool, and it works with every hub. `cub mini` adds commands that each do a whole job in one step, and runs the same `cub` commands underneath ([`cub mini` and plain `cub`](docs/cub-mini-and-cub.md)).

## Commands in Claude Code

```
/confighub:changes        what agents changed, and why
/confighub:why LOG_LEVEL  every change to one setting, and what was asked each time
/confighub:inventory      what this repository deploys, and what deploys it
/confighub:permissions    what your agents may run
/confighub:checks         how closely MCP tool calls are watched
/confighub:to-hub         copy the record into a hub
/confighub:staging        a staging and a production copy for this app
/confighub:start-from APP start this app from another app in the hub
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
