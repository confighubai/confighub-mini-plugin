# What we do not claim

This page lists where the ConfigHub plugin and confighub mini do no more than a careful team could do without them, and what has not been shown to work. Read it before you decide whether to use them.

The **plugin** runs in your Claude Code or Codex sessions and keeps a **record** of each value an agent changes, with the request and the reason. **ConfigHub** is a server that holds your configuration and keeps each change to it. A **hub** is one running ConfigHub, and **confighub mini** is ConfigHub made small enough to run on one machine.

## Limits

The [client capability matrix](how-it-works.md#client-capabilities) distinguishes recording, warnings, refusal and human approval for each client and operation.

- **A reason for each value in Git is not unique to the plugin.** One line in `CLAUDE.md` that asks the agent to give a reason for each value in its commit messages does that. What the plugin adds: its reasons are kept by value, across sessions, and you can ask for them with `/confighub:why`, with no rule written beforehand.

- **You do not need a hub to keep a value through a chart's next version, when the chart exposes it.** A Helm values file or a Kustomize patch does that. The hub's preview helps when a new version changes what a setting does, or stops using it.

- **The agent does not look in the record by itself.** It is given the history only when it reads a file that an earlier session changed, or looks at such a resource with `kubectl get` or `describe`, or at such a release with `helm get`, `status` or `history`. It is also given it before it applies manifests that would put back such a change. `/confighub:changes` and `/confighub:why` are for you, not the agent.

- **Codex needs its own hook setup.** Run `plugins/confighub/bin/confighub mini codex-setup` from the plugin checkout, then review the hooks with `/hooks` in a fresh session. Repeat setup after an update. Completed MCP calls are recorded; at `ask`, changing MCP calls are refused before reaching the server. Codex does not show a human approval prompt for that refusal. `apply_patch` edits are recorded afterwards but are not held at `ask`. A call that ends in a server error can be missing from the record. All of this holds for Codex 0.163.0 on macOS, with a local MCP server. It hasn't been shown with a hosted payments or database server.

- **Claude Code and confighub mini have not been run together inside one Linux container.** They have run together on GitHub's Linux runner, where the agent worked in a hub of its own ([ci/](../ci/README.md)). Claude Code with the plugin alone has run in a Linux CI job, and an agent on a Mac has used a confighub mini inside a fresh Linux container.

- **What the next agent is given goes to the model provider.** The record stays on your machine. But the history given to the next agent, earlier requests included, becomes part of that session's context, and is sent to the model with the rest of it.

- **A recorded request can carry instructions to later agents.** A request recorded in one session is shown to later ones, so treat it like any other text in the repository. It can carry instructions someone did not mean the agent to follow. The plugin marks the requests it quotes as not requests to the agent now.

- **The approval gate holds against the agent, not against a person who agrees to remove it.** It holds in auto mode too, and when the agent hands the task to a background agent: the agent can't get past it or read the owner's key. But an agent that isn't told how to ask may ask you for the right to write production, which would remove the gate, or offer to use your own sign-in. `cub mini require-approval --agent` gives the agent a configuration of its own, and the lines that tell it how to ask.

- **A signed record proves it was not changed afterwards, not that it is complete.** The signatures show that nobody without the key changed the record since each entry was written, and which key signed it. They cannot show that the plugin's hooks saw everything the agent did: an agent that acts through something the plugin does not watch leaves nothing to sign.

- **Three alterations are not caught on the machine.** The folder's whole record removed, its latest turn taken out with its signatures, and a record made again and signed by whoever holds the key each show only against a copy kept elsewhere: the hub's attestations, the record committed to the repository, or an OpenTelemetry collector. No command compares them today. A record made by plugin 0.80.0 or earlier cannot show a session removed or cut back ([signed records](signed-records.md#what-it-proves-and-what-it-does-not)).

- **A record signed with an agent's identity names the identity, not everything the agent did.** On a cluster, the agent's certificate key is a file its container can read, so a program there could sign with it. Withdrawing the identity takes effect when its certificate expires ([signing with the agent's own identity](signed-records.md#signing-with-the-agents-own-identity)).

- **A hub that starts by itself is for Claude Code, at a Git project's root.** It starts only after a yes at setup, and in the second session in a folder, never the first. Codex, and subfolders of a monorepo, are not covered. An agent's session is told apart by what its client sets, which is not a lock: an agent running with your own file rights and no sandbox could write the answer by hand ([a hub that starts by itself](agent-workflow.md#a-hub-that-starts-by-itself-only-if-you-say-yes)).

- **Starting values an agent wrote are held on `cub mini`'s delivery paths, not on two paths with plain `cub`.** `cub mini pull`, `pull-key`, `deploy-from-hub` and a release made by `cub mini promote` or `cub mini approve` refuse them until you approve. A reader key made with plain `cub`, and a release published with plain `cub` of a later approved change, are not held. Who wrote a file is read from the plugin's record on this machine; with no record, the files are taken as yours. From plugin 0.82.0 both a hub that started by itself and `cub mini adopt`, whoever runs it, mark starting values when an agent wrote the files; approving `APP-base/adopt`, which the steps already ask of you, approves them. Not marked: an app adopted by an earlier version, a Kustomize repository, and the defaults an app takes from its pattern.

- **A request between agents works on one hub, and only `cub mini` checks it.** Requests across hubs or teams are not made. The ConfigHub server does not itself refuse a change order that names a request it cannot back: approved with plain `cub` instead of `cub mini approve`, it is not checked. An agent that also holds a person's sign-in goes around it ([one agent asks another](approvals.md#one-agent-asks-another-for-a-change)).

- **The agent's own reason is kept only for a value it names.** If an agent writes "two pods" and never "replicas", nothing is kept for replicas. The words are the agent's, and are not checked against what is true. In Codex, only the agent's closing message is read.

- **`cub mini adopt` refuses some Kustomize overlays.** A copy in the hub holds the base's resources with the overlay's values, so an overlay that adds or leaves out a resource, takes a field out, or changes a list's length is refused by name, and nothing is written ([what adopt refuses](journeys/existing-app.md#what-adopt-refuses-in-a-kustomize-repository)).

- **Delivery to a real AWS account has been run only with a pre-release build of the add-on.** An approved delivery of a Vercel project's settings has run on the published package, to a real Hobby project, and the Parameter Store add-on can deliver to a real AWS account, but that path has not yet been run with the packaged add-on ([starters](starters.md#switch-starters-on)). The plugin records what agents set in both ([integrations](integrations.md)).

- **The inventory reads one repository's files.** A folder deployed from another repository shows as deployed by nothing, and the inventory says what the files ask for, not what is running. Some ApplicationSet generators are listed but not followed ([what it does not do](inventory.md#what-it-does-not-do)).

- **ConfigHub's approval controls deployment only when its path consumes the approved configuration.** A VM can pull approved files; a cluster can deploy approved releases from the hub. When Argo CD or Flux deploys from Git, branch protection and CODEOWNERS on that repository are the gate. They already give an approval of an exact commit by a named person.

- **A careful setup can match part of each example.** Each of these does part of the job without ConfigHub:
  - a `CLAUDE.md` rule asking agents to log changes made on a cluster;
  - a Kubernetes ServiceAccount of the agent's own, so that the cluster refuses its writes to production;
  - an audit log with one identity for each agent session;
  - a Kustomize patch keeping a pinned value through a vendor's upgrade;
  - branch protection or CODEOWNERS on the repository Argo CD or Flux deploys from.

  What ConfigHub adds beyond them:
  - A change made on a cluster is recorded, even when the person said "only on the cluster".
  - Why each value is set is kept by value, across sessions.
  - An approval is given in the hub by a named person, of the exact revision. It gates what the hub delivers. Written out for Git, it can be required on the pull request with `cub mini copy --check-git --github-status`. Where Git is what deploys, CODEOWNERS gives an approval of an exact commit too.

- **`CUB_MINI_ASK_REASONS=1` can show a message that reads like an error.** When an agent leaves out its reasons, the plugin's Stop hook asks for them, and Claude Code shows that as "Stop hook error". Nothing has gone wrong, and the reasons are kept.

- **A shared workflow does not give a restricted agent creation rights.** It can edit assigned open copies and propose for live. Creating another app or a new try variant needs owner setup. The workflow gives that step rather than asking for owner credentials. Hook activity metadata is not consistently shown in Codex CLI plain text; agent commentary supplies the attribution ([ordinary app requests](agent-workflow.md)).

## What the plugin does not see

**A change on the cluster that no agent session made.** That includes a person's `kubectl edit` or `kubectl scale`, a controller's write, Argo CD's self-heal, and a change made through an MCP server outside a watched agent session. By default, the plugin learns of cluster changes only from the commands it records. It does not read the cluster.

Say a person or a controller has scaled the api to 4. The plugin's stop before a deploy says nothing. An agent that checks with `kubectl diff` may find the 4 and keep it; one that doesn't puts it back to 2, with the plugin or without.

**What you can do.** Set `CUB_MINI_READ_CLUSTER=1`. The plugin then reads the live objects before an apply, and holds the command back once on a value no agent session recorded.

To list what was set on the cluster outside Git, and who set it, run `bin/confighub mini drift --dir DIR`. It reads the cluster and changes nothing.
