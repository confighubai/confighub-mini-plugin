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
| Attach ConfigHub to an app that Argo CD or Flux already deploys, with `CUB_MINI_STARTERS` set | Use reference section 0: one adopt line the person runs, which starts the hub, and one approval. Do not use sections 1–3 for it. |
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
The hooks also supply activity metadata and a reminder for recognised direct shell
commands. Some clients show this metadata; Codex CLI does not consistently display it
in plain text. Your commentary is the person-facing attribution. Do not repeat it after
receiving the hook reminder, announce routine reads, or claim completion before the result.
For scripts and MCP calls, provide the same brief attribution yourself.

Read [app operations](references/app-operations.md) only for the operation needed:
an app Argo CD or Flux already deploys, with a starter (0), setup/adoption and patterns (1–2), proposals and secrets (3), isolated tries (4).
For CI readers, use the public [snapshot contract](https://github.com/confighubai/confighub-mini-plugin/blob/main/examples/extensions/config-snapshot/README.md)
and [working example](https://github.com/confighubai/confighub-mini-plugin/tree/main/examples/extensions/config-snapshot).
For hub continuation, inspect `cub mini copy --help` and `cub mini connect --help` for the
installed version. Copying configuration does not by itself move the running service,
merge histories, or prove that a hosted/team path works.

## Keep the boundaries clear

- A chat "yes" is not authenticated owner approval. Never run `cub mini approve`, use the
  owner's ConfigHub identity, remove the gate, or ask for live write rights. Give the owner
  the exact terminal command from `cub mini waiting`. A fresh restricted session is needed
  after `require-approval --agent`; changing settings does not restrict this session.
- After setup, end your reply with the lines `require-approval --agent` printed under
  "Tell the person this, in these words", as they are, and give the person no other command.
- Read with your own key. Listing Spaces, what waits, an app's status, a Unit's data and the
  cluster's objects are reads you run yourself; hand the person only what approves or moves
  production.
- Keep credentials out of chat, command arguments, exports and records. Secret setup is an
  owner-terminal step. A reader cannot propose or approve; a proposer cannot approve.
- Distinguish settings stored, service running and approved revision deployed. Verify each
  result you promise. `copy`, `set` and approval alone do not prove production changed.
- The app may run on this machine, another machine, in CI, one or many sandboxes, a shared
  dev cluster or production. Neither this workflow nor an app requires Kubernetes.
- Follow the person's request: making a try does not authorise keeping, deploying or deleting it;
  sharing a setup does not authorise sending it or granting access to someone.
- `try --keep` promotes its differences; `try --drop` deletes the isolated copy. Leave a
  try available for inspection unless the person asks to promote or delete it.
