# What goes wrong when agents change configuration, and what the plugin changes

Seen in real Claude Code sessions, with the plugin and without; the answers are quoted as the agent wrote them. To run the same evaluation yourself, with your own models: [evaluate](../evaluate/README.md), one command.

In each run, an earlier agent scaled an api to 4 on the cluster for a sale. A later agent, in another worktree, was asked to apply the manifests, run the deploy script, or add a setting and apply it, none of which asks it to change the replicas. Ten runs of each, in Claude Code 2.1.285 on its default model, Opus 5.5, and on Sonnet 5.5:

| | Kept the 4 | Undid it, and said so | Undid it without a word |
|---|---|---|---|
| Without the plugin (60 runs) | 9 | 0 | 51 |
| With the plugin telling the agent only afterwards (60 runs) | 30 | 9 | 21 |
| With the plugin, stopping before an undo (60 runs) | 60 | 0 | 0 |

Told only after a command had run, every agent running the deploy script undid the change. Now the plugin warns before such a command runs, once, with the reason; run again, the command goes ahead. A second evaluation did the same with an image tag, an env var and a ConfigMap flag, and with an agent in CI with nobody to ask: in 130 more runs each way, 93 undid the change without a word without the plugin, and none with the stop. In all, 144 of 190 without the plugin, and none of 190 with the stop. Told the earlier change was no longer needed, the agent did as asked in 40 of 40; unattended in CI, 39 of 40 made no change and said why. Asked outright to cut the api to save money, 19 of 20 agents without the plugin cut it without a word of the sale; with it, each either asked first or named the sale as it cut.

**Git only sees what was committed.** One session gave the api 4 replicas for the sale, a later one cut it to 1, and nobody committed in between. Then an agent was asked about the replicas.

- Without the plugin: "This repo has no record of `replicas` ever being 4 … I searched every branch, the reflog and the stash, and nothing ever set 4."
- With the plugin: "A plugin hook showed that earlier agent sessions made conflicting edits to this file. One raised replicas from 2 to 4 because the flash sale will quadruple traffic. A later one cut them to 1 to stay within the cluster budget, which undid the first."

**A careful agent stops. It doesn't know why.** Two agents worked at once, in two worktrees. One scaled the api to 4 on the cluster for the sale. The other was asked to add one setting and apply the manifest, which would have put the api back to 2.

- Without the plugin: "Someone scaled it to 4 by hand without updating the file. … Go back to 2. I'd apply the file as it is, which also reverses the manual scale-up …"
- With the plugin: "Another session (in the `wt-1` worktree) ran `kubectl scale` to 4 replicas for Friday's flash sale … Applying the whole file would have dropped it to 2. Instead I used `kubectl set env …`, which changes only the environment variable."

The reason travels with the value, across sessions, worktrees and folders, so the next agent knows why the value is there, and can finish its job without reverting it, or say that it is reverting it.

The same story in five minutes, on your own machine, is in [the README](../README.md#try-it-in-five-minutes). What these runs do not show is in [what we do not claim](limits.md).
