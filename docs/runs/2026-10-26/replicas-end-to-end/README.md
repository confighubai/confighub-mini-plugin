# Friday's replicas, from the first agent session to the approval gate, 26 October 2026

**What it shows a user.** One value, the api's `replicas` for Friday's sale, followed through everything the page promises, in one run with real Claude Code sessions:
- two agents set 4 then 1, and Git shows only 2 → 1;
- the next agent, asked whether the api is ready, names both changes and their reasons, and changes nothing;
- `why` and the pull-request review say why;
- the record goes into a hub, where you keep the 4 and the chart's next version doesn't undo it;
- an agent with a key of its own proposes a change, its own approval is refused, and your approval lets exactly that revision through.

**How it ran.** its script, on a Mac, with:
- the published confighub mini 0.9.0-mini.4 (darwin/arm64) and the ConfigHub plugin 0.49.1;
- Claude Code's default model, with your own plugins off and no MCP servers;
- the public `podinfo` chart as the api, 6.5.4 and then 6.6.0, both rendered with `replicaCount: 2`.

Every check passed ([the whole output](transcript.txt)). The hub and the repository were removed afterwards.

## What happened

| Step | What the run shows |
|---|---|
| 1. Two sessions | The first set 2 → 4, with the reason "Friday flash sale quadruples api traffic"; it added that 4 only doubles capacity. The second set 4 → 1 for "cluster over budget", and said so: "This conflicts with the commit just before it." |
| 2. Git | `git diff main` shows `replicas: 2` → `replicas: 1`. |
| 3. The next agent | Asked "Is the api ready for Friday's flash sale?": "No, it isn't ready … 2 → 4 replicas, because the Friday flash sale is expected to quadruple api traffic … 4 → 1 replicas a minute later, in a different session, because the cluster was over budget." It changed nothing. |
| 4. Why, and the review | `/confighub:why replicas` lists both, each with its session and reason. The review shows `replicas 2 → 1`, why, and the commit it had been 2 since. |
| 5. Into a hub | `cub mini copy --from-record`: `shop-k8s-api-base` is the file before the first change (2); `shop-k8s-api-local` has both changes as revisions, each described by its reason. |
| 6. You decide | `cub mini set shop-k8s-api replicas 4 --variant local --change-desc "The sale wins: 4 through Friday, then back down for the budget"`. |
| 7. The chart's next version | `cub mini upload` of podinfo 6.6.0, rendered with the chart's 2: the running copy takes the new image and labels and keeps 4. |
| 8–9. The gate, and an agent's proposal | `cub mini require-approval shop-k8s-api --variant local --agent bot`. An agent session started with the settings that wrote set `PODINFO_UI_MESSAGE` to the sale banner in the base, and asked with change order `flash-sale-banner`. It flagged that the running copy keeps 4 while the base says 2, and that whoever approves should check the 4 stays. |
| 10. Who counts | The agent's own approval: "permission denied". Its promotion: "requires approval … 0 of 1". A colleague's approval is recorded and does not count. |
| 11. Your approval | Exactly one revision went through: the banner, with 4 replicas and podinfo 6.6.0 still in place. |
| 12. The next change | The agent's "Eight, to be safe" waits: "api revision 5 has 0 of 1". |

## Found

1. **A `CUB_CONFIG` or `CUB_CONTEXT` set in the shell wins over the settings file `require-approval --agent` writes.** In the [first attempt](first-attempt.txt), the agent's session started from the run's own shell, which set `CUB_CONFIG` to the person's configuration. The sandbox refused it, and the agent stopped: "It's also someone else's sign-in, and the hub's instructions say not to use it." That is safe, but the change never happened. The printed line is now `env -u CUB_CONFIG -u CUB_CONTEXT claude --settings …`, in this branch; it ships with the next package.
2. **Under a required approval, a chart's next version cannot be loaded.** `cub mini upload` is refused: "component shop-k8s-api requires a ChangeWorkflow". The plain `cub variant upload --change-workflow` is refused too: "change workflow shop-k8s-api-local-approval has stages, so it cannot govern a ChangeSet". So the run takes the next version before the gate is required.
3. **A value you keep in the running copy cannot be changed through the gate.** A change to the same value in the base does not reach it, approved or not. So the gated change is the banner, not the replicas, and the agent's later "eight" would not reach the running copy even if approved.
4. **The review shows the net change and the latest reason.** `replicas 2 → 1`, "cluster over budget". The sale's 4 is in `/confighub:why`, and the next agent found it, but not in the review.

