<!-- walkthrough
id: starter-temporal-worker
starts_with: mini
starter: temporal-worker
needs: [confighub mini package with the Temporal worker starter, Go, Temporal CLI, Python 3]
budget_seconds: 360
-->
# Change what a Temporal worker retries

A dependency is overloaded. Try one Activity attempt in staging while production continues retrying. When you approve the change, new workflow runs use the released policy. If callers need the old behavior, approve a rollback and watch the Temporal worker succeed again.

## Human

Use an unpacked mini package containing the Temporal worker starter, plus Go, Python 3 and the [Temporal CLI](https://docs.temporal.io/cli). The comparison uses disposable hubs on loopback and a real Temporal development service.

### Steps

1. From an empty directory, run the package example. It conducts steps 2–6 in disposable hubs, with scripted approvals. Use the commands in the example's `examples/temporal/starter/README.md` when connecting your own app. Approve production from your account.
   <!-- run: setup -->
   ```sh
   export MINI=/absolute/path/to/unpacked-confighub-mini
   test -x "$MINI/examples/temporal/starter/check-worker"
   ```
   <!-- run: deploy -->
   ```sh
   "$MINI/examples/temporal/starter/check-worker" --package "$MINI" --out "$PWD/temporal-results"
   ```
2. Switch starters on with `CUB_MINI_STARTERS=on`. Adopt the checkout containing the worker executable and `app.env`. Review the structured catalog in the hub. Verify `cub mini receipts worker --setup` identifies the approved catalog revision. A newer pending starter should be ignored.
3. Use the scoped reader to write the approved policy. Start the Temporal worker from the example. Run the probe. The sample Activity fails twice and succeeds on its third attempt.
4. Propose one attempt with `cub mini set worker ACTIVITY_MAX_ATTEMPTS=1 --variant base --change-desc "Reduce retries during the incident"` and create a live change order. The old revision should still succeed on its third attempt. Then approve the order. Use the add-on with the exact order and live revision, and run a new probe. It should now fail after one attempt.
5. Propose restoring the retry limit. The probe should still fail once while rollback waits. After approving and applying the rollback, a new probe should again succeed on attempt three, reporting the new revision. The example stops the test worker, Temporal development service and test hubs.
6. To use a shared hub, copy the app to a disposable destination and check its approval workflow. Use the destination order, revision and reader to deliver; verify them with another probe. The local example does not run this step. Remove the destination app and workflow when finished.

## Agent

Ask which Activity needs different retries and what outcome a probe should see. Show staging, the pending order and the running policy. Give the owner the exact approval command. In a new workflow run, report the number of attempts and the revision the worker actually loaded. Use the disposable example for checks; only the owner approves real production.

## Testing

The comparison uses a real Temporal service and the same worker for two arms. It verifies the approved starter catalog, the pending order boundary, a planted local settings change with the old receipt, the applied revision and hash, and recovery after rollback. Both arms must reach the same behavior. The starter wins only if its separate catalog and per-app setup costs are reported accurately.

<!-- agent-task: deploy -->
> Connect the disposable Temporal worker and show the approved catalog and initial behavior.
<!-- agent-check deploy: jq -e '.arms[0].starter_publication.app_source and .arms[0].before_change.succeeded' temporal-results/result.json -->
<!-- agent-task: update -->
> Try one attempt, and show what happens before and after the owner's approval.
<!-- agent-check update: jq -e '.arms[0] | .before_approval.attempts==3 and .after_approval.attempts==1 and (.after_approval.succeeded|not)' temporal-results/result.json -->
<!-- agent-task: undo -->
> Restore the policy and show the Temporal worker uses the new rollback revision.
<!-- agent-check undo: jq -e '.arms[0] | .after_rollback.succeeded and .after_rollback.attempts==3 and .after_rollback.config.revision>.after_approval.config.revision' temporal-results/result.json -->
<!-- agent-task: move -->
> Explain which orders and reader I need on the destination hub.
<!-- agent-task: delete -->
> Stop and remove the example's test resources after checking the result.
<!-- next-step: try the runtime policy | Want to compare the retries your Temporal worker uses before and after approval? -->
<!-- arms: b -->

This proves: the structured starter is stored and selected, and a real Temporal worker runs the exact approved policy and its rollback on a local service. A shared-hub delivery needs its own observation.


<!-- results:begin -->

Candidate result, 14 November 2026, macOS arm64. The real local Temporal worker comparison passed 17/17 for the starter and 11/11 for manual mini. Both used scripted fixture approvals. The worker kept revision 3 while the change waited, loaded approved revision 4 and failed after one attempt, then loaded approved rollback revision 5 and succeeded after three attempts. The starter used one per-app connection command in 11.6 seconds; manual mini used two in 16.2 seconds with a new pattern. The starter also needed two catalog setup commands once per fresh hub. The run did not exercise a shared hub or a public package. No agent pilot was run.

<!-- results:end -->
