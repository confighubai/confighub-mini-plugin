<!-- walkthrough
id: starter-unikraft
starts_with: mini
starter: unikraft
needs: [confighub mini package with the Unikraft starter, Unikraft CLI, disposable Cloud service, BuildKit, jq, curl]
budget_seconds: 600
-->
# Preview an incident banner on Unikraft Cloud

An incident starts and you need a banner change without rebuilding the image. Connect a disposable service and see the endpoint keep serving its current banner while the first delivery awaits approval.

## Human

Use an unpacked mini package containing the Unikraft starter. Use a new test hub and a disposable single-instance service in an organization where you can also delete the resources. The packaged example at `examples/unikraft/README.md` gives the provider setup and scoped reader commands.

### Steps

1. Build the example banner image, pin its digest and create the HTTPS service. Start the baseline instance with a blue banner. Save the service name, metro, pinned image and endpoint in `app/.confighub-unikraft.json` as shown in the packaged example.
2. Import the running settings, seed and review the structured starter catalog, then connect your test app. A catalog review publishes the starter for later adoptions; a separate app approval authorizes delivery.
   <!-- run: deploy -->
   ```sh
   export MINI=/absolute/path/to/unpacked-confighub-mini
   export CUB_MINI_STARTERS=on
   "$MINI/starters/addons/unikraft/run" --live --dir app import
   cub mini adopt app --name banner-catalog --live
   cub unit data unikraft --space starters-base
   cub variant approve starters-approved --all --note "Review packaged starter definitions"
   cub mini adopt app --name banner --live
   cub mini receipts banner --setup
   ```
3. Set up the scoped reader in the packaged example. Try applying the pending connect order and confirm the add-on refuses it.
4. Read the HTTPS endpoint again. It should still return blue with revision `baseline`. Keep that response with the add-on's refusal.
5. Remove the disposable test instance, service and image. Delete the test apps or stop the disposable mini.

## Agent

Keep the provider sign-in with the person or delivery service. Read the endpoint, check the pending-order refusal, and report the banner, revision and pinned image. Leave the order pending for this test.

## Testing

Without a provider account, run the local stand-in test from the unpacked package:

```sh
"$MINI/examples/starter-check/check" "$MINI/starters/unikraft.yaml" --package "$MINI" --check-addon
```

It checks import, apply, compare and planted faults. The real-service test checks the approved catalog source, pending-order refusal and HTTPS baseline.

<!-- agent-task: deploy -->
> Connect this test app to the approved Unikraft starter and show the current blue banner.
<!-- agent-check deploy: cub component get banner -o json | jq -e '.Component.Annotations["confighub-mini.starter-source"] | startswith("starters-approved/unikraft@")' -->
<!-- agent-task: update -->
> Use the local stand-in contract to test delivery of a pinned revision. For the real Cloud app, show that the first delivery is still blocked while approval is pending.
<!-- agent-task: undo -->
> On the stand-in, confirm that reapplying the same revision leaves the settings unchanged. Report that undo on the real Cloud service still awaits a live test.
<!-- agent-task: move -->
> Identify the destination's starter version, approval order and reader before attempting any shared-hub delivery. Report this as a walkthrough of the prerequisites.
<!-- agent-task: delete -->
> Remove this test service and its app after recording the result.
<!-- next-step boundary=same-tier: try an incident banner | Want to see what the endpoint serves while the next change waits for approval? -->
<!-- arms: b -->

This proves: the candidate selected the approved hub starter and refused an unapproved order while the real Cloud app kept serving blue. Live delivery of a newly approved revision, its rollback and delivery from a shared hub still require their own runs with the packaged adapter.


<!-- results:begin -->

Candidate result, 14 November 2026. A real disposable Frankfurt Cloud service reported blue at its baseline while the candidate refused the unapproved connect order. Adoption used `starters-approved/unikraft@2` after a scripted catalog review. The instance, service and image were removed. An earlier native owner approval test rolled out green and then restored blue with a different delivery script. The packaged live rollout, rollback, shared-hub delivery and agent pilots were not run.

<!-- results:end -->
