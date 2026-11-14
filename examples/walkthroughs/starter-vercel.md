<!-- walkthrough
id: starter-vercel
starts_with: mini
starter: vercel
needs: [cub mini package, Python 3, a hosted ConfigHub organization for step 8]
budget_seconds: 200
live_budget_seconds: 1200
-->
# An app on Vercel, with production behind your approval
Connect a Vercel app and keep a reason for every approved production setting. Try a personal Hobby project or use the local stand-in without a Vercel account.

## Human
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
**Real Hobby project.** For a personal, noncommercial test app, [sign in with the Vercel CLI](https://vercel.com/docs/cli/login), use `vercel teams ls` to find the Hobby scope and set `WALKTHROUGH_VERCEL_SCOPE` to its slug and choose a unique disposable project name. A Pro team can use a disposable project in its own scope. Use a package whose adoption help lists `--live`. Keep the Vercel sign-in with the person or delivery service. A user with direct production access in Vercel can still write there.
- Create a test app with an `/api/settings` route that returns its `EDGE_CACHE_SECONDS` value (or `baseline` if absent), and write `EDGE_REGION=fra1` in `shop/.env.production`. Run `vercel link --cwd shop --scope "$WALKTHROUGH_VERCEL_SCOPE" --project "$PROJECT"` and `vercel deploy --cwd shop --scope "$WALKTHROUGH_VERCEL_SCOPE" --prod`. Copy the production URL into `URL`; `curl -fsS "$URL/api/settings"` should report the baseline.
- Run `cub mini adopt shop --live` and read `cub mini receipts shop --setup`. Before the first delivery, run `cub mini approve shop-live/connect` in the owner's context. Set `READER=$(CUB_CONFIG="$PWD/reader" cub context get -o jq=.name)` after the separate reader sign-in in step 4. Grant `shop-delivery` read access to the base order and its attestations using `cub space update shop-base --permission View:serviceaccount:shop-delivery --permission ViewChildren:serviceaccount:shop-delivery`, then use the reader sign-in in step 4.
- To deliver each approved order, use its exact name as `ORDER`, read `REV=$(cub unit get app --space shop-live -o jq=.Unit.HeadRevisionNum)` as owner, then run the add-on from the separate reader context. Check the production alias with `vercel inspect "$URL" --scope "$WALKTHROUGH_VERCEL_SCOPE" --json` and match its deployment ID to the receipt. Read it with `curl -fsS "$URL/api/settings"`.
  ```sh
  CUB_CONFIG="$PWD/reader" "$MINI/starters/addons/vercel/run" --live --dir "$PWD/shop" \
    --scope "$WALKTHROUGH_VERCEL_SCOPE" --project "$PROJECT" --space shop-live \
    --order "$ORDER" --revision "$REV" --context "$READER" --keys EDGE_CACHE_SECONDS apply
  ```
- Propose the sale cache change with step 5. Check that the endpoint keeps its old value while the order waits. After owner approval, run the same delivery and check the new setting. To undo, restore the previous cache value in the file and upload it with the reason. Verify the endpoint before approval, then again after delivery of that rollback. Follow steps 8 and 9 to copy the app and verify approval on the shared hub. Remove the test project and the local app when finished.
<!-- run: live-delivery vercel-live -->
```sh
bash "${WALKTHROUGH_VERCEL_SCRIPT:?set to the path to examples/vercel-hobby.sh}"
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
   ```text
   Imported environment files; owner can now run cub mini adopt.
   ```
3. Deploy it. `cub mini adopt` connects the app with the Vercel starter. The hub keeps three copies of the settings: `shop-base`, shared by the other two; `shop-staging`; and `shop-live`, for production. The starter adds three settings, each with its reason, and leaves your Frankfurt region alone.
   <!-- run: deploy vercel-fixture -->
   ```sh
   cub mini adopt shop --provider-root shop-project
   ```
   ```text
     Leaves EDGE_REGION alone in live: it is set already, EDGE_REGION=fra1, by you, in .env.production.
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
   ```text
   Set back on shop-live, each with the reason:
     app: EDGE_CACHE_SECONDS 30 → 60
   …
   Production runs with {'SHOP_CURRENCY': 'EUR', 'EDGE_REGION': 'fra1', 'EDGE_CACHE_SECONDS': '60', 'EDGE_MAX_DURATION': '10', 'LOG_LEVEL': 'warn'}
   ```
8. Move it to your team's shared hub. Sign in once (`auth login` opens a browser). The app's name there, `TEAM_APP`, starts with your user name, so it does not clash with a teammate's.
   <!-- run: sign-in sign-in vercel-fixture -->
   ```sh
   cub context create shared --server https://hub.confighub.com
   cub --context shared auth login
   export PREFIX="${WALKTHROUGH_PREFIX:-$USER-}"
   export TEAM_APP="${PREFIX}shop"
   ```
   The copy keeps every value and its reason. Check the destination's approval rule before delivery. The commands after the copy install or verify the destination workflow and bind it to the app on a hub of version 0.11.1 or later. On an older hub, run `cub --context shared mini require-approval "$TEAM_APP" --variant live`.
   <!-- run: move vercel-fixture -->
   ```sh
   cub --context shared mini copy --from-context "$LOCAL_HUB" shop --name "$TEAM_APP"
   ME=$(cub --context shared user get "$(cub --context shared context get -o jq=.coordinate.user)" -o jq=.User.UserID)
   cub --context shared changeworkflow create --allow-exists --space workflows "$TEAM_APP-live-approval" --stage live --attestation-prerequisite approval --attestation-prerequisite-from-users approval="$ME" --stage-prerequisites live=approval
   WF=$(cub --context shared changeworkflow get --space workflows "$TEAM_APP-live-approval" -o jq=.ChangeWorkflow.ChangeWorkflowID)
   COMP=$(cub --context shared component get "$TEAM_APP" -o jq=.Component.ComponentID)
   echo "{\"RequireChangeWorkflow\": true, \"AllowedChangeWorkflowIDs\": [\"$WF\"]}" | cub --context shared api PATCH "component/$COMP" --content-type application/merge-patch+json --data - > /dev/null
   ```
9. Check that production in the shared hub waits for you, without changing anything there: the app takes a change only through its change workflow (the first `true`), and that workflow's production stage needs an approval (the second).
   <!-- run: move-waits vercel-fixture -->
   ```sh
   cub --context shared component get "$TEAM_APP" -o jq=.Component.RequireChangeWorkflow
   cub --context shared changeworkflow get --space workflows "$TEAM_APP-live-approval" -o jq='.ChangeWorkflow.Stages[] | select(.Name == "live") | .Prerequisites | length > 0'
   ```
   ```text
   true
   true
   ```
10. Delete the app from your own hub, now that the shared hub holds it. The Vercel project keeps the settings it was last given.
    <!-- run: delete vercel-fixture -->
    ```sh
    cub component delete --recursive --detach shop
    cub space delete --recursive shop-file-proposals
    ```
    ```text
    Successfully deleted component shop (ID)
    ```
In the shared hub: `cub --context shared component delete --recursive --detach "$TEAM_APP"` and `cub --context shared changeworkflow delete --space workflows "$TEAM_APP-live-approval"`. Here: `cub mini uninstall --name shop --delete-data` and `rm -rf ~/starter-example`.
## Agent
Use the app folder and the Human steps. Give the owner the exact approval command. Observe staging and the live value separately. Use the fixture for agent trials. After the copy, verify the shared approval workflow. Never approve production, put a secret into a setting, or write to the fixture's state file.
## Testing
The fixture tests the copy to a shared hub. The real run independently verifies the production alias and HTTP value against each delivery receipt. Agent pilots use the fixture; arm a uses ordinary tools without a hub.
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
<!-- next-step boundary=same-tier: use the starter again | Want to use the same starting settings and approval for your next Vercel app? -->
<!-- arms: a,b,c -->
This proves: the real Hobby run checks what the production endpoint serves before and after first delivery, an update and a rollback. The no-account run checks delivery to the local stand-in and the move to a shared hub.

<!-- results:begin -->

Results, 14 November 2026, confighub mini 0.11.1-mini.2. Figures from this page's own test runs, shown here for whoever checks the page; they are not a promise.

- Scripted run: passed, 95 seconds for the steps, within the page's budget of 200.
- Scripted run on Vercel Hobby (local build with the mini.1 server and CLI): passed, 467 seconds for the steps, within the page's budget of 1200.

- In the Hobby test, the running endpoint held its prior value while each order waited. After three separate owner approvals it served 60, then 30, then 60 from revisions 3, 4 and 5. The production alias matched the deployment in each receipt. The test project was deleted and the lookup returned project not found. The published mini.2 run used the stand-in and verified the copy to a shared hub separately.

- A separate build of the updated starter selected approved `starters-approved/vercel@2` when asked to connect a linked project. Staging got the 60-second setting, production kept its Frankfurt region, and the same checkout did not match without opt-in. This check used a local hub and a test link file.

- The checksum-verified macOS arm64 mini.4 package selected `starters-approved/vercel@2` with `--live` and kept the Frankfurt override. Without the flag, the link did not select the Vercel starter. This was a clean hub with a test link, and it was removed afterward. The live Hobby endpoint was not exercised by this run.

- Live Hobby rerun on checksum-verified mini.4 for macOS arm64, 14 November 2026: the disposable project served the baseline. The starter prepared revision 3 with a 60-second cache and kept the Frankfurt region. The adapter refused delivery before the first owner approval, and the production endpoint still served the baseline. The runner timed out waiting for that approval. The Vercel project was deleted and a subsequent lookup returned project not found. The local hub was stopped. The update and rollback on mini.4 did not run.

- A fresh live run with the same published mini.4 package completed first delivery. After owner approval, the Hobby production alias matched the receipt for revision 3 and the endpoint returned a 60-second cache. Staging then took the 30-second change. The adapter refused the pending update, and the endpoint continued serving 60 seconds. The run timed out at the second owner approval. The update and rollback were not delivered. The disposable project and test hub were removed, and a provider lookup confirmed the project was gone.

- The live Hobby walkthrough passed on checksum-verified mini.4 for macOS arm64 using a disposable project and three separate human approvals. The adapter refused each pending order; the endpoint kept serving its baseline, then 60 seconds, then 30 seconds while the respective orders waited. After approval and delivery it served 60 seconds on revision 3, 30 on revision 4, and 60 again on rollback revision 5. The production alias matched the ready deployment in each receipt. The rollback receipt had the same settings hash as revision 3. The live run used the walkthrough script in an isolated mini with an extended approval window. A provider lookup confirmed the project was deleted, and the test hub was stopped and removed.

<!-- results:end -->
