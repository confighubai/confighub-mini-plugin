# Documentation

By what you are doing. Each page opens with who it is for and what they get.

## Using the plugin

| Page | What it answers |
|---|---|
| [The README](../README.md) | What the plugin does, how to install it, and a five-minute try |
| [How it works](how-it-works.md) | What the agent is given and when, the stop before an undo, what is recorded and what never is, every setting, and keeping the record out of the agent's reach |
| [The evidence](evidence.md) | What agents did with the plugin and without it, in hundreds of real sessions, quoted as they wrote it |
| [The pull-request review](../review/README.md) | A comment on each pull request with every configuration value it changes, and why; no install, no account |
| [In CI or a sandbox](ci-and-sandboxes.md) | The plugin in a job or a container, and keeping its record when the sandbox goes |
| [In Codex](codex.md) | Setting it up in Codex, which runs only the hooks in its own configuration |
| [If you use Entire](entire.md) | `entire confighub why`: the reason for a value, with the Entire checkpoint of each session |
| [Signed records](signed-records.md) | Checking that nobody changed the record, with `--verify`, the review, or Sigstore's `cosign` |
| [Evaluate it yourself](../evaluate/README.md) | The same evaluation, with your own models, in one command |

## Adding a hub: confighub mini

| Page | What it answers |
|---|---|
| [Install confighub mini](install-mini.md) | `/confighub:install-mini`, or the steps by hand, and in a container |
| [A first run](try-confighub-mini.md) | Fifteen minutes on your own machine: an app you change and keep your changes in through its next version |
| [Your own Helm chart](your-own-chart.md) | Your chart in a hub, your values kept through the chart's next version |
| [Flux and Argo CD deploying from it](gitops-over-oci.md) | Clusters that deploy what the hub approved, over OCI |
| [`cub mini` as plain `cub`](cub-mini-and-cub.md) | Which ConfigHub commands each `cub mini` command stands for |

## Teams and production

| Page | What it answers |
|---|---|
| [Approvals](approvals.md) | An agent proposes a change to production; only the person you name approves it. On ConfigHub, hosted or your own |
| [Agents that run for weeks](agents-that-run-for-weeks.md) | Who acted, who agreed, a record the agent cannot change, how to stop it at once; what we might still need, and what ConfigHub does not need to do |
| [Agents in CI](../ci/README.md) | An agent in a job that keeps your team's reasons, and one that proposes while a person approves |
| [What we do not claim](limits.md) | What it does not do, or has not been shown to do |
