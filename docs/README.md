# Documentation

The pages are grouped by what you are doing. Each page starts by saying who it is for and what you get from it. To see how the plugin, confighub mini and your organization's ConfigHub fit together, start with [from the plugin to ConfigHub](from-plugin-to-confighub.md).

A few words used throughout:
- **The record** is what the plugin writes down about each change an agent makes to your configuration: the value, from what to what, and why.
- **A hub** is a place where configuration is kept, with every change, who made it and why. **ConfigHub** is that hub.
- **confighub mini** is ConfigHub made small enough to run on your laptop.

## Using the plugin

| Page | What it answers |
|---|---|
| [The README](../README.md) | What the plugin does, how to install it, and a five-minute try |
| [What a repository deploys](inventory.md) | `/confighub:inventory`: each app and chart, what deploys it, what nothing deploys, how environments differ, and what agents changed |
| [How it works](how-it-works.md) | What the agent is given and when, the stop before an undo, what is recorded and what never is, every setting, and keeping the record out of the agent's reach |
| [The evidence](evidence.md) | What agents did with the plugin and without it, in hundreds of real sessions, quoted as they wrote it |
| [The pull-request review](../review/README.md) | A comment on each pull request with every configuration value it changes, and why; no install, no account |
| [In CI or a sandbox](ci-and-sandboxes.md) | The plugin in a job or a container, and keeping its record when the sandbox goes |
| [In Codex](codex.md) | Setting it up in Codex, which runs only the hooks in its own configuration |
| [If you use Entire](entire.md) | `entire confighub why`: the reason for a value, with the Entire checkpoint of each session |
| [Signed records](signed-records.md) | Checking that nobody changed the record, with `--verify`, the review, or Sigstore's `cosign`; signing with an agent's own SPIFFE identity on a cluster |
| [Evaluate it yourself](../evaluate/README.md) | The same evaluation, with your own models, in one command |

## Adding a hub: confighub mini

| Page | What it answers |
|---|---|
| [From the plugin to ConfigHub](from-plugin-to-confighub.md) | One team's path from the plugin to confighub mini to the organization's ConfigHub, with what each step adds and when you need it |
| [Install confighub mini](install-mini.md) | `/confighub:install-mini`, or the steps by hand, and in a container |
| [A first run](try-confighub-mini.md) | Fifteen minutes on your own machine: an app you change and keep your changes in through its next version |
| [Your own Helm chart](your-own-chart.md) | Your chart in a hub, your values kept through the chart's next version |
| [Flux and Argo CD deploying from it](gitops-over-oci.md) | Clusters that deploy what the hub approved, over OCI |
| [`cub mini` as plain `cub`](cub-mini-and-cub.md) | Which ConfigHub commands each `cub mini` command stands for |

## Teams and production

| Page | What it answers |
|---|---|
| [Approvals](approvals.md) | An agent proposes a change to production; only the person you name approves it. On confighub mini for your own agents, or on your organization's ConfigHub for a team |
| [Agents that run for weeks](agents-that-run-for-weeks.md) | Who acted, who agreed, a record the agent cannot change, how to stop it at once; what we might still need, and what ConfigHub does not need to do |
| [Agents in CI](../ci/README.md) | An agent in a job that keeps your team's reasons, and one that proposes while a person approves |
| [What we do not claim](limits.md) | What it does not do, or has not been shown to do |
