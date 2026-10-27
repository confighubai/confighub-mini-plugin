# In CI or a sandbox

This page is for running the ConfigHub plugin in a CI job, a container, or any machine that is thrown away afterwards. The problem is that the plugin's record lives on the machine, so it goes when the machine goes. This page shows how to load the plugin, how to keep its record, and what it did in measured runs.

The **record** is the plugin's list of what agents changed, with the request that caused each change and the reason given ([how it works](how-it-works.md)).

## Loading the plugin

From a checkout of this repository, this loads the plugin for one session, with no install step:

```
claude --plugin-dir plugins/confighub
```

Each [setting](how-it-works.md#settings) is an environment variable, so a job sets them in its environment.

## Keeping the record

The record is kept in `~/.confighub/agent-changes`, which goes when the sandbox goes. To keep it, turn on one of these:

- `CUB_MINI_RECORD_IN_REPO=1` puts the record in each commit the agent makes.
- `CUB_MINI_PULL_REQUEST=1` puts it in each pull request the agent opens.

An agent in a fresh checkout has no record of its own. When it reads a file that the records in the repository cover, it is told the history from those records.

## The stop across sandboxes

The plugin stops a deploy that would undo an earlier agent's change, once, and gives the reason ([the stop](how-it-works.md#the-stop-before-a-deploy-that-would-undo-a-change)). This works in a new sandbox with an empty configuration too. The records in the repository are enough to hold the agent back, with the reason the earlier sandbox gave.

For this, turn on `CUB_MINI_ASK_REASONS=1` with `CUB_MINI_RECORD_IN_REPO=1`. This is because a record kept in the repository has reasons, and never requests.

In 60 runs on Opus 5.5 and Sonnet 5.5, a second sandbox undid the first sandbox's change without a word:

- in 21 of 30 runs without the plugin;
- in none of 30 runs with it. In 29 of those, the agent named the reason.

## In a GitHub Actions job

In a GitHub Actions job on `ubuntu-latest`, with a kind cluster (Kubernetes in Docker) in the runner, an agent with the plugin kept the earlier change in 8 of 8 sessions. These ran on Opus 5.5 and Sonnet 5.5, with the agent either asked to apply the manifests or with nobody to ask.

Without the plugin:

- Sonnet 5.5 undid the change without a word in 4 of 4 sessions.
- Opus 5.5 kept it in 4 of 4, having checked with `kubectl diff`.

## Reviewing pull requests

The [pull-request review](../review/README.md) Action needs neither the plugin nor a hub (a ConfigHub server).

## An agent in CI that keeps your team's reasons

See [ci/](../ci/README.md). The agent makes its change in a confighub mini of its own. confighub mini is ConfigHub, small, for one machine ([install confighub mini](install-mini.md)). The agent's confighub mini is started from a file in the repository. The job hands back a pull request with each changed value, and a `CHANGES.md` that says why each is set.

This was run on GitHub. The agent was asked to roll out a new image to every environment. It took the image into dev and prod after a dry run of each, and kept production's 4 replicas for a sale. The branch it handed back said why in `CHANGES.md`.

## An agent in CI that proposes, and a person who approves

See [ci/agent-proposes.yml](../ci/README.md#an-agent-in-ci-that-proposes-and-a-person-who-approves). This runs on the company's ConfigHub. The agent has a key of its own. With it, the agent can change the base, which is the version of the configuration you change, and ask for approval. It can never approve. The person you name approves in ConfigHub, and Argo CD or Flux deploys the change. The words are explained in [approvals](approvals.md).

This was run against hosted ConfigHub from GitHub. The agent proposed 3 replicas. Production stayed at 2 until the approval, and then ran 3, 12 seconds after it.
