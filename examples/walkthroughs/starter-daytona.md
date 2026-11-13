<!-- walkthrough
id: starter-daytona
starts_with: mini
starter: daytona
needs: [confighub mini package, hosted ConfigHub for the shared step]
budget_seconds: 240
-->
# Bring a sandbox experiment back for review

Try a larger batch in a disposable environment, then take its settings and reason to your team without letting the experiment change production.

## Human

Use an unpacked [mini package](../../docs/install-mini.md) that includes the Daytona starter. The commands below run a local rehearsal first. Use an empty working directory and keep its keys and evidence private. The shared step needs a disposable app name in an organization where you can create and remove test resources.

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
   cub unit get daytona --space starters -o jq=.Unit.ToolchainType
   cub variant approve starters --change-order starters/package-starters-v1 --note "Review the packaged starters"
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

Use only the supplied proposer context. Try the new batch size and give the owner the proposed value, reason, and approval command. Ask the owner to install or approve a starter, create or delete a cloud sandbox, and copy to the shared hub if you lack access. Never approve a production change. If a sandbox was deleted, use the downloaded files; do not report the original approval history as transferred.

## Testing

The checks read the structured starter, the staging and live Units, and the shared hub's new pending order. The local scripted path tests configuration and the approval boundary. A separate real Daytona run is needed to test loopback and separate OS users. Neither path proves that a batch job ran.

<!-- agent-task: deploy -->
> Set up my batch job so I can try changes while keeping production at 120.
<!-- agent-check deploy: cub unit get daytona --space starters -o jq=.Unit.ToolchainType | grep -qx AppConfig/YAML && cub unit data app --space batch-live | grep -qx DAYTONA_BATCH_LIMIT=120 -->
<!-- agent-task: update -->
> Try 240 because the queue spiked, and leave production at 120.
<!-- agent-check update: cub unit data app --space batch-staging | grep -qx DAYTONA_BATCH_LIMIT=240 && cub unit data app --space batch-live | grep -qx DAYTONA_BATCH_LIMIT=120 && grep -q 'after a queue spike' returned/proposal.txt -->
<!-- agent-task: undo -->
> Put my local file back and keep the experiment for later.
<!-- agent-check undo: grep -qx DAYTONA_BATCH_LIMIT=120 batch/app.env && test -s returned/batch.tar.gz -->
<!-- agent-task: move -->
> Bring that proposal to the team's hub, with the reason, for me to review.
<!-- agent-check move: cub --context shared changeorder get sandbox-batch --space "$TEAM_APP-base" -o json | jq -e '.ChangeOrder | .State != "Released" and .Description == "Increase the batch size after a queue spike."'  && cub --context shared unit data app --space "$TEAM_APP-live" | grep -qx DAYTONA_BATCH_LIMIT=120 -->
<!-- agent-task: delete -->
> Remove only my local copy once the team has it.
<!-- agent-check delete: cub space get pattern-daytona >/dev/null && ! cub component get batch >/dev/null 2>&1 -->
<!-- agent-cleanup: cub --context shared component delete --recursive --detach "$TEAM_APP" || true -->
<!-- agent-cleanup: cub --context shared changeworkflow delete --space workflows "$TEAM_APP-live-approval" || true -->
<!-- arms: b -->
<!-- next-step: reuse the test | Want to try the next change in a disposable sandbox before bringing it back for review? -->

This proves: the starter and the settings are stored and the experiment can become a new pending proposal. Verify the value and reason on the destination; a copied file by itself is insufficient.

<!-- results:begin -->

Results, 13 November 2026, confighub mini 0.11.1-mini.1. Figures from this page's own test runs, shown here for whoever checks the page; they are not a promise.

- Scripted run: FAILED, 39 seconds for the steps, within the page's budget of 240.

- The published package did not have the Daytona manifest or the structured catalog that the walkthrough expects. It stopped at the catalog check.
- A separate run with the released Linux package ran in a real EU Daytona sandbox. The mini API and registry were loopback-only. A restricted proposer could not read the owner key or approve. The proposal changed the base from 120 to 240 and recorded its reason while live stayed at 120. After sandbox deletion, the value and reason were recovered and a fresh pending proposal was created on the parent mini. That was a scripted proposer, not an agent pilot or a running batch job.

- Hosted ConfigHub with released mini 0.11.1-mini.1: importing the already-changed archive did not leave a pending order. Importing the baseline and replaying 240 with the original reason did: the order was New and live still held 120. The shared app and approval workflow were removed. Upstream starter rules and version lineage were not transferred or verified.

<!-- results:end -->
