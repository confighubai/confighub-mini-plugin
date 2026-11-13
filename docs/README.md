# Documentation

Every page about the ConfigHub plugin and confighub mini, grouped by what you're doing. To see a job done from start to finish, with every command and what it prints, pick one of [the walkthroughs](../examples/walkthroughs/README.md): one for each tool, each starter and each user story. New here? Start with the overview: https://confighub.github.io/helm-expt/ai-agents/, or the [README](../README.md) for installing and a first try.

The words these pages use, such as *hub*, *base*, *change order* and *Space*, are explained in [Words](#words), at the end of this page.

## Get started

| Page | What it's for |
|---|---|
| [Walkthroughs](../examples/walkthroughs/README.md) | One job from start to finish for each tool, starter and user story, with every command and what it prints |
| [Try the plugin on its own](try-the-plugin.md) | See the record at work, with no hub; what it records, and setting it up for your whole team |
| [A new app](journeys/new-app.md) | One request in Claude Code gives you the app, with staging and production settings in a hub |
| [An app you already have](journeys/existing-app.md) | Attach `.env` files, Terraform var files, Kustomize or Helm values, with your values kept as they are |
| [An app that Argo CD or Flux deploys](journeys/gitops-app.md) | A hub beside Git, a check on each pull request, or the hub as the app's source, and the way back |
| [Install confighub mini](install-mini.md) | The hub on your laptop, free and with no account: from Claude Code in one step, or on its own without the plugin; upgrading and removing it |
| [A first run of confighub mini](try-confighub-mini.md) | Install it, try one story, put your agents' record into the hub, and tell us how it went |

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
| [What a repository deploys](inventory.md) | `/confighub:inventory`: each app and chart, and what deploys it |
| [Working with the tools you already have](integrations.md) | What the plugin does with each tool, and how far along each one is |
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
| [Testing the plugin and confighub mini](testing.md) | Runnable checks, comparisons and evidence by task |
| [What agents did with the plugin and without it](evidence.md) | Real sessions, quoted as the agents wrote them |
| [Evaluate it yourself](../evaluate/README.md) | The same evaluation, with your own models, in one command |
| [Run records](runs/README.md) | Each dated run, as it came out |

## Words

Every page uses these words in the same sense. A page links here instead of repeating them.

- **ConfigHub** is a server that keeps your apps' configuration with every change, who made it and why, and holds a change to production until a person approves it. A **hub** is one running ConfigHub server.
- **confighub mini** is ConfigHub made small enough to run a hub on one machine, such as a laptop, a sandbox or a CI job. The server and its PostgreSQL database run as two ordinary processes. It is free and needs no account, no Docker and no cluster ([install it](install-mini.md)).
- A **shared hub** is one your team reaches over the network: hosted ConfigHub, which we run for you, or ConfigHub's enterprise edition on your own servers. Both support many people in one organization. Some pages call it your organization's ConfigHub.
- **`cub`** is ConfigHub's command-line tool, and works with every hub. **`cub mini`** is the set of commands confighub mini adds to it; each runs `cub`'s own commands and fills in the rest of the request ([which](cub-mini-and-cub.md)). A **context** is a named hub and sign-in that `cub` uses.
- The **plugin** is the ConfigHub plugin for Claude Code and Codex. Its **record** is what it writes down about each change an agent makes: the value, from what to what, the request behind it and the reason. A **session** is one Claude Code or Codex conversation, from start to `/exit`, and a **turn** is one request you make in it and the agent's work on that request.
- A **Space** is a folder in a hub. It holds configuration as **Units**: one Unit for each file or resource. A name such as `pattern-web/web-service` is the Unit `web-service` in the Space `pattern-web`. A **revision** is one saved state of a Unit; the hub numbers each change to a Unit as its next revision.
- A **Component** is one app or piece of software, such as `api`. Its **base**, such as the Space `api-base`, holds the settings every copy shares, so a change is made once. A **variant**, or **copy**, is made from the base for one place the app runs, and keeps its **own values**, the ones it sets differently, when the base changes. **Staging** takes a change to the base at once. **Production**, the copy `cub` commands call **live** (`api-live`), takes a change only when you approve it.
- A **change order** asks for a change to reach a copy, usually production. It waits until a person **approves** it, with `cub mini approve`, or **refuses** it, with `cub mini refuse`. A **ChangeWorkflow** says what a change order needs first, such as a named person's approval. ConfigHub keeps each approval as an **attestation**: who approved, when and why, covering one revision.
- To **promote** a copy is to bring the base's changes into it. A **release** is a numbered, published version of a copy that a cluster pulls. A **target** is the cluster or service a copy is aimed at.
- A **service account** is an account for a program, such as an agent, rather than a person. Its **key** is a private key in a file, which the program signs in with. **The agent's key**, which `cub mini require-approval --agent` makes, can change the base and staging and propose a change to production, and cannot approve one. A **reader key** can read one copy and nothing else, for the machine or the add-on that delivers it.
- A **Link** ties a value in one Unit to another Unit, such as a database's address to the database's provider, so that a change to the provider reaches the copy.
- A **starter** is one short file of default settings for a kind of app, each with its reason ([starters](starters.md)). A **pattern** is a set of shared defaults kept in the hub, such as `pattern-web`, that apps are made from; each app keeps its own values over them.
- A **provider** is a service that runs an app and takes its settings, such as Vercel. An **add-on** is the small program that delivers an approved copy to a provider.
- **Argo CD** and **Flux** are GitOps controllers. They run in a cluster and keep it matching configuration they pull from a source, usually a Git repository. **Self-heal** means the controller puts back a change made on the cluster by hand. **OCI** is the format and protocol container registries use. Each hub has an OCI registry, which Argo CD and Flux can pull from as they pull images. **k8sbot** is ConfigHub's small program in the cluster that asks the controller to deploy each release, and reports back whether it is running; some `cub` messages and names still use its old name, argobot.
- A **snapshot** is one pinned revision of a copy, as a program reads it ([the snapshot contract](../examples/extensions/config-snapshot/README.md)).

[`llms.txt`](../llms.txt) lists every page for AI agents.
