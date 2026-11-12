# Documentation

The pages are grouped by what you are doing. Each page starts by saying who it is for and what you get from it. To see how the plugin, confighub mini and your organization's ConfigHub fit together, start with [from the plugin to ConfigHub](from-plugin-to-confighub.md). For an AI agent, [`llms.txt`](../llms.txt) lists every page with the question it answers.

**One app, two people.** You ship an app with your agent, and approve what reaches production ([a new app](journeys/new-app.md)). Then someone makes it fit for production, each value with its reason, and shares the setup; your next app starts from their fixes ([an app from a setup someone shared](from-plugin-to-confighub.md#an-app-from-a-setup-someone-shared)). Two people sharing one hub in the cloud is not available yet. Today each of you runs a hub on your own machine and you share setups as files, or you share one hub on a server you both reach.

## What are you doing?

| You are | Start here | You end with |
|---|---|---|
| In Claude Code, making a new app | [A new app](journeys/new-app.md) | The app, staging configuration that takes changes at once, and live configuration that changes only when you approve; a second app made from the first |
| In Claude Code, changing an app you already have: `.env` files, Terraform var files, a Kustomize repository or Helm values | [An app you already have](journeys/existing-app.md) | Your staging and production values kept exactly as they are, your files unchanged, and changes to live configuration waiting for your approval |
| Running an app that Argo CD or Flux deploys from Git | [An app that Argo CD or Flux deploys](journeys/gitops-app.md) | The hub beside Git, a check on each pull request, or the hub as the app's source; and the way back to Git |
| Using software that came with ConfigHub inside it | [Software with ConfigHub inside](journeys/bundled.md) | What exists today, what does not, and how to keep your changes through its next version |
| Letting agents change configuration, and wanting them to stop undoing each other | [The README](../README.md) | A record of what each agent changed and why, told to the next agent; no hub, no account |
| Growing from your laptop to your team | [From the plugin to ConfigHub](from-plugin-to-confighub.md) | Each step from the plugin to confighub mini to your organization's ConfigHub, with what it adds |
| Undoing a step, or leaving | [Going back](journeys/going-back.md) | Your apps as plain files with each reason, and each part removed |

A few words used throughout:
- **The record** is what the plugin writes down about each change an agent makes to your configuration: the value, from what to what, and why.
- **A hub** is a place where configuration is kept, with every change, who made it and why. **ConfigHub** is that hub.
- **confighub mini** is ConfigHub made small enough that every agent can have a hub of its own: on your laptop, in a sandbox or in a CI job.

**Not using Kubernetes yet?** [Compare the plugin, mini hub and shared hub](from-plugin-to-confighub.md#before-you-use-kubernetes). All three offer value for apps outside Kubernetes. The comparison separates hub hosting from app deployment.

Run [four product examples](../examples/roadmap/README.md): a VM service with approval and rollback, reused settings, a hub round trip, and a scoped [extension](../examples/extensions/config-snapshot/README.md).

An experimental [delivery add-on contract](../examples/extensions/delivery/README.md) applies one approved revision to a provider. It has been tried against a directory stand-in only, not a real provider.

## Where the app runs

An app can run on your own machine, on another machine, in a CI job, on one sandbox node or across many sandbox nodes, in a shared development cluster, and onward through staging to production. Each is a useful place to start or stay. A CI test or a temporary sandbox does not need to become a production service.

An app can have several running copies, each with its own settings and lifetime. Several sandbox nodes might run independent copies for parallel tests, or parts of one distributed app. A shared development cluster might run several apps and environments.

The hub keeps configuration for those copies. The hub's location and the app's location are separate choices. Creating staging and live configuration in a hub does not start those services; a process or deployment system must read the configuration and run the app.

For the paths documented here, see [CI and sandboxes](ci-and-sandboxes.md), [a service on a VM](vm.md), and [Flux or Argo CD deploying from the hub](gitops-over-oci.md). Each guide says what was tested. A remote service needs a hub it can reach, and production approval depends on its deployment path using the approved configuration.

## Using the plugin

| Page | What it answers |
|---|---|
| [The README](../README.md) | What the plugin does, how to install it, and a five-minute try |
| [What a repository deploys](inventory.md) | `/confighub:inventory`: each app and chart, what deploys it, what nothing deploys, how environments differ, and what agents changed |
| [How it works](how-it-works.md) | What the agent is given and when, the stop before an undo, what is recorded and what never is, every setting, and keeping the record out of the agent's reach |
| [The evidence](evidence.md) | What agents did with the plugin and without it, in hundreds of real sessions, quoted as they wrote it; and what a request for an app with ConfigHub, a try in a copy, a Postgres or a shared setup gave, in measured sessions |
| [The pull-request review](../review/README.md) | A comment on each pull request with every configuration value it changes, and why; no install, no account |
| [Git, GitHub and a hub](git-and-github.md) | What the plugin does with Git and GitHub, a hub with no confighub mini (`/confighub:to-hub`), and a hub beside Git with branch protection |
| [Working with the tools you already have](integrations.md) | What the plugin does with each tool, how to set it up, and how far it has been run |
| [In CI or a sandbox](ci-and-sandboxes.md) | The plugin in a job or a container, and keeping its record when the sandbox goes |
| [In Codex](codex.md) | Setting it up in Codex, which runs only the hooks in its own configuration |
| [If you use Entire](entire.md) | `entire confighub why`: the reason for a value, with the Entire checkpoint of each session |
| [Signed records](signed-records.md) | Checking that nobody changed the record, with `--verify`, the review, or Sigstore's `cosign`; signing with an agent's own SPIFFE identity on a cluster |
| [Evaluate it yourself](../evaluate/README.md) | The same evaluation, with your own models, in one command |
| [Run records](runs/README.md) | Each dated run the pages quote a transcript or a figure from, as it came out |

## Adding a hub: confighub mini

| Page | What it answers |
|---|---|
| [From the plugin to ConfigHub](from-plugin-to-confighub.md) | One team's path from the plugin to confighub mini to the organization's ConfigHub, with what each step adds and when you need it |
| [The app in one request](from-plugin-to-confighub.md#the-app-in-one-request) | Ask for an app "using ConfigHub" and get its base, staging and live copies on a hub the agent starts; [the app you have](from-plugin-to-confighub.md#the-app-you-have), with its `.env.staging`, its tfvars or its Kustomize overlays, attached the same way; [a secret for live](from-plugin-to-confighub.md#a-secret-for-live-that-no-agent-can-read) that no agent can read |
| [Try a change in a copy first](from-plugin-to-confighub.md#try-a-change-in-a-copy-first) | `cub mini try`: a copy of staging or live in a tenth of a second, then `--keep` for staging now and live once you approve, or `--drop` |
| [A service the app needs](from-plugin-to-confighub.md#a-service-the-app-needs) | `cub mini provide` and `cub mini need`: a Postgres, a Redis, an S3 bucket or a mail sender, staging taking its provider's settings at once and live once you approve, with no password in them |
| [An app from a setup someone shared](from-plugin-to-confighub.md#an-app-from-a-setup-someone-shared) | `cub mini copy --from-file FILE --name NAME`, then `cub mini adopt FOLDER --pattern NAME`: your own app from a teammate's setup, with its reasons |
| [Starters](starters.md) | An option, off by default: one short file per kind of app that gives each app you connect the settings it should start with, each with its reason, never over a value you set; kept in the hub with versions you approve |
| [Install confighub mini](install-mini.md) | `/confighub:install-mini`, or the steps by hand, and in a container; [moving to a newer one](install-mini.md#move-to-a-newer-confighub-mini) with everything kept |
| [Approvals on confighub mini](approvals.md#on-confighub-mini-ask-for-it-in-about-a-minute) | About a minute, asked for in your own words: agents on keys of their own, changing staging at once and proposing changes to live that only you can approve |
| [A first run](try-confighub-mini.md) | Fifteen minutes on your own machine: an app you change and keep your changes in through its next version |
| [Your own Helm chart](your-own-chart.md) | Your chart in a hub, your values kept through the chart's next version |
| [Flux and Argo CD deploying from it](gitops-over-oci.md) | Clusters that deploy what the hub approved, over OCI |
| [A service on a VM](vm.md) | The service's files written from the hub on a timer; only approved values reach them; agents with a hub key and no SSH key; an app platform on the same hub |
| [`cub mini` as plain `cub`](cub-mini-and-cub.md) | Which ConfigHub commands each `cub mini` command stands for, `adopt`, `upload`, `try`, `provide`, `need`, `secret` and `reach` included |

## Teams and production

| Page | What it answers |
|---|---|
| [Approvals](approvals.md) | An agent proposes a change to production; only the person you name approves it. On confighub mini for your own agents, or on your organization's ConfigHub for a team. Several agents proposing at once, each with an order of its own; a secret for live that the agent cannot read |
| [Agents that run for weeks](agents-that-run-for-weeks.md) | Who acted, who agreed, a record the agent cannot change, how to stop it at once; what we might still need, and what ConfigHub does not need to do |
| [Agents in CI](../ci/README.md) | An agent in a job that keeps your team's reasons, and one that proposes while a person approves |
| [What we do not claim](limits.md) | What it does not do, or has not been shown to do |
