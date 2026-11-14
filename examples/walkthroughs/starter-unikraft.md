<!-- walkthrough
id: starter-unikraft
starts_with: mini
starter: unikraft
needs: [confighub mini package with the Unikraft starter, Unikraft CLI, disposable Cloud service, BuildKit, jq, curl]
budget_seconds: 600
-->
# Roll out an incident banner on Unikraft Cloud

An incident starts and you need a banner change without rebuilding the image. An owner approves the change before the delivery add-on rolls the service. The same public endpoint reports which setting and ConfigHub revision the service is using.

## Human

Use an unpacked mini package containing the Unikraft starter. Use a new test hub and a disposable single-instance service in an organization where you can also delete the resources. The packaged example at `examples/unikraft/README.md` gives the provider setup and scoped reader commands.

### Steps

1. Build the example banner image, pin its digest and create the HTTPS service. Start the baseline instance with a blue banner. Save the service name, metro, pinned image and endpoint in `app/.confighub-unikraft.json` as shown in the packaged example.
2. Import the running settings, seed and review the structured starter catalog, then connect your test app. A catalog review publishes the starter for later adoptions; a separate app approval authorizes delivery.
   <!-- run: deploy -->
   ```sh
   export MINI=/absolute/path/to/unpacked-confighub-mini
   export CUB_MINI_STARTERS=on
   "$MINI/starters/addons/unikraft/run" --dir app import
   cub mini adopt app --name banner-catalog
   cub unit data unikraft --space starters-base
   cub variant approve starters-approved --all --note "Review packaged starter definitions"
   cub mini adopt app --name banner
   cub mini receipts banner --setup
   ```
3. Give the delivery process a separate reader configuration as shown in the example. Try applying the pending connect order. The add-on should refuse it and HTTPS should still report blue. Approve the connect order from your own account. Apply its exact revision and compare the receipt with the endpoint.
4. Propose green with the incident reason, keep reading blue while the order waits, then approve and apply the change. The same endpoint should serve green at the revision in the receipt using the same image digest. Restore blue in the file and propose the rollback. Repeat the approval and check blue arrives at a new revision.
5. To move the app, copy its settings to a disposable destination app. Verify the destination approval rule with a pending order and an unchanged service. Use a destination release and reader before claiming shared-hub delivery.
6. Delete the test instance, service and image. Delete the disposable destination app and workflow, and stop the local mini.

## Agent

Keep the provider sign-in with the person or delivery service. Offer the exact order for the owner to review. Observe the endpoint before and after delivery and report the setting, revision and image digest. Do not approve production or borrow the owner's provider credentials. A contributor without a Unikraft account can run the pending-order Go test from the mini source repository.

## Testing

The no-account Go test uses a pending order and checks that the add-on never calls the provider. The live check separately verifies the real endpoint and the pinned image. Verify the current approved starter source and the live revision for each result.

<!-- agent-task: deploy -->
> Connect this test app to the approved Unikraft starter and show the current blue banner.
<!-- agent-check deploy: cub component get banner -o json | jq -e '.Component.Annotations["confighub-mini.starter-source"] | startswith("starters-approved/unikraft@")' -->
<!-- agent-task: update -->
> Propose green and show that the HTTPS endpoint stays blue before approval.
<!-- agent-task: undo -->
> Propose restoring the original banner and verify the released rollback after I approve it.
<!-- agent-task: move -->
> Show how to move this app and check approval at the destination.
<!-- agent-task: delete -->
> Remove this test service and its app after recording the result.
<!-- next-step: try an incident banner | Want to see what the endpoint serves while the next change waits for approval? -->
<!-- arms: b -->

This proves: the candidate selected the approved hub starter and refused an unapproved order while the real Cloud app kept serving blue. Live delivery of a newly approved revision, its rollback and delivery from a shared hub still require their own runs with the packaged adapter.


<!-- results:begin -->

Candidate result, 14 November 2026. A real disposable Frankfurt Cloud service reported blue at its baseline while the candidate refused the unapproved connect order. Adoption used `starters-approved/unikraft@2` after a scripted catalog review. The instance, service and image were removed. An earlier native owner approval test rolled out green and then restored blue with a different delivery script. The packaged live rollout, rollback, shared-hub delivery and agent pilots were not run.

<!-- results:end -->
