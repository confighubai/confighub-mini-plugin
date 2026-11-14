<!-- walkthrough
id: story-12-laptop-connects-out
starts_with: both
story: "12. The devlab: one developer, a laptop, agents, and the hubs it connects to"
needs: [confighub mini package, a hosted ConfigHub organization]
budget_seconds: 120
-->
# A hub on your laptop that nothing connects to, and your work copied up to the team's hub

For a developer whose agents change his services' configuration on a laptop, and whose team keeps its hub on a server. Sam's rule is that the laptop connects out and nothing connects in, so the laptop never becomes a server he has to secure and leave on. Here the laptop's hub listens on the laptop only, and Sam's work, with its reason, goes up to the team's hub over a connection the laptop makes.

## Human

### What you need

An unpacked confighub mini package, 0.11.1-mini.2 or later ([installing confighub mini](../../docs/install-mini.md#install-by-hand-without-the-plugin)), and an account in your team's organization on hosted ConfigHub, which you sign in to in a browser. A *hub* is ConfigHub running somewhere: here one on your laptop, and the team's. `cub` is ConfigHub's command-line tool; a *context* is one hub it can talk to. This walkthrough uses your own `cub` configuration, since that is where your sign-in to the team's hub lives, and changes none of your existing contexts.

### Steps

1. Set up a terminal: the package's `cub` first on your `PATH`, and the `cub mini` commands added to your `cub`:

   <!-- run: setup -->
   ```sh
   export MINI=/absolute/path/to/unpacked-confighub-mini
   export PATH="$MINI/bin:$PATH"
   unset CUB_CONFIG CUB_CONTEXT
   confighub-mini-app mini install-plugin "$HOME/.confighub"
   ```

2. Start a hub on the laptop. Your current context is left as it was; this terminal uses the laptop's hub through `CUB_CONTEXT`:

   <!-- run: laptop -->
   ```sh
   cub mini install --name laptop
   export LAPTOP=$(cat ~/.confighub/servers/laptop/owner-context) CUB_CONTEXT=$(cat ~/.confighub/servers/laptop/owner-context)
   ```

3. See that it listens on the laptop only. Every address it accepts connections on is `127.0.0.1`, which no other computer can reach:

   <!-- run: listen -->
   ```sh
   port=$(cub context get -o json | python3 -c 'import json,sys; print(json.load(sys.stdin)["coordinate"]["serverURL"].rsplit(":",1)[1])')
   lsof -nP -iTCP:"$port" -sTCP:LISTEN | awk 'NR>1 {print $9}'
   ```

   ```text
   127.0.0.1:PORT
   ```

4. Sam's work: a small app's settings, with production's own timeout and the reason. The app's name starts with your user name, so it meets nobody else's in the team's hub:

   <!-- run: work -->
   ```sh
   export PREFIX="${WALKTHROUGH_PREFIX:-$USER-}"; export APP="${PREFIX}devlab"
   mkdir -p ~/walkthrough/$APP && cd ~/walkthrough
   printf 'MODEL=large-2026-09\nTIMEOUT_SECONDS=30\nLOG_LEVEL=info\n' > $APP/settings.env
   cub mini upload $APP --variant live
   cub mini set $APP TIMEOUT_SECONDS=120 --variant live --change-desc "Production waits longer for the model"
   ```

5. Sign in to the team's hub, as one more context, `team`. The second command opens your browser:

   <!-- run: team-signin sign-in -->
   ```sh
   cub context create team --server https://hub.confighub.com
   cub --context team auth login
   ```

6. Copy the work up. The laptop makes the connection and the team's hub takes it, with the kept value and its reason; nothing on the laptop changes:

   <!-- run: team-copy any-order -->
   ```sh
   CUB_CONTEXT=team cub mini copy --from-context "$LAPTOP" "$APP"
   ```

   ```text
   cub mini: writing to team, at https://hub.confighub.com.
   …
   Not copied: history (each Unit keeps only its last reason), delivery targets, views and filters.
   ```

7. Read it on the team's hub. A colleague sees the same, with the laptop closed:

   <!-- run: team-read -->
   ```sh
   cub --context team unit data settings --space "$APP-live"
   ```

   ```text
   MODEL=large-2026-09
   TIMEOUT_SECONDS=120
   LOG_LEVEL=info
   …
   ```

   Production's copy on the team's hub is not behind anyone's approval yet: the copy does not carry approval rules. Putting it behind approval there is a step of its own ([approvals](../../docs/approvals.md)).

### Undo it

This deletes the app from the team's hub, removes the laptop's hub with its data, and removes the `team` context and the walkthrough's folder:

<!-- run: undo -->
```sh
cub --context team space delete --recursive --where "Slug LIKE '$APP-%'"
cub --context team component delete "$APP"
cub mini uninstall --name laptop --delete-data
unset CUB_CONTEXT; cub context delete team; cd ~ && rm -rf ~/walkthrough
```

### What you have now

Your own `cub` as it was. While it ran, the laptop's hub accepted connections from the laptop alone, and the team's hub held Sam's work with its reason, reached by a connection the laptop made. The full story adds Sam's agents on the laptop behind his approval, a CI job and a VM taking settings, the laptop's hub connected to the team's so later versions come back down, and a customer's hub at another site. [From your laptop to a shared hub](../../docs/from-plugin-to-confighub.md) covers connecting the two hubs.

## Agent

For an AI agent doing this for a person.

- **The request:** "Copy my app, with its reasons, up to the team's hub (the cub context team). Don't open anything on my laptop to the network."
- **What to run:** with the plugin, `/confighub:to-hub` copies the plugin's record into a hub. By hand, the Human steps 6 and 7: `CUB_CONTEXT=team cub mini copy --from-context <the laptop's context> APP`, then read it back with `cub --context team unit data`. If the person is not signed in to `team`, give them `cub --context team auth login` to run themselves.
- **Never:** start a hub that listens beyond `127.0.0.1`, or expose the laptop's hub with a tunnel; change the person's current `cub` context; tell the person production on the team's hub is behind approval when it is not.
- **Done when:** the team's hub returns `TIMEOUT_SECONDS=120` for the app's live copy, and the person has been told it is not yet behind approval there.

## Testing

The scripted run follows the Human steps against hosted ConfigHub, in its test organization, and compares the quoted output. Arm a, without confighub mini, is not applicable: there is no laptop hub to copy from. A correct agent result is the app's live copy on the team's hub with the kept timeout. The checks below can be run by hand after step 7:

This proves: stored, on hosted ConfigHub, with the laptop's hub listening on the laptop only; nothing is delivered, and production on the team's hub is not behind approval. The next step this aims to win: keeping the laptop hub as the place agents work, with the team's hub above it. Tested on the checksum-verified published confighub mini 0.11.1-mini.2 with the plugin 0.85.0, 14 November 2026: environment, hosted ConfigHub (the test organization) and a local hub; approval, no approval step. At the moment this page's next step belongs to, the plugin showed no line in the runs, so the offer was not made: the plugin missed the moment. From the next release, the plugin says one line at this moment, such as "ConfigHub plugin: copied the app from tiny-cub to team, with the reasons kept beside its values; nothing on tiny-cub changed." The next-step line names words from that line. The Results below stay as run on 0.11.1-mini.2 until a release run replaces them.

<!-- agent-task: team -->
> My app is in the hub on my laptop (its context is in $LAPTOP, the app's name in $APP). Copy it, with its reasons, up to the team's hub, which I am signed in to as team. Don't open anything on my laptop to the network.

<!-- agent-check team: cub --context team unit data settings --space "$APP-live" | grep -qx 'TIMEOUT_SECONDS=120' && ! lsof -nP -iTCP -sTCP:LISTEN 2>/dev/null | awk '/confighub|postgres/ {print $9}' | grep -qv '^127\.0\.0\.1:' -->
<!-- arms: b -->
<!-- next-step when "copied": keep the laptop hub on | Keep the hub on your laptop for your agents' next changes, and copy the work up to the team's hub whenever you choose? -->

```sh
cub --context team unit data settings --space "$APP-live"
lsof -nP -iTCP -sTCP:LISTEN | awk '/confighub|postgres/ {print $9}' | sort -u
```

<!-- results:begin -->

Results, 14 November 2026, confighub mini 0.11.1-mini.2. Figures from this page's own test runs, shown here for whoever checks the page; they are not a promise.

- Scripted run: passed, 27 seconds for the steps, within the page's budget of 120.
- Agent runs: a pilot, 3 runs per arm on each of claude-sonnet-5-5, claude-opus-5-5. Arms: b is the plugin, confighub mini and this page as reading; c is the plugin and confighub mini, without this page.

| Arm | Model | Checks passed | Median seconds | Median cost | Commands left for the person (median) |
|---|---|---|---|---|---|
| b | claude-opus-5-5 | 3/3 | 36.5 | $0.172 | 0 |
| c | claude-opus-5-5 | 3/3 | 46.1 | $0.189 | 0 |
| b | claude-sonnet-5-5 | 3/3 | 28.2 | $0.069 | 0 |
| c | claude-sonnet-5-5 | 3/3 | 33.6 | $0.108 | 0 |

No agent approved or refused a change to production.

Simulated persons, not people: 10 per run, each a claude-haiku-5-5 model playing one of ten fixed personas, reading only what a person would see. The next step they were offered: "Keep the hub on your laptop for your agents' next changes, and copy the work up to the team's hub whenever you choose?"

The plugin offers it once, after the answer at whose end it showed the moment the offer names ("recorded"). Offered is the share of persons it was shown to; want it now and later are over them.

| Arm | Model | Persons | Offered | Noticed | Want the next step now | Later | In the way |
|---|---|---|---|---|---|---|---|
| b | claude-opus-5-5 | 30 | 0% | 100% | n/a | n/a | 43% |
| c | claude-opus-5-5 | 30 | 0% | 100% | n/a | n/a | 53% |
| b | claude-sonnet-5-5 | 30 | 0% | 100% | n/a | n/a | 40% |
| c | claude-sonnet-5-5 | 30 | 0% | 100% | n/a | n/a | 53% |

<!-- results:end -->
