<!-- walkthrough
id: starter-unikraft
starts_with: mini
starter: unikraft
needs: [confighub mini package with the Unikraft starter, Unikraft CLI, disposable Cloud service, BuildKit, jq, curl]
budget_seconds: 600
-->
# Roll out and undo an incident banner on Unikraft Cloud

An incident starts and you need a banner change without rebuilding the image. Connect a disposable service, approve a green incident banner, and restore blue when the incident ends. The same image serves each change. The HTTPS response includes the ConfigHub revision that the service loaded.

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
3. Set up the scoped reader in the packaged example. Try applying the pending `banner-live/connect` order. The adapter should refuse it and the endpoint should still return blue at `baseline`. Approve `banner-live/connect` from your account. Apply the live revision and check the endpoint returns blue and that revision.
4. Propose green with `cub mini set banner UNIKRAFT_BANNER=green --variant live --change-desc "Show the incident banner"`. Use the order printed by that command. Give the reader `View` and `ViewChildren` on `banner-file-proposals` so the adapter can verify the approval. Before approving, try delivery and check the endpoint still serves blue. Approve the order, read the new live head, deliver it and verify green and that revision over HTTPS.
5. Restore blue with the same `cub mini set` command, this time setting `UNIKRAFT_BANNER=blue` and giving the reason for the rollback. Check that green stays live while the rollback waits. After approving the new order, deliver its exact live revision and verify blue over HTTPS.
6. To move to a shared hub, export the app with `cub mini copy --to-file banner.tar.gz banner`. Sign in to the shared hub and import with `cub --context shared mini copy --from-file banner.tar.gz --name "$TEAM_APP"`. Use a unique name for this test. Verify that the destination requires a change workflow. Run `cub --context shared mini require-approval "$TEAM_APP" --variant live --file-proposals` to enable file proposals there. Make a separate destination reader with `cub --context shared mini pull-key "$TEAM_APP-reader" "$TEAM_APP" --variant live` and grant it read access to the destination's file proposals Space. Propose green in the destination's live variant with `cub --context shared mini set`. Check that the service still returns blue, then approve in the shared hub, apply the released revision using the destination reader and check green over HTTPS.
7. Remove the Unikraft instance, service and image. Delete the disposable shared app, its proposal Space, workflows, invocation and reader account. Stop and uninstall the test mini.

Grant the reader access with `cub space update "$PROPOSALS" --permission "View:serviceaccount:$READER_NAME" --permission "ViewChildren:serviceaccount:$READER_NAME"`, where `PROPOSALS` is the app’s file proposals Space and `READER_NAME` is its delivery service account. For the shared hub, add `--context shared` to the command. For each delivery, read the current live head with `cub unit get app --space "$LIVE" -o jq=.Unit.HeadRevisionNum` as the owner and use the separate reader to apply the exact order and revision. Set `LIVE`, `ORDER`, `REV`, `READER_CONFIG` and `READER_CONTEXT` to the app and hub you are delivering from:

```sh
CUB_CONFIG="$READER_CONFIG" CUB_CONTEXT="$READER_CONTEXT" \
  "$MINI/starters/addons/unikraft/run" --live --dir app \
  --space "$LIVE" --order "$ORDER" --revision "$REV" apply
curl -fsS "$(jq -r .endpoint app/.confighub-unikraft.json)"
```

## Agent

Keep the provider sign-in with the person or delivery service. Give the owner the order and wait for their approval. Before and after delivery, read the endpoint and report the banner, revision and pinned image.

## Testing

Without a provider account, run the local stand-in test from the unpacked package:

```sh
"$MINI/examples/starter-check/check" "$MINI/starters/unikraft.yaml" --package "$MINI" --check-addon
```

It checks import, apply, compare and planted faults. The live run checks the approved catalog source, delivery refusal before each approval, and HTTPS readback after each delivery.

<!-- agent-task: deploy -->
> Connect this test app to the approved Unikraft starter and show the current blue banner.
<!-- agent-check deploy: cub component get banner -o json | jq -e '.Component.Annotations["confighub-mini.starter-source"] | startswith("starters-approved/unikraft@")' -->
<!-- agent-task: update -->
> Propose a green incident banner. Check that blue is still live, then deliver after I approve and show the revision the endpoint serves.
<!-- agent-task: undo -->
> Propose restoring blue. Check that green is still live. After I approve, deliver the rollback and verify the new revision.
<!-- agent-task: move -->
> Copy the app to a shared hub. Show that production waits for my approval there, then use the destination reader to deliver the approved revision.
<!-- agent-task: delete -->
> Remove this test service and its app after recording the result.
<!-- next-step boundary=same-tier: try an incident banner | Want to see what the endpoint serves while the next change waits for approval? -->
<!-- arms: b -->

This proves: owner approval controls delivery of a specific revision to Unikraft Cloud. The HTTPS response verifies the live setting and revision after update and rollback. The shared-hub test also checks the destination's approval and reader.

<!-- results:begin -->

Published confighub mini 0.11.1-mini.7 (macOS arm64), 14 November 2026. The downloaded archive matched the published checksum. The stand-in passed 38 of 38 checks, including all eight planted faults.

The live run used a disposable Frankfurt Unikraft Cloud service. The app selected starter version 1 from the hub's approved catalog at revision 2. The real owner approved production through ConfigHub. The delivery adapter refused each pending proposal, and the endpoint continued to serve the previous banner and revision.

| Step | Observed over HTTPS |
| --- | --- |
| Before first approval | Blue at the provider baseline |
| First approved delivery | Blue at local revision 3 |
| Approved update | Green at local revision 5 |
| Approved rollback | Blue at local revision 6 |
| Approved shared-hub delivery | Green at hosted revision 5 |

An initial update attempt used a separate base order. That order released local revision 4 with the same blue value as revision 3. The retry used the order generated by `cub mini set --variant live`, which showed blue → green before the owner approved it. On the shared hub, the copied app required approval. The destination reader refused the pending green order, and the endpoint still served blue at local revision 6. After the owner approved the hosted order, the destination reader delivered hosted revision 5. HTTPS returned green at that revision, and the adapter receipt matched the SHA-256 of the released settings. The service had one running instance on the original pinned image (`sha256:d7880421670ab27fb7e3a7bf8f32b2b86a5442259614b9bfd240cf505a798f47`). A separate compare reported unchanged. The run removed the Unikraft instance, service and image, the shared app and its approval resources, and the local test hub.

Two Claude Sonnet 5.5 pilots with the plugin ran a local rehearsal of the packaged stand-in contract. Both passed the result check (2 of 2). The pilots exercised the stand-in only. Ten simulated readers noticed the result. One reported friction, and the plugin showed no next-step offer.

<!-- results:end -->
