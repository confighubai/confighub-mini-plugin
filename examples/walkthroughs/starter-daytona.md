<!-- walkthrough
id: starter-daytona
starts_with: mini
starter: daytona
needs: [confighub mini package, hosted ConfigHub for the shared step]
budget_seconds: 240
-->
# Bring a sandbox experiment back for review

A queue spikes and you want to try batches of 240 instead of 120. Use a disposable Daytona sandbox so the experiment cannot approve its own change. When you delete the sandbox, your team can still review the setting and the reason. Production stays at 120.

## Human

Use an unpacked [mini package](../../docs/install-mini.md) that includes the Daytona starter. Start with the local rehearsal: it needs no Daytona account and tests the proposal, export, and shared review. It does not run a batch job. Use an empty working directory and keep its keys and evidence private. The shared step needs a disposable app name in an organization where you can create and remove test resources.

### Steps

1. Start a disposable mini with its own configuration.
   <!-- run: setup -->
   ```sh
   export MINI=/absolute/path/to/unpacked-confighub-mini
   export PATH="$MINI/bin:$PATH" CUB_MINI_STARTERS=on
   "$MINI/bin/confighub-mini-app" mini install-plugin "$HOME/.confighub"
   cub mini install --name batch-sandbox --use
   export LOCAL_HUB=$(cub context get -o jq=.name)
   mkdir -p ~/starter-example/batch ~/starter-example/returned; cd ~/starter-example
   ```
2. Connect the batch job. Read the starter and its defaults in the hub, then approve the packaged definitions. Production approval for this job is separate.
   <!-- run: deploy -->
   ```sh
   printf 'DAYTONA_BATCH_LIMIT=120\n' > batch/daytona.env
   cp batch/daytona.env batch/app.env
   cub mini adopt batch
   cub unit get daytona --space starters-base -o jq=.Unit.ToolchainType
   cub variant approve starters-approved --all --note "Review the packaged starters"
   cub mini require-approval batch --variant live --agent batch-proposer
   cub mini copy batch --to-file "$PWD/returned/baseline.tar.gz"
   ```
3. In a real Daytona run, the first two steps run inside the sandbox under the owner account, using a Linux package of the sandbox's architecture. Put only the app folder and the restricted ConfigHub configuration in the separate proposer user's home. Sign that user in with its own key and the loopback URL. Do not give the proposer access to the Daytona CLI on your machine or the sandbox owner's OS account. This rehearsal checks the hub key, not OS isolation.
   <!-- run: update -->
   ```sh
   CUB_CONFIG="$HOME/.confighub-agent-batch-proposer" CUB_CONTEXT=batch-proposer \
     "$MINI/examples/daytona-starter/propose" "$PWD/batch" "$PWD/returned"
   ```
   ```text
   Proposal returned; sandbox production remains at 120.
   ```
4. Back out of the experiment for this app: discard the local file edit and leave production alone. Export current settings and separately keep the reason. For a real sandbox, download the baseline, returned settings and proposal to the owner's machine before deleting that sandbox. The archive contains the current copies, not the pending order or its history.
   <!-- run: undo -->
   ```sh
   cp batch/daytona.env batch/app.env
   cub mini copy batch --to-file "$PWD/returned/batch.tar.gz"
   test -s returned/proposal.txt
   cub unit data app --space batch-live | grep -Fx DAYTONA_BATCH_LIMIT=120
   ```
   ```text
   DAYTONA_BATCH_LIMIT=120
   ```
5. Move the stored app to a shared hub. From your own terminal sign in there. In the real sandbox path, import the baseline archive, verify the returned setting and reason, then reapply the change to the destination base. Importing a changed base first can leave no new diff to review.
   <!-- run: sign-in sign-in -->
   ```sh
   cub context create shared --server https://hub.confighub.com
   cub --context shared auth login
   export TEAM_APP="${WALKTHROUGH_PREFIX:-$USER-}batch"
   ```
   <!-- run: move -->
   ```sh
   cub --context shared mini copy --from-file "$PWD/returned/baseline.tar.gz" --name "$TEAM_APP"
   cub --context shared changeworkflow get --space workflows "$TEAM_APP-live-approval" >/dev/null
   grep -F 'after a queue spike' returned/proposal.txt >/dev/null
   cub --context shared function set --space "$TEAM_APP-base" --unit app --toolchain AppConfig/Env \
     --change-desc "Increase the batch size after a queue spike." -- set-string-path '*' DAYTONA_BATCH_LIMIT 240
   cub --context shared changeorder create --space "$TEAM_APP-base" sandbox-batch \
     --in-scope-space "$TEAM_APP-live" --change-workflow "workflows/$TEAM_APP-live-approval" \
     --description "Increase the batch size after a queue spike."
   cub --context shared unit data app --space "$TEAM_APP-live" | grep -Fx DAYTONA_BATCH_LIMIT=120
   ```
6. Remove the sandbox's app once you have verified the shared copy. When you have finished reviewing the disposable shared app, delete that copy and its workflow too.
   <!-- run: delete -->
   ```sh
   cub component delete --recursive --detach batch
   ```

For cleanup, remove only the app named by `TEAM_APP` from the shared hub, then its workflow, with `cub --context shared component delete --recursive --detach "$TEAM_APP"` and `cub --context shared changeworkflow delete --space workflows "$TEAM_APP-live-approval"`. Stop the local rehearsal hub with `cub mini stop --name batch-sandbox`. In Daytona, use `daytona sandbox delete YOUR_TEST_SANDBOX` and confirm it is gone.

## Agent

Ask: “Try a batch size of 240 because the queue spiked. Leave production at 120 and bring me back a proposal I can review.” Use only the supplied proposer context. Report what changed in staging, what live still holds, the reason, and where the owner can review it.

- **Deploy:** run step 2's `cub mini adopt batch`. The starter approval, the proposer key and the baseline export are the owner's, so end with step 2's last three commands for them to run.
- **Update:** run step 3 with the proposer context, and write the reason to `returned/proposal.txt`.
- **Move:** a proposer key cannot sign in to or write to the team's hub, so do not try. Give the owner the exact commands of step 5, from the copy to the change order, and stop; they run them in their own terminal.
- **Delete:** step 6, only once the team's hub holds the app.

Never approve a production change, create or delete a cloud sandbox, or report the original approval history as transferred; if a sandbox was deleted, use the downloaded files.

## Testing

The checks read the structured starter, the staging and live Units, and the shared hub's new pending order. The local scripted path tests configuration and the approval boundary. A separate real Daytona run is needed to test loopback and separate OS users. Neither path proves that a batch job ran.

<!-- agent-task: deploy -->
> Set up my batch job so I can try changes while keeping production at 120.
<!-- agent-person deploy: cub variant approve starters-approved --all --note "Read them" && cub mini require-approval batch --variant live --agent batch-proposer && cub mini copy batch --to-file "$PWD/returned/baseline.tar.gz" -->
<!-- agent-check deploy: cub unit get daytona --space starters-base -o jq=.Unit.ToolchainType | grep -qx AppConfig/YAML && cub unit data app --space batch-live | grep -qx DAYTONA_BATCH_LIMIT=120 -->
<!-- agent-task: update -->
> Try 240 because the queue spiked, and leave production at 120.
<!-- agent-check update: cub unit data app --space batch-staging | grep -qx DAYTONA_BATCH_LIMIT=240 && cub unit data app --space batch-live | grep -qx DAYTONA_BATCH_LIMIT=120 && grep -q 'after a queue spike' returned/proposal.txt -->
<!-- agent-task: undo -->
> Put my local file back and keep the experiment for later.
<!-- agent-check undo: grep -qx DAYTONA_BATCH_LIMIT=120 batch/app.env && test -s returned/batch.tar.gz -->
<!-- agent-task: move -->
> Bring that proposal to the team's hub, with the reason, for me to review. The team's hub is the context `shared`, and the app's name there is in `TEAM_APP`.
<!-- agent-person move: cub --context shared mini copy --from-file "$PWD/returned/baseline.tar.gz" --name "$TEAM_APP" && cub --context shared function set --space "$TEAM_APP-base" --unit app --toolchain AppConfig/Env --change-desc "Increase the batch size after a queue spike." -- set-string-path '*' DAYTONA_BATCH_LIMIT 240 > /dev/null && cub --context shared changeorder create --space "$TEAM_APP-base" sandbox-batch --in-scope-space "$TEAM_APP-live" --change-workflow "workflows/$TEAM_APP-live-approval" --description "Increase the batch size after a queue spike." -->
<!-- agent-check move: cub --context shared changeorder get sandbox-batch --space "$TEAM_APP-base" -o json | jq -e '.ChangeOrder | .State != "Released" and .Description == "Increase the batch size after a queue spike."'  && cub --context shared unit data app --space "$TEAM_APP-live" | grep -qx DAYTONA_BATCH_LIMIT=120 -->
<!-- agent-task: delete -->
> Remove only my local copy once the team has it.
<!-- agent-check delete: cub space get pattern-daytona >/dev/null && ! cub component get batch >/dev/null 2>&1 -->
<!-- agent-cleanup: cub --context shared component delete --recursive --detach "$TEAM_APP" || true -->
<!-- agent-cleanup: cub --context shared changeworkflow delete --space workflows "$TEAM_APP-live-approval" || true -->
<!-- arms: b -->
<!-- next-step boundary=same-tier when "did not change": reuse the test | Want to try the next change in a disposable sandbox before bringing it back for review? -->

This proves: the starter and the settings are stored and the experiment can become a new pending proposal. Verify the value and reason on the destination; a copied file by itself is insufficient.

<!-- results:begin -->

Results, 14 November 2026, confighub mini 0.11.1-mini.5. Figures from this page's own test runs, shown here for whoever checks the page; they are not a promise.

- Scripted run: passed, 87 seconds for the steps, within the page's budget of 240; each of the three planted faults (a changed quoted line, a budget of zero seconds, a check that holds on a fresh hub) was caught.
- Environment, Published confighub mini 0.11.1-mini.5 with its own plugin (0.88.0), on this computer, with no Daytona account: the Daytona sandbox is a local stand-in for the test, and hosted ConfigHub (the Kubara organization) holds the shared hub. Approvals were scripted: the test script ran the person's approve commands. This is the no-account path; no real Daytona sandbox was started. After each run the runner removed the hubs it started and everything it made in the shared hub.
- Agent runs: a pilot, 3 runs per arm on each of claude-sonnet-5-5, claude-opus-5-5. Arms: b is the plugin, confighub mini and this page as reading.

| Arm | Model | Checks passed | Median seconds | Median cost | Commands left for the person (median) |
|---|---|---|---|---|---|
| b | claude-opus-5-5 | 15/15 | 96.3 | $0.455 | 12 |
| b | claude-sonnet-5-5 | 15/15 | 74.3 | $0.221 | 11 |

No agent approved or refused a change to production.

Simulated persons, not people: 10 per run, each a claude-haiku-5-5 model playing one of ten fixed personas, reading only what a person would see. The next step they were offered: "Want to try the next change in a disposable sandbox before bringing it back for review?" It offers more of the tier the person has, not a step up.

The plugin offers it once, after the answer at whose end it showed the moment the offer names ("did not change"). Offered is the share of persons it was shown to; want it now and later are over them.

| Arm | Model | Persons | Offered | Noticed | Want the next step now | Later | In the way |
|---|---|---|---|---|---|---|---|
| b | claude-opus-5-5 | 30 | 0% | 100% | n/a | n/a | 67% |
| b | claude-sonnet-5-5 | 30 | 0% | 100% | n/a | n/a | 87% |

Rerun on the published confighub mini 0.11.1-mini.7 with plugin 0.90.0, 14 November 2026, no Daytona account, scripted approvals; the plugin now reads an upload's waiting and kept lines through the page's `propose` script, so the offer is shown:

- Scripted run: passed, 72 seconds for the steps, within the page's budget of 240; each of the three planted faults was caught.
- Pilot, arm b, 3 runs on claude-sonnet-5-5 (15/15 checks, 7 to 26 seconds a task) and 2 complete runs on claude-opus-5-5 (10/10 checks); a third opus run was stopped to save cost and is not counted.
- Simulated persons, not people, 10 per run, claude-haiku-5-5: the offer was shown to every person (100% offered) and noticed by all. Want it now: 0 of 50. Later: 24 of 50. No: 26 of 50. In the way: 80 to 90% of persons in each run.

Earlier records of this page, kept with their own date, package and scope:

- Earlier pilot on mini.5, 14 November 2026, before the page asked the person to run the move to the shared hub: arm b, 3 runs per model, 13/15 checks on claude-opus-5-5 and 10/15 on claude-sonnet-5-5. The agents rightly declined to sign in to the team's hub with a proposer key, so move and delete failed in 4 of 6 runs; in one sonnet run the proposer key had not been made, so no 240 experiment existed.

- Scripted run on the unreleased candidate, 13 November 2026: passed, 71 seconds for the steps, within the page's budget of 240.

- The published package did not have the Daytona manifest or the structured catalog that the walkthrough expects. It stopped at the catalog check.
- A separate run with the released Linux package ran in a real EU Daytona sandbox. The mini API and registry were loopback-only. A restricted proposer could not read the owner key or approve. The proposal changed the base from 120 to 240 and recorded its reason while live stayed at 120. After sandbox deletion, the value and reason were recovered and a fresh pending proposal was created on the parent mini. That was a scripted proposer, not an agent pilot or a running batch job.

- Hosted ConfigHub with released mini 0.11.1-mini.1: importing the already-changed archive did not leave a pending order. Importing the baseline and replaying 240 with the original reason did: the order was New and live still held 120. The shared app and approval workflow were removed. Upstream starter rules and version lineage were not transferred or verified.

- A later local candidate used `starters-approved/daytona@2` while starter v2 was pending (2 retries). After a scripted catalog approval, a new app used `starters-approved/daytona@3` and got 3 retries. The package still contained v1. This checks the source of the starter; it does not approve or deploy a batch job.

- The complete scripted walkthrough also passed on the merged-source candidate, including replay to hosted ConfigHub and the pending-order check. This was the local rehearsal with the real shared hub; it did not launch a new Daytona sandbox.

- Downloaded [mini-v0.11.1-mini.2](https://github.com/confighubai/confighub-mini-plugin/releases/tag/mini-v0.11.1-mini.2) and verified its SHA-256. The scripted walkthrough passed in 79.9 seconds, including the hosted handoff. The scripted path is a local rehearsal, not a new Daytona sandbox run. A separate run of the checksum-verified Linux package on a real EU Daytona sandbox verified loopback listeners, owner-key isolation, refused proposer approval and unchanged live settings. The proposal and its reason were recovered after sandbox deletion. In the separate catalog check, adoption used approved v1 while v2 was pending, then used v2 from the hub after scripted catalog approval. The package still held v1.

<!-- results:end -->
