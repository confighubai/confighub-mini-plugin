# Work normally; see when ConfigHub acts

After installing the plugin, ask Claude Code or Codex for development work in your own
words. Recording does not need a hub or account. In Codex, run the existing
[setup command](codex.md) again after updating so fresh sessions get the app workflow
as well as the recording hooks.

The walkthrough [Theo's first app](../examples/walkthroughs/story-23-theo-first-app.md) shows the plugin keeping the reason for each setting an agent writes, from the first prompt, with no hub; [a new app that fits the team's pattern](../examples/walkthroughs/story-18-dev-intent.md) shows an app asked for with ConfigHub.

## Start with the app

“Build a small API” is an ordinary coding request. The agent builds it using your current
setup. It does not install a hub just because you are making an app.

“Why did we turn caching off?” can use the reasons recorded by earlier sessions. When
that history explains the answer, ConfigHub is credited briefly. You do not need a hub
to retain the record or use it in another session on this machine.

If an app already uses ConfigHub, its `.confighub-app` file identifies its configuration.
The shared app workflow helps the agent choose the next step:

| You ask | What happens |
|---|---|
| “Try 2048 MB without touching staging or production.” | Use an assigned isolated copy and show the difference. A restricted key cannot create new variants: if no copy is assigned, the agent gives you the setup commands and leaves staging and live alone. A configuration copy does not start a sandbox service. |
| “Ship this change.” | Propose the exact settings revision and show the owner's approval command. A chat “yes” does not approve it. After approval, delivery and service checks still depend on the connected deployment path. |
| “Make another app like this, on port 3002.” | Prepare the new app with its own values and offer the first app's base as its pattern. A restricted key cannot create a new app: owner adoption and a new scoped session remain explicit setup steps. Credentials are kept out of the shared setup. |
| “Have CI use these settings.” | Check reachability and choose read access for a consumer or proposal access for changes. Neither can approve. A local-only hub needs a reachable path before a remote job can use it. |
| “Let my colleague use this setup.” | Prepare a secret-free export, or copy the app to a shared hub: hosted ConfigHub or the enterprise edition, where many people share one organization. Sharing access or sending the export needs your instruction. |

When you explicitly ask to use or attach ConfigHub, that is already your setup choice: the agent completes it, using the bundled installer if cub is absent. It does not ask you to choose ConfigHub again. A restricted key still needs the owner setup steps above.

If you have not chosen ConfigHub, the agent first checks whether the existing Git, files or
deployment setup meets the need. If a hub would help, it offers one relevant step and
explains its cost: the local download and processes, or connection to a chosen existing
hub. It continues independent coding while you decide. It does not silently sign you up.

## Short notices, at the point of use

Before a meaningful ConfigHub action, the agent gives a brief line such as:

> ConfigHub: proposing the memory change for api live; it will wait for your approval.

One line covers a related batch. Routine reads stay quiet. The hooks also attach a
fallback notice for recognised direct `cub mini` changes, grouped by action kind in the
turn. When recent commentary already announces the batch, the hook omits the duplicate. They never echo arguments that might contain secrets. Hook metadata display varies
by client; visible agent commentary supplies the attribution in Codex CLI too.

A notice before a command describes the intended action. The result says separately
whether settings were stored, files were written, or the service actually runs the approved
revision. Approval and copying files alone do not prove production changed.

## Decline an offer once

Say this as a direct instruction:

> Don't suggest ConfigHub here.

The plugin acknowledges it and remembers it for this project on this machine, across new
sessions. Recording, history, safety notices and explicitly requested ConfigHub actions
continue. A generic “no”, quoted example or “don't install yet” is not saved as a project
preference. To enable relevant suggestions again, say:

> Suggest ConfigHub here again.

Other wording of an explicit project-wide decline can be saved by the agent with
`cub mini changes --hub-suggestions off` (`on` to resume); you do not need to learn that
command. An explicit later request to use ConfigHub still works without enabling future
unsolicited offers. `CUB_MINI_TIPS=0` also remains available for turning off tips globally.

## A hub that starts by itself, only if you say yes

A hub can also start without your asking, to keep the settings files of an app an agent
works on (`.env`, `.env.staging`, `.env.production`) as a staging and a production copy.
This is off until you say yes to one question at setup.

**The question.** The first time you set up confighub mini in a terminal, with
`bin/confighub mini get` from the plugin, `cub mini install` or
`cub mini require-approval --agent`, it asks:

```
One question, asked once on this machine. When an agent works in a folder that holds an app's settings files (.env, .env.staging, .env.production), may a hub start by itself to keep them, as a staging and a production copy? Your files are not changed, nothing is deployed, production's copy waits for your approval, and you are told in one line when it starts. Turn it on? [y/N]
```

Enter means no. Your answer is kept, and the question is not asked again on that machine.
A script answers with `--arrival yes` or `--arrival no` on the same commands. In Claude
Code, `/confighub:install-mini` asks nothing, since whatever you could type there the
agent could type too. It prints this line instead, once in a session, and the setting
stays off. The command in it is the package's own `cub`, with your version and platform, so it runs as printed on a
machine where `cub` is not yet on your `PATH`:

```
ConfigHub: one setting only you can turn on. With it on, when an agent works in a folder that holds an app's settings files, a hub (a ConfigHub server on this machine) starts by itself and keeps those settings. It is off. To turn it on, run this in your own terminal: ~/.confighub/mini/confighub-mini-VERSION-OS-ARCH/bin/cub mini install --arrival yes. To keep it off and stop this line, run it with --arrival no instead.
```

**After a yes.** When an agent works in a Git project folder that holds one of those
files, the end of its turn prepares the folder, without a word: sessions started there
from then on run as the agent, on a key that cannot approve, in a sandbox that keeps your
own ConfigHub configuration out of reach. The session that was running is yours, and
never starts a hub. The next session started in the folder brings the hub at its first
request, and shows you one line:

```
ConfigHub: as chosen at setup on this machine, this folder's settings are now also kept in a hub the plugin started, as a staging and a production copy. Your files are unchanged and nothing is deployed. Turn this off with cub mini changes --arrival off, or remove the hub from your own terminal: cub mini uninstall --delete-data.
```

**Values an agent wrote wait for you.** When an agent wrote the file production's copy
starts from, such as the `.env` of a new app, that copy is marked "starting values, not
approved". Nothing delivers it until you approve that exact revision. The line above then
ends: `An agent wrote production's settings, so nothing delivers them until you approve them: run cub mini waiting.` `cub mini waiting` lists it first,
with who wrote the values and when, and the command that approves them,
`cub mini approve APP-live`. Files you kept before any agent wrote to them are yours, and
are not marked.

The same holds when you ask for the app yourself. `cub mini adopt`
marks production's copy in the same way when an agent wrote its files, whoever runs the
command. Approving `APP-base/adopt`, which [the new-app steps](journeys/new-app.md) already
ask of you, approves those values too, so you type nothing extra; `cub mini waiting` names
that command while the order waits.

**To turn it off.** For one folder, `cub mini changes --arrival off`; edits to its files
are then no longer sent to the hub either. For the machine, `cub mini install --arrival no`.
To turn one folder on again, in your own terminal: `cub mini changes --arrival on --dir PROJECT`.
What a hub already holds stays until `cub mini uninstall --delete-data`, which removes
the hub and every app it holds, not this folder's alone. What this does not cover:
[limits](limits.md).

## Where the app runs

An app can run on your own machine, on another machine, in a CI job, on one sandbox node or
across many, in a shared development cluster, and onward through staging to production. Each
is a useful place to start or stay. A CI test or a temporary sandbox doesn't need to become a
production service. The plugin and a hub can help before you use Kubernetes
([before you use Kubernetes](from-plugin-to-confighub.md#before-you-use-kubernetes)).

An app can have several running copies, each with its own settings and lifetime. Several
sandbox nodes might run independent copies for parallel tests, or parts of one distributed
app. A shared development cluster might run several apps and environments.

The hub keeps the configuration for those copies. Where the hub runs and where the app runs
are separate choices, and so are access and deployment. Making staging and live
configuration in a hub doesn't start those services: a process or deployment system has to
read the configuration and run the app. Keep a working delivery path until you choose to
change it. For the paths documented here, see [CI and sandboxes](ci-and-sandboxes.md),
[a service on a VM](vm.md), and [Flux or Argo CD deploying from the hub](gitops-over-oci.md).
A remote service needs a hub it can reach, and approval of production only holds if its
deployment path uses the approved configuration.

The agent's scoped key still cannot approve, read the owner's identity or broaden its own
rights. An in-chat authenticated approval control and automatic provisioning of restricted
agents' new apps or variants remain outside this workflow.
