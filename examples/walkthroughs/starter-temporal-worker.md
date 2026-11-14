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
4. Propose one attempt with `cub mini set worker ACTIVITY_MAX_ATTEMPTS=1 --variant base --change-desc "Reduce retries during the incident"` and create a live change order. The old revision should still succeed on its third attempt. Then approve the order. Use the add-on with `--live`, the exact order and live revision, and run a new probe. It should now fail after one attempt.
5. Propose restoring the retry limit. The probe should still fail once while rollback waits. After approving and applying the rollback, a new probe should again succeed on attempt three, reporting the new revision. The example stops the test worker, Temporal development service and test hubs.
6. To use a shared hub, copy the app to a disposable destination and check its approval workflow. Use the destination order, revision and reader to deliver; verify them with another probe. The local example does not run this step. Remove the destination app and workflow when finished.

## Agent

Ask which Activity needs different retries and what outcome a probe should see. Show staging, the pending order and the running policy. Give the owner the exact approval command. In a new workflow run, report the number of attempts and the revision the worker actually loaded. Use the disposable example for checks; only the owner approves real production.

## Testing

The comparison uses a real Temporal service and the same worker for two arms. The starter writes its policy and receipt together in `temporal-activity-policy.json`. The manual arm uses the full settings file and ordinary mini pull receipt. It verifies the approved starter catalog, the pending order boundary, a planted local settings change with the old receipt, the applied revision and hash, and recovery after rollback. Both arms must reach the same behavior. The starter wins only if its separate catalog and per-app setup costs are reported accurately.

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
<!-- next-step boundary=same-tier: try the runtime policy | Want to compare the retries your Temporal worker uses before and after approval? -->
<!-- arms: b -->

This proves: the structured starter is stored and selected, and a real Temporal worker runs the exact approved policy and its rollback on a local service. A shared-hub delivery needs its own observation.


In the local macOS arm64 mini.908 comparison, the starter passed 19/19 checks and manual mini passed 11/11 using scripted approvals. Both used revisions 3, 4 and 5 and showed the same retry behavior. The starter kept the original runtime environment and rejected a changed policy with the old digest. After catalog review it connected in one command (9.2 s). Manual mini took two (12.3 s) to create and connect a new pattern. Shared-hub delivery and agent pilots still need their own runs.

<!-- results:begin -->

Results, 14 November 2026, confighub mini 0.11.1-mini.7. Figures from this page's own test runs, shown here for whoever checks the page; they are not a promise.

- Scripted run: passed, 158 seconds for the steps, within the page's budget of 360. The real local Temporal worker passed 19 of 19 checks with the starter and 11 of 11 with manual mini. Both arms used scripted approvals.

<!-- results:end -->
