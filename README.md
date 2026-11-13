# ConfigHub for AI agents

**Ship faster with coding agents. You decide what reaches production.**

ConfigHub is a small server, called a hub, that holds your app's settings. Your agents can change the staging settings whenever they like, but nothing changes in production until you say yes. And every change comes with a note on why it was made.

New here? Start with the overview: https://confighub.github.io/helm-expt/ai-agents/

Are you an AI agent, or asking one about this project? Have it read [AGENTS.md](AGENTS.md) first.

The hub can run on your laptop as [confighub mini](docs/install-mini.md), which is free and needs no account. We also run it for you as hosted ConfigHub, or you can run the enterprise edition on your own servers. Hosted ConfigHub and the enterprise edition support many people in one organization. The commands are the same everywhere, and when your team is ready you copy your apps from your laptop to the shared hub ([from your laptop to a shared hub](docs/from-plugin-to-confighub.md)).

**Get confighub mini** through the plugin (ask for an app "using ConfigHub", or type `/confighub:install-mini`), or on its own, without the plugin ([installing confighub mini](docs/install-mini.md), and the downloads on the [releases page](https://github.com/confighubai/confighub-mini-plugin/releases)).

This repository holds the ConfigHub plugin for Claude Code, the easiest way to start. It works with Codex too. From the first session it keeps a record of what your agents change and why, and tells the next agent before it undoes an earlier change. That needs no hub. When you ask for an app "using ConfigHub", it sets up a hub on your laptop.

It's for you if your coding agents change your app's settings and you want production to change only when you say so. The app can be new, or one you already have with `.env` files, Terraform var files, Helm values, or a Kustomize repository that Argo CD or Flux deploys.

## Install

You need Claude Code and Git. In a terminal:

```
claude plugin marketplace add confighubai/confighub-mini-plugin
claude plugin install confighub@confighub
```

It works on macOS and Linux. Codex needs [one more command](docs/codex.md). The first time you ask for a hub, the agent downloads confighub mini ([its size](docs/install-mini.md#the-current-release)). It doesn't need Docker.

## A first try

1. Make an empty folder and start Claude Code in it: `mkdir my-app && cd my-app && git init -q && claude`
2. Ask: `Build me a small web service using ConfigHub, with a staging and a production setup.`
3. The agent writes the app, starts confighub mini if no hub is running, and puts the staging and production settings in it. It ends with one command for you to paste into your own terminal: `cub mini approve`, with the full path to `cub`, ConfigHub's command-line tool.
4. Run it to approve production's starting settings. From then on, agents change staging right away, and production changes wait for you: `cub mini waiting` shows them, and `cub mini approve` or `cub mini refuse` decides.

[A new app](docs/journeys/new-app.md) explains each step, and the walkthrough [your first hour](examples/walkthroughs/story-13-first-hour.md) shows every command and what it prints. Already have an app? Ask the agent to "attach ConfigHub to this app". It won't touch your files ([an app you already have](docs/journeys/existing-app.md)). To remove confighub mini, run `cub mini uninstall --delete-data`. More walkthroughs, one for each tool, starter and user story, are in [walkthroughs](examples/walkthroughs/README.md).

## An example

You ask your agent to turn on debug logging, and staging and production both read the same `.env` file. Without ConfigHub, production starts logging customers' email addresses. With ConfigHub, staging and production get their settings from the hub instead. Staging gets debug logging right away, and production waits. `cub mini waiting` shows `LOG_LEVEL=info → LOG_LEVEL=debug`, and you refuse it with a reason: "Debug logs leak customer emails." The next agent that tries is told you said no, and why. An agent that also holds your cloud or cluster credentials can still go around this ([what an agent can reach](docs/agents-that-run-for-weeks.md#limiting-what-an-agent-can-reach)).

## Why `cub mini`

`cub` is ConfigHub's command-line tool, and it works with every hub. `cub mini` adds a few commands that each do a whole job in one step. `cub mini adopt` connects an app and makes its staging and production copies. `cub mini require-approval` puts production behind your yes and gives an agent a key that can suggest a change but not approve one. `cub mini approve` shows you the change before it approves it. With plain `cub`, each of these takes several commands, and agents get them wrong more often. Underneath, `cub mini` runs the same `cub` commands, so anything it does, you can also do with plain `cub` on any hub. [`cub mini` and plain `cub`](docs/cub-mini-and-cub.md) lists each command next to the `cub` commands it stands for.

## When agents do real work

Once agents run for hours, or several of them share an app, you'll want more control. A hub gives you:

- **A key for each agent,** with only the rights it needs. It can suggest a production change, but it can't approve one ([agent keys](docs/agents-that-run-for-weeks.md#who-acted-give-the-agent-a-key-of-its-own)).
- **Approval of the exact change.** Anything that comes after it needs its own approval ([approvals](docs/approvals.md)).
- **A way to stop them.** Take away one agent's access, or shut the hub down. The agent is cut off at its next request ([stopping an agent](docs/agents-that-run-for-weeks.md#stopping-an-agent)).
- **A record nobody can quietly edit.** Every change is signed when it's recorded, and one command tells you if anything was edited, added or deleted later ([signed records](docs/signed-records.md)).
- **Agents asking each other.** When one agent asks another for a change, the hub records who asked ([requests between agents](docs/approvals.md#one-agent-asks-another-for-a-change)).
- **What it cost.** Every change shows how many tokens the agent spent making it ([model use](docs/how-it-works.md#model-use)).

## Starters

A starter gives every new app of one kind your team's default settings, such as retries, timeouts and worker limits, each with a note on why it is set. It is one short YAML file, the same idea as a [Spring Boot starter](https://docs.spring.io/spring-boot/reference/using/build-systems.html#using.build-systems.starters) but for any kind of app. When you connect an app, it gets the starter's settings, except where you have already set a value. When your team fixes a default, the fix goes into the starter's next version, and every new app gets it.

confighub mini comes with starters for [a small web service](examples/walkthroughs/starter-web.md) and for a Kustomize repository that [Argo CD](examples/walkthroughs/starter-kustomize-argocd.md) or [Flux](examples/walkthroughs/starter-kustomize-flux.md) deploys. Starters for [apps on Vercel](examples/walkthroughs/starter-vercel.md), [apps that read AWS Parameter Store](examples/walkthroughs/starter-parameter-store.md) and [an experiment in a Daytona sandbox](examples/walkthroughs/starter-daytona.md) are in preview: each runs against a local stand-in with no account, or against your own account. Starters are off until you switch them on. [Starters](docs/starters.md) shows how to [switch them on](docs/starters.md#switch-starters-on), use them and [write your own](docs/starters.md#what-a-starter-is).

## Works with your tools

Git and GitHub, Argo CD and Flux, Vault, Sigstore, OpenTelemetry, Entire, Codex, and sandboxes and containers. [Integrations](docs/integrations.md) says what you get with each one and how far along it is.

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

If something doesn't work, open an [issue](https://github.com/confighubai/confighub-mini-plugin/issues) with the command you ran and what it printed. Fixes to the docs and examples are welcome as pull requests. Changes to `plugins/` belong in an issue.

The plugin is MIT-licensed ([LICENSE](LICENSE)). Third-party licenses are in [`plugins/confighub/THIRD_PARTY_LICENSES.txt`](plugins/confighub/THIRD_PARTY_LICENSES.txt).
