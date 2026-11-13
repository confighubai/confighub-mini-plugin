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

1. Set up a terminal and start a hub. `CUB_MINI_STARTERS` switches starters on, naming the team's folder of starter files:
   <!-- run: setup -->
   ```sh
   export MINI=/absolute/path/to/unpacked-confighub-mini
   export PATH="$MINI/bin:$PATH"
   export CUB_CONFIG="$HOME/.confighub-walkthrough"
   unset CUB_CONTEXT
   "$MINI/bin/confighub-mini-app" mini install-plugin "$CUB_CONFIG" >/dev/null
   cub mini install --name alice --use --arrival no >/dev/null
   export CUB_MINI_STARTERS=~/walkthrough/team-starters
   ```

2. The files: the team's starters, beginning with the package's `web` starter (the package's folder is the one in step 1), and `shop`, which Alice's agents wrote:
   <!-- run: files files -->
   ```sh
   mkdir -p ~/walkthrough/team-starters && cd ~/walkthrough
   cp /absolute/path/to/unpacked-confighub-mini/starters/web.yaml team-starters/
   mkdir shop && printf 'PORT=3000\nLOG_LEVEL=debug\nRELEASE=shop-1.0.0\nDB_POOL_SIZE=5\n' > shop/.env && printf 'LOG_LEVEL=error\n' > shop/.env.production
   ```

3. Keep the starter in the hub, so each version of it is one Alice approved. A Space `starters` holds the file; a rule, `workflows/starters-approval`, names Alice as the one whose approval makes a revision a version:
   <!-- run: starter -->
   ```sh
   ME=$(cub user get "$(cub context get -o jq=.coordinate.user)" -o jq=.User.UserID)
   cub space create starters --label Stage=starters >/dev/null
   cub space create workflows --allow-exists >/dev/null
   cub changeworkflow create --space workflows starters-approval --stage starters --attestation-prerequisite approval --attestation-prerequisite-from-users approval=$ME --stage-prerequisites starters=approval >/dev/null
   cub unit create --space starters web team-starters/web.yaml --toolchain AppConfig/Text --change-desc "The team's web starter, version 1" >/dev/null
   cub changeorder create --space starters web-v1 --in-scope-space starters --change-workflow workflows/starters-approval --description "Version 1 of the web starter" >/dev/null
   cub variant approve starters --change-order starters/web-v1 --note "Read it: the team's settings for a web service"
   ```
   ```text
   Recorded pass Approval attestation ID in starters, covering 1 revision(s)
   ```

4. Alice connects `shop` in one action and approves production's settings; the starter fills in what the app does not set. Then she gives Bob a key of his own: it can change shop's base and staging and propose starter versions and production changes, but approve nothing:
   <!-- run: connect -->
   ```sh
   cub mini adopt shop
   cub mini approve shop-base/adopt --note "What the agents built" --yes >/dev/null
   cub mini require-approval shop --variant live --agent bob >/dev/null
   BOB=$(cub serviceaccount get bob -o jq=.ServiceAccount.UserID)
   cub space update starters --permission View:$BOB --permission ViewChildren:$BOB --permission Edit:$BOB --permission EditChildren:$BOB --quiet
   ```
   ```text
   Starter: web (version 1, starters/web revision 2): A small web service whose settings are in a .env, app.env or compose file, made from adopt's starter pattern.
   …
     Sets REPLICAS=2, as a setting: Two instances, so that one can restart without the service going down.
   …
     Leaves LOG_LEVEL alone: it is set already, LOG_LEVEL=debug, by you, in .env.
     Leaves LOG_LEVEL alone in live: it is set already, LOG_LEVEL=error, by you, in .env.production.
   ```

5. Bob hardens shop on his key, each value with his reason:
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

6. Bob's first two fixes suit every web service; the pool size is shop's alone. He writes them into version 2 of the starter, with his reasons, and proposes it. His own approval is refused; Alice reads it and approves:
   <!-- run: harden-starter -->
   ```sh
   sed -e 's/^version: 1/version: 2/' -e 's/value: info/value: warn/' -e 's/reason: Logs say what.*/reason: Debug logs carry request bodies; warn keeps what an incident needs./' -e 's/value: "2"/value: "3"/' -e 's/reason: Two instances.*/reason: Three instances, so one can fail during a deploy and two still serve./' team-starters/web.yaml > web-v2.yaml
   cub --context bob unit update --space starters web web-v2.yaml --change-desc "Version 2: Bob's hardening of shop, for every web service" >/dev/null
   cub --context bob changeorder create --space starters web-v2 --in-scope-space starters --change-workflow workflows/starters-approval --description "Version 2 of the web starter" >/dev/null
   cub --context bob variant approve starters --change-order starters/web-v2 --note "mine" || true
   cub variant approve starters --change-order starters/web-v2 --note "Read it: Bob's fixes, for every web service"
   ```
   ```text
   Failed to approve in starters: permission denied
   …
   Recorded pass Approval attestation ID in starters, covering 1 revision(s)
   ```

7. Alice's second app, `cart`, is born with Bob's fixes:
   <!-- run: second-app -->
   ```sh
   mkdir cart && printf 'PORT=3100\nRELEASE=cart-1.0.0\n' > cart/.env
   cub mini adopt cart
   ```
   ```text
   …
   Starter: web (version 2, starters/web revision 3): A small web service whose settings are in a .env, app.env or compose file, made from adopt's starter pattern.
   …
     Sets LOG_LEVEL=warn, as a setting: Debug logs carry request bodies; warn keeps what an incident needs.
     Sets REPLICAS=3, as a setting: Three instances, so one can fail during a deploy and two still serve.
   ```

8. Shop takes version 2: its base by one upgrade, staging at once, and production by a change order Bob proposes. What waits for Alice keeps production's own log level:
   <!-- run: first-app -->
   ```sh
   cub mini upgrade pattern-web/web-service --change-desc "Version 2 of the web starter: Bob's fixes" >/dev/null
   cub mini promote shop-staging --change-desc "Staging takes Bob's fixes" >/dev/null
   cub --context bob changeorder create --space shop-base hardening --in-scope-space shop-live --change-workflow workflows/shop-live-approval --description "Bob's hardening, and version 2 of the web starter" >/dev/null
   cub mini waiting
   ```
   ```text
   A change to production waits for your approval: Bob's hardening, and version 2 of the web starter. It was made just now; its name is shop-base/hardening.
     Approving it changes production:
       REPLICAS: 2 → 3
       DB_POOL_SIZE: 5 → 20
     Production keeps its own value for these, so approving does not change them there:
       LOG_LEVEL=error
   ```

9. Alice approves. Production has Bob's fixes and still her own log level:
   <!-- run: approve -->
   ```sh
   cub mini approve shop-base/hardening --note "Read Bob's fixes" --yes >/dev/null
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
- Write version 2 of the starter from `cub unit data --space starters web`: raise `version`, change only the defaults that suit every app (not shop's own `DB_POOL_SIZE`), each with its reason. Propose it with `cub unit update --space starters web FILE --change-desc WHY` and a change order under `workflows/starters-approval`.
- Never approve the starter or production; tell the person the commands that do: `cub variant approve starters --change-order starters/NAME`, and `cub mini approve` for production.
- Done when `cub unit data --space shop-base app` has the three values and the proposed starter has `version: 2` with `warn` and `"3"`.

## Testing

This proves: the settings and the starter's versions were stored in the hub, each value with who set it and why, and production's copy changed only by an approved change order. What was really used: confighub mini on this computer, with Bob as a second key; nothing is delivered and no service runs. A correct agent result has Bob's three values on shop's base and a proposed version 2 of the starter with the two fixes for every app, and without shop's pool size. The checks below can be run by hand, in bash, in the walkthrough's folder:

<!-- agent-task: harden after=harden -->
> Harden shop for production. Debug logs carry request bodies, so LOG_LEVEL should be warn; it needs 3 replicas so one can fail during a deploy; its database takes 20 connections (DB_POOL_SIZE). Then make the fixes that suit every web service version 2 of the team's web starter, each with its reason.

<!-- agent-check harden: cub unit data --space shop-base app | grep -qx 'DB_POOL_SIZE=20' && cub unit data --space shop-base app | grep -qx 'REPLICAS=3' && cub unit data --space starters web | grep -q '^version: 2' && cub unit data --space starters web | grep -q 'value: warn' && ! cub unit data --space starters web | grep -q DB_POOL_SIZE -->
<!-- agent-check-a harden: g(){ grep -rlsE "^[ -]*\"?$1\"?[=:] *\"?$2" --exclude-dir='.*' --exclude-dir=Library * .env* 2>/dev/null; }; g DB_POOL_SIZE 20 | grep -q shop && grep -rlsE '^version: 2' --exclude-dir='.*' team-starters | grep -q . && ! grep -rqs DB_POOL_SIZE team-starters -->
<!-- arms: a,b,c -->

```sh
cub unit data --space shop-base app | grep -qx 'DB_POOL_SIZE=20' && cub unit data --space shop-base app | grep -qx 'REPLICAS=3' && cub unit data --space starters web | grep -q '^version: 2' && cub unit data --space starters web | grep -q 'value: warn' && ! cub unit data --space starters web | grep -q DB_POOL_SIZE
g(){ grep -rlsE "^[ -]*\"?$1\"?[=:] *\"?$2" --exclude-dir='.*' --exclude-dir=Library * .env* 2>/dev/null; }; g DB_POOL_SIZE 20 | grep -q shop && grep -rlsE '^version: 2' --exclude-dir='.*' team-starters | grep -q . && ! grep -rqs DB_POOL_SIZE team-starters
```
