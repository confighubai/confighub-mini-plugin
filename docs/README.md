# Documentation

Every page about the ConfigHub plugin and confighub mini, grouped by what you're doing. New here? Start with the overview: https://confighub.github.io/helm-expt/ai-agents/, or the [README](../README.md) for installing and a first try.

Words we use on these pages:

- A **hub** is one running ConfigHub server, the place your app's settings are kept, with every change, who made it and why.
- **confighub mini** is a hub on your laptop, in a sandbox or in a CI job. It's free and needs no account.
- A **shared hub** is one your team reaches over the network: hosted ConfigHub, or the enterprise edition on your own servers. Some pages call it your organization's ConfigHub.
- The **plugin** is the ConfigHub plugin for Claude Code and Codex. Its **record** is what it writes down about each change an agent makes: the value, from what to what, and why.
- **Staging** takes an agent's changes right away. **Production**, called live in `cub` commands, changes only when you approve.
- A **starter** is one short file of default settings for a kind of app, each with its reason.

## Get started

| Page | What it's for |
|---|---|
| [Try the plugin on its own](try-the-plugin.md) | See the record at work in a minute, with no hub; what it records, and setting it up for your whole team |
| [A new app](journeys/new-app.md) | One request in Claude Code gives you the app, with staging and production settings in a hub |
| [An app you already have](journeys/existing-app.md) | Attach `.env` files, Terraform var files, Kustomize or Helm values, with your values kept as they are |
| [An app that Argo CD or Flux deploys](journeys/gitops-app.md) | A hub beside Git, a check on each pull request, or the hub as the app's source, and the way back |
| [A first run of confighub mini](try-confighub-mini.md) | Fifteen minutes: keep your own values through a chart's next version, and put the record in the hub |

## Concepts

| Page | What it's for |
|---|---|
| [When ConfigHub acts](agent-workflow.md) | Why ordinary coding requests don't start a hub, the one question the plugin may ask you, and where your app runs |
| [How the plugin works](how-it-works.md) | What agents are told and when, what's recorded and what never is, every setting, and the tokens each change cost |
| [Approvals](approvals.md) | An agent proposes a change to production and only the person you name approves it, including when one agent asks another for a change |
| [Starters](starters.md) | Your team's default settings for every new app. Your own values always win. Off unless you switch them on |
| [From your laptop to a shared hub](from-plugin-to-confighub.md) | Each step from the plugin to confighub mini to your organization's ConfigHub, and what it adds |
| [Agents that run for weeks](agents-that-run-for-weeks.md) | A key for each agent, approval of the exact change, stopping an agent, and limiting what it can reach |
| [Signed records](signed-records.md) | Checking that nobody tampered with the record, and having each agent sign its own changes |

## Reference

| Page | What it's for |
|---|---|
| [`cub mini` and plain `cub`](cub-mini-and-cub.md) | Which ConfigHub commands each `cub mini` command stands for |
| [Install confighub mini](install-mini.md) | Installing it from Claude Code, by hand or in a container; upgrading and removing it |
| [What a repository deploys](inventory.md) | `/confighub:inventory`: each app and chart, and what deploys it |
| [Working with the tools you already have](integrations.md) | What the plugin does with each tool, and how much of that we've tested |
| [Going back](journeys/going-back.md) | Undoing a step, taking your apps out as plain files, and removing each part |
| [Limits](limits.md) | What the plugin and confighub mini don't do, or haven't been shown to do |

## Other tools and setups

| Page | What it's for |
|---|---|
| [Codex](codex.md) | The one setup command Codex needs |
| [CI and sandboxes](ci-and-sandboxes.md) | The plugin in a job or a container, and keeping its record after the sandbox is deleted |
| [Agents in CI](../ci/README.md) | GitHub Actions jobs that run a coding agent, from the plugin alone to an agent whose changes a person approves |
| [Git and GitHub](git-and-github.md) | The plugin with Git and GitHub, `/confighub:to-hub`, and a hub beside Git |
| [The pull-request review](../review/README.md) | A comment on each pull request with every setting it changes, and why; no hub needed |
| [Entire](entire.md) | If you use [Entire](https://entire.io): `entire confighub why` gives the reason for a value, with each session's Entire checkpoint |
| [A service on a VM](vm.md) | A service's files written from the hub, with only approved values |
| [A Helm chart you use, with your values](your-own-chart.md) | Keep your own values, each with its reason, through a vendor chart's next version |
| [GitOps over OCI](gitops-over-oci.md) | Flux and Argo CD deploying what the hub approved |
| [Software with ConfigHub inside](journeys/bundled.md) | An app, platform or chart that comes with a hub: what exists today and what doesn't |
| [Runnable examples](../examples/roadmap/README.md) | A service on a VM with approval and rollback, settings reused across apps, and copying an app between hubs and back to plain files |
| [Extensions](../examples/extensions/config-snapshot/README.md) | A small program that reads one version of an app's settings from a hub, and an [experimental add-on](../examples/extensions/delivery/README.md) that delivers an approved version outside Kubernetes |

## How this was tested

| Page | What it's for |
|---|---|
| [What agents did with the plugin and without it](evidence.md) | Real sessions, quoted as the agents wrote them |
| [Evaluate it yourself](../evaluate/README.md) | The same evaluation, with your own models, in one command |
| [Run records](runs/README.md) | Each dated run the pages quote, as it came out |

[`llms.txt`](../llms.txt) lists every page for AI agents.
