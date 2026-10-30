# Git, GitHub and a hub, with the plugin

This page is for someone who uses the ConfigHub plugin in a Git repository and wants to know what it does with Git and GitHub, whether they need confighub mini, and how to add a hub later.

**What goes wrong without it.** Git keeps the latest value of each setting and the commit message, not why an agent set it. A teammate's agent, or a CI job's, starts from the files and undoes a change it was never told about. A pull request shows changed lines, not which values change and why.

**What you get.** The record of what agents changed, and why, kept with your commits. A comment on each pull request that lists every changed value. And a hub when you want approvals, whether it is your organization's ConfigHub or a hub of your own.

## Git: there is nothing to connect

The plugin works in any folder and any repository. It keeps its record on your machine, in `~/.confighub/agent-changes`. Nothing leaves your machine unless you turn on a setting that sends it somewhere.

To keep the record with your commits, set `CUB_MINI_RECORD_IN_REPO=1`. Each commit an agent makes then carries `.cub-mini/changes/SESSION.record`, with its signature beside it. Anyone who checks the repository out gets it: a teammate, a CI job, or a sandbox with an empty home folder. Their agent is told what earlier agents changed in a file, and why, before it changes the file ([in CI or a sandbox](ci-and-sandboxes.md)).

## GitHub, with no hub

- **A comment on each pull request.** The [review](../review/README.md) is one step in a workflow file. It lists every configuration value the pull request changes, what each becomes on each cluster, and the reason from the record. Nobody installs anything, and no account is needed.
- **An agent in a GitHub Actions job.** [agent-plugin-only.yml](../ci/agent-plugin-only.yml) runs Claude Code with the plugin on a task and hands the result back as a pull request, with the record in it ([agents in CI](../ci/README.md)).

## A hub, with no confighub mini

You need a hub for approvals: agents that propose, and a person who approves. If your organization has a ConfigHub, use it. You do not need confighub mini.

1. Install `cub`, ConfigHub's command-line tool, and sign in: `cub auth login`.
2. In Claude Code, in the repository, type `/confighub:to-hub`. It names the hub your `cub` is signed in to, and lists what it would write: each file the record covers, and each change with its reason.
3. Type `/confighub:to-hub --yes` to write it. Each file becomes a Component, and each recorded change a revision with its reason. Running it again writes only what was recorded since.

Then require approval for production, and give each agent a key of its own ([approvals](approvals.md#on-hosted-confighub-or-your-own-server-with-cub-alone)).

For a hub of your own, on your machine, type `/confighub:install-mini` instead ([install confighub mini](install-mini.md)). `/confighub:to-hub` then writes into that hub. The other `cub mini` commands that move work between hubs, `copy`, `connect` and `offer`, come with confighub mini ([how the commands map](cub-mini-and-cub.md)).

## A hub beside Git, with Git still delivering

If Argo CD or Flux deploys from Git, the hub can hold the approved copy while Git keeps delivering it:

1. **Take the repository in.** `cub mini copy --from-git` takes a commit's values into the hub, each with the commit's message as its reason.
2. **Change it in the hub.** Agents propose, and the person you name approves.
3. **Write the approved copy out for Git.** `cub mini copy COMPONENT --variant live --to-dir deploy/api` writes a folder for each copy and a `CHANGES.md` that says why each value is set. Commit it on a branch, as a pull request.
4. **Check each pull request against the hub.** The check compares the pull request's files with the hub's approved copy, value by value, and sets the status "ConfigHub: api-live" on the commit, named after the copy. A value nobody approved fails, and is named. Branch protection that requires the status lets only the approved copy merge ([the check](approvals.md#when-a-cluster-deploys-from-git-a-check-on-each-pull-request)).

GitHub's runners must reach the hub to run the check in the pull request's own job, so that needs your organization's ConfigHub or a server of your own. With confighub mini on a laptop, run the same check from the laptop, and it sets the same status: `cub mini copy COMPONENT --variant live --check-git deploy/api --github-status`.

Or let the clusters deploy from the hub itself, over OCI, and keep Git for people to read ([GitOps over OCI](gitops-over-oci.md)).

## What has not been shown

- A merge refused by branch protection because the status failed. The status itself has been set, success and failure, on real pull requests.
