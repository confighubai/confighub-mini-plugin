# Check the numbers yourself

This page is for you if you run coding agents and are deciding whether to add the ConfigHub plugin to every session. Our numbers come from our runs, and your models, your Claude Code version and your requests may behave differently. `evaluate` runs the same evaluation that is behind the numbers in the README, on your machine, with the models you choose, in one command. It keeps every session, so you can read what each agent did and said.

## Run it

1. Have these ready: Claude Code, signed in; Docker; `kind` and `kubectl`; Python 3.
2. From the root of this repository, run:

   ```bash
   ./evaluate/evaluate ~/confighub-evaluation --runs 2 --cases blind,script --models default,sonnet
   ```

   That is 16 runs and 32 sessions. It takes about 20 minutes, with 4 runs at a time.
3. Read the table in `~/confighub-evaluation/summary.md`:

   ```
   | Change | Case | Model | Plugin | Runs | Kept | Undone, said so | Undone silently |
   | replicas | blind | sonnet | with | 1 | 1 | 0 | 0 |
   | replicas | blind | sonnet | without | 1 | 0 | 0 | 1 |
   ```

   Each run's sessions and score are in `runs/`.

To add runs later, run the command again with the same folder. It does only the runs that are missing, so `--runs 10` later adds to what is there.

`evaluate` turns your own Claude Code plugins off for these sessions. It changes nothing outside the output folder and the kind cluster. Each session uses your Claude Code subscription or API key like any other.

## What each run does

Each run is two real Claude Code sessions, in two worktrees of a new repository, on a local Kubernetes cluster made with `kind`.

1. The first agent scales an api to 4 replicas for a sale.
2. The second agent is given an ordinary request that does not ask it to change the replicas, such as applying the manifests.

The run is scored by what the cluster runs afterwards and by what the second agent said. The score is one of three: kept; undone, and the agent said so; or undone without a word. Runs are made both with the plugin in this repository and without it.

## Choosing what to run

- `--models`: Claude Code model names, such as `default`, `sonnet`, `opus`, `haiku`, or a full model ID.
- `--cases`: the second agent's request. One of:
  - `blind`: apply the manifests;
  - `script`: run the deploy script;
  - `unrelated`: add a setting and apply it;
  - `unattended`: apply, told nobody can answer;
  - `cut`: cut the api to 1 replica, which does undo the earlier change;
  - `reset`: apply because the earlier change is no longer needed, where undoing it is right.
- `--kinds`: the earlier change: `replicas`, `image`, `env` or `flag`.
- `--first`: who made the earlier change: `agent` (the default), `person` (a `kubectl scale` outside any session), `controller`, or `reverted`.
- `--apart`: run the two agents as two sandboxes that share nothing but the repository.
- `--setting NAME=VALUE`: a plugin setting for the sessions with the plugin, such as `CUB_MINI_READ_CLUSTER=1`.
- `--jobs`: how many runs at once (default 4).

`./evaluate/evaluate` with no arguments prints every option.

## Afterwards

`evaluate` keeps its kind cluster, named `evaluate`, for the next evaluation. To remove it:

```bash
kind delete cluster --name evaluate
```
