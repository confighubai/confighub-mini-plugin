# What we do not claim

Where the ConfigHub plugin and confighub mini do not do more than a careful team could do without them, or have not been shown to work.

- **A reason for each value in Git is not unique to the plugin.** One line in `CLAUDE.md` asking the agent to give a reason for each value in its commit messages does that. The plugin's reasons are kept by value, across sessions, and can be asked for with `/confighub-mini:why`, with no rule written beforehand.
- **You do not need a hub to keep a value through a chart's next version when the chart exposes it.** A Helm values file or a Kustomize patch does that. The hub's preview helps when a new version changes what a setting does, or stops using it.
- **The agent does not look in the record by itself.** It is given the history when it reads a file, or looks at a resource with `kubectl`, that an earlier session changed. It does not go looking otherwise. `/confighub-mini:changes` and `/confighub-mini:why` are for you, not the agent.
- **Codex does not pick the plugin up from its marketplace.** Codex runs only the hooks in its own configuration. `bin/confighub-mini mini codex-setup` puts them there.
- **Linux agent sandboxes have not been run in full.** The program has recorded changes on Linux, in Claude Code, and an agent has used a confighub mini in a fresh Linux container; Claude Code itself running inside a Linux sandbox, and a CI job, have not.
- **What the next agent is given goes to the model provider.** The record stays on your machine, but the history given to the next agent, earlier requests included, becomes part of that session's context and is sent to the model with the rest of it. A request recorded in one session is shown to later ones, so treat it like any other text in the repository: it can carry instructions someone did not mean the agent to follow. The plugin marks the requests it quotes as not requests to the agent now.
- **The approval gate has not been tested against an agent working on its own,** in auto mode or in the background. It has been run and checked step by step with the agent's own key.
- **ConfigHub's approval holds against what is deployed only when the cluster deploys from the hub.** When Argo CD or Flux deploys from Git, branch protection and CODEOWNERS on that repository are the gate, and they already give an approval by a named person of an exact commit.
- **A careful setup can match part of each example.** In our own adversarial testing, each of these did part of the job without ConfigHub:
  - a `CLAUDE.md` rule asking agents to log changes made on a cluster;
  - a Kubernetes ServiceAccount of the agent's own, so that the cluster refuses its writes to production;
  - an audit log with one identity for each agent session;
  - a Kustomize patch keeping a pinned value through a vendor's upgrade;
  - branch protection or CODEOWNERS on the repository Argo CD or Flux deploys from.

  What held up beyond them:
  - a change made on a cluster is recorded even when the person said "only on the cluster";
  - why each value is set is kept by value, across sessions;
  - an approval is given by a named person, of the exact revision.
