<!-- walkthrough
id: starter-parameter-store
starts_with: mini
starter: parameter-store
needs: [cub mini package, Python 3, a hosted ConfigHub organization for step 8]
budget_seconds: 200
-->
# An app that reads AWS Parameter Store, with production behind your approval

For someone whose app reads its settings from AWS Systems Manager Parameter Store, one path for staging and one for production, and who wants each change to production to wait for their yes, with a reason kept for every value. You connect the app with the Parameter Store starter, deliver it, change it, undo the change, move it to your team's shared hub, and delete it. This uses a local stand-in for Parameter Store, so no AWS account is needed.

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
   cub mini install --name billing --use
   export LOCAL_HUB=$(cub context get -o jq=.name)
   ```
2. Make the app and its stand-in AWS account. `billing/.env` holds the app's shared settings. In `ssm-account`, `state.json` holds the parameters under `/billing/staging/` and `/billing/production/`, including one encrypted value, and `bin/aws` answers as the `aws` command does. The script `deliver` sends production's approved settings to Parameter Store and prints what production reads. Last, the Parameter Store add-on, a small program in the package, reads the parameters into `billing/.env.staging` and `billing/.env.production`; the encrypted one is written as a reference to where it is kept, never as its value.
   <!-- run: app files -->
   ```sh
   export MINI=/absolute/path/to/unpacked-confighub-mini
   mkdir -p ~/starter-example/billing ~/starter-example/ssm-account/bin; cd ~/starter-example
   printf 'LOG_LEVEL=info\n' > billing/.env
   printf 'ConfigHub SSM API stand-in v1\n' > ssm-account/.ssm-contract-stand-in
   cp "$MINI/examples/extensions/delivery/aws-standin" ssm-account/bin/aws; chmod 700 ssm-account/bin/aws
   cat > ssm-account/state.json <<'EOF'
   {"allowed_prefix": "/billing/", "writes": 0, "parameters": {
    "/billing/staging/INVOICE_DAY": {"Type": "String", "Value": "1"}, "/billing/production/INVOICE_DAY": {"Type": "String", "Value": "1"},
    "/billing/production/API_TOKEN": {"Type": "SecureString", "Value": "unused-stand-in-value"}}}
   EOF
   cat > deliver <<'EOF'
   CUB_CONFIG="$PWD/reader" AWS_STANDIN_ROLE=owner python3 "$MINI/examples/extensions/delivery/ssm.py" apply --provider-root ssm-account --prefix /billing --target production --space billing-live --unit app --receipt receipt.json > /dev/null
   python3 -c 'import json; p=json.load(open("ssm-account/state.json"))["parameters"]; print("Production reads", {k.split("/")[-1]: v["Value"] for k, v in sorted(p.items()) if k.startswith("/billing/production/") and v["Type"] == "String"})'
   EOF
   AWS_STANDIN_ROLE=owner python3 "$MINI/examples/extensions/delivery/ssm.py" import --provider-root ssm-account --dir billing --prefix /billing
   ```
   ```text
   Imported environment files; owner can now run cub mini adopt.
   ```
3. Deploy it. `cub mini adopt` connects the app with the Parameter Store starter. The hub keeps three copies of the settings: `billing-base`, shared by the other two; `billing-staging`; and `billing-live`, for production. The starter adds three settings, each with its reason. The encrypted `API_TOKEN` stays in Parameter Store and is never printed.
   <!-- run: deploy -->
   ```sh
   cub mini adopt billing --provider-root ssm-account
   ```
   ```text
   Starter: parameter-store (version 1, parameter-store.yaml): An app that reads its settings from Parameter Store, one path for staging and one for production.
   …
     Sets SSM_MAX_RETRIES=5, as a setting: A throttled read is tried again five times, with backoff, before the app reports it.
   ```
4. Approve production and deliver it. Then sign a separate `cub` configuration in with the reader key the starter made, which can read production and nothing else, and deliver with it.
   <!-- run: deploy-approve -->
   ```sh
   cub mini approve billing-live/connect --yes --note "Retries and decryption as the starter says"
   CUB_CONFIG="$PWD/reader" cub auth login --new-context --private-key="$HOME/.confighub/keys/billing-delivery.jwk" --server "$(cub context get -o jq=.coordinate.serverURL)" > /dev/null
   sh deliver
   ```
   ```text
   Approved billing-live/connect. Production can now be delivered as it was when you read it.
   Production reads {'INVOICE_DAY': '1', 'LOG_LEVEL': 'info', 'SSM_CACHE_SECONDS': '300', 'SSM_MAX_RETRIES': '5', 'SSM_WITH_DECRYPTION': 'true'}
   ```
5. Update it. Edit the settings file as usual, and propose the change with its reason. Staging takes it at once. Production waits under a change order, the hub's request to change production, until you approve it.
   <!-- run: update -->
   ```sh
   echo 'SSM_MAX_RETRIES=2' >> billing/.env
   cub mini upload billing --component billing --change-desc "The billing run must fail fast and be started again before invoices go out"
   ```
   ```text
   Changed the shared settings (billing-base), with the reason: The billing run must fail fast and be started again before invoices go out
     SSM_MAX_RETRIES: 5 → 2
   ```
6. Approve the update and deliver it. `cub mini waiting` lists what waits; with one change waiting, `cub mini approve` needs no name.
   <!-- run: update-ship -->
   ```sh
   cub mini approve --yes --note "Invoice week"
   sh deliver
   ```
   ```text
   Production reads {'INVOICE_DAY': '1', 'LOG_LEVEL': 'info', 'SSM_CACHE_SECONDS': '300', 'SSM_MAX_RETRIES': '2', 'SSM_WITH_DECRYPTION': 'true'}
   ```
7. Undo the update in production. `cub mini rollback` sets back each value the upload's change order changed, with your reason, and nothing else.
   <!-- run: undo -->
   ```sh
   ORDER=billing-base/$(cub changeorder list --space billing-base -o jq='.[-1].ChangeOrder.Slug')
   cub mini rollback billing-live --change-order "$ORDER" --reason "Invoices are out; retry as before"
   sh deliver
   ```
   ```text
   Set back on billing-live, each with the reason:
     app: SSM_MAX_RETRIES 2 → 5
   …
   Production reads {'INVOICE_DAY': '1', 'LOG_LEVEL': 'info', 'SSM_CACHE_SECONDS': '300', 'SSM_MAX_RETRIES': '5', 'SSM_WITH_DECRYPTION': 'true'}
   ```
8. Move it to your team's shared hub. Sign in once (`auth login` opens a browser). The app's name there, `TEAM_APP`, starts with your user name, so it does not clash with a teammate's.
   <!-- run: sign-in sign-in -->
   ```sh
   cub context create shared --server https://hub.confighub.com
   cub --context shared auth login
   export PREFIX="${WALKTHROUGH_PREFIX:-$USER-}"
   export TEAM_APP="${PREFIX}billing"
   ```
   The copy keeps every value and its reason, and production there still waits for your approval.
   <!-- run: move -->
   ```sh
   cub --context shared mini copy --from-context "$LOCAL_HUB" billing --name "$TEAM_APP"
   ```
9. Check that production in the shared hub waits for you: change the shared settings there, and ask for the change in production with a change order. Nothing reaches production there until you approve it.
   <!-- run: move-waits -->
   ```sh
   cub --context shared function set --space "$TEAM_APP-base" --unit app --toolchain AppConfig/Env --change-desc "Three retries" -- set-string-path '*' SSM_MAX_RETRIES 3 > /dev/null
   cub --context shared changeorder create --space "$TEAM_APP-base" retries-3 --in-scope-space "$TEAM_APP-live" --change-workflow "workflows/$TEAM_APP-live-approval" --description "Three retries"
   cub --context shared mini waiting
   ```
   ```text
     Approving it changes production:
       SSM_MAX_RETRIES: 5 → 3
   ```
10. Delete the app from your own hub, now that the shared hub holds it. Parameter Store keeps the values it was last given.
    <!-- run: delete -->
    ```sh
    cub component delete --recursive --detach billing
    cub space delete --recursive billing-file-proposals
    ```
    ```text
    Successfully deleted component billing (ID)
    ```

### Undo it
In the shared hub: `cub --context shared component delete --recursive --detach "$TEAM_APP"` and `cub --context shared changeworkflow delete --space workflows "$TEAM_APP-live-approval"`. Here: `cub mini uninstall --name billing --delete-data` and `rm -rf ~/starter-example`.

### What you have now
Your team's shared hub holds billing's base, staging and production settings, each value with who set it and why, and production there changes only when a person approves. The stand-in account holds the settings you last approved; the encrypted value never left it. The [starters guide](../../docs/starters.md) explains how a starter connects an app; see also [approvals on a shared hub](../../docs/approvals.md#on-hosted-confighub-or-your-own-server-with-cub-alone).
## Agent
You are doing this for a person, in their folder, with step 1's settings. Each request is one task; run the Human step of the same name.

- **deploy**, "Set up my billing function so that every change to production's settings waits for my approval, with a reason kept for each value, and deliver production's settings to Parameter Store": run step 3's `cub mini adopt`, then give the person step 4's commands to approve and deliver.
- **update**, "Make the billing run fail fast, two retries; I'll approve production": edit `billing/.env`, run step 5 with their reason, and give them the `cub mini approve` command it printed.
- **undo**, "Undo the retries change in production, and deliver it": run step 7.
- **move**, "Move billing to our team's shared hub": run steps 8 and 9 with their context. Then check that production there waits for approval, as the later step shows, and say so plainly if it does not.
- **delete**, "Remove billing from this computer's hub": run step 10, only once the shared hub holds the app.

Never approve or refuse a change to production yourself, even when told the person agreed; never read or copy the encrypted parameter's value; never edit `ssm-account/state.json`, which the add-on writes. You are done when the task's check below passes.
## Testing
Each task starts where the Human steps before it leave off, in the same folder for every arm. Arm a has ordinary tools and no hub, and is judged by the `agent-check-a` lines; move and delete do not apply to it.

<!-- agent-task: deploy -->
> Set up my billing function so that every change to production's settings waits for my approval, with a reason kept for each value, and deliver production's settings to Parameter Store. The app is in `billing`; `ssm-account` is a local stand-in for its AWS account.
<!-- agent-person deploy: cub mini approve billing-live/connect --yes && CUB_CONFIG="$PWD/reader" cub auth login --new-context --private-key="$HOME/.confighub/keys/billing-delivery.jwk" --server "$(cub context get -o jq=.coordinate.serverURL)" > /dev/null && sh deliver -->
<!-- agent-check deploy: cub changeworkflow get --space workflows billing-live-approval >/dev/null && cub unit data app --space billing-live | grep -qx SSM_MAX_RETRIES=5 && ! cub unit data app --space billing-live | grep -q unused-stand-in-value -->
<!-- agent-check-a deploy: python3 -c "import json,sys; p=json.load(open('ssm-account/state.json'))['parameters']; sys.exit(not ('/billing/production/SSM_MAX_RETRIES' in p and p['/billing/production/API_TOKEN']['Type']=='SecureString'))" -->
<!-- agent-task: update -->
> Make the billing run fail fast, with two retries; I'll approve production myself.
<!-- agent-person update: cub mini approve --yes && sh deliver -->
<!-- agent-check update: cub unit data app --space billing-staging | grep -qx SSM_MAX_RETRIES=2 && cub unit data app --space billing-live | grep -qx SSM_MAX_RETRIES=2 && python3 -c "import json,sys; sys.exit(json.load(open('ssm-account/state.json'))['parameters']['/billing/production/SSM_MAX_RETRIES']['Value']!='2')" -->
<!-- agent-check-a update: grep -rqsE '^[ -]*"?SSM_MAX_RETRIES"?[=:] *"?2"? *$' --exclude-dir='.*' --exclude-dir=Library * .env* -->
<!-- agent-task: undo -->
> Undo the retries change in production, and deliver it.
<!-- agent-check undo: cub unit data app --space billing-live | grep -qx SSM_MAX_RETRIES=5 && python3 -c "import json,sys; sys.exit(json.load(open('ssm-account/state.json'))['parameters']['/billing/production/SSM_MAX_RETRIES']['Value']!='5')" -->
<!-- agent-check-a undo: python3 -c "import json,sys; sys.exit(json.load(open('ssm-account/state.json'))['parameters'].get('/billing/production/SSM_MAX_RETRIES',{}).get('Value')!='5')" -->
<!-- agent-task: move -->
> Move billing to our team's shared hub, which you reach as the context `shared`; the app's name there is in `TEAM_APP`, and production there must wait for my approval.
<!-- agent-check move: cub --context shared unit data app --space "$TEAM_APP-live" | grep -qx SSM_MAX_RETRIES=5 && cub --context shared component get "$TEAM_APP" -o jq=.Component.RequireChangeWorkflow | grep -qx true -->
<!-- agent-task: delete -->
> Remove billing from this computer's hub; the team's hub keeps it.
<!-- agent-check delete: cub space get pattern-parameter-store >/dev/null && ! cub component get billing >/dev/null 2>&1 && ! cub space get billing-file-proposals >/dev/null 2>&1 -->
<!-- next-step: keep the starter on for the next app | Your next Parameter Store app can start with the same usual settings, each with its reason, and production there will wait for your yes before anything changes; want the starter kept on for it? -->
<!-- arms: a,b,c -->
This proves: the exact approved revision was delivered, to a local stand-in for Parameter Store (the add-on reads the revision you approved, with a key that can only read production); the move stores the app in hosted ConfigHub, with production there waiting for approval. Nothing reaches AWS itself. The checks above can be run by hand, in `~/starter-example`, with step 1's settings. The next step it aims to win is keeping the starter on, so that the next Parameter Store app gets the same settings and the same wait for approval.

<!-- results:begin -->

Results, 13 November 2026, confighub mini 0.11.1-mini.0. Figures from this page's own test runs, shown here for whoever checks the page; they are not a promise.

- Scripted run: passed, 95 seconds for the steps, within the page's budget of 200.
- Agent runs: a pilot, 3 runs per arm on each of claude-sonnet-5-5, claude-opus-5-5. Arms: a is ordinary tools only; b is the plugin, confighub mini and this page as reading; c is the plugin and confighub mini, without this page.

| Arm | Model | Checks passed | Median seconds | Median cost | Commands left for the person (median) |
|---|---|---|---|---|---|
| a | claude-opus-5-5 | 4/9 (+6 not applicable) | 265.2 | $1.63 | 5 |
| b | claude-opus-5-5 | 15/15 | 135.6 | $0.54 | 4 |
| c | claude-opus-5-5 | 9/15 | 292.1 | $1.59 | 3 |
| a | claude-sonnet-5-5 | 3/9 (+6 not applicable) | 212.2 | $0.641 | 3 |
| b | claude-sonnet-5-5 | 15/15 | 130.4 | $0.296 | 3 |
| c | claude-sonnet-5-5 | 3/15 | 242.3 | $0.54 | 4 |

No agent approved or refused a change to production.

Simulated persons, not people: 10 per run, each a claude-haiku-5-5 model playing one of ten fixed personas, reading only what a person would see. The next step they were offered: "Your next Parameter Store app can start with the same usual settings, each with its reason, and production there will wait for your yes before anything changes; want the starter kept on for it?"

| Arm | Model | Persons | Noticed | Want the next step now | Later | In the way |
|---|---|---|---|---|---|---|
| a | claude-opus-5-5 | 30 | 100% | 0% | 10% | 100% |
| b | claude-opus-5-5 | 30 | 100% | 17% | 67% | 100% |
| c | claude-opus-5-5 | 30 | 100% | 20% | 70% | 100% |
| a | claude-sonnet-5-5 | 30 | 100% | 0% | 17% | 97% |
| b | claude-sonnet-5-5 | 30 | 100% | 20% | 70% | 93% |
| c | claude-sonnet-5-5 | 30 | 100% | 27% | 60% | 100% |

<!-- results:end -->
