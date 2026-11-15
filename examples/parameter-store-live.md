# Live AWS Parameter Store walkthrough

Use a package containing `starters/addons/parameter-store/parameter-store-delivery`, AWS CLI, and two Standard String parameters under a new `/confighub-test/NAME` path: `staging/SSM_MAX_RETRIES` and `production/SSM_MAX_RETRIES`. Use a profile that can read both for import. Use a different profile that can read and overwrite only the production parameter for delivery; keep it out of agent sessions. A runtime profile should only read. This adapter never imports SecureString values.

Start the hub as in step 1 of the [Parameter Store walkthrough](walkthroughs/starter-parameter-store.md). In a new directory, create `billing`, then import with the actual profile, region and path:

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

## Test the live path

1. With the read-only AWS profile, run `aws ssm get-parameter --profile confighub-test-runtime --region "$AWS_REGION" --name "$AWS_PATH/production/SSM_MAX_RETRIES" --query 'Parameter.{value:Value,version:Version}'`. Record that result before the proposal, while it is pending, and after each apply.
2. Try the same `apply` before the owner approves; it must refuse. A proposer IAM role must also be denied `ssm:PutParameter` on this disposable parameter. Confirm that the runtime's value and AWS version did not change.
3. Apply the owner-approved revision. Check the receipt's revision and SHA-256 and read back its AWS version from the application or a read-only runtime. Repeat with a fresh proposal that restores the original value, and check that a second apply of the same revision reports `unchanged` without creating a new AWS version.
4. With the owner's sign-in, copy to the shared hub. Check the live value and approval workflow in the destination. Give the delivery process a scoped ConfigHub reader on the destination. It needs to read the destination live revision and the source space's order and approval records. Keep the AWS writer scoped to the disposable production parameter.
5. Propose a change on the shared hub. Run the same `apply` command with the new reader configuration, its context, and the destination's live space, order and revision. Try it while the order is pending and confirm AWS returns the old value and version. Have the owner approve that exact order and wait for release to complete. Apply again, compare with the read-only profile, and check that the receipt's revision and digest match the destination revision.
6. Remove the disposable app, its approval workflow and reader, and the AWS parameters and roles created for this test.

For an agent: ask it to propose or check one setting, with the reason you give it. Keep the AWS writer and the ConfigHub owner context out of its session. The owner alone approves and runs delivery.
