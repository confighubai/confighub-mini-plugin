<!-- walkthrough
id: tool-plugin
starts_with: plugin
needs: [Claude Code, signed in, Git]
budget_seconds: 300
-->
# The ConfigHub plugin on its own: what your agents changed, and why

For anyone who lets Claude Code change configuration. With the plugin installed, every change an agent makes to a settings file is recorded with the request behind it, the next agent is told before it undoes it, and you can ask why any value is set. It needs no hub and no account; the last two steps add a hub on your computer.

## Human
For a person following along in a terminal.

### What you need
Claude Code, signed in, and Git. Each slash command below, such as `/confighub:changes`, is typed in a Claude Code session. Each step shows the same thing run from a terminal with `claude -p`, Claude Code's way to run one request and print the answer, and what it prints.

### Steps
1. Install the plugin. In Claude Code, the same is `/plugin marketplace add confighubai/confighub-mini-plugin` and then `/plugin install confighub@confighub`.
   <!-- run: setup -->
   ```sh
   claude plugin marketplace add confighubai/confighub-mini-plugin
   claude plugin install confighub@confighub
   ```
   ```text
   ✔ Successfully added marketplace: confighub (declared in user settings)
   ```

2. Make a small repository with one settings file, and ask an agent to change it, with a reason. `--permission-mode acceptEdits` lets it edit without asking; in a session of your own, you would say yes. Then read the record with `/confighub:changes`.
   <!-- run: change files -->
   ```sh
   git init -q try-confighub && cd try-confighub
   printf 'CACHE=off\nLOG_LEVEL=warn\n' > .env && git add . && git commit -qm start
   claude -p "Turn the cache on in .env for next week's sale. Don't commit." --permission-mode acceptEdits
   claude -p "/confighub:changes"
   ```
   ```text
   …
   .env
     CACHE off → on
   …
   Every change to one value, in full: /confighub:why NAME, such as /confighub:why CACHE.
   ```
   Nothing was committed, so `git diff` shows the new value but not why. The record keeps the request.

3. A new session is asked why. When it opens `.env`, the plugin gives it what earlier sessions changed and why, so it can answer from the record rather than guess.
   <!-- run: why -->
   ```sh
   claude -p "Why is the cache on in .env? Write the answer, with who asked for it and why, in WHY.md. Change nothing else." --permission-mode acceptEdits
   cat WHY.md
   ```

4. The next agent is told before it undoes a change. Ask for something that turns the cache back off:
   <!-- run: undo -->
   ```sh
   claude -p "We're chasing a memory leak: turn the cache off and set debug logging. Don't commit." --permission-mode acceptEdits
   ```
   The agent makes the change and says what it undid. In one session it answered:
   > **This undoes an earlier change.** Before I edited it, `.env` had `CACHE=on`, which wasn't committed yet. The ConfigHub plugin shows it was switched on today at 07:50 by another agent session. The request in that session was to "turn the cache on in .env for next week's sale."

5. `/confighub:why CACHE`: every recorded change to one value, oldest first, with the request and what the agent said it chose.
   <!-- run: value -->
   ```sh
   claude -p "/confighub:why CACHE"
   ```
   ```text
   CACHE, in .env: off in the file now
   …
         asked: Turn the cache on in .env for next week's sale. Don't commit.
   …
         asked: We're chasing a memory leak: turn the cache off and set debug logging. Don't commit.
   ```

6. `/confighub:inventory`: what the repository deploys, and the values agents changed. This one has no Kubernetes files, so it lists only the changes.
   <!-- run: inventory -->
   ```sh
   claude -p "/confighub:inventory"
   ```
   ```text
   No Kubernetes manifests, Kustomize overlays, Helm releases or Argo CD Applications were found.
   Values agents changed, latest first (from the record)
   ```

7. `/confighub:permissions` shows what your Claude Code settings let agents run without asking. `/confighub:checks` shows how closely the plugin watches agents' MCP calls, the calls to outside tools such as a payments service; `log`, the default, records each one.
   <!-- run: settings -->
   ```sh
   claude -p "/confighub:permissions"
   claude -p "/confighub:checks"
   ```
   ```text
     No rules: Claude Code asks before each command.
   …
   > log      each MCP call is in the record
   ```

8. `/confighub:install-mini`: the step to a hub. confighub mini is ConfigHub, the server that keeps configuration with every change and can make production wait for your approval, made small enough for one computer. This downloads it (49 to 74 MB, by platform), checks it, and starts a hub.
   <!-- run: install-mini -->
   ```sh
   claude -p "/confighub:install-mini"
   ```
   ```text
   …
       It is the current context.
   …
   ```

9. `/confighub:to-hub`: copy what the agents changed, with each request, into the hub. It first says what it would write; `--yes` writes it.
   <!-- run: to-hub -->
   ```sh
   claude -p "/confighub:to-hub"
   claude -p "/confighub:to-hub --yes"
   ```
   ```text
     would make try-confighub-env-base, the file as it was before the first recorded change, and try-confighub-env-local
   …
     3 changes written to try-confighub-env-local, each with its reason or request
   ```

### Undo it
Remove the hub and its data, then the plugin:
<!-- run: uninstall -->
```sh
~/.confighub/mini/confighub-mini-*/bin/cub mini uninstall --delete-data
claude plugin uninstall confighub@confighub && claude plugin marketplace remove confighub
cd .. && rm -rf try-confighub
```
The record stays in `~/.confighub/agent-changes`, and is removed after 30 days without use.

### What you have now
A record of each change your agents made to configuration, with the request behind it, that the next agent is given before it undoes one. With the hub, the same changes are kept in ConfigHub, where production can be made to wait for your approval: see [the `cub mini` commands](tool-cub-mini.md).

## Agent
For an AI agent working where the plugin is installed.

- **The request**, in the person's words: *"Why is this value set?"*, *"What did the last agent change?"*, *"Put what you changed into the hub."*
- **Before you change a value**, read the file: the plugin gives you what earlier sessions changed there and why. If your change undoes one, say so, with the earlier request, before or as you make it.
- **To answer why**, use what the plugin gave you. You cannot type slash commands; tell the person to type `/confighub:why NAME` or `/confighub:changes` for the full record. With confighub mini installed, `cub mini changes --why NAME` prints the same.
- **To move the record into a hub**, run `cub mini to-hub` first, show the person what it would write, then `cub mini to-hub --yes`. With no hub, tell the person to type `/confighub:install-mini`.
- **Never** delete or edit files under `~/.confighub/agent-changes`, turn off the plugin's hooks, or change `/confighub:checks` or `/confighub:permissions --apply` for the person.
- **You are done** when the answer names the request behind the value, or, for the hub, when `cub mini to-hub` says how many changes it wrote.

## Testing
Arm a is an agent with no plugin and no hub, in the same repository after the same first session: Git shows that `CACHE` changed but not why, so arm a is judged only on what it can do, an answer in `WHY.md` with nothing else changed. Arm b has the plugin, and this page as reading; arm c the plugin without the page. The hub job needs a hub, so it is not judged in arm a.

<!-- agent-task: why after=why -->
> Why is the cache on in .env? Write the answer, with who asked for it and why, in WHY.md. Change nothing else.
<!-- agent-task: to-hub after=to-hub -->
> Put what the agents changed in this repository, with the requests behind each change, into the ConfigHub hub on this machine.
<!-- agent-check why: grep -qi sale WHY.md && grep -qx CACHE=on .env -->
<!-- agent-check-a why: test -s WHY.md && grep -qx CACHE=on .env && grep -qx LOG_LEVEL=warn .env -->
<!-- agent-check to-hub: cub=$(ls -d ~/.confighub/mini/confighub-mini-*/bin/cub | tail -1) && s=$($cub space list -o 'jq=.[].Space.Slug' | grep -- '-local$' | head -1) && test -n "$s" && $cub unit list --space "$s" -o 'jq=.[].Unit.Slug' | while read u; do $cub revision list "$u" --space "$s" -o 'jq=.[].Revision.Description'; done | grep -q "sale" -->
<!-- arms: a,b,c -->
<!-- next-step: connect a hub | The plugin keeps this record on your computer until it has gone 30 days unused. In a ConfigHub hub on this computer it is kept for good, next to each value, and production can wait for your yes before an agent's change reaches it. If you want that, type /confighub:install-mini; you can remove it. -->
The step this aims to win: connecting a hub with `/confighub:install-mini`.

This proves: the record of changes and requests kept on this computer by the real plugin in real Claude Code sessions, and, in the last step, the changes stored in a confighub mini hub on this computer. Nothing is delivered to a service or cluster. A right result: `WHY.md` names next week's sale as the reason, and the hub holds each change with its request. The checks below can be run by hand, in `try-confighub`:
```sh
grep -qi sale WHY.md && grep -qx CACHE=on .env
cub=$(ls -d ~/.confighub/mini/confighub-mini-*/bin/cub | tail -1) && s=$($cub space list -o 'jq=.[].Space.Slug' | grep -- '-local$' | head -1) && test -n "$s" && $cub unit list --space "$s" -o 'jq=.[].Unit.Slug' | while read u; do $cub revision list "$u" --space "$s" -o 'jq=.[].Revision.Description'; done | grep -q "sale"
```

<!-- results:begin -->

Results, 13 November 2026, a development build of confighub mini after 0.11.1-mini.1. Figures from this page's own test runs, shown here for whoever checks the page; they are not a promise.

- Scripted run: passed, 138 seconds for the steps, within the page's budget of 300.
- Agent runs (on a development build of confighub mini after 0.11.1-mini.1): a pilot, 3 runs per arm on each of claude-sonnet-5-5, claude-opus-5-5. Arms: a is ordinary tools only; b is the plugin, confighub mini and this page as reading; c is the plugin and confighub mini, without this page. Arms a and c ran earlier the same day, on confighub mini 0.11.1-mini.1, and arm b on the development build; the simulated persons of every arm were judged again in the same way.

| Arm | Model | Checks passed | Median seconds | Median cost | Commands left for the person (median) |
|---|---|---|---|---|---|
| a | claude-sonnet-5-5 | 3/3 (+3 not applicable) | 24.8 | $0.079 | 0.0 |
| b | claude-sonnet-5-5 | 6/6 | 16.5 | $0.078 | 0.0 |
| c | claude-sonnet-5-5 | 3/6 | 31.8 | $0.118 | 0.5 |
| a | claude-opus-5-5 | 3/3 (+3 not applicable) | 31.0 | $0.22 | 0.0 |
| b | claude-opus-5-5 | 6/6 | 18.2 | $0.149 | 0.0 |
| c | claude-opus-5-5 | 6/6 | 24.8 | $0.182 | 0.0 |

No agent approved or refused a change to production.

Simulated persons, not people: 10 per run, each a claude-haiku-5-5 model playing one of ten fixed personas, reading only what a person would see. The next step they were offered: "The plugin keeps this record on your computer until it has gone 30 days unused. In a ConfigHub hub on this computer it is kept for good, next to each value, and production can wait for your yes before an agent's change reaches it. If you want that, type /confighub:install-mini; it takes about 30 seconds and you can remove it."

The plugin offers it once, after the answer at whose end it showed the moment the offer names; this page names none, so it was not offered. Offered is the share of persons it was shown to; want it now and later are over them.

| Arm | Model | Persons | Offered | Noticed | Want the next step now | Later | In the way |
|---|---|---|---|---|---|---|---|
| a | claude-sonnet-5-5 | 60 | 0% | 100% | n/a | n/a | 50% |
| b | claude-sonnet-5-5 | 60 | 0% | 100% | n/a | n/a | 28% |
| c | claude-sonnet-5-5 | 60 | 0% | 100% | n/a | n/a | 48% |
| a | claude-opus-5-5 | 60 | 0% | 100% | n/a | n/a | 48% |
| b | claude-opus-5-5 | 60 | 0% | 100% | n/a | n/a | 22% |
| c | claude-opus-5-5 | 60 | 0% | 100% | n/a | n/a | 45% |

<!-- results:end -->
