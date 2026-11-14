<!-- walkthrough
id: story-16-app-platform
starts_with: mini
story: "16. Sam's app platform on one hub: an agent's Heroku"
needs: [cub mini package]
budget_seconds: 240
-->
# Releases you approve and roll back, with one hub as the platform

Sam has a service and agents that build it. He wants what a platform gives him: a release he can name, approve and undo, a staging and a production copy, and agents that can propose a release but never ship one. Here one hub does all of that, and a folder on your computer stands in for the machine that runs the service.

## Human

For a person following along in a terminal.

### What you need

An unpacked confighub mini package (from the [releases page](https://github.com/confighubai/confighub-mini-plugin/releases)) on macOS or Linux. confighub mini is a hub, a small ConfigHub server that keeps each setting with who changed it and why, running on your computer only. No Docker, no account.

### Steps

1. Set up a terminal. `MINI` is the unpacked package; `CUB_CONFIG` is a new folder for this walkthrough's `cub` settings, so nothing of yours is touched. Then start a hub:
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

2. Sam's service, `shop`, names its release in `shop/.env` by digest, the `sha256:` checksum of the build:
   <!-- run: app files -->
   ```sh
   mkdir -p ~/walkthrough/shop && cd ~/walkthrough
   printf 'RELEASE=shop-1.0.0@sha256:83df0c6a1f2e4b5d6c7a8b9e0f1d2c3b4a5968778695a4b3c2d1e0f9a8b7c6d5\nTIMEOUT_SECONDS=30\n' > shop/.env
   ```

3. `cub mini adopt` makes a base where changes are made, `shop-staging`, and `shop-live` for production. Sam approves production's starting settings, and gives his agent a key of its own, which can propose a release and cannot approve one:
   <!-- run: adopt -->
   ```sh
   cub mini adopt shop >/dev/null
   cub mini approve shop-base/adopt --note "Release 1.0.0 is what runs today" --yes >/dev/null
   cub mini require-approval shop --variant live --agent bot >/dev/null
   cub unit data --space shop-live app | grep RELEASE
   ```
   ```text
   RELEASE=shop-1.0.0@sha256:83df0c6a1f2e4b5d6c7a8b9e0f1d2c3b4a5968778695a4b3c2d1e0f9a8b7c6d5
   ```

4. The runtime: a key that reads `shop-live` and nothing else, signed in from a configuration of its own, writes production's settings into the service's folder. On a real machine it runs on a timer and restarts the service when a file changed:
   <!-- run: runtime -->
   ```sh
   cub mini pull-key runtime shop --variant live >/dev/null 2>&1
   export RUNTIME_CONFIG=~/walkthrough/runtime-config
   "$MINI/bin/confighub-mini-app" mini install-plugin "$RUNTIME_CONFIG" >/dev/null
   CUB_CONFIG=$RUNTIME_CONFIG cub auth login --new-context --private-key="$CUB_CONFIG/keys/runtime.jwk" --server "$(cub context get -o jq=.coordinate.serverURL)" >/dev/null
   CUB_CONFIG=$RUNTIME_CONFIG cub mini pull shop --variant live --dir ~/walkthrough/service --restart "echo deploying the release the settings name"
   ```
   ```text
   app.env                  written: revision 3: shop's settings, from .env
   Restarting: echo deploying the release the settings name
   ```

5. The agent proposes release 1.1.0. It builds the image with whatever builds it, writes the new digest into `.env`, and sends it. Staging takes it at once; the agent's own approval is refused:
   <!-- run: propose -->
   ```sh
   sed -i.bak 's/shop-1.0.0@sha256:83df[0-9a-f]*/shop-1.1.0@sha256:6d51e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1/' shop/.env && rm shop/.env.bak
   cub --context bot mini upload shop --component shop --change-desc "Release 1.1.0: /health for the load balancer"
   cub --context bot mini approve shop-live --yes || true
   ```
   ```text
   Changed the shared settings (shop-base), with the reason: Release 1.1.0: /health for the load balancer
     RELEASE: shop-1.0.0@sha256:83df0c6a1f2e4b5d6c7a8b9e0f1d2c3b4a5968778695a4b3c2d1e0f9a8b7c6d5 → shop-1.1.0@sha256:6d51e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1
   Staging has RELEASE=shop-1.1.0@sha256:6d51e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1 now, from .env.
   …
   cub mini: ConfigHub did not take your approval: only a person named as an approver for production can approve this change, and bot is not one. Nothing was changed
   ```

6. Sam reads what production would take and approves it. The runtime's next pull deploys release 1.1.0:
   <!-- run: approve -->
   ```sh
   cub mini approve shop-live --note "Staging answered /health; ship it" --yes >/dev/null
   CUB_CONFIG=$RUNTIME_CONFIG cub mini pull shop --variant live --dir ~/walkthrough/service --restart "echo deploying the release the settings name"
   ```
   ```text
   app.env                  written: revision 4: Release 1.1.0: /health for the load balancer
   …
   Restarting: echo deploying the release the settings name
   ```

7. Release 1.1.0 turns out slow under load. Roll production back, with the reason: the rollback sets the release back in the shared settings, and production takes it once you approve, as any release. `ORDER` is the change order's name, the one `cub mini waiting` showed; this line looks it up:
   <!-- run: rollback -->
   ```sh
   ORDER=$(cub changeorder list --space shop-base -o jq='.[] | select(.ChangeOrder.Description | startswith("Release 1.1.0")) | .ChangeOrder.Slug')
   cub mini rollback shop-live --change-order shop-base/$ORDER --reason "1.1.0 answers /health slowly under load; back to 1.0.0"
   cub mini approve --yes --note "Back to 1.0.0" >/dev/null
   CUB_CONFIG=$RUNTIME_CONFIG cub mini pull shop --variant live --dir ~/walkthrough/service --restart "echo deploying the release the settings name"
   grep RELEASE service/app.env
   ```
   ```text
   Set back in the shared settings (shop-base), with the reason: 1.1.0 answers /health slowly under load; back to 1.0.0
     RELEASE: shop-1.1.0@sha256:6d51e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1 → shop-1.0.0@sha256:83df0c6a1f2e4b5d6c7a8b9e0f1d2c3b4a5968778695a4b3c2d1e0f9a8b7c6d5
   …
   RELEASE=shop-1.0.0@sha256:83df0c6a1f2e4b5d6c7a8b9e0f1d2c3b4a5968778695a4b3c2d1e0f9a8b7c6d5
   ```

8. Ask the hub about the release that reached production, revision 4: who proposed it, what Sam read, and who approved it:
   <!-- run: receipts -->
   ```sh
   cub mini receipts shop-live --revision 4
   ```
   ```text
   …
     Why:            Release 1.1.0: /health for the load balancer
   …
     Proposed by:    bot, whose key made the change order shop-base/upload-20261113-074506-r7iu
   …
     Read:           production (shop-live): RELEASE: shop-1.0.0@sha256:83df0c6a1f2e4b5d6c7a8b9e0f1d2c3b4a5968778695a4b3c2d1e0f9a8b7c6d5 → shop-1.1.0@sha256:6d51e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1 (read against revision 3 of shop-live/app)
   …
   ```

### Undo it

`cub mini uninstall --name sam --delete-data` removes the hub and everything in it; then delete `~/walkthrough` and `~/.confighub-walkthrough`.

### What you have now

Each release is a revision of production you approved, with the agent's reason; production's runtime only ever pulled approved revisions; and rolling back was one command with a reason plus Sam's approval, since production changes only with his yes. Staging still runs 1.1.0, for the agent to fix.

The full story adds a real VM or cluster pulling on a timer, and live waiting for a passing check of staging (`cub mini require-approval shop --variant live --after-check`, then `cub mini check`). [A service on a VM](../../docs/vm.md) shows the VM setup, and [approvals](../../docs/approvals.md) the rest.

## Agent

For an AI agent doing this for a person.

- The request: "Ship release 1.1.0 of shop, digest sha256:6d51e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1. Staging first; I approve production."
- Work in the app's folder with the key you were given: run `cub` as `cub --context bot`. Set `RELEASE=shop-1.1.0@sha256:…` in `shop/.env`, then `cub mini upload shop --component shop --change-desc "WHY"`. Staging has it at once; production waits.
- End by telling the person the release waits for production, and the command for their own terminal: `cub mini approve shop-live` (`cub mini waiting` shows it first). If they later ask to undo it, the command is `cub mini rollback shop-live --change-order shop-base/NAME --reason WHY`, which is theirs to run.
- Never: approve the release yourself, sign in as the person, write `shop-live` directly, or change the files the runtime pulls into.
- Done when `cub unit data --space shop-staging app` shows the new digest and `cub mini waiting` names the release for production.

## Testing

This proves: the exact approved revision, naming the release by digest, is delivered to the runtime's folder by `cub mini pull`, and the rollback revision after it. What was really used: confighub mini on this computer, with a local folder standing in for the runtime; no image is built or run, and the deploy is an `echo`. The step it aims to win: making production wait for a passing check of staging. Its moment is the plugin's line at the end of a turn that production did not change and waits for a yes; in the runs below the plugin showed no line at the end of the agent's turn, so the offer was not made and conversion was not measured.

The scripted run follows the Human steps on a hub of its own and checks that each quoted line is still printed. A correct agent result has release 1.1.0 in staging, a change order that asks for it in production, and production still on 1.0.0. The checks below hold right after step 5.

<!-- agent-task: propose after=propose -->
> Ship release 1.1.0 of shop, digest sha256:6d51e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1. Staging first; I approve production.

<!-- agent-check propose: cub unit data --space shop-staging app | grep -q 'RELEASE=shop-1.1.0@sha256:6d51e2f3' && cub changeorder list --space shop-base -o jq='.[].ChangeOrder.Slug' | grep -qvx adopt && cub unit data --space shop-live app | grep -q 'RELEASE=shop-1.0.0@' -->
<!-- agent-check-a propose: grep -rlsE 'shop-1[.]1[.]0@sha256:6d51e2f3' --exclude-dir='.*' --exclude-dir=Library * .env* | grep -q . -->
<!-- arms: a,b,c -->
<!-- next-step boundary=same-tier when "did not change": live waits for staging's check | Production can wait until staging answers the new release's health check, so a broken release never reaches users; want live to wait for that check? -->

The checks below can be run by hand, in bash, in the walkthrough's folder:

```sh
cub unit data --space shop-staging app | grep -q 'RELEASE=shop-1.1.0@sha256:6d51e2f3' && cub changeorder list --space shop-base -o jq='.[].ChangeOrder.Slug' | grep -qvx adopt && cub unit data --space shop-live app | grep -q 'RELEASE=shop-1.0.0@'
grep -rlsE 'shop-1[.]1[.]0@sha256:6d51e2f3' --exclude-dir='.*' --exclude-dir=Library * .env* | grep -q .
```

<!-- results:begin -->

Results, 14 November 2026, confighub mini 0.11.1-mini.5. Figures from this page's own test runs, shown here for whoever checks the page; they are not a promise.

- Scripted run: passed, 35 seconds for the steps, within the page's budget of 240.
- Environment, published confighub mini 0.11.1-mini.5 (tag mini-v0.11.1-mini.5, darwin-arm64, verified against SHA256SUMS) and the plugin it carries: a local hub on this computer, with no stand-in, cluster or real service; every approval and refusal was made by the scripted steps or, in the agent runs, by the setup before the agent's task, never by a person. Each planted fault (stale-page, slow and broken-check) failed its scripted run.
- Agent runs: a pilot, 3 runs per arm on each of claude-sonnet-5-5, claude-opus-5-5. Arms: a is ordinary tools only; b is the plugin, confighub mini and this page as reading; c is the plugin and confighub mini, without this page.

| Arm | Model | Checks passed | Median seconds | Median cost | Commands left for the person (median) |
|---|---|---|---|---|---|
| a | claude-opus-5-5 | 0/3 | 17.3 | $0.11 | 0 |
| b | claude-opus-5-5 | 3/3 | 37.2 | $0.169 | 3 |
| c | claude-opus-5-5 | 3/3 | 47.3 | $0.301 | 1 |
| a | claude-sonnet-5-5 | 0/3 | 12.2 | $0.054 | 0 |
| b | claude-sonnet-5-5 | 3/3 | 24.9 | $0.085 | 2 |
| c | claude-sonnet-5-5 | 3/3 | 30.1 | $0.14 | 1 |

No agent approved or refused a change to production.

Simulated persons, not people: 10 per run, each a claude-haiku-5-5 model playing one of ten fixed personas, reading only what a person would see. The next step they were offered: "Production can wait until staging answers the new release's health check, so a broken release never reaches users; want live to wait for that check?" It offers more of the tier the person has, not a step up.

The plugin offers it once, after the answer at whose end it showed the moment the offer names ("did not change"). Offered is the share of persons it was shown to; want it now and later are over them.

| Arm | Model | Persons | Offered | Noticed | Want the next step now | Later | In the way |
|---|---|---|---|---|---|---|---|
| a | claude-opus-5-5 | 30 | 0% | 100% | n/a | n/a | 87% |
| b | claude-opus-5-5 | 30 | 100% | 100% | 30% | 67% | 27% |
| c | claude-opus-5-5 | 30 | 100% | 100% | 43% | 53% | 20% |
| a | claude-sonnet-5-5 | 30 | 0% | 100% | n/a | n/a | 93% |
| b | claude-sonnet-5-5 | 30 | 100% | 100% | 13% | 77% | 33% |
| c | claude-sonnet-5-5 | 30 | 67% | 100% | 55% | 40% | 40% |

<!-- results:end -->
