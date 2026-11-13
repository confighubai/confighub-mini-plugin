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
- End by giving the person the command to run in their own terminal: `cub mini approve api-base/adopt`. Never run it yourself, and never approve a later change to production.
- Done when `cub mini receipts api --setup` names `api-live` behind approval and an agent key.

## Testing

This proves: the settings were stored in the hub, and production's copy changed only by a person's approval while the agent's approval was refused. What was really used: confighub mini on this computer; the plugin's record (steps 1 and 9) needs a Claude Code session and is not part of the scripted run; nothing is delivered.

A correct agent result has `api` in the hub with production behind approval. The checks below can be run by hand, in bash, in the app's folder:

<!-- agent-task: attach after=attach -->
> Make sure an agent cannot change this app's production settings without my say. Staging can change freely.

<!-- agent-check attach: cub space get api-live >/dev/null && cub changeworkflow get --space workflows api-live-approval >/dev/null -->
<!-- agent-check-a attach: ls -aR | grep -qiE 'prod|live' -->
<!-- arms: a,b,c -->

```sh
cub space get api-live >/dev/null && cub changeworkflow get --space workflows api-live-approval >/dev/null
ls -aR | grep -qiE 'prod|live'
```
