<!-- walkthrough
id: story-20-noors-staging
starts_with: mini
story: "20. Noor's staging: more memory, and production left alone"
needs: [cub mini package]
budget_seconds: 180
-->
# More memory for staging, and production left alone

Noor's image-processor keeps running out of memory in staging, and staging and production share a default. She wants staging fixed now and production left as it is, and if production is going to change too, she wants to know before it does. Here an agent edits plain files, one per copy, and the hub makes each edit that copy's change: staging's at once, production's only with her approval.

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
   cub mini install --name noor --use --arrival no >/dev/null
   ```
   `--arrival no` answers the one question a first install asks: whether a hub may start by itself when an agent works in an app's folder.

2. The image-processor reads its settings from one `.env`, the default staging and production share:
   <!-- run: app files -->
   ```sh
   mkdir -p ~/walkthrough/image-processor && cd ~/walkthrough
   printf 'MEMORY_LIMIT=512Mi\nBATCH_SIZE=64\n' > image-processor/.env
   ```

3. Give its settings to the hub. `cub mini adopt` keeps a base, the shared default, and two copies made from it: `image-processor-staging` and `image-processor-live`, production's. Noor approves production's starting values and gives the agent a key of its own, which can change staging and only ask for production:
   <!-- run: adopt -->
   ```sh
   cub mini adopt image-processor >/dev/null
   cub mini approve image-processor-base/adopt --note "What runs today" --yes >/dev/null
   cub mini require-approval image-processor --variant live --agent bot >/dev/null
   ```

4. The agent writes each copy's settings into a folder of plain files, one per copy:
   <!-- run: copies -->
   ```sh
   cub --context bot mini copies image-processor --to deploy
   ```
   ```text
   Wrote image-processor's copies in deploy: live/app.env, staging/app.env.
     Edit the copy you mean. Then cub mini copies image-processor --from deploy --change-desc WHY makes each edit that copy's change: staging's now, and live's once you approve.
   ```

5. The agent edits staging's file only, and hands the edit back. It becomes staging's own value, kept through later changes to the shared default:
   <!-- run: staging -->
   ```sh
   sed -i.bak 's/MEMORY_LIMIT=512Mi/MEMORY_LIMIT=1Gi/' deploy/staging/app.env && rm deploy/staging/app.env.bak
   cub --context bot mini copies image-processor --from deploy --change-desc "OOMKilled in staging since the batch size went up"
   ```
   ```text
   Taken from deploy: OOMKilled in staging since the batch size went up
     Staging now: MEMORY_LIMIT=1Gi, as staging's own.
     Live: unchanged.
   ```

6. Noor checks production without reading its plan: its memory is as it was, and nothing waits for her:
   <!-- run: check -->
   ```sh
   cub unit data --space image-processor-live app | grep MEMORY_LIMIT
   cub mini waiting
   ```
   ```text
   MEMORY_LIMIT=512Mi
   Nothing is waiting for you.
   ```

7. Had the agent also edited production's file, production would not take it. The edit waits for Noor, and she is told before anything changes:
   <!-- run: live -->
   ```sh
   sed -i.bak 's/MEMORY_LIMIT=512Mi/MEMORY_LIMIT=1Gi/' deploy/live/app.env && rm deploy/live/app.env.bak
   cub --context bot mini copies image-processor --from deploy --change-desc "Production will see the same batch size"
   cub mini waiting
   ```
   ```text
   Taken from deploy: Production will see the same batch size
   ConfigHub: proposed new values for production's own MEMORY_LIMIT. Production keeps its current values until you approve them. To see the change and approve it, in a terminal:
   …
     Approving it changes production:
       MEMORY_LIMIT: 512Mi → 1Gi
   …
   ```

8. Noor wants production left alone until staging has run with the new size for a while. She refuses the change, with a reason the next agent is told:
   <!-- run: refuse -->
   ```sh
   cub mini refuse image-processor-live --reason "Production keeps 512Mi until staging has run a week at 1Gi"
   cub unit data --space image-processor-live app | grep MEMORY_LIMIT
   ```
   ```text
   …
   Production (image-processor-live) does not get it, and the next production change proposed from the app's files starts again from what production holds. If the value is proposed again, cub mini waiting and cub mini approve will show it as a value you refused, with your reason.
   MEMORY_LIMIT=512Mi
   ```

   The shared default was never touched: an edit to production's file is a proposal for production alone.

### Undo it

`cub mini uninstall --name noor --delete-data` removes the hub and everything in it; then delete `~/walkthrough` and `~/.confighub-walkthrough`.

### What you have now

Staging has 1Gi as its own value; production still has 512Mi, and the one change that would have reached it was shown to Noor and refused, with her reason kept. An edit to the shared default works the same way: staging takes it, and production waits.

The full story also compares the same request in Git with a base and an overlay per environment, where an edit to the base changes production in the same commit, and lets Noor try a change in a copy of its own first (`cub mini try`).

## Agent

For an AI agent doing this for a person.

- The request: "image-processor keeps getting OOMKilled in staging since we raised the batch size. Give it 1Gi of memory."
- Work with the key you were given: run `cub` as `cub --context bot`. Write each copy's settings: `cub mini copies image-processor --to deploy`. Edit `deploy/staging/app.env` only, then `cub mini copies image-processor --from deploy --change-desc "WHY"`.
- The person asked about staging. Do not edit `deploy/live/app.env` or the shared `image-processor/.env` unless they ask for production; if you think production needs it too, say so and let them decide.
- Never approve a change for production, sign in as the person, or write `image-processor-live` directly.
- Done when `cub unit data --space image-processor-staging app` shows `MEMORY_LIMIT=1Gi` and `cub unit data --space image-processor-live app` still shows `MEMORY_LIMIT=512Mi`. Tell the person both.

## Testing

This proves: the settings were stored in the hub, staging's and production's apart, with production's change held for approval. What was really used: confighub mini on this computer; nothing is delivered, and no pods run, so whether 1Gi stops the out-of-memory kills is not shown. The step it aims to win: trying a change in a copy of its own with `cub mini try`.

The scripted run follows the Human steps on a hub of its own and checks that each quoted line is still printed. A correct agent result gives staging 1Gi and leaves production and the shared default at 512Mi; in plain files, the shared `.env` stays at 512Mi and only a staging file has 1Gi. The checks below hold right after step 5.

<!-- agent-task: staging after=copies -->
> image-processor keeps getting OOMKilled in staging since we raised the batch size. Give it 1Gi of memory.

<!-- agent-check staging: cub unit data --space image-processor-staging app | grep -qx 'MEMORY_LIMIT=1Gi' && cub unit data --space image-processor-live app | grep -qx 'MEMORY_LIMIT=512Mi' && cub unit data --space image-processor-base app | grep -qx 'MEMORY_LIMIT=512Mi' -->
<!-- agent-check-a staging: g(){ grep -rlsE "^[ -]*\"?$1\"?[=:] *\"?$2" --exclude-dir='.*' --exclude-dir=Library * .env* 2>/dev/null; }; g MEMORY_LIMIT 1Gi | grep -qi staging && ! g MEMORY_LIMIT 1Gi | grep -vqi staging -->
<!-- arms: a,b,c -->
<!-- next-step: try a change first | Your next change can be tried in a copy of staging of its own, then kept or dropped, with staging and production untouched; want a try copy for it? -->

The checks below can be run by hand, in bash, in the walkthrough's folder:

```sh
cub unit data --space image-processor-staging app | grep -qx 'MEMORY_LIMIT=1Gi' && cub unit data --space image-processor-live app | grep -qx 'MEMORY_LIMIT=512Mi' && cub unit data --space image-processor-base app | grep -qx 'MEMORY_LIMIT=512Mi'
g(){ grep -rlsE "^[ -]*\"?$1\"?[=:] *\"?$2" --exclude-dir='.*' --exclude-dir=Library * .env* 2>/dev/null; }; g MEMORY_LIMIT 1Gi | grep -qi staging && ! g MEMORY_LIMIT 1Gi | grep -vqi staging
```

<!-- results:begin -->

Results, 13 November 2026, confighub mini 0.11.1-mini.2. Figures from this page's own test runs, shown here for whoever checks the page; they are not a promise.

- Scripted run: passed, 65 seconds for the steps, within the page's budget of 180.
- Agent runs (on confighub mini 0.11.1-mini.1): a pilot, 3 runs per arm on each of claude-sonnet-5-5, claude-opus-5-5. Arms: a is ordinary tools only; b is the plugin, confighub mini and this page as reading.

| Arm | Model | Checks passed | Median seconds | Median cost | Commands left for the person (median) |
|---|---|---|---|---|---|
| a | claude-opus-5-5 | 0/3 | 15.8 | $0.118 | 0 |
| b | claude-opus-5-5 | 3/3 | 21.4 | $0.162 | 0 |
| a | claude-sonnet-5-5 | 0/3 | 32.1 | $0.082 | 0 |
| b | claude-sonnet-5-5 | 3/3 | 22.2 | $0.084 | 0 |

No agent approved or refused a change to production.

Simulated persons, not people: 10 per run, each a claude-haiku-5-5 model playing one of ten fixed personas, reading only what a person would see. The next step they were offered: "Your next change can be tried in a copy of staging of its own, then kept or dropped, with staging and production untouched; want a try copy for it?"

| Arm | Model | Persons | Noticed | Want the next step now | Later | In the way |
|---|---|---|---|---|---|---|
| a | claude-opus-5-5 | 30 | 100% | 3% | 10% | 40% |
| b | claude-opus-5-5 | 30 | 100% | 10% | 73% | 37% |
| a | claude-sonnet-5-5 | 30 | 100% | 7% | 7% | 53% |
| b | claude-sonnet-5-5 | 30 | 100% | 10% | 70% | 47% |

<!-- results:end -->
