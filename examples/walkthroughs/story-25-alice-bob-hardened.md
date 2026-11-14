<!-- walkthrough
id: story-25-alice-bob-hardened
starts_with: mini
story: "25. Alice ships it, Bob hardens it: each fix becomes where the next app starts"
needs: [cub mini package]
budget_seconds: 300
-->
# Each fix Bob makes becomes where Alice's next app starts

Alice connects an app her agents built with a starter, the team's default settings for a kind of app, each with its reason. Bob hardens the running app on a key of his own, and the fixes that suit every app become the starter's version 2. Alice's second app starts with them, and her first app takes them while keeping its own values. Alice and Bob are fictional.

## Human

For a person following along in a terminal. Alice is the hub's owner; Bob is a second key on the same hub.

### What you need

An unpacked confighub mini package (from the [releases page](https://github.com/confighubai/confighub-mini-plugin/releases)) on macOS or Linux. confighub mini is a hub, a small ConfigHub server that keeps each setting with who changed it and why, running on your computer only. No Docker, no account.

### Steps

1. Set up a terminal and start a hub. `CUB_MINI_STARTERS=on` switches starters on, with the hub as where they are kept:
   <!-- run: setup -->
   ```sh
   export MINI=/absolute/path/to/unpacked-confighub-mini
   export PATH="$MINI/bin:$PATH"
   export CUB_CONFIG="$HOME/.confighub-walkthrough"
   unset CUB_CONTEXT
   "$MINI/bin/confighub-mini-app" mini install-plugin "$CUB_CONFIG" >/dev/null
   cub mini install --name alice --use --arrival no >/dev/null
   export CUB_MINI_STARTERS=on
   ```

2. The files: `shop`, which Alice's agents wrote, and a copy of the package's `web` starter as a file, for reading (the package's folder is the one in step 1):
   <!-- run: files files -->
   ```sh
   mkdir -p ~/walkthrough/team-starters && cd ~/walkthrough
   cp /absolute/path/to/unpacked-confighub-mini/starters/web.yaml team-starters/
   mkdir shop && printf 'PORT=3000\nLOG_LEVEL=debug\nRELEASE=shop-1.0.0\nDB_POOL_SIZE=5\n' > shop/.env && printf 'LOG_LEVEL=error\n' > shop/.env.production
   ```

3. Alice connects `shop` in one action. The first time, the package's starters go into the hub as version 1, kept as a Component, `starters`, whose approved copy is the Space `starters-approved`; they wait for her, and she reads and approves them, then production's settings. Then she gives Bob a key of his own, which can change shop's base and staging and propose starter versions and production changes, but approve nothing:
   <!-- run: connect -->
   ```sh
   cub mini adopt shop
   cub variant approve starters-approved --all --note "Read them" >/dev/null
   cub mini approve shop-base/adopt --note "What the agents built" --yes >/dev/null
   cub mini require-approval shop --variant live --agent bob >/dev/null
   BOB=$(cub serviceaccount get bob -o jq=.ServiceAccount.UserID)
   cub space update starters-base --permission View:$BOB --permission ViewChildren:$BOB --permission Edit:$BOB --permission EditChildren:$BOB --quiet
   cub space update starters-approved --permission View:$BOB --permission ViewChildren:$BOB --permission Use:$BOB --permission UseChildren:$BOB --quiet
   ```
   ```text
   Starter: your hub keeps no starters, so the package's 5 (kustomize-argocd, kustomize-flux, parameter-store, vercel, web) are now in it, as version 1, waiting for your approval: the Component starters, whose approved Variant is the Space starters-approved. Until you approve them, adopt uses the package's files. Read them with cub unit list --space starters-approved, and approve them, which is for the person to do, not an agent, with:
   …
     Sets REPLICAS=2, as a setting: Two instances, so that one can restart without the service going down.
   …
     Leaves LOG_LEVEL alone: it is set already, LOG_LEVEL=debug, by you, in .env.
     Leaves LOG_LEVEL alone in live: it is set already, LOG_LEVEL=error, by you, in .env.production.
   ```

4. Bob hardens shop on his key, each value with his reason:
   <!-- run: harden -->
   ```sh
   cub --context bob mini set shop LOG_LEVEL=warn --variant base --change-desc "Debug logs carry request bodies; warn keeps what an incident needs." | tail -1
   cub --context bob mini set shop REPLICAS=3 --variant base --change-desc "Three instances, so one can fail during a deploy and two still serve." | tail -1
   cub --context bob mini set shop DB_POOL_SIZE=20 --variant base --change-desc "This shop's database takes twenty connections." | tail -1
   ```
   ```text
   Saved in shop-base, with the reason: Debug logs carry request bodies; warn keeps what an incident needs. A later version of what shop-base is made from will not overwrite this value.
   Saved in shop-base, with the reason: Three instances, so one can fail during a deploy and two still serve. A later version of what shop-base is made from will not overwrite this value.
   Saved in shop-base, with the reason: This shop's database takes twenty connections. A later version of what shop-base is made from will not overwrite this value.
   ```

5. Bob's first two fixes suit every web service; the pool size is shop's alone. The starter is data, so each default is one change in `starters-base`, with his reason, the first raising the version to 2. He asks for them in `starters-approved` with a change order; his own approval is refused, and Alice reads it and approves:
   <!-- run: harden-starter -->
   ```sh
   cub --context bob function set --space starters-base --unit web --toolchain AppConfig/YAML --change-desc "Debug logs carry request bodies; warn keeps what an incident needs." -- set-yq '.version = 2 | (.defaults[] | select(.key == "LOG_LEVEL") | .value) = "warn" | (.defaults[] | select(.key == "LOG_LEVEL") | .reason) = "Debug logs carry request bodies; warn keeps what an incident needs."' >/dev/null
   cub --context bob function set --space starters-base --unit web --toolchain AppConfig/YAML --change-desc "Three instances, so one can fail during a deploy and two still serve." -- set-yq '(.defaults[] | select(.key == "REPLICAS") | .value) = "3" | (.defaults[] | select(.key == "REPLICAS") | .reason) = "Three instances, so one can fail during a deploy and two still serve."' >/dev/null
   cub --context bob changeorder create --space starters-base web-v2 --in-scope-space starters-approved --change-workflow workflows/starters-approved-approval --description "Version 2 of the web starter" >/dev/null
   cub --context bob mini approve starters-base/web-v2 --yes || true
   cub mini approve starters-base/web-v2 --note "Read it: Bob's fixes, for every web service" --yes | tail -1
   ```
   ```text
   Done. Each copy kept its own values.
   cub mini: ConfigHub did not take your approval: only a person named as an approver for starters-approved can approve this change, and bob is not one. Nothing was changed
   ```

6. Alice's second app, `cart`, is born with Bob's fixes:
   <!-- run: second-app -->
   ```sh
   mkdir cart && printf 'PORT=3100\nRELEASE=cart-1.0.0\n' > cart/.env
   cub mini adopt cart
   ```
   ```text
   Starter: web (version 2, starters-approved/web revision 3): A small web service whose settings are in a .env, app.env or compose file, made from adopt's starter pattern.
   …
     Sets LOG_LEVEL=warn, as a setting: Debug logs carry request bodies; warn keeps what an incident needs.
     Sets REPLICAS=3, as a setting: Three instances, so one can fail during a deploy and two still serve.
   ```

7. Every app made from the starter takes version 2 in one command: each app's staging at once, and each app's production by a change order of its own. What waits for Alice on shop keeps production's own log level:
   <!-- run: first-app -->
   ```sh
   cub mini upgrade pattern-web/web-service --change-desc "Version 2 of the web starter: Bob's fixes" --fleet
   cub mini waiting
   ```
   ```text
   2 apps took pattern-web/web-service's version 4.
   …
   Staging took it now: cart, shop.
   …
     Approving it changes production:
       REPLICAS: 2 → 3
       DB_POOL_SIZE: 5 → 20
     Production keeps its own value for these, so approving does not change them there:
       LOG_LEVEL=error
   ```

8. Alice approves shop's production. It has Bob's fixes and still her own log level:
   <!-- run: approve -->
   ```sh
   cub mini approve shop-live --note "Read Bob's fixes" --yes >/dev/null
   cub unit data --space shop-live app
   ```
   ```text
   PORT=3000
   LOG_LEVEL=error
   REPLICAS=3
   …
   DB_POOL_SIZE=20
   ```

### Undo it

`cub mini uninstall --name alice --delete-data`; then delete `~/walkthrough` and `~/.confighub-walkthrough`.

### What you have now

A starter whose version 2 is Bob's fixes with his reasons, approved by Alice; a second app born with them; and a first app that took them with its own values kept: shop's pool size stays its own and is not in the starter, and production's log level stays Alice's. `cub mini receipts shop --setup` lists who set each value and why. The full story adds a customer who runs the app with a hub and the starter inside and keeps their own changes through version 3, and Alice and Bob on two machines with a hub both reach. [Starters](../../docs/starters.md#keep-a-starter-in-your-hub-with-versions-you-approve) covers starters kept in a hub.

## Agent

For an AI agent working as Bob, on Bob's key: run `cub` as `cub --context bob`.

- The request: "Harden shop for production. Debug logs carry request bodies, so LOG_LEVEL should be warn; it needs 3 replicas so one can fail during a deploy; its database takes 20 connections (DB_POOL_SIZE). Then make the fixes that suit every web service version 2 of the team's web starter, each with its reason."
- Set each value on shop's base with its reason: `cub mini set shop KEY=VALUE --variant base --change-desc "WHY"`.
- Make version 2 of the starter: one `cub function set --space starters-base --unit web --toolchain AppConfig/YAML --change-desc WHY -- set-yq '...'` for each default that suits every app (not shop's own `DB_POOL_SIZE`), the first also setting `.version = 2`; then a change order in `starters-base` with `--in-scope-space starters-approved --change-workflow workflows/starters-approved-approval`.
- Never approve the starter or production; tell the person the command that does: `cub mini approve starters-base/NAME` for the starter, and `cub mini approve` for production.
- Done when `cub unit data --space shop-base app` has the three values and the proposed starter has `version: 2` with `warn` and `"3"`.

## Testing

This proves: the settings and the starter's versions were stored in the hub, each value with who set it and why, and production's copy changed only by an approved change order. What was really used: confighub mini on this computer, with Bob as a second key; nothing is delivered and no service runs. A correct agent result has Bob's three values on shop's base and a proposed version 2 of the starter with the two fixes for every app, and without shop's pool size. The step it aims to win: keeping the starter on for the next app. The checks below can be run by hand, in bash, in the walkthrough's folder:

<!-- agent-task: harden after=harden -->
> Harden shop for production. Debug logs carry request bodies, so LOG_LEVEL should be warn; it needs 3 replicas so one can fail during a deploy; its database takes 20 connections (DB_POOL_SIZE). Then make the fixes that suit every web service version 2 of the team's web starter, each with its reason.

<!-- agent-check harden: cub unit data --space shop-base app | grep -qx 'DB_POOL_SIZE=20' && cub unit data --space shop-base app | grep -qx 'REPLICAS=3' && cub unit data --space starters-base web | grep -q '^version: 2' && cub unit data --space starters-base web | grep -q 'value: warn' && ! cub unit data --space starters-base web | grep -q DB_POOL_SIZE -->
<!-- agent-check-a harden: g(){ grep -rlsE "^[ -]*\"?$1\"?[=:] *\"?$2" --exclude-dir='.*' --exclude-dir=Library * .env* 2>/dev/null; }; g DB_POOL_SIZE 20 | grep -q shop && grep -rlsE '^version: 2' --exclude-dir='.*' team-starters | grep -q . && ! grep -rqs DB_POOL_SIZE team-starters -->
<!-- arms: a,b,c -->
<!-- next-step when "did not change": keep the starter on | Your next app can start with Bob's fixes already in place, each with its reason; want the starter kept on for it? -->

```sh
cub unit data --space shop-base app | grep -qx 'DB_POOL_SIZE=20' && cub unit data --space shop-base app | grep -qx 'REPLICAS=3' && cub unit data --space starters-base web | grep -q '^version: 2' && cub unit data --space starters-base web | grep -q 'value: warn' && ! cub unit data --space starters-base web | grep -q DB_POOL_SIZE
g(){ grep -rlsE "^[ -]*\"?$1\"?[=:] *\"?$2" --exclude-dir='.*' --exclude-dir=Library * .env* 2>/dev/null; }; g DB_POOL_SIZE 20 | grep -q shop && grep -rlsE '^version: 2' --exclude-dir='.*' team-starters | grep -q . && ! grep -rqs DB_POOL_SIZE team-starters
```

<!-- results:begin -->

Results, 13 November 2026, a build of confighub mini from main at f699fc25. Figures from this page's own test runs, shown here for whoever checks the page; they are not a promise.

- Scripted run: passed, 104 seconds for the steps, within the page's budget of 300.
- Agent runs: a pilot, 3 runs per arm on each of claude-sonnet-5-5, claude-opus-5-5. Arms: a is ordinary tools only; b is the plugin, confighub mini and this page as reading.

| Arm | Model | Checks passed | Median seconds | Median cost | Commands left for the person (median) |
|---|---|---|---|---|---|
| a | claude-opus-5-5 | 3/3 | 37.5 | $0.184 | 0 |
| b | claude-opus-5-5 | 3/3 | 33.6 | $0.198 | 2 |
| a | claude-sonnet-5-5 | 3/3 | 25.2 | $0.07 | 0 |
| b | claude-sonnet-5-5 | 3/3 | 29.2 | $0.079 | 2 |

No agent approved or refused a change to production.

Simulated persons, not people: 10 per run, each a claude-haiku-5-5 model playing one of ten fixed personas, reading only what a person would see. The next step they were offered: "Your next app can start with Bob's fixes already in place, each with its reason; want the starter kept on for it?"

The plugin offers it once, after the answer at whose end it showed the moment the offer names ("did not change"). Offered is the share of persons it was shown to; want it now and later are over them.

| Arm | Model | Persons | Offered | Noticed | Want the next step now | Later | In the way |
|---|---|---|---|---|---|---|---|
| a | claude-opus-5-5 | 30 | 0% | 100% | n/a | n/a | 60% |
| b | claude-opus-5-5 | 30 | 100% | 100% | 43% | 43% | 80% |
| a | claude-sonnet-5-5 | 30 | 0% | 100% | n/a | n/a | 17% |
| b | claude-sonnet-5-5 | 30 | 100% | 100% | 27% | 57% | 57% |

<!-- results:end -->
