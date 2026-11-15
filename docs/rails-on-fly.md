# Two Rails apps on Fly, one shared setup

**Build preview.** This guide needs a confighub mini build that contains `starters/rails-fly.yaml`. The starter manages settings in ConfigHub. You keep using Fly's own tools to deploy. Try this on disposable apps first.

Suppose a shop and a cart use the same support hours. Each has its own banner, and the cart needs quieter logs. Start the cart from the shop's setup, then change the hours once. You can try the change in both staging copies before touching production.

## Try it without a Fly account

Set `MINI` to the absolute path of the unpacked candidate package. The package has a small Rails app and a script that runs the two-app scenario on a disposable local hub, removes the hub, and leaves the two staging env files. Use Python 3 for the script and Docker to read those settings from two actual Rails processes.

```sh
OUT="$(mktemp -d)"
python3 "$MINI/examples/starter-examples/rails-fly/run.py" --package "$MINI" --out "$OUT"
cat "$OUT/result.json"
cat "$OUT/waiting.txt"
docker build -t confighub-rails-fly-example "$MINI/examples/starter-examples/rails-fly/app"
docker run --rm --name rails-shop-example --env-file "$OUT/rails-shop.staging.env" \
  -e SECRET_KEY_BASE_DUMMY=1 -p 127.0.0.1:3101:3000 -d confighub-rails-fly-example
docker run --rm --name rails-cart-example --env-file "$OUT/rails-cart.staging.env" \
  -e SECRET_KEY_BASE_DUMMY=1 -p 127.0.0.1:3102:3000 -d confighub-rails-fly-example
```

Once both start, read `/api/settings` on [port 3101](http://127.0.0.1:3101/api/settings) and [port 3102](http://127.0.0.1:3102/api/settings). Both should show `Daily`, with the separate values below. Stop the two containers with `docker stop rails-shop-example rails-cart-example`.

## Connect the two apps

Start with two Rails folders with a `Gemfile`, `bin/rails`, `config/application.rb` and a `fly.toml` in each. Give them these non-secret settings. Keep passwords, keys and Rails credentials in your existing secret store.

| File | Settings |
|---|---|
| `./shop/.env` | `APP_BANNER=coral` and `APP_SUPPORT_HOURS=Weekdays` |
| `./cart/.env` | `APP_BANNER=indigo` and `RAILS_LOG_LEVEL=warn` |

Use an empty test hub. From a fresh terminal, set `MINI` to the absolute path of the unpacked candidate package and run:

```sh
unset CUB_CONTEXT
export CUB_CONFIG="$(mktemp -d "$HOME/.confighub-rails-example.XXXXXX")"
"$MINI/bin/confighub-mini-app" mini install-plugin "$CUB_CONFIG"
cub() { "$MINI/bin/cub" "$@"; }
cub mini install --name rails-fly-example --use
```

Then move to the directory containing `shop` and `cart`:


```sh
export CUB_MINI_STARTERS=on
cub mini adopt ./shop --name rails-shop --dry-run
```

Look for `rails-fly` in the plan. It fills in `RAILS_LOG_LEVEL=info` with a reason and says delivery is left to you. If you're using Claude Code or Codex, have the agent read the plan and report the selected starter before it connects either app.

```sh
cub mini adopt ./shop --name rails-shop
cub mini adopt ./cart --name rails-cart --pattern rails-shop
```

The cart takes the support hours from the shop. The cart's banner and log level stay its own.

## Change the hours and check staging

```sh
cub mini set rails-shop APP_SUPPORT_HOURS=Daily --variant base --change-desc "The help desk now opens daily"
cub mini upgrade rails-shop-base/app --change-desc "The help desk now opens daily"
cub mini promote rails-shop-staging
cub mini promote rails-cart-staging
cub unit data --space rails-shop-staging app
cub unit data --space rails-cart-staging app
cub mini waiting
```

Look for `Daily` in both staging copies, `coral` and `info` in the shop, and `indigo` and `warn` in the cart. To try the change in Rails, supply those three values to each app's staging process and check the page or endpoint that uses them. For this example, use an endpoint that returns the banner, support hours and Rails log level. Do not replace a whole env file with the hub output: it includes metadata and omits secrets.

`cub mini waiting` shows the exact ConfigHub orders and the commands the owner can use to review each. Leave them pending for this exercise. ConfigHub does not block a direct Fly deploy by someone with Fly credentials. A hub approval changes the hub's production copy; it does not deploy a Fly Machine.

When done, remove the disposable hub with `cub mini uninstall --name rails-fly-example --delete-data`.

## Testing

On an unreleased mini build, a disposable local hub stored the two apps' settings. One change moved both staging copies from revision 2 to 3. Two Rails processes running locally read the staging settings and served `Daily`, with their own banners and log levels. Both hub production copies stayed at revision 2 and orders still waited for the owner. The starter check also caught three planted faults.

In a separate Fly.io run with the same candidate package, two staging Machines served the daily hours from revision 3. The shop kept `coral` and `info`, and the cart kept `indigo` and `warn`. The test's delivery check refused both pending orders, and both production Machines still served `Weekdays`. The test used Fly's CLI and a separate revision check; the starter does not ship a Fly delivery add-on.

**What did not run yet:** owner-approved production delivery, rollback on Fly, or a shared-hub move. The starter is still a build preview.
