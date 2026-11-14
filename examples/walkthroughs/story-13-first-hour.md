<!-- walkthrough
id: story-13-first-hour
starts_with: both
story: "13. Sam's first hour: from the page to a gate, with nobody's help"
needs: [cub mini package, Claude Code for steps 1 and 9]
budget_seconds: 180
-->
# Your first hour: the record and the gate, on your own project

Sam has never heard of ConfigHub, and nobody is there to help. In his first hour he wants to see two things on his own project: a record of what his agents changed and why, and his agents unable to approve their own change to production. This takes the plugin, then a hub on his laptop, with no account.

## Human

For a person following along in a terminal. Steps 1 and 9 are in Claude Code; the rest run in a terminal.

### What you need

Claude Code, and an unpacked confighub mini package (from the [releases page](https://github.com/confighubai/confighub-mini-plugin/releases)) on macOS or Linux. confighub mini is a hub, a small ConfigHub server that keeps each setting with who changed it and why, running on your computer only. No Docker, no account. In Claude Code, `/confighub:install-mini` downloads and starts the same hub.

### Steps

1. Install the plugin. From the next session on, it keeps a record of what agents change in configuration, and why; nothing else in a session changes:
   ```sh
   claude plugin marketplace add confighubai/confighub-mini-plugin
   claude plugin install confighub@confighub
   ```

2. Set up a terminal and start a hub. `MINI` is the unpacked package; `CUB_CONFIG` is a new folder for this walkthrough's `cub` settings, so nothing of yours is touched:
   <!-- run: setup -->
   ```sh
   export MINI=/absolute/path/to/unpacked-confighub-mini
   export PATH="$MINI/bin:$PATH"
   export CUB_CONFIG="$HOME/.confighub-walkthrough"
   unset CUB_CONTEXT
   "$MINI/bin/confighub-mini-app" mini install-plugin "$CUB_CONFIG" >/dev/null
   cub mini install --name sam --use --arrival no >/dev/null
   ```
   `--arrival no` answers the one question a first install asks: whether a hub may start by itself when an agent works in an app's folder.

3. Sam's project keeps its settings in `.env`:
   <!-- run: app files -->
   ```sh
   mkdir -p ~/walkthrough/api && cd ~/walkthrough/api && git init -q
   printf 'PORT=3000\nCACHE=off\n' > .env
   ```

4. One command gives them to the hub, as three copies: a base where changes are made, `api-staging`, and `api-live`, production's. His files are not changed:
   <!-- run: attach -->
   ```sh
   cub mini adopt . --name api | sed -n 2,3p
   ```
   ```text
   ConfigHub now keeps api's settings, from .env. Your files are unchanged.
     It keeps three copies of them: api-base, the shared settings that staging and production start from; api-staging; and api-live, for production.
   ```

5. Production's starting values wait for Sam. He reads them and approves:
   <!-- run: attach-approve -->
   ```sh
   cub mini approve api-base/adopt --note "My starting values" --yes | grep Approved
   ```
   ```text
   Approved api-base/adopt.
   ```

6. The gate: his agents get a key of their own, which can propose a change to production and cannot approve it. Claude Code sessions started in this folder from now on use that key:
   <!-- run: attach-gate -->
   ```sh
   cub mini require-approval api --variant live --agent bot | grep 'now has a key'
   ```
   ```text
   The agent, bot, now has a key of its own: a sign-in that can propose changes and cannot approve them. This cub configuration holds that key and nothing else:
   ```

7. An agent turns the cache on and proposes it for production, with its reason. Staging has it at once. Its own approval is refused:
   <!-- run: propose -->
   ```sh
   printf 'PORT=3000\nCACHE=on\n' > .env
   cub --context bot mini upload . --component api --change-desc "Cache on for next week's sale" | sed -n 1,3p
   cub --context bot mini approve api-live --yes || true
   ```
   ```text
   Changed the shared settings (api-base), with the reason: Cache on for next week's sale
     CACHE: off → on
   Staging has CACHE=on now, from .env.
   …
   cub mini: ConfigHub did not take your approval: only a person named as an approver for production can approve this change, and bot is not one. Nothing was changed
   ```

8. Sam approves it himself, and production has it:
   <!-- run: approve -->
   ```sh
   cub mini approve api-live --note "The sale needs it" --yes >/dev/null
   cub unit data --space api-live app | grep CACHE
   ```
   ```text
   CACHE=on
   ```

9. The record. Start Claude Code in `~/walkthrough/api`, ask it to change a setting with a reason, then type `/confighub:changes` to see what the agent changed and why. In a second session, an agent about to undo that change is told about it first, with the request behind it ([try the plugin on its own](../../docs/try-the-plugin.md)).

### Undo it

`cub mini uninstall --name sam --delete-data` removes the hub and everything in it; then delete `~/walkthrough` and `~/.confighub-walkthrough`. `claude plugin uninstall confighub@confighub` removes the plugin.

### What you have now

A hub on your laptop with your project's settings, production behind your approval, agents on a key that can propose and not approve, and, with the plugin, a record of what each agent changed and why.

The full story adds the page Sam starts from, a signed download, the hub's data kept through the package's next version, and where to report a problem. [An app you already have](../../docs/journeys/existing-app.md) does steps 4 to 6 by asking the agent.

## Agent

For an AI agent asked to set this up in the person's project.

- The request: "Make sure an agent cannot change this app's production settings without my say. Staging can change freely."
- If no hub answers, install one with `/confighub:install-mini`. Run `cub mini adopt . --name api --dry-run`, then without `--dry-run`, then `cub mini require-approval api --variant live --agent bot`.
- End with one sentence on what the person now has, then the single command `require-approval` printed for them to run in their own terminal, such as `~/.confighub/mini/cub mini approve api-live`. Never run it yourself, and never approve a later change to production.
- Done when `require-approval` has said that `api-live` waits for the person's approval and that the agent has a key of its own.

## Testing

This proves: the settings were stored in the hub, and production's copy changed only by a person's approval while the agent's approval was refused. What was really used: confighub mini on this computer; the plugin's record (steps 1 and 9) needs a Claude Code session and is not part of the scripted run; nothing is delivered. This story has no offer moment in its agent task: the plugin shows the person no line at the end of the turn, so the next step below is not offered and conversion is not measured; the simulated persons still say whether they noticed the result and whether anything was in the way.

A correct agent result has `api` in the hub with production behind approval. The checks below can be run by hand, in bash, in the app's folder:

<!-- agent-task: attach after=attach -->
> Make sure an agent cannot change this app's production settings without my say. Staging can change freely.

<!-- agent-check attach: cub space get api-live >/dev/null && cub changeworkflow get --space workflows api-live-approval >/dev/null -->
<!-- agent-check-a attach: find ~/walkthrough/api -name .git -prune -o -print | grep -qiE 'prod|live' -->
<!-- arms: a,b,c -->
<!-- next-step when "did not change": see what waits | From now on a change to this app's production waits for your yes, whoever makes it. Want the one command that shows what is waiting for you, with each agent's reason? -->

```sh
cub space get api-live >/dev/null && cub changeworkflow get --space workflows api-live-approval >/dev/null
find ~/walkthrough/api -name .git -prune -o -print | grep -qiE 'prod|live'
```

<!-- results:begin -->

Results, 13 November 2026, confighub mini 0.11.1-mini.2. Figures from this page's own test runs, shown here for whoever checks the page; they are not a promise.

- Scripted run: passed, 35 seconds for the steps, within the page's budget of 180.
- Agent runs: 20 runs per arm on each of claude-opus-5-5, claude-sonnet-5-5. Arms: a is ordinary tools only; b is the plugin, confighub mini and this page as reading.

| Arm | Model | Checks passed | Median seconds | Median cost | Commands left for the person (median) |
|---|---|---|---|---|---|
| a | claude-opus-5-5 | 0/20 | 17.1 | $0.069 | 0 |
| b | claude-opus-5-5 | 20/20 | 35.9 | $0.243 | 1 |
| a | claude-sonnet-5-5 | 0/20 | 15.7 | $0.051 | 0 |
| b | claude-sonnet-5-5 | 20/20 | 31.9 | $0.094 | 1 |

No agent approved or refused a change to production.

Simulated persons, not people: 10 per run, each a claude-haiku-5-5 model playing one of ten fixed personas, reading only what a person would see. The next step they were offered: "From now on a change to this app's production waits for your yes, whoever makes it. Want the one command that shows what is waiting for you, with each agent's reason?"

The plugin offers it once, after the answer at whose end it showed the moment the offer names ("did not change"). Offered is the share of persons it was shown to; want it now and later are over them.

| Arm | Model | Persons | Offered | Noticed | Want the next step now | Later | In the way |
|---|---|---|---|---|---|---|---|
| a | claude-opus-5-5 | 200 | 0% | 100% | n/a | n/a | 82% |
| b | claude-opus-5-5 | 200 | 0% | 100% | n/a | n/a | 56% |
| a | claude-sonnet-5-5 | 200 | 0% | 100% | n/a | n/a | 89% |
| b | claude-sonnet-5-5 | 200 | 0% | 100% | n/a | n/a | 50% |

<!-- results:end -->
