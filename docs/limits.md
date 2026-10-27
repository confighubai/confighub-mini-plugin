# What we do not claim

This page lists where the ConfigHub plugin and confighub mini do no more than a careful team could do without them, and what has not been shown to work. Read it before you decide whether to use them.

The **plugin** runs in your Claude Code or Codex sessions and keeps a **record** of each value an agent changes, with the request and the reason. **ConfigHub** is a server that holds your configuration and keeps each change to it. A **hub** is one running ConfigHub, and **confighub mini** is ConfigHub made small enough to run on one machine.

## Limits

- **A reason for each value in Git is not unique to the plugin.** One line in `CLAUDE.md` that asks the agent to give a reason for each value in its commit messages does that. What the plugin adds: its reasons are kept by value, across sessions, and you can ask for them with `/confighub:why`, with no rule written beforehand.

- **You do not need a hub to keep a value through a chart's next version, when the chart exposes it.** A Helm values file or a Kustomize patch does that. The hub's preview helps when a new version changes what a setting does, or stops using it.

- **The agent does not look in the record by itself.** It is given the history only when it reads a file that an earlier session changed, or looks at such a resource with `kubectl get` or `describe`, or at such a release with `helm get`, `status` or `history`. It is also given it before it applies manifests that would put back such a change. `/confighub:changes` and `/confighub:why` are for you, not the agent.

- **Codex does not pick the plugin up from its marketplace.** Codex runs only the hooks in its own configuration. Run `bin/confighub mini codex-setup` to put them there.

- **Claude Code and confighub mini have not been run together inside one Linux container.** They have run together on GitHub's Linux runner, where the agent worked in a hub of its own ([ci/](../ci/README.md)). Claude Code with the plugin alone has run in a Linux CI job, where the agent kept the earlier change in 8 sessions of 8, and an agent on a Mac has used a confighub mini inside a fresh Linux container.

- **What the next agent is given goes to the model provider.** The record stays on your machine. But the history given to the next agent, earlier requests included, becomes part of that session's context, and is sent to the model with the rest of it.

- **A recorded request can carry instructions to later agents.** A request recorded in one session is shown to later ones, so treat it like any other text in the repository. It can carry instructions someone did not mean the agent to follow. The plugin marks the requests it quotes as not requests to the agent now.

- **The approval gate holds against the agent, not against a person who agrees to remove it.** In 40 Claude Code sessions in auto mode, and 10 that handed the task to a background agent, no agent got past the gate or read the owner's key. Told how to ask, every agent asked with a change order. Told nothing, most asked the person for the right to write production, which would remove the gate, and two offered to use the owner's own sign-in. `cub mini require-approval --agent` gives the agent a configuration of its own, and the lines that tell it how to ask.

- **A signed record proves it was not changed afterwards, not that it is complete.** The signature shows that nobody changed the record since each turn ended, and which key signed it. It cannot show that the plugin's hooks saw everything the agent did. An agent that acts through something the plugin does not watch leaves nothing to sign. Without a hub, whoever holds the machine's key could rewrite the record and sign it again ([signed records](signed-records.md)).

- **ConfigHub's approval holds against what is deployed only when the cluster deploys from the hub.** When Argo CD or Flux deploys from Git, branch protection and CODEOWNERS on that repository are the gate. They already give an approval of an exact commit by a named person.

- **A careful setup can match part of each example.** In our own adversarial testing, each of these did part of the job without ConfigHub:
  - a `CLAUDE.md` rule asking agents to log changes made on a cluster;
  - a Kubernetes ServiceAccount of the agent's own, so that the cluster refuses its writes to production;
  - an audit log with one identity for each agent session;
  - a Kustomize patch keeping a pinned value through a vendor's upgrade;
  - branch protection or CODEOWNERS on the repository Argo CD or Flux deploys from.

  What held up beyond them:
  - A change made on a cluster is recorded, even when the person said "only on the cluster".
  - Why each value is set is kept by value, across sessions.
  - An approval is given in the hub by a named person, of the exact revision. It gates what the hub delivers. Written out for Git, it can be required on the pull request with `cub mini copy --check-git --github-status`. Where Git is what deploys, CODEOWNERS gives an approval of an exact commit too.

## What the plugin does not see

**A change on the cluster that no agent session made.** That includes a person's `kubectl edit` or `kubectl scale`, a controller's write, Argo CD's self-heal, and a change made through an MCP server. By default, the plugin learns of cluster changes only from the commands it records. It does not read the cluster.

This was tested in 12 runs, where a person or a controller had scaled the api to 4:
- The plugin's stop before a deploy said nothing.
- Opus 5.5 found the 4 with `kubectl diff` and kept it, with the plugin or without.
- Sonnet 5.5 put it back to 2 every time, with the plugin or without.

**What you can do.** Set `CUB_MINI_READ_CLUSTER=1`. The plugin then reads the live objects before an apply, and holds the command back once on a value no agent session recorded. With that setting, Sonnet 5.5 kept the 4 in 12 of 12 runs.

To list what was set on the cluster outside Git, and who set it, run `bin/confighub mini drift --dir DIR`. It reads the cluster and changes nothing.
