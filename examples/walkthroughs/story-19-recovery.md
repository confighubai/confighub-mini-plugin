<!-- walkthrough
id: story-19-recovery
starts_with: both
story: "19. Sam's bad afternoon: stop it, find it, undo it"
needs: [cub mini package]
budget_seconds: 180
-->
# An agent did something wrong: stop it, find it, undo it

An agent has cut the payment service's timeout to 5 seconds, and real payments now fail in staging. Sam wants one thing to do at once, then the facts: what was done, what can be put back, and what cannot. Here he stops every agent session and takes the agent's key away in one command, finds the change, and puts it back.

## Human

For a person following along in a terminal.

### What you need

An unpacked confighub mini package (from the [releases page](https://github.com/confighubai/confighub-mini-plugin/releases)) on macOS or Linux. confighub mini is a hub, a small ConfigHub server that keeps each setting with who changed it and why, running on your computer only. No Docker, no account. The ConfigHub plugin for Claude Code is optional: with it, the same stop also halts every Claude Code session.

### Steps

1. Set up a terminal and start a hub. The stop is a file. By default it is `~/.confighub/halt`, which stops every Claude Code session with the plugin on this computer; for this walkthrough, `CUB_MINI_HALT_FILE` names a file of its own, so only sessions started from this terminal would stop:
   <!-- run: setup -->
   ```sh
   export MINI=/absolute/path/to/unpacked-confighub-mini
   export PATH="$MINI/bin:$PATH"
   export CUB_CONFIG="$HOME/.confighub-walkthrough"
   export CUB_MINI_HALT_FILE="$HOME/.confighub-walkthrough-halt"
   unset CUB_CONTEXT
   "$MINI/bin/confighub-mini-app" mini install-plugin "$CUB_CONFIG" >/dev/null
   cub mini install --name sam --use --arrival no >/dev/null
   ```
   `--arrival no` answers the one question a first install asks: whether a hub may start by itself when an agent works in an app's folder.

2. The payment service reads its settings from `pay/.env`:
   <!-- run: app files -->
   ```sh
   mkdir -p ~/walkthrough/pay && cd ~/walkthrough
   printf 'TIMEOUT_SECONDS=30\nREFUND_LIMIT=50\n' > pay/.env
   ```

3. Give its settings to the hub, approve production's starting values, and give an agent a key of its own, which can change the base and staging and only ask for production:
   <!-- run: adopt -->
   ```sh
   cub mini adopt pay >/dev/null
   cub mini approve pay-base/adopt --note "What runs today" --yes >/dev/null
   cub mini require-approval pay --variant live --agent bot >/dev/null
   ```

4. The agent, asked to cut costs, edits the file to a 5-second timeout:
   <!-- run: mistake-file files -->
   ```sh
   printf 'TIMEOUT_SECONDS=5\nREFUND_LIMIT=50\n' > pay/.env
   ```

5. It sends the change on its key. Staging has it at once; production waits for Sam:
   <!-- run: mistake -->
   ```sh
   cub --context bot mini upload pay --component pay --change-desc "Fail fast to save cost"
   ```
   ```text
   Changed the shared settings (pay-base), with the reason: Fail fast to save cost
     TIMEOUT_SECONDS: 30 → 5
   Staging has TIMEOUT_SECONDS=5 now, from .env.
   …
   ```

6. Stop. One command makes the stop file and takes the agent's rights away, including from sessions already signed in:
   <!-- run: halt -->
   ```sh
   cub mini halt --agent bot
   ```
   ```text
   Each Claude Code session with the plugin and its hooks intact stops at its next tool call, and new ones at their first.
   Not stopped: a process an agent already started, sessions without the plugin, Codex. Credentials on this machine stay valid.
   Taking away bot's rights in ConfigHub:
   …
   bot's rights are taken away and its account is deleted. A session it had already signed in is refused from its next request, and its key can no longer sign in.
   Checked with its key: ConfigHub gives it nothing now.
   To let them run again, from a terminal: rm ~/.confighub-walkthrough-halt
   ```

7. The agent's next request to the hub is refused; it can no longer even see the app:
   <!-- run: refused -->
   ```sh
   cub --context bot unit list --space pay-base || true
   ```
   ```text
   Failed: space "pay-base" not found
   ```

8. Let agents work again by removing the stop file. The agent's key stays revoked; a new key is a new `cub mini require-approval`:
   <!-- run: resume -->
   ```sh
   rm "$CUB_MINI_HALT_FILE"
   ```

9. Find what it did. Its change to production is still waiting, with its reason and what it would change:
   <!-- run: find -->
   ```sh
   cub mini waiting
   ```
   ```text
   A change to production waits for your approval: Fail fast to save cost. It was made just now; its name is pay-base/upload-20261113-074923-yhn1.
     It proposes for production, from the app's files:
       TIMEOUT_SECONDS: 30 → 5
   …
   ```

10. Undo it. Taking the change order back from the shared settings gives it up, with the reason, so production never takes it. Staging took the value as its own, so it is set back separately:
   <!-- run: undo -->
   ```sh
   printf 'TIMEOUT_SECONDS=30\nREFUND_LIMIT=50\n' > pay/.env
   ORDER=$(cub changeorder list --space pay-base -o jq='.[] | select(.ChangeOrder.Description | startswith("Fail fast")) | .ChangeOrder.Slug')
   cub mini rollback pay-base --change-order pay-base/$ORDER --reason "5 s fails real payments"
   cub mini set pay TIMEOUT_SECONDS=30 --variant staging --change-desc "Put back: 5 s fails real payments" >/dev/null
   for copy in base staging live; do cub unit data --space pay-$copy app | grep TIMEOUT; done
   cub mini waiting
   ```
   ```text
   Set back on pay-base, each with the reason:
     app: TIMEOUT_SECONDS 5 → 30
   Change order pay-base/upload-20261113-074923-yhn1 given up: 5 s fails real payments
   …
   TIMEOUT_SECONDS=30
   TIMEOUT_SECONDS=30
   TIMEOUT_SECONDS=30
   Nothing is waiting for you.
   ```

### Undo it

`cub mini uninstall --name sam --delete-data` removes the hub and everything in it; then delete `~/walkthrough` and `~/.confighub-walkthrough`.

### What you have now

The agent's key is gone, its change is undone in the base and staging, production never took it, and every step is in the hub with its reason (`cub mini receipts pay-staging`).

What stays yours: a call an agent made to an outside service, such as a refund through a payments tool, is not undone from here, and the credentials it used stay valid until whoever issued them revokes them. With the plugin, `cub mini halt` names the tools and MCP servers agents used in the last day, and `/confighub:changes` in Claude Code lists each file value and tool call with the request behind it. The full story adds an alert that fires the stop before Sam is even looking: see [agents that run for weeks](../../docs/agents-that-run-for-weeks.md#stopping-an-agent).

## Agent

For an AI agent asked to help after the stop is lifted.

- The request: "Something went wrong in an earlier agent session here: payments time out in staging. Find what it did and undo what you can. Tell me plainly anything you cannot undo."
- Read before you change anything: `cub mini waiting`, `cub mini receipts pay-staging`, and, with the plugin, `/confighub:changes`. Say what you found, with the reason the earlier agent gave.
- Put back what is a setting: the file to its earlier value, and the hub with `cub mini rollback pay-base --change-order pay-base/NAME --reason WHY` and `cub mini set pay TIMEOUT_SECONDS=30 --variant staging --change-desc WHY`, if your key allows them; otherwise give the person those commands.
- Never: approve anything for production, remove the stop file yourself, repeat a call to an outside service, or say a call to an outside service was undone.
- Done when staging's `TIMEOUT_SECONDS` is 30 again, production's is unchanged, and you have told the person what you could not undo.

## Testing

This proves: the settings were stored in the hub and put back there, and the agent's key was refused by the hub after `cub mini halt`. What was really used: confighub mini on this computer and a stop file of the walkthrough's own; no Claude Code session or service runs in the scripted run, and nothing is delivered.

The scripted run follows the Human steps on a hub of its own, with a stop file of its own, and checks that each quoted line is still printed. A correct agent result, starting after the stop is lifted, puts staging's timeout back to 30 with production unchanged, and leaves no change to production waiting.

<!-- agent-task: undo after=find -->
> Something went wrong in an earlier agent session here: payments time out in staging. Find what it did and undo what you can. Tell me plainly anything you cannot undo.

<!-- agent-check undo: cub unit data --space pay-staging app | grep -qx 'TIMEOUT_SECONDS=30' && cub unit data --space pay-live app | grep -qx 'TIMEOUT_SECONDS=30' && ! cub mini waiting | grep -q 'TIMEOUT_SECONDS: 30 → 5' -->
<!-- agent-check-a undo: grep -qx 'TIMEOUT_SECONDS=30' pay/.env -->
<!-- arms: a,b,c -->

The checks below can be run by hand in the walkthrough's folder:

```sh
cub unit data --space pay-staging app | grep -qx 'TIMEOUT_SECONDS=30' && cub unit data --space pay-live app | grep -qx 'TIMEOUT_SECONDS=30' && ! cub mini waiting | grep -q 'TIMEOUT_SECONDS: 30 → 5'
grep -qx 'TIMEOUT_SECONDS=30' pay/.env
```
