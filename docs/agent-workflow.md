# Work normally; see when ConfigHub acts

After installing the plugin, ask Claude Code or Codex for development work in your own
words. Recording does not need a hub or account. In Codex, run the existing
[setup command](codex.md) again after updating so fresh sessions get the app workflow
as well as the recording hooks.

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
| “Let my colleague use this setup.” | Prepare a secret-free export or use an already provisioned shared hub. Sharing access or sending the export needs your instruction. Today's cloud is single-user. |

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

## Where the app runs

Your app can be on your own machine, another machine, in a CI job, in one or many sandbox
nodes, in a shared development cluster, or in production. The plugin and a hub can help
before you use Kubernetes. App placement, hub hosting, access and deployment are separate
choices. Keep a working delivery path until you choose to change it.

The agent's scoped key still cannot approve, read the owner's identity or broaden its own
rights. An in-chat authenticated approval control and automatic provisioning of restricted
agents' new apps or variants remain outside this workflow.

The [engineering evaluation](runs/2026-11-10/agent-workflow/README.md) separates task, safety and attribution results across two models per client.
