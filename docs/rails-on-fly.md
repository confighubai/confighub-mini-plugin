# Rails on Fly

Connect a Rails app that already runs on Fly. Give your agent a staging copy of its settings and review what goes to production.

## Connect and approve with two commands

You need Claude Code with the [ConfigHub plugin](../README.md#install) 0.97.0 or later, a signed-in `flyctl`, and a `fly.toml` naming your Fly app. Use a disposable app with one Machine, a Fly registry image pinned by digest, and a readable, non-secret setting such as `APP_SUPPORT_HOURS`. If the Machine uses a tag, see [how to pin its image](#pin-the-fly-machine-image).

1. **Connect.** In the app folder in Claude Code, type `/confighub:staging`. ConfigHub installs and starts the local hub if needed. **Start a new Claude Code session in the same folder** to pick up the agent’s key.
2. **Ask for a change.** “Set `APP_SUPPORT_HOURS` to `Daily` in staging. Propose the same change for production and show me the approval command.” This updates the hub’s staging settings. The running Fly app still serves its old value.
3. **Review and deliver.** In your own terminal, paste the printed approval command, such as `~/.confighub/mini/cub mini approve SPACE/ORDER`. On the first delivery you’ll confirm two things:
   - **Approve the change.** Check the old and new values.
   - **Authorize delivery.** Check the Fly app name. That permission applies to future delivery to the same app. Each production change still needs approval.

When the command reports **Live on Fly**, check the new value in the running app. The sample Rails app exposes it at `/api/settings`. See [what ran on Fly](#testing).

### Pin the Fly Machine image

Run `flyctl machines list --app APP --json` to find the Machine ID, image repository, and `image_ref.digest`. Pin the image the Machine already runs with `flyctl machine update MACHINE --app APP --image registry.fly.io/IMAGE_REPOSITORY@DIGEST`. Use the full digest, starting with `sha256:`. Delivery expects one Machine without extra containers or processes.

## Use the starter for two Rails apps

Suppose a shop and a cart use the same support hours. Each has its own banner, and the cart needs quieter logs. Start the cart from the shop’s setup, then change the hours once and see it in both staging copies.

Use the [current local hub package](install-mini.md#the-current-release). The local example uses Python 3 and Docker.

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

`cub mini waiting` shows the exact ConfigHub orders and the commands the owner can use to review each. Leave them pending for this exercise. When you approve one, the same command sends the approved settings to the app's Fly Machine, as [the next section](#send-approved-settings-to-an-app-on-fly) shows. ConfigHub does not block a direct Fly deploy by someone with Fly credentials.

When done, remove the disposable hub with `cub mini uninstall --name rails-fly-example --delete-data`.

## Send approved settings to an app on Fly

With a signed-in `flyctl` and an app on Fly with one Machine, approving is enough. Run this in your own terminal:

```sh
cub mini approve rails-shop
```

When the shop's folder has a `fly.toml`, the approval carries on: it finds the app's one Machine, sends production's approved settings to it, and prints what is now live. The first time, it asks once whether approved settings should go to the Fly app named in `fly.toml` from now on. Credentials and `secret://` settings are left on Fly as they are. `cub mini deliver rails-shop` sends production's approved settings again, and `cub mini deliver rails-shop --compare` checks the Machine without changing it. `--no-deliver` approves only.

### With explicit flags, for a delivery service

A delivery service that signs in with a reader key, rather than as you, runs the program with every value given. This step needs a build with `bin/fly-settings`, a signed-in `flyctl`, and a test app on Fly with one Machine running an image pinned by digest in the Fly registry. Use `flyctl machines list --app "$FLY_APP"` to find the Machine ID.

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

**Published mini.15 and plugin 0.97.0, 17 November 2026.** A disposable Rails app ran on one Fly Machine. The initial Fly deploy used an image tag, so we pinned that Machine to the digest of its running image before connecting. We called the published plugin’s staging command directly with a clean ConfigHub setup. It downloaded mini.15 for macOS arm64, started a local hub, and imported the Machine’s readable settings.

- A scoped key set the hub’s staging support hours to `Daily` and proposed the production change. The hub refused approval from that key, delivery refused the pending order, and the Rails endpoint still served `Weekdays`.
- The owner approved the change and authorized delivery in two separate confirmations through a temporary browser helper that displayed the CLI’s prompts. The published flow asks for both confirmations in the owner’s terminal.
- The Machine reported approved revision 3 and kept its ID and image digest. The Rails endpoint served `Daily` and kept the `coral` banner and `info` log level. We removed the Fly app and local hub. This run covered one production change. The two-app and rollback results below come from separate runs.

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
