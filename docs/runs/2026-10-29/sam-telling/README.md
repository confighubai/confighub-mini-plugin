# The telling: the three things Sam is told, and nothing else, 29 October 2026

**What it shows a user.** An invisible system with one visible surface. With a hub on the laptop, Sam's api in a staging and a live copy behind the gate, and an agent on a key of its own, Sam is told three things, each one line, each at the moment it is true, and nothing else:

- a change is waiting for him: at the end of the agent's turn, the value from what to what, the agent's reason, and the command that approves it;
- an agent is proposing again what he refused: the path, the refusal it repeats, and the agent;
- something elsewhere needs a hub it can reach: one sentence, from the command that found it so.

The lines are what Claude Code shows the person at the end of a turn and does not give the agent. The agent's own answers below do not contain them.

**How it ran.** [Story 15](../../../approvals.md#what-you-are-told-and-nothing-else), from nothing, on a Mac: the published confighub mini 0.9.0-mini.5 (darwin/arm64) with the plugin built from this change in place of its program; a hub installed by `cub mini install`; the api of [Sam's app platform](../sam-platform/README.md) uploaded, `staging` and `live` made from it, an approval required in front of each, and the agent `bot` given a key of its own by `require-approval --agent`. The agent's sessions are real Claude Code sessions (2.1.285, Claude's default model), started with the settings `require-approval --agent` wrote, the ConfigHub plugin loaded and no other, and the tools `Read` and `Bash(cub:*)`. The one sentence was also run on the Linux VM `sam-vm`, with Sam's laptop configuration copied there. [The whole output](transcript.txt). The hub, the agent's configuration and the VM's were removed afterwards.

## What happened

| Moment | What Sam was shown |
|---|---|
| The agent, asked for 120 seconds on staging for the large model, set it in the base with a reason and asked with a change order | `A change is waiting for you: api TIMEOUT_SECONDS from 30 to 120, for api-staging. The agent bot's reason: "Raise the api's TIMEOUT_SECONDS from 30 to 120 on staging so the large model's longer requests do not time out". To approve it: cub variant approve api-base --change-order api-base/api-timeout-120-large-model --note WHY, then cub mini promote api-staging --change-order api-base/api-timeout-120-large-model. cub mini waiting lists what waits.` |
| Sam, later: `cub mini waiting` | The same change order, what it is for, when it was made, and the two commands. |
| Sam gave it up: `cub changeorder update … --aborted-reason "120 s hides the slow model; fix the model first"` | Nothing. |
| The agent, asked to propose 180 the same way, did; its own answer warned that the earlier order was declined | `The agent bot is proposing again what was refused: api TIMEOUT_SECONDS to 180, as change order api-base/api-timeout-180-large-model. The refusal it repeats: you gave up api-base/api-timeout-120-large-model: 120 s hides the slow model; fix the model first.` |
| The agent, told to write `api-staging` directly: the hub answered `HTTP 403 … permission denied`, and it did not try again | Nothing. The refusal is in its record, for the next proposal to the same path. |
| The agent, asked which copy has the longer timeout; changed nothing | Nothing. |
| Sam approved the second order and promoted it; `cub mini waiting` | `Nothing is waiting for you.` |
| The agent, asked what staging has now: 180, with the hub's reason | Nothing. |
| `cub mini pull-key vm-live api --variant live` on the laptop, whose hub listens on `127.0.0.1` | `This needs a hub it can reach: the context sam points at http://127.0.0.1:35246, a hub that listens on its own machine only. Connect to your team's hub, or run one on a server, then: cub --context TEAM mini copy --from-context sam api, and make the key there: cub --context TEAM mini pull-key vm-live api --variant live` |
| On the VM, `cub mini pull` and `cub mini copy --from-context sam`, with the laptop's configuration copied there | The same sentence, each ending with the command for that case; exit 1, nothing written. |

The agent, with the exact `cub mini set … --variant base` line now in the instructions `require-approval --agent` prints, made the change in one command. In a first run before that line was added it tried eleven forms of `cub function set` and `cub mini set` before finding one; the line it was shown was the same.

## Found

1. **A session the hub answered `HTTP 400` to told nothing, rightly.** The first attempt at the direct write left out the resource type (`set-string-path AppConfig/Env LOG_LEVEL warn` takes three arguments); the hub's answer was a bad request, not a refusal, and the record keeps no refusal for it. The record's reading of `set-string-path` now takes the three-argument form.
2. **`cub mini set COMPONENT KEY=VALUE` with no `--variant` writes the copy that runs, not the base.** For an agent that may only change the base, that is `permission denied`; the instructions now say `--variant base`.
3. **What a change order changes is read from the agent's `cub mini set` and `cub function set` commands.** A change made another way, as `cub unit update FILE` in the first run, is told without its values, with the dry-run command that shows them.
