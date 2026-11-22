<!-- walkthrough
id: starter-addons-stripe-supabase-resend
starts_with: mini
starter: stripe
needs: [confighub mini package, a hosted ConfigHub organization for step 6]
budget_seconds: 200
-->
# Stripe, Supabase, and Resend Mail add-on starters: deploy, update, undo, move, delete

You run a web app wired to Stripe, Supabase, and Resend Mail. Keep `STRIPE_MODE=test`, `SUPABASE_SSL_MODE=require`, and `MAIL_DELIVERY_MODE=sandbox` explicit in staging while gating live billing, database pool limits, and production email delivery behind your approval.

## Quick start

You need: the [local hub](../../docs/install-mini.md), unpacked, with starters switched on (`starters/stripe.yaml`, `starters/supabase.yaml`, `starters/resend-mail.yaml`).

| | By hand | Ask your agent |
|---|---|---|
| Connect the app | `cub mini adopt shop-addons` | "Connect shop-addons with the Stripe, Supabase, and Resend starters; keep staging in test/sandbox mode and hold production for my approval." |
| Change a setting | Edit `shop-addons/.env`, then `cub mini upload shop-addons --change-desc "Raise mail rate limit for launch"` | "Raise MAIL_RATE_LIMIT_PER_MIN from 30 to 120 for launch and hold production for my approval." |
| Approve production | `cub mini approve BASE/ORDER` (step 4) | You approve it yourself. |
| Undo | `cub mini rollback shop-addons-live --change-order BASE/ORDER --reason "Return to 30/min after launch"` | "Undo the mail rate limit increase in production; return to 30 per minute." |

Staging stays on test billing and sandbox email, production changes only when you approve, and `cub mini pull` writes production's approved settings where the app reads them.

Without ConfigHub: an agent editing `.env` directly can flip `STRIPE_MODE` or `MAIL_DELIVERY_MODE` across environments with no approval gate and no record of why.

## Deeper dive

The rest of this page is the full version: every command for staging and live add-on settings, moving the setup to a shared hub, what an agent leaves to you, and what has been tested.

<details>
<summary>Show the full walkthrough</summary>

## Human
For a person following along in a terminal.

### What you need
The local hub, unpacked as [installing the local hub](../../docs/install-mini.md) shows. For step 6 you also need a shared hub context (`shared`).

### Steps
1. Start a local hub with starters enabled (`MINI` is the unpacked package folder):
   <!-- run: setup -->
   ```sh
   export MINI=/absolute/path/to/unpacked-confighub-mini
   export PATH="$MINI/bin:$PATH" CUB_MINI_STARTERS="$MINI/starters"
   cub plugin install "$MINI" >/dev/null
   cub mini install --use
   export LAPTOP=$(cub context get -o jq=.name)
   ```
2. Create the sample `shop-addons` folder with explicit Stripe, Supabase, and Resend settings:
   <!-- run: app files -->
   ```sh
   mkdir shop-addons
   cat > shop-addons/.env <<'EOF'
   STRIPE_MODE=test
   STRIPE_CURRENCY=usd
   SUPABASE_POOL_MAX=10
   SUPABASE_SSL_MODE=require
   MAIL_DELIVERY_MODE=sandbox
   MAIL_RATE_LIMIT_PER_MIN=30
   EOF
   printf 'STRIPE_MODE=test\nMAIL_DELIVERY_MODE=sandbox\n' > shop-addons/.env.staging
   ```
3. Deploy it: adopt `shop-addons` into the local hub so `base`, `staging`, and `live` copies are created with defaults and plain-English reasons, then approve the initial production revision:
   <!-- run: deploy -->
   ```sh
   cub mini adopt shop-addons
   cub mini approve shop-addons-base/adopt --note "Initial add-on settings for production" --yes
   cub mini pull shop-addons --variant live --dir shop-addons-running
   ```
4. Update it: raise `MAIL_RATE_LIMIT_PER_MIN` to `120` for launch, upload with a reason, inspect `cub mini waiting`, and approve the exact order:
   <!-- run: update -->
   ```sh
   sed -i.bak 's/MAIL_RATE_LIMIT_PER_MIN=30/MAIL_RATE_LIMIT_PER_MIN=120/' shop-addons/.env && rm -f shop-addons/.env.bak
   UPDATE=$(cub mini upload shop-addons --change-desc "Raise mail rate limit for launch")
   UPDATE_ORDER=$(printf '%s\n' "$UPDATE" | sed -nE 's/^.*mini approve (shop-addons-base\/upload-[a-z0-9-]+)[[:space:]]*$/\1/p')
   cub mini waiting
   cub mini approve "${UPDATE_ORDER:?Review the update first}" --yes --note "Approved launch mail limit"
   cub mini pull shop-addons --variant live --dir shop-addons-running
   ```
5. Undo the update in production via `cub mini rollback` and approve the rollback order:
   <!-- run: undo -->
   ```sh
   ROLLBACK=$(cub mini rollback shop-addons-live --change-order "${UPDATE_ORDER:?Run the update first}" --reason "Return to 30/min after launch")
   ROLLBACK_ORDER=$(printf '%s\n' "$ROLLBACK" | sed -nE 's/^.*mini approve (shop-addons-base\/upload-[a-z0-9-]+)[[:space:]]*$/\1/p')
   cub mini waiting
   cub mini approve "${ROLLBACK_ORDER:?Review the rollback first}" --yes --note "Back to 30/min"
   cub mini pull shop-addons --variant live --dir shop-addons-running
   ```
6. Move it to your team's shared hub (`shared` context), keeping every setting, reason, and the live approval gate:
   <!-- run: move -->
   ```sh
   export PREFIX="${WALKTHROUGH_PREFIX:-$USER-}"
   export TEAM_APP="${PREFIX}shop-addons"
   cub --context shared mini copy --from-context "$LAPTOP" shop-addons --name "$TEAM_APP"
   cub --context shared unit data app --space "$TEAM_APP-live"
   ```
7. Delete the local copy once the shared hub holds the app (your local `shop-addons/.env` files stay untouched):
   <!-- run: delete -->
   ```sh
   cub space delete --space shop-addons-live,shop-addons-staging,shop-addons-base,shop-addons-file-proposals --recursive
   cub component delete shop-addons
   cub changeworkflow delete --space workflows shop-addons-live-approval
   cub changeworkflow delete --space workflows shop-addons-file-review
   ```

### Undo it
In the shared hub, delete `$TEAM_APP-live`, `$TEAM_APP-staging`, `$TEAM_APP-base`, component `$TEAM_APP`, and workflow `$TEAM_APP-live-approval`. Locally, `cub mini uninstall --delete-data` removes the local hub.

### What you have now
`shop-addons/.env` untouched, `shop-addons-running/app.env` holding approved production settings, and your team's shared hub gating live billing, database, and email changes behind owner approval.

## Agent
For an AI agent doing these jobs for a person:
- **Deploy:** `cub mini adopt shop-addons`. Keep `STRIPE_MODE=test` and `MAIL_DELIVERY_MODE=sandbox` in staging, and hand the person the exact `BASE/ORDER` from `cub mini waiting` to approve production.
- **Update:** edit `shop-addons/.env`, run `cub mini upload shop-addons --change-desc "WHY"`, and hand the person the exact `BASE/ORDER` to approve.
- **Undo:** restore the previous value or propose a rollback with a reason, and hand the person the exact rollback order to approve.
- **Move:** copy to the `shared` context and verify `RequireChangeWorkflow` is `true` without modifying production.
- **Delete:** remove the local hub spaces/component only after the shared hub holds the app; never delete the person's repo files.

Never approve a production change order yourself, and never write raw Stripe secret keys, Supabase service-role tokens, or Resend API keys into plain-text non-secret settings.

## Testing
`starters/stripe.yaml`, `starters/supabase.yaml`, and `starters/resend-mail.yaml` are validated by `go test ./internal/starter/...` in `confighubai/confighub-mini`. End-to-end delivery against external Stripe, Supabase, and Resend accounts has not been run in CI yet; these tasks verify the local hub, staging/live isolation, and owner-approval gate with no external credentials.

<!-- agent-task: deploy -->
> Connect shop-addons with the Stripe, Supabase, and Resend starters; keep staging in test/sandbox mode and hold production for my approval.
<!-- agent-task: update -->
> Raise MAIL_RATE_LIMIT_PER_MIN from 30 to 120 for launch in shop-addons and hold production for my approval.
<!-- agent-task: undo -->
> Undo the mail rate limit increase in shop-addons production; return to 30 per minute.
<!-- agent-task: move -->
> Copy shop-addons to our team's shared hub (context `shared`) as `TEAM_APP`, keeping production behind my approval.
<!-- agent-task: delete -->
> Remove shop-addons from this computer's local hub now that the shared hub holds it. Keep my files.

<!-- agent-check deploy: cub unit data app --space shop-addons-live | grep -qx SUPABASE_SSL_MODE=require && cub unit data app --space shop-addons-staging | grep -qx STRIPE_MODE=test -->
<!-- agent-check update: cub unit data app --space shop-addons-live | grep -qx MAIL_RATE_LIMIT_PER_MIN=120 -->
<!-- agent-check undo: cub unit data app --space shop-addons-live | grep -qx MAIL_RATE_LIMIT_PER_MIN=30 && test -f shop-addons/.env -->
<!-- agent-check move: cub --context shared unit data app --space "$TEAM_APP-live" | grep -qx SUPABASE_SSL_MODE=require -->
<!-- agent-check delete: test -f shop-addons/.env && ! cub space get shop-addons-live >/dev/null 2>&1 -->
<!-- next-step boundary=same-tier when "did not change": keep add-on starters on | Production waited for your yes because the Stripe, Supabase, and Resend starters set this app up with staging/live separation and reasons. Want to keep these add-on starters on for your next app? -->
This proves: the add-on starter settings were stored in the local hub and copied to a shared hub with production waiting for owner approval, while staging kept test billing and sandbox email defaults. External Stripe, Supabase, and Resend API delivery is not run here.

</details>
