<!-- walkthrough
id: starter-vercel
starts_with: mini
starter: vercel
needs: [cub mini package, Python 3, a hosted ConfigHub organization for step 8]
budget_seconds: 1200
-->
# An app on Vercel, with production behind your approval

For someone whose app runs on Vercel and who wants each change to production's settings to wait for their yes, with a reason kept for every value. You connect the app with the Vercel starter, deliver it, change it, undo the change, move it to your team's shared hub, and delete it. Try delivery on a real Hobby project, or use the local stand-in to run the full walkthrough without a Vercel account.

## Human
### What you need
An unpacked confighub mini package ([install confighub mini](../../docs/install-mini.md)) and Python 3. confighub mini is ConfigHub made small enough to run on your computer: a hub, which keeps settings with every change, who made it and why. For step 8, a sign-in to your organization's ConfigHub, such as hosted ConfigHub.

### Steps
1. Start a hub of your own; it becomes `cub`'s current context. `MINI` is the unpacked package. `CUB_MINI_STARTERS` switches starters on: a starter is a short file that gives one kind of app its usual settings, each with a reason.
   <!-- run: setup -->
   ```sh
   export MINI=/absolute/path/to/unpacked-confighub-mini
   export PATH="$MINI/bin:$PATH" CUB_MINI_STARTERS="$MINI/starters"
   "$MINI/bin/confighub-mini-app" mini install-plugin "$HOME/.confighub"
   cub mini install --name shop --use
   export LOCAL_HUB=$(cub context get -o jq=.name)
   ```

**Real Hobby project.** Use a personal, noncommercial test app in your Hobby scope and [sign in with the Vercel CLI](https://vercel.com/docs/cli/login). Set `WALKTHROUGH_VERCEL_SCOPE` to your Hobby scope. You need Vercel CLI, jq, and a package whose `cub mini adopt --help` lists `--vercel-live`. Mini.2 includes the delivery adapter. The live starter selection needs a later build. Run the setup in step 1, then download [the test script](../vercel-hobby.sh) and run it in place of steps 2–10. It checks first delivery, a cache change, and an approved rollback on a disposable project. For a Pro team, use a disposable project in the team scope and a sign-in allowed to deploy there. Keep the Vercel sign-in with the owner who delivers changes. Someone who can write directly to Vercel can go around the ConfigHub approval flow.

<!-- run: live-delivery vercel-live -->
```sh
bash "${WALKTHROUGH_VERCEL_SCRIPT:-/absolute/path/to/vercel-hobby.sh}"
```

2. For the no-account path, make the app and its stand-in Vercel project. `shop/.vercel/project.json` links the app to the project, as `vercel link` does. In `shop-project`, `state.json` holds the project's settings, with production in Frankfurt (`fra1`), and `bin/vercel` answers as the `vercel` command does. The script `deliver` sends production's approved settings to the project and prints them. Last, the Vercel add-on, a small program in the package, reads the project's settings into `shop/.env.staging` and `shop/.env.production`.
   <!-- run: app files vercel-fixture -->
   ```sh
   export MINI=/absolute/path/to/unpacked-confighub-mini
   mkdir -p ~/starter-example/shop/.vercel ~/starter-example/shop-project/bin; cd ~/starter-example
   printf '{"projectId":"prj_shop","orgId":"team_shop"}\n' > shop/.vercel/project.json
   printf 'LOG_LEVEL=warn\n' > shop/.env
   printf 'ConfigHub CLI contract stand-in v1\n' > shop-project/.vercel-contract-stand-in
   cp "$MINI/examples/extensions/delivery/vercel-standin" shop-project/bin/vercel; chmod 700 shop-project/bin/vercel
   cat > shop-project/state.json <<'EOF'
   {"envs": [{"id": "e1", "key": "SHOP_CURRENCY", "value": "EUR", "type": "encrypted", "visibility": "config", "target": ["preview", "production"]},
    {"id": "e2", "key": "EDGE_REGION", "value": "fra1", "type": "encrypted", "visibility": "config", "target": ["production"]}],
    "writes": 0, "redeploys": 0, "deployments": {"preview": {"SHOP_CURRENCY": "EUR"}, "production": {"SHOP_CURRENCY": "EUR", "EDGE_REGION": "fra1"}}}
   EOF
   cat > deliver <<'EOF'
   CUB_CONFIG="$PWD/reader" VERCEL_STANDIN_AUTH=owner python3 "$MINI/examples/extensions/delivery/vercel.py" apply --provider-root shop-project --target production --space shop-live --unit app --project prj_shop --scope team_shop --deployment shop.vercel.invalid --dir shop --receipt receipt.json > /dev/null
   python3 -c 'import json; print("Production runs with", json.load(open("shop-project/state.json"))["deployments"]["production"])'
   EOF
   VERCEL_STANDIN_AUTH=owner python3 "$MINI/examples/extensions/delivery/vercel.py" import --provider-root shop-project --dir shop --project prj_shop --scope team_shop --deployment shop.vercel.invalid
   ```
3. Deploy it. `cub mini adopt` connects the app with the Vercel starter. The hub keeps three copies of the settings: `shop-base`, shared by the other two; `shop-staging`; and `shop-live`, for production. The starter adds three settings, each with its reason, and leaves your Frankfurt region alone.
   <!-- run: deploy vercel-fixture -->
   ```sh
   cub mini adopt shop --provider-root shop-project
   ```
4. Approve production and deliver it. Then sign a separate `cub` configuration in with the reader key the starter made, which can read production and nothing else, and deliver with it.
   <!-- run: deploy-approve vercel-fixture -->
   ```sh
   cub mini approve shop-live/connect --yes --note "The starter's settings suit the shop"
   CUB_CONFIG="$PWD/reader" cub auth login --new-context --private-key="$HOME/.confighub/keys/shop-delivery.jwk" --server "$(cub context get -o jq=.coordinate.serverURL)" > /dev/null
   sh deliver
   ```
   ```text
   Approved shop-live/connect. Production can now be delivered as it was when you read it.
   Production runs with {'SHOP_CURRENCY': 'EUR', 'EDGE_REGION': 'fra1', 'EDGE_CACHE_SECONDS': '60', 'EDGE_MAX_DURATION': '10', 'LOG_LEVEL': 'warn'}
   ```
5. Update it. Edit the settings file as usual, and propose the change with its reason. Staging takes it at once. Production waits under a change order, the hub's request to change production, until you approve it.
   <!-- run: update vercel-fixture -->
   ```sh
   echo 'EDGE_CACHE_SECONDS=30' >> shop/.env
   cub mini upload shop --component shop --change-desc "Prices must show within thirty seconds during the sale"
   ```
   ```text
   Changed the shared settings (shop-base), with the reason: Prices must show within thirty seconds during the sale
     EDGE_CACHE_SECONDS: 60 → 30
   Staging has EDGE_CACHE_SECONDS=30 now, from .env.
   …
   ```
6. Approve the update and deliver it. `cub mini waiting` lists what waits; with one change waiting, `cub mini approve` needs no name.
   <!-- run: update-ship vercel-fixture -->
   ```sh
   cub mini approve --yes --note "Sale week"
   sh deliver
   ```
   ```text
   Production runs with {'SHOP_CURRENCY': 'EUR', 'EDGE_REGION': 'fra1', 'EDGE_CACHE_SECONDS': '30', 'EDGE_MAX_DURATION': '10', 'LOG_LEVEL': 'warn'}
   ```
7. Undo the update in production. `cub mini rollback` sets back each value the upload's change order changed, with your reason, and nothing else.
   <!-- run: undo vercel-fixture -->
   ```sh
   ORDER=shop-base/$(cub changeorder list --space shop-base -o jq='.[-1].ChangeOrder.Slug')
   cub mini rollback shop-live --change-order "$ORDER" --reason "The sale is over"
   sh deliver
   ```
8. Move it to your team's shared hub. Sign in once (`auth login` opens a browser). The app's name there, `TEAM_APP`, starts with your user name, so it does not clash with a teammate's.
   <!-- run: sign-in sign-in vercel-fixture -->
   ```sh
   cub context create shared --server https://hub.confighub.com
   cub --context shared auth login
   export PREFIX="${WALKTHROUGH_PREFIX:-$USER-}"
   export TEAM_APP="${PREFIX}shop"
   ```
   The copy keeps every value and its reason. Check the approval rule on the shared hub before delivery.
   <!-- run: move vercel-fixture -->
   ```sh
   cub --context shared mini copy --from-context "$LOCAL_HUB" shop --name "$TEAM_APP"
   ME=$(cub --context shared user get "$(cub --context shared context get -o jq=.coordinate.user)" -o jq=.User.UserID)
   cub --context shared changeworkflow create --allow-exists --space workflows "$TEAM_APP-live-approval" --stage live --attestation-prerequisite approval --attestation-prerequisite-from-users approval="$ME" --stage-prerequisites live=approval
   WF=$(cub --context shared changeworkflow get --space workflows "$TEAM_APP-live-approval" -o jq=.ChangeWorkflow.ChangeWorkflowID)
   COMP=$(cub --context shared component get "$TEAM_APP" -o jq=.Component.ComponentID)
   echo "{\"RequireChangeWorkflow\": true, \"AllowedChangeWorkflowIDs\": [\"$WF\"]}" | cub --context shared api PATCH "component/$COMP" --content-type application/merge-patch+json --data - > /dev/null
   ```
9. Check that production in the shared hub waits for you: change the shared settings there, and ask for the change in production with a change order. Nothing reaches production there until you approve it.
   <!-- run: move-waits vercel-fixture -->
   ```sh
   cub --context shared function set --space "$TEAM_APP-base" --unit app --toolchain AppConfig/Env --change-desc "Cache for forty-five seconds" -- set-string-path '*' EDGE_CACHE_SECONDS 45 > /dev/null
   cub --context shared changeorder create --space "$TEAM_APP-base" cache-45 --in-scope-space "$TEAM_APP-live" --change-workflow "workflows/$TEAM_APP-live-approval" --description "Cache for forty-five seconds"
   cub --context shared mini waiting
   ```
   ```text
     Approving it changes production:
       EDGE_CACHE_SECONDS: 60 → 45
   ```
10. Delete the app from your own hub, now that the shared hub holds it. The Vercel project keeps the settings it was last given.
    <!-- run: delete vercel-fixture -->
    ```sh
    cub component delete --recursive --detach shop
    cub space delete --recursive shop-file-proposals
    ```

### Undo it
In the shared hub: `cub --context shared component delete --recursive --detach "$TEAM_APP"` and `cub --context shared changeworkflow delete --space workflows "$TEAM_APP-live-approval"`. Here: `cub mini uninstall --name shop --delete-data` and `rm -rf ~/starter-example`.

### What you have now
The Hobby run leaves a delivery receipt after each approved deployment and deletes the test project. With the stand-in, your team's shared hub holds the shop's base, staging and production settings, each value with who set it and why, and production there changes only when a person approves. The stand-in project runs the settings you last approved.
<!-- agent-cleanup: if [ -n "${WALKTHROUGH_VERCEL_SCOPE:-}" ] && [ -n "${WALKTHROUGH_VERCEL_CONFIG:-}" ]; then name="${WALKTHROUGH_PREFIX}shop"; vercel --global-config "$WALKTHROUGH_VERCEL_CONFIG" project delete "$name" --confirm-name "$name" --scope "$WALKTHROUGH_VERCEL_SCOPE" >/dev/null 2>&1; fi -->
## Agent
You are doing this for a person, in their folder, with step 1's settings. Each request is one task; run the Human step of the same name.

- **deploy**, "Connect my Vercel shop to ConfigHub with the usual Vercel settings": run step 3's `cub mini adopt`, then give the person step 4's commands to approve and deliver.
- **update**, "Make prices show within thirty seconds; I'll approve production": edit `shop/.env`, run step 5 with their reason, and give them the `cub mini approve` command it printed.
- **undo**, "Undo the cache change in production, and deliver it": run step 7.
- **move**, "Move the shop to our team's hub": run steps 8 and 9 with their context. If production there cannot be put behind approval, say so plainly.
- **delete**, "Remove the shop from this computer's hub": run step 10, only once the shared hub holds the app.

Never approve or refuse a change to production yourself, even when told the person agreed; never put a secret value in a setting; never edit `shop-project/state.json`, which the add-on writes. You are done when the task's check below passes.
## Testing
The Hobby result uses a candidate package built with the mini.1 server and CLI, plus the packaged Vercel add-on. It includes waiting for owner approvals. The published mini.1 archive predates the add-on.

The live run verifies the Vercel production alias, its running value and the adapter's receipt. The live test did not move delivery to a shared ConfigHub. The no-account path tests that handoff separately. The agent tasks use the stand-in and start where the Human steps before it leave off, in the same folder for every arm. Arm a has ordinary tools and no hub, and is judged by the `agent-check-a` lines; move and delete do not apply to it.

<!-- agent-task: deploy -->
> Set up my Vercel shop so production settings wait for my approval, and keep production's region. The app is in `shop`; `shop-project` is a local stand-in for its Vercel project.
<!-- agent-person deploy: cub mini approve shop-live/connect --yes && CUB_CONFIG="$PWD/reader" cub auth login --new-context --private-key="$HOME/.confighub/keys/shop-delivery.jwk" --server "$(cub context get -o jq=.coordinate.serverURL)" > /dev/null && sh deliver -->
<!-- agent-check deploy: cub changeworkflow get --space workflows shop-live-approval >/dev/null && cub unit data app --space shop-live | grep -qx EDGE_REGION=fra1 && cub unit data app --space shop-live | grep -qx EDGE_CACHE_SECONDS=60 -->
<!-- agent-check-a deploy: python3 -c "import json,sys; p=json.load(open('shop-project/state.json'))['deployments']['production']; sys.exit(not (p.get('EDGE_REGION')=='fra1' and len(p)>2))" -->
<!-- agent-task: update -->
> Make prices show within thirty seconds; I'll approve production myself.
<!-- agent-person update: cub mini approve --yes && sh deliver -->
<!-- agent-check update: cub unit data app --space shop-staging | grep -qx EDGE_CACHE_SECONDS=30 && cub unit data app --space shop-live | grep -qx EDGE_CACHE_SECONDS=30 && grep -q '"EDGE_CACHE_SECONDS": "30"' shop-project/state.json -->
<!-- agent-check-a update: grep -rqs 'EDGE_CACHE_SECONDS=30' shop -->
<!-- agent-task: undo -->
> Undo the cache change in production, and deliver it.
<!-- agent-check undo: cub unit data app --space shop-live | grep -qx EDGE_CACHE_SECONDS=60 && grep -q '"EDGE_CACHE_SECONDS": "60"' shop-project/state.json -->
<!-- agent-check-a undo: python3 -c "import json,sys; sys.exit(json.load(open('shop-project/state.json'))['deployments']['production'].get('EDGE_CACHE_SECONDS')!='60')" -->
<!-- agent-task: move -->
> Move the shop to our shared hub. Keep the production region and require my approval for production changes. The shared context is named `shared`, and the destination is in `TEAM_APP`.
<!-- agent-check move: cub --context shared unit data app --space "$TEAM_APP-live" | grep -qx EDGE_REGION=fra1 && cub --context shared api GET "component/$(cub --context shared component get "$TEAM_APP" -o jq=.Component.ComponentID)" | grep -q '"RequireChangeWorkflow":true' -->
<!-- agent-task: delete -->
> Remove the shop from this computer's hub; the team's hub keeps it.
<!-- agent-check delete: cub space get pattern-vercel >/dev/null && ! cub component get shop >/dev/null 2>&1 && ! cub space get shop-file-proposals >/dev/null 2>&1 -->
<!-- next-step: use the starter again | Want to use the same starting settings and approval for your next Vercel app? -->
<!-- arms: a,b,c -->
This proves: the real Hobby run checks what the production endpoint serves before and after first delivery, an update and a rollback. The no-account run checks delivery to the local stand-in and the move to a shared hub.

<!-- results:begin -->

Results, 14 November 2026, confighub mini 0.11.1-mini.2. Figures from this page's own test runs, shown here for whoever checks the page; they are not a promise.

- Scripted run: passed, 88 seconds for the steps, within the page's budget of 1200.
- Scripted run on Vercel Hobby (local build with the mini.1 server and CLI): passed, 467 seconds for the steps, within the page's budget of 1200.

- In the Hobby test, the running endpoint held its prior value while each order waited. After three separate owner approvals it served 60, then 30, then 60 from revisions 3, 4 and 5. The production alias matched the deployment in each receipt. The test project was deleted and the lookup returned project not found. The published mini.2 run used the stand-in and verified the copy to a shared hub separately.

- A separate build of the updated starter selected approved `starters-approved/vercel@2` when asked to connect a linked project. Staging got the 60-second setting, production kept its Frankfurt region, and the same checkout did not match without opt-in. This check used a local hub and a test link file.

<!-- results:end -->
