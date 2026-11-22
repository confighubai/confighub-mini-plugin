# Stripe, Supabase, and Resend Mail add-on starters

Keep payment mode, database pool/SSL limits, and transactional email sandbox defaults explicit across `base`, `staging`, and `live`—so an AI coding agent can wire and tune staging freely while live billing, production database limits, and real customer email stay behind your approval.

**Starts with:** the local hub (`cub mini`) and the shipped add-on starter YAMLs (`starters/stripe.yaml`, `starters/supabase.yaml`, `starters/resend-mail.yaml` in `confighubai/confighub-mini`).

---

## Human

1. **Create a sample web app folder** with `.env` settings for Stripe, Supabase, and Resend:
   ```sh
   mkdir shop-addons && cd shop-addons && git init -q
   cat > .env <<'EOF'
   STRIPE_MODE=test
   STRIPE_CURRENCY=usd
   SUPABASE_POOL_MAX=10
   SUPABASE_SSL_MODE=require
   MAIL_DELIVERY_MODE=sandbox
   MAIL_RATE_LIMIT_PER_MIN=30
   EOF
   ```
2. **Adopt the app into your local hub** so `base`, `staging`, and `live` copies are created with defaults and plain-English reasons:
   ```sh
   cub mini adopt shop-addons --dir .
   ```
3. **Inspect what staging and live hold** before making changes:
   ```sh
   cub mini changes --dir . --mode envelope
   ```
4. **Propose a production change** (for example, switching Stripe from `test` to `live` or raising `MAIL_RATE_LIMIT_PER_MIN` for launch):
   - Staging takes changes immediately while keeping `STRIPE_MODE=test` and `MAIL_DELIVERY_MODE=sandbox` for safe testing.
   - Any proposal to `shop-addons-live` waits in `cub mini waiting` until **you** approve it in your own terminal:
     ```sh
     cub mini waiting
     cub mini approve PROPOSAL_ID --note "Verified webhook secret and live Stripe keys before launch"
     ```
5. **Undo if needed:**
   ```sh
   cub mini rollback shop-addons-live --change-order PROPOSAL_ID --reason "Return to previous approved launch limits"
   ```

---

## Agent

Paste this into Claude Code or Codex inside your app folder:

```text
Wire this app with ConfigHub's Stripe, Supabase, and Resend Mail starters. Keep STRIPE_MODE=test, SUPABASE_SSL_MODE=require, and MAIL_DELIVERY_MODE=sandbox in staging and preview. Propose live production defaults for my review, and do not approve production yourself.
```

**What the agent runs:**
- Detects `.env` and links the `stripe`, `supabase`, and `resend-mail` starter defaults (`STRIPE_*`, `SUPABASE_*`, `MAIL_*`).
- Updates `staging` and opens a local preview safely without sending real emails or touching live Stripe keys.
- Leaves the `live` change order waiting for the owner.

**What the agent must never do:**
- Never approve a `live` change order (refused by the hub on a scoped agent key).
- Never store raw Stripe secret keys, Supabase service-role tokens, or Resend API keys in plain-text non-secret settings (secret patterns are redacted).

---

## Testing

- **What ran and passed:** `starters/stripe.yaml`, `starters/supabase.yaml`, and `starters/resend-mail.yaml` are validated by `go test ./internal/starter/...` in `confighubai/confighub-mini` (schema, prefix ownership, defaults, reasons, and approval wiring).
- **What still needs a live external account run:** End-to-end delivery against live external Stripe, Supabase, and Resend accounts (using live webhooks and real SMTP/API delivery) has not been run in CI yet; this walkthrough exercises the local hub, staging/live isolation, and owner-approval gate with no external cloud credentials required.
