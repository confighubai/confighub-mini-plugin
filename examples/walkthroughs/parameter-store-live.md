# Live AWS Parameter Store walkthrough

Use a package containing `starters/addons/parameter-store/parameter-store-delivery`, AWS CLI, and two Standard String parameters under a new `/confighub-test/NAME` path: `staging/SSM_MAX_RETRIES` and `production/SSM_MAX_RETRIES`. Use a profile that can read both for import. Use a different profile that can read and overwrite only the production parameter for delivery; keep it out of agent sessions. A runtime profile should only read. This adapter never imports SecureString values.

Start the hub as in step 1 of the [Parameter Store walkthrough](starter-parameter-store.md). In a new directory, create `billing`, then import with the actual profile, region and path:

```sh
ADDON="$MINI/starters/addons/parameter-store/run"
AWS_PATH=/confighub-test/YOUR-TEST-NAME
AWS_REGION=eu-north-1
"$ADDON" --live --profile confighub-test-import --region "$AWS_REGION" --path "$AWS_PATH" --key SSM_MAX_RETRIES --dir billing import
cub mini adopt billing
```

Read and approve the starter catalog once as prompted. Separately, use the owner terminal to approve `billing-live/connect`. In a separate ConfigHub configuration, use a scoped delivery identity that can read the live revision and the order and approval records; do not put the owner key in an agent session. To apply, replace `NUMBER` with the live revision number and use that delivery context:

```sh
CUB_CONFIG="$PWD/delivery-config" "$ADDON" --live --context delivery-reader \
  --profile confighub-test-delivery --region "$AWS_REGION" --path "$AWS_PATH" \
  --key SSM_MAX_RETRIES --dir billing --space billing-live --order billing-live/connect --revision NUMBER apply
```

Use `compare` instead of `apply` with the read-only AWS runtime profile to check the same revision without writing. For an update or rollback, first propose the new value, confirm the provider still returns its previous version, and have the owner approve the new order. Use that order and revision for the next apply. The adapter reports the AWS parameter version; your app must read or reload the parameter before you can say it is running with the change. The main walkthrough’s shared-hub steps copy settings and recreate a gate. They do not switch AWS credentials or delivery. Remove only the disposable test parameters and roles you created.

