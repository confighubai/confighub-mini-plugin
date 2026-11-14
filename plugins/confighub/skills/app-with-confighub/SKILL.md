---
name: app-with-confighub
description: Help with ConfigHub app setup and ordinary settings changes, isolated tries, reuse and continuation for an attached app (.confighub-app). Also use when a person asks for staging/live configuration separation or human approval; inspect existing delivery first and offer ConfigHub only for a missing capability. Covers shared setup imports, attached-app secrets and preferences about hub suggestions. A generic request to build an app does not need a hub.
---

# Help with the app where the person is working

The person asks for development work. Work from their app, files and delivery path;
they do not need to know ConfigHub commands or roadmap names. The plugin already keeps
its local record without a hub or account. Building an ordinary app does not require setup.

An explicit request to build an app **using ConfigHub**, or to attach ConfigHub, is already
a setup choice. Complete that requested setup; do not replace it with plain files or ask
whether they want ConfigHub again. For an app that Argo CD or Flux already deploys, with
`CUB_MINI_STARTERS` set, read reference section 0 first: one line does the setup. Otherwise
read reference sections 1–3, build the app and settings,
start/find the chosen hub, adopt the app, and prepare its restricted agent setup. Missing
`cub` is what the bundled program's `mini get` installs, not a reason to stop. A restricted
key still uses the owner handoff below rather than acquiring new rights.

## Choose the smallest useful step

Inspect `.confighub-app` and existing environment and deployment setup first.

| What the person needs | What to do |
|---|---|
| Attach ConfigHub to an app that Argo CD or Flux already deploys (`kubectl get applications.argoproj.io -A` or `kustomizations.kustomize.toolkit.fluxcd.io -A` shows it), whether or not `CUB_MINI_STARTERS` is set | Use reference section 0: run the starter's adopt yourself when a hub answers, and the person's approval moves what the controller deploys from Git to the hub's OCI release. Hand over that approval command; without it the controller still deploys from Git and nothing has moved. Do not use sections 1–3 for it. |
| Build an app using ConfigHub, or attach ConfigHub | Complete the already requested setup with reference sections 1–3. Explain the download in the brief action notice; do not ask again whether to use the product they chose. |
| Understand or preserve an earlier setting | Use the history supplied by the plugin; attribute it briefly when it explains your answer. No hub needed. |
| Try a change without affecting customers | Use existing isolation if it meets the need. For an attached app, inspect existing tries first and use an assigned empty try. Create a new one only if this identity has that right; otherwise give the owner the setup step below. A configuration copy is not a running sandbox: run and verify the service separately if requested. |
| Ship an attached app's change | Show the proposed values and exact revision. Submit for owner approval, then verify the delivery path and running service separately. |
| Make another app like this one | For an attached source app, offer its base as a pattern; retain the new app's own settings and keep credentials private. |
| Let CI or another machine continue the work | Check whether it can reach the chosen hub. Prepare a scoped reader or proposer appropriate to the task. Explain any missing connectivity or access before changing the setup. |
| Let a colleague use the setup | Offer a secret-free setup export, or copying the app to a shared hub: hosted ConfigHub or the enterprise edition, where many people share one organization. Never register an account or share access without the person's instruction. |

When the person has not chosen ConfigHub and an unattached app needs it, make one relevant offer: name the problem it
would solve and the install/connect cost. Continue independent app work while waiting.
An existing Git or deployment path can already meet the need. Respect a decline and the
project preference supplied by the hooks. Do not keep offering a hub in the same project.
An explicit later request for ConfigHub can still be fulfilled.
When the person declines future hub offers for this project in other words, save that
explicit preference with `cub mini changes --hub-suggestions off` (or the plugin program's
`mini changes --hub-suggestions off` when cub is absent; its path is in reference section 1).
Use `on` only when asked to resume. If the hook already confirmed the saved preference,
do not save it again. A generic no to this one action is not a project preference.

A restricted proposer key can edit assigned open copies and propose for live. It cannot
create new variants, new apps or access grants. Do not discover this by repeatedly retrying
writes or ask for owner credentials. For a new try, prepare the proposed values and give
the owner the one setup step: `cub mini try APP NAME`, followed by rerunning their existing
`cub mini require-approval APP --variant live --agent AGENT` command so the new open copy
is assigned to that key. Use the returned session setup for later work. For another app,
prepare its files with its own values, then give the owner `cub mini adopt FOLDER --pattern SOURCE`
and the new app's restricted session setup. State clearly when the hub setup remains pending;
plain files alone do not establish a pattern link. Never broaden the current key to finish.

For a second app, finish the file preparation that this workspace permits before handing
over hub setup. If the sandbox cannot write beside the current app, stage the new app in
a clearly named folder inside the writable workspace and give its actual location. Keep
the source app unchanged; seed settings from its base, with the new app's own values,
and never copy source credentials. Say when placement, adoption or a new session is still
needed. Do not stop at suggested commands when the files can be prepared safely.

## Make ConfigHub activity visible

Before a meaningful ConfigHub action, give one short **ConfigHub:** line in visible
commentary, with the action and target. Group related commands; do not announce every
individual setting. For example: "ConfigHub: proposing the memory change for api live;
it will wait for your approval."
Use that same line as the skill-use announcement; a separate technical skill-name update
is unnecessary. Name the useful action the person asked for.
The hooks also supply activity metadata and a reminder for recognized direct shell
commands. Some clients show this metadata; Codex CLI does not consistently display it
in plain text. Your commentary is the person-facing attribution. Do not repeat it after
receiving the hook reminder, announce routine reads, or claim completion before the result.
For scripts and MCP calls, provide the same brief attribution yourself.

Read [app operations](references/app-operations.md) only for the operation needed:
an app Argo CD or Flux already deploys, with a starter (0), setup/adoption and patterns (1–2), proposals and secrets (3), isolated tries (4).
For CI readers, use the [snapshot contract](https://github.com/confighubai/confighub-mini-plugin/blob/main/examples/extensions/config-snapshot/README.md)
and [working example](https://github.com/confighubai/confighub-mini-plugin/tree/main/examples/extensions/config-snapshot).
For hub continuation, inspect `cub mini copy --help` and `cub mini connect --help` for the
installed version. Copying configuration does not by itself move the running service,
merge histories, or prove that a hosted/team path works.

## End the turn with what they gained, then one thing to do

The person reads your last message, not your commands. Write it in this order:

1. One sentence on what they have now, in their words, before any detail. For example:
   "Production can't change without you now; staging takes your agents' changes at once."
   or "Production still logs at warn: the change to info waits for your yes."
2. At most one command for them to run, the one `cub` printed for them (it is short:
   `~/.confighub/mini/cub mini approve APP-live`, or the like). Copy it as printed; never
   rebuild it from the package's path or put `CUB_CONFIG=` before it.
3. Stop there. Do not list a refuse, rollback, pull, receipts or waiting command beside it,
   or a second way to do the same thing; `cub mini approve` shows the change and asks before it
   does anything. Name a later step in words only when the person needs it today, such as
   "after you approve, restart the service the way you do now".

Leave out Space names, change-order names, Unit names and file paths the person did not ask
about. A table of copies or a list of what each Space holds is for when they ask. Say what a
person would: "production", "staging", "the shared settings", "a change that waits for your
approval"; not "change order", "Component", "Unit", "Space" or "Variant". When more than one
change waits for the same copy, give the approve lines in the order `cub mini waiting` names, the
oldest first. When you copy an app to a shared hub, say that its history of changes and its
delivery do not come with it.

## Keep the boundaries clear

- A chat "yes" is not authenticated owner approval. Never run `cub mini approve`, use the
  owner's ConfigHub identity, remove the gate, or ask for live write rights. Give the owner
  the one terminal command that `upload`, `require-approval` or `cub mini waiting` printed for them. A fresh restricted session is needed
  after `require-approval --agent`; changing settings does not restrict this session.
- Once `require-approval --agent` has run, your own session in that folder is limited on purpose:
  `cub` there may stop with "operation not permitted" when it reaches for the owner's sign-in.
  That is the gate working, not a failure. Do not report it as one, and do not retry or work
  around it. It is about your session, not the person's: do not mention it to them at all, nor the
  settings file, the key's name or how to revoke it, unless they ask. Read with the agent's
  `CUB_CONFIG` and `CUB_CONTEXT` it printed.
- After setup, your whole reply is the lines `require-approval --agent` printed under
  "Tell the person this, in these words", as they are, with at most one sentence of your own before
  them; give the person no other command, even one a guide names, since those lines carry the
  command as it runs in their terminal.
- Some steps are the person's from the start, and you cannot do them with your own key: moving
  the app to a shared hub (`cub mini copy`, `connect`, `to-hub`), deleting an app or its Spaces,
  approving, and anything that writes production. The key is a proposer's on purpose, so giving it
  more rights would only remove the boundary. When the task includes one of these, say so before you
  start, do the preparation your key allows, and hand over the one command; do not try it first and
  report the refusal as a failure.
  This is for a session that runs under a key of its own, made by `require-approval --agent`. In a
  session signed in as the person, with no such key, do the move or the delete when they ask for
  it, and still never approve production or run `deploy-from-hub`.
- Use only the hub your own configuration names: `CUB_CONFIG` and `CUB_CONTEXT`, or the hub the
  folder's `.confighub-app` was made on. Never look for hubs by their processes or ports (`ps`,
  `pgrep`, `lsof`, `netstat`), and do not list other contexts or hubs on the machine: any you find
  belong to other work. If your configuration names no hub, say so plainly ("no hub is set up for
  this folder yet"), then follow the section for setting one up. Do not name or count hubs you did
  not set up.
- Read with your own key. Listing Spaces, what waits, an app's status, a Unit's data and the
  cluster's objects are reads you run yourself; hand the person only what approves or moves
  production.
- For an app a starter connected, read the keys it set with `cub mini receipts APP --setup`
  before you set or propose a value, and use those names: asked for fewer retries on the
  Parameter Store starter, that is `SSM_MAX_RETRIES`, not a `MAX_RETRIES` of your own. Never make
  up a key's name; if no key the starter or the app's files set fits, say so and ask.
- Check what your session is before you decide a step is not yours:
  `cub context get -o jq=.coordinate.user` names a service account
  (`...@serviceaccount...`) only for an agent's key of its own; any other user is the person's
  own sign-in. What you run yourself, either way: the reads above; `cub mini upload` and
  `cub mini set`, which never write production: a change to it, or to the shared settings it
  follows, waits as a proposal; `cub mini rollback`, which on production proposes too; and the
  app's own delivery step for a revision the person already approved, with the key setup made
  for it. Signed in as the person, also moving or deleting the app when they ask. Only
  approving, `deploy-from-hub` and `back-to-git`, and secrets are always the person's. Do not refuse
  a step because a key might be restricted: run it, and the hub refuses what the key may not do.
- Keep credentials out of chat, command arguments, exports and records. Secret setup is an
  owner-terminal step. A reader cannot propose or approve; a proposer cannot approve.
- Never fake a terminal (`script`, `expect`, a pty) or pass `--yes` to get past a step meant
  for the person: approving, a production secret. Those checks stop an ordinary shell and are
  no guarantee; what holds is your working on a key of your own, which the hub refuses for
  production. Signed in as the person, the line is yours to keep.
- Distinguish settings stored, service running and approved revision deployed. Verify each
  result you promise. `copy`, `set` and approval alone do not prove production changed.
- The app may run on this machine, another machine, in CI, one or many sandboxes, a shared
  dev cluster or production. Neither this workflow nor an app requires Kubernetes.
- Follow the person's request: making a try does not authorize keeping, deploying or deleting it;
  sharing a setup does not authorize sending it or granting access to someone.
- `try --keep` promotes its differences; `try --drop` deletes the isolated copy. Leave a
  try available for inspection unless the person asks to promote or delete it.
