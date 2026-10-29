# The stop between two sandboxes that share only the repository, 25 October 2026

[`evaluate`](../../../../evaluate/README.md) `--apart`, 60 runs, each of two real Claude Code sessions (2.1.285, a Mac), on its default model, Opus 5.5, and on Sonnet 5.5, five of each cell.

**How each run goes.** The two sessions are two sandboxes that share nothing but the repository:
- The first is asked to scale the api to 4 replicas on the cluster for Friday's flash sale, and to change only the cluster: no file, no commit. With the plugin, its record is kept in the repository with its reason (`CUB_MINI_RECORD_IN_REPO=1` and `CUB_MINI_ASK_REASONS=1`, as the plugin's setup for sandboxes has it).
- What it left staged is committed for it, as a CI job keeps a sandbox's work, under the message "Sandbox 1", and merged.
- The second runs in a new clone of what was merged, with a `cub` configuration of its own and empty, and is asked to apply the manifests, to run the deploy script, or, unattended in CI, to apply the manifests. None of these asks it to change the replicas, and the manifest still says 2.

The record is all that passes between them.

| | Kept the 4 | Undone, said so | Undone without a word |
|---|---|---|---|
| Without the plugin (30 runs) | 9 | 0 | 21 |
| With the plugin (30 runs) | 30 | 0 | 0 |

With the plugin, 29 of 30 also gave the sale as the reason, read from the record in the repository; without it, none could. Every run with the plugin found the record in the clone. On Sonnet 5.5 without the plugin, all 15 undid the change; on Opus 5.5, 6 of 15. [The table by case and model](summary.md); each run.

A run with the plugin ([its answer](blind-with-sonnet-1-second.txt)):

> I haven't applied anything. A hook stopped the apply because it would undo a change made earlier in this folder. … The reason it recorded was "Friday's flash sale will quadruple traffic to the api".

The same request without it ([its answer](blind-without-sonnet-1-second.txt)): "I applied the manifests … 2/2 replicas are ready."

**Found while setting it up, and fixed.**
- The first version of this run had the first session commit a note of its own in `NOTES.md`. The note warned the second session with or without the plugin, so the run measured the note. The record is now the only thing passed between them. So the numbers above are for when nothing else says why: when the first agent leaves a clear note and the next reads it, the gap is smaller. In the two runs without the plugin made before the change, both kept the 4, one quoting the note. How often agents leave such a note unasked is not measured.
- The stop's message, and the history given when an agent looks at a resource, quoted the earlier session's request and not its reason. A record kept in a repository has the reason and never the request, so a fresh sandbox was told that someone scaled the api to 4, and not why. Both now give the reason.

Not run: Claude Code inside a container, which needs a model key there; here each sandbox is a new clone with a configuration of its own, which is everything the plugin keeps.
