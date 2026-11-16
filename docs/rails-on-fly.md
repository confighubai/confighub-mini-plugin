# Two Rails apps on Fly, one shared setup

Use the [current local hub package](install-mini.md#the-current-release). The starter sets up your Rails settings in ConfigHub. You can try the example on your computer without a Fly account.

Suppose a shop and a cart use the same support hours. Each has its own banner, and the cart needs quieter logs. Start the cart from the shop's setup, then change the hours once. You can try the change in both staging copies before touching production.

## Quick start

You need: the [current local hub package](install-mini.md#the-current-release), Python 3 and Docker. Sending settings to Fly also needs a signed-in `flyctl` and an app on Fly.

| | By hand | Ask your agent |
|---|---|---|
| Try it without Fly | `python3 "$MINI/examples/starter-examples/rails-fly/run.py" --package "$MINI" --out "$OUT"` | Your agent can run the same command. |
| Connect both apps | `cub mini adopt ./shop --name rails-shop`, then `cub mini adopt ./cart --name rails-cart --pattern rails-shop` | Your agent can run the same commands. |
| Change the hours | `cub mini set rails-shop APP_SUPPORT_HOURS=Daily --variant base --change-desc "The help desk now opens daily"`, then upgrade and promote ([the full list](#change-the-hours-and-check-staging)) | Your agent can run the same command. |
| Approve and send to Fly | Approve the order, then run `"$MINI/bin/fly-settings" apply` with its order and revision ([the full command](#send-approved-settings-to-an-app-on-fly)) | You approve it yourself. |

Without ConfigHub: your agent changes the settings directly with `flyctl`, production included, and the next session has no record of why.

## Deeper dive

The sections below give each command in full: a run without a Fly account, connecting the two apps, changing the hours in both staging copies, and sending approved settings to Fly.

## Try it without a Fly account

Set `MINI` to the absolute path of the unpacked package. The package has a small Rails app and a script that runs the two-app scenario on a disposable local hub, removes the hub, and leaves the two staging env files. Use Python 3 for the script and Docker to read those settings from two actual Rails processes.

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

Use an empty test hub. From a fresh terminal, set `MINI` to the absolute path of the unpacked package and run:

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

Look for `rails-fly` in the plan. It fills in `RAILS_LOG_LEVEL=info` with a reason and says delivery is left to you.

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

Look for `Daily` in both staging copies, `coral` and `info` in the shop, and `indigo` and `warn` in the cart. Pass those three values to each staging app. Check the page or endpoint that uses them. For the sample app, use `/api/settings`. Copy only those three values so you don’t lose any settings your app already uses.

`cub mini waiting` shows the exact ConfigHub orders and the commands the owner can use to review each. Leave them pending for this exercise. ConfigHub does not block a direct Fly deploy by someone with Fly credentials. A hub approval changes the hub's production copy; it does not deploy a Fly Machine.

When done, remove the disposable hub with `cub mini uninstall --name rails-fly-example --delete-data`.

## Send approved settings to an app on Fly

This step uses the package’s `fly-settings` command. You’ll need a signed-in `flyctl` and an app on Fly with one Machine running an image pinned by digest in the Fly registry. Use `flyctl machines list --app "$FLY_APP"` to find the Machine ID.

First review the order in ConfigHub. When you approve it, note the new production revision from `cub unit get --space rails-shop-live app -o jq=.Unit.HeadRevisionNum`. Set `FLY_APP`, `MACHINE`, `HUB_CONTEXT`, `ORDER` (the full order name), and `REVISION` to the values for this app. Keep using the same `CUB_CONFIG` as above.

```sh
"$MINI/bin/fly-settings" apply --cub "$MINI/bin/cub" \
  --app "$FLY_APP" --machine "$MACHINE" \
  --context "$HUB_CONTEXT" --space rails-shop-live \
  --order "$ORDER" --revision "$REVISION" \
  --keys APP_BANNER,APP_SUPPORT_HOURS,RAILS_LOG_LEVEL
```

The command checks the approval before contacting Fly. It changes only the named settings and adds the ConfigHub revision number. It keeps the image and starts the Machine if it was stopped. Use `compare` in place of `apply` to check the Machine without changing it. Open the app afterward to see what it serves.

To go back, propose the old settings as a new change. Wait for approval, then use the new order and revision in the same command. Anyone with Fly deploy access can still deploy directly; this check applies only to this command.

## Testing

An early test used a disposable local hub to store the two apps’ settings. One change moved both staging copies from revision 2 to 3. Two Rails processes running locally read the staging settings and served `Daily`, with their own banners and log levels. Both hub production copies stayed at revision 2 and orders still waited for the owner. The starter check also caught three planted faults.

On 15–16 November, both Fly staging apps served `Daily` from revision 3. We then checked production with separate approvals for the update and rollback:

| What Fly served | Shop | Cart |
| --- | --- | --- |
| While the update waited | Weekdays | Weekdays |
| After update approval and delivery | Daily (revision 3) | Daily (revision 5) |
| While the rollback waited | Daily | Daily |
| After rollback approval and delivery | Weekdays (revision 4) | Weekdays (revision 6) |

The shop kept `coral` and `info`; the cart kept `indigo` and `warn`. The delivery command refused pending orders. It delivered the cart update and both rollbacks without changing the image. The final cart rollback ran from the Mac archive built for the next release, before it was published. We removed all four test apps and the local hub.

The run used one Fly Machine per app and a local hub. It did not test a shared hub or a group of Machines.
