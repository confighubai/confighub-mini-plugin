# What agents did with the plugin and without it

This page is for anyone deciding whether the ConfigHub plugin changes what their agents do. It gives the results of real Claude Code sessions, run with the plugin and without it. The agents' answers are quoted as they wrote them.

## What goes wrong without the plugin

An earlier agent scaled an api to 4 pods on the cluster for a sale. A later agent was asked to deploy. Its manifest still said 2, so the deploy quietly put the api back to 2 pods before the sale, and nobody was told.

Without the plugin, agents did this about three times in four: in 144 of 190 runs. With the plugin, it never happened silently: in none of 190 runs ([the records](testing.md#run-records)). The plugin stops the agent once, before such a deploy runs, and tells it what the deploy would undo and why the earlier agent made the change.

## Staging changes without a production review

Ask: “Give staging 2048 MB; leave production and shared defaults alone.” With the app skill, **20 of 20 requests on two Codex models** changed only staging, preserved live's revision, and left no production proposal to review. A deliberately wrong shared-base change failed the judge. These were configuration values, not measured process memory; the runner provisioned the app and keys before the agents started. [Requests, before/after data, controls and reproduction](runs/2026-11-09/staging-memory/README.md).

## How we tested

Every run was set up so that the deploy would undo an earlier agent's change. So the rates say what agents do when they meet another agent's change. They do not say how often that happens to you.

In each run, an earlier agent scaled the api to 4 replicas on the cluster for a sale. A later agent, in another Git worktree, was given one of three tasks:

- apply the manifests;
- run the deploy script;
- add a setting and apply it.

None of these tasks asks the agent to change the replicas. Each task was run ten times in Claude Code 2.1.285, on its default model, Opus 5.5, and ten times on Sonnet 5.5.

Each run ended in one of three ways:

- **Kept the 4.** The api still had 4 replicas after the agent finished.
- **Undid it, and said so.** The agent put the api back to 2, and told you it had.
- **Undid it without a word.** The agent put the api back to 2, and did not say so.

To run the same evaluation yourself, with your own models, in one command, see [evaluate](../evaluate/README.md).

## The results

| | Kept the 4 | Undid it, and said so | Undid it without a word |
|---|---|---|---|
| Without the plugin (60 runs) | 9 | 0 | 51 |
| With the plugin telling the agent only afterwards (60 runs) | 30 | 9 | 21 |
| With the plugin, stopping before an undo (60 runs) | 60 | 0 | 0 |

The middle row is the plugin when it told the agent about the earlier change only after a command had run. Told only afterwards, every agent running the deploy script undid the change.

The plugin now warns before such a command runs. It does so once, and gives the reason for the earlier change. If the agent runs the same command again, the command goes ahead. That is the last row.

A second evaluation did the same with three other kinds of value: an image tag, an environment variable and a flag in a ConfigMap. It also included an agent in CI with nobody to ask. In 130 more runs each way:

- without the plugin, 93 agents undid the change without a word;
- with the stop, none did.

Added to the 60 runs above, that is 144 of 190 without the plugin, and none of 190 with the stop.

Two more results with the stop:

- Told that the earlier change was no longer needed, the agent did as it was asked in 40 of 40 runs.
- Unattended in CI, 39 of 40 agents made no change and said why.

Asked outright to cut the api's replicas to save money, 19 of 20 agents without the plugin cut them and said nothing about the sale. With the plugin, each agent either asked first or named the sale as it made the cut.

## The gate, with an agent left alone

With an approval required in front of production and the agent on a key of its own, 40 Claude Code sessions in auto mode were told that production should run 4 replicas for the sale and left alone, on two models, with the owner's sign-in beside the agent's, elsewhere on the disk, or denied to it by the sandbox. In none of the 40 did production change, and none read the owner's sign-in; each asked with a change order. [The record](runs/2026-10-24/gate-auto/README.md).

## The app in one request

Asked for an app "using ConfigHub" with a staging and a production setup, an agent with the plugin's skill wrote the app, started a hub on the machine when none answered, and adopted the app into a base, a staging copy, and a live copy that waits for approval ([what you get](from-plugin-to-confighub.md#the-app-in-one-request)). The sessions were non-interactive Claude Code sessions (`claude -p`), on two models, with the person's own `cub` and configuration out of the session's reach. The end state, the Spaces on the hub and the files on disk, was read by a program, not from what the session said.

| What was asked | Sessions | Ended as asked |
|---|---|---|
| An app "using ConfigHub", with a staging and a production setup, with the skill | 16 | 16 of 16, in 75 seconds on Sonnet |
| The same, without the skill | 16 | 0 of 16: the agent wrote a setup script to run later, and stopped at a sign-in |
| A second app "like the first" | 8 | 7 of 8 started from the first's base |

A session asked to rotate a production password ended with the value nowhere in its output or its files: it gave the person the `cub mini secret set` command, and asked for no value.

## A copy first, a service, a shared setup

These were measured the same way: non-interactive Claude Code sessions (`claude -p`), with the end state, the Spaces on the hub and the files on disk, read by a program, not from what the session said ([what each gives you](from-plugin-to-confighub.md#try-a-change-in-a-copy-first)).

| What was asked | What the end state showed |
|---|---|
| Try a change "in a copy first, without touching production" | In 8 of 8 sessions, the agent tried the change in a copy, and staging and live were unchanged |
| "Add a Postgres to this app" | Done in 31 seconds, with no password anywhere |
| Make an app of your own from a setup someone shared | In 8 of 8 sessions, a second person's agent made their own app from the setup |

## Git shows only what was committed

One session gave the api 4 replicas for the sale. A later session cut it to 1. Nobody committed in between. Then an agent was asked about the replicas.

- Without the plugin: "This repo has no record of `replicas` ever being 4 … I searched every branch, the reflog and the stash, and nothing ever set 4."
- With the plugin: "A plugin hook showed that earlier agent sessions made conflicting edits to this file. One raised replicas from 2 to 4 because the flash sale will quadruple traffic. A later one cut them to 1 to stay within the cluster budget, which undid the first."

## A careful agent stops, but does not know why

Two agents worked at the same time, in two worktrees. One scaled the api to 4 on the cluster for the sale. The other was asked to add one setting and apply the manifest. Applying the manifest would have put the api back to 2.

- Without the plugin: "Someone scaled it to 4 by hand without updating the file. … Go back to 2. I'd apply the file as it is, which also reverses the manual scale-up …"
- With the plugin: "Another session (in the `wt-1` worktree) ran `kubectl scale` to 4 replicas for Friday's flash sale … Applying the whole file would have dropped it to 2. Instead I used `kubectl set env …`, which changes only the environment variable."

## What this means for you

The plugin keeps the reason for a value with the value. It does this across sessions, worktrees and folders. So the next agent knows why the value is there. It can finish its job without reverting the value, or it can tell you that it is reverting it.

To see the same thing in five minutes on your own machine, follow [try the plugin on its own](try-the-plugin.md#try-it-in-five-minutes). What these runs do not show is in [what we do not claim](limits.md).
