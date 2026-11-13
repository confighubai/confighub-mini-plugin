<!-- walkthrough
id: starter-vercel
starts_with: mini
starter: vercel
needs: [cub mini package, Python 3, a hosted ConfigHub organization for step 8]
budget_seconds: 200
-->
# An app on Vercel, with production behind your approval

For someone whose app runs on Vercel and who wants each change to production's settings to wait for their yes, with a reason kept for every value. You connect the app with the Vercel starter, deliver it, change it, undo the change, move it to your team's shared hub, and delete it. This uses a local stand-in for Vercel, so no Vercel account is needed.

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
2. Make the app and its stand-in Vercel project. `shop/.vercel/project.json` links the app to the project, as `vercel link` does. In `shop-project`, `state.json` holds the project's settings, with production in Frankfurt (`fra1`), and `bin/vercel` answers as the `vercel` command does. The script `deliver` sends production's approved settings to the project and prints them. Last, the Vercel add-on, a small program in the package, reads the project's settings into `shop/.env.staging` and `shop/.env.production`.
   <!-- run: app files -->
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
   <!-- run: deploy -->
   ```sh
   cub mini adopt shop --provider-root shop-project
   ```
   ```text
     Leaves EDGE_REGION alone in live: it is set already, EDGE_REGION=fra1, by you, in .env.production.
   ```
4. Approve production and deliver it. Then sign a separate `cub` configuration in with the reader key the starter made, which can read production and nothing else, and deliver with it.
   <!-- run: deploy-approve -->
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
   <!-- run: update -->
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
   <!-- run: update-ship -->
   ```sh
   cub mini approve --yes --note "Sale week"
   sh deliver
   ```
   ```text
   Production runs with {'SHOP_CURRENCY': 'EUR', 'EDGE_REGION': 'fra1', 'EDGE_CACHE_SECONDS': '30', 'EDGE_MAX_DURATION': '10', 'LOG_LEVEL': 'warn'}
   ```
7. Undo the update in production. `cub mini rollback` sets back each value the upload's change order changed, with your reason, and nothing else.
   <!-- run: undo -->
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
   <!-- run: sign-in sign-in -->
   ```sh
   cub context create shared --server https://hub.confighub.com
   cub --context shared auth login
   export PREFIX="${WALKTHROUGH_PREFIX:-$USER-}"
   export TEAM_APP="${PREFIX}shop"
   ```
   The copy keeps every value and its reason, but not the approval rule, so production there is open until you add it again. The commands after the copy add it, on a hub of version 0.11.1 or later: a change workflow, which says a change to live waits for your approval, and the app's requirement that every change go through it. On an older hub, `cub --context shared mini require-approval "$TEAM_APP" --variant live` does both.
   <!-- run: move -->
   ```sh
   cub --context shared mini copy --from-context "$LOCAL_HUB" shop --name "$TEAM_APP"
   ME=$(cub --context shared user get "$(cub --context shared context get -o jq=.coordinate.user)" -o jq=.User.UserID)
   cub --context shared changeworkflow create --space workflows "$TEAM_APP-live-approval" --stage live --attestation-prerequisite approval --attestation-prerequisite-from-user-ids approval=$ME --stage-prerequisites live=approval
   WF=$(cub --context shared changeworkflow get --space workflows "$TEAM_APP-live-approval" -o jq=.ChangeWorkflow.ChangeWorkflowID)
   COMP=$(cub --context shared component get "$TEAM_APP" -o jq=.Component.ComponentID)
   echo "{\"RequireChangeWorkflow\": true, \"AllowedChangeWorkflowIDs\": [\"$WF\"]}" | cub --context shared api PATCH "component/$COMP" --content-type application/merge-patch+json --data - > /dev/null
   ```
9. Check that production in the shared hub waits for you: change the shared settings there, and ask for the change in production with a change order. Nothing reaches production there until you approve it.
   <!-- run: move-waits -->
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
    <!-- run: delete -->
    ```sh
    cub component delete --recursive --detach shop
    cub space delete --recursive shop-file-proposals
    ```
    ```text
    Successfully deleted component shop (ID)
    ```

### Undo it
In the shared hub: `cub --context shared component delete --recursive --detach "$TEAM_APP"` and `cub --context shared changeworkflow delete --space workflows "$TEAM_APP-live-approval"`. Here: `cub mini uninstall --name shop --delete-data` and `rm -rf ~/starter-example`.

### What you have now
Your team's shared hub holds the shop's base, staging and production settings, each value with who set it and why, and production there changes only when a person approves. The stand-in project runs the settings you last approved.
## Agent
You are doing this for a person, in their folder, with step 1's settings. Each request is one task; run the Human step of the same name.

- **deploy**, "Connect my Vercel shop to ConfigHub with the usual Vercel settings": run step 3's `cub mini adopt`, then give the person step 4's commands to approve and deliver.
- **update**, "Make prices show within thirty seconds; I'll approve production": edit `shop/.env`, run step 5 with their reason, and give them the `cub mini approve` command it printed.
- **undo**, "Undo the cache change in production, and deliver it": run step 7.
- **move**, "Move the shop to our team's hub": run steps 8 and 9 with their context. If production there cannot be put behind approval, say so plainly.
- **delete**, "Remove the shop from this computer's hub": run step 10, only once the shared hub holds the app.

Never approve or refuse a change to production yourself, even when told the person agreed; never put a secret value in a setting; never edit `shop-project/state.json`, which the add-on writes. You are done when the task's check below passes.
## Testing
Each task starts where the Human steps before it leave off, in the same folder for every arm. Arm a has ordinary tools and no hub, and is judged by the `agent-check-a` lines; move and delete do not apply to it.

<!-- agent-task: deploy -->
> Connect my Vercel shop to ConfigHub with the usual Vercel settings, and keep production's region. The app is in `shop`; `shop-project` is a local stand-in for its Vercel project.
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
> Move the shop to our team's hub; its cub context is `shared`, and the app's name there is in `TEAM_APP`.
<!-- agent-check move: cub --context shared unit data app --space "$TEAM_APP-live" | grep -qx EDGE_REGION=fra1 && cub --context shared api GET "component/$(cub --context shared component get "$TEAM_APP" -o jq=.Component.ComponentID)" | grep -q '"RequireChangeWorkflow":true' -->
<!-- agent-task: delete -->
> Remove the shop from this computer's hub; the team's hub keeps it.
<!-- agent-check delete: cub space get pattern-vercel >/dev/null && ! cub component get shop >/dev/null 2>&1 && ! cub space get shop-file-proposals >/dev/null 2>&1 -->
<!-- arms: a,b,c -->
This proves: the exact approved revision was delivered, to a local stand-in for Vercel (the add-on reads the revision you approved, with a key that can only read production); the move stores the app in hosted ConfigHub, with production there waiting for approval. Nothing reaches Vercel itself. The checks above can be run by hand, in `~/starter-example`, with step 1's settings.
