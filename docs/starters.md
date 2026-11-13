# Starters: the settings a kind of app starts with

A starter gives any kind of app a good starting setup, much like Spring Boot's starters. It is one short file, written for one kind of app, that lists the settings an app of that kind should start with, a value for each, and the reason for that value. When you connect an app of that kind to a hub, the app gets those settings, except where you have set a value yourself. A starter is easy to make: you can read one in a minute, there is no program to write, and one command checks it before anyone uses it. When your team fixes a setting, the fix becomes the starter's next version, so every new app starts with it. AI agents given this guide and nothing else wrote working starters, including one for a hosting service that confighub mini did not support.

ConfigHub keeps your apps' settings, with every change, who made it and why, and holds a change to production until a person approves it. A hub is one running ConfigHub server. It can run on your own computer, as confighub mini, or be shared by a team on a network; this page uses confighub mini. This page is for someone who gives each new app of one kind the same settings by hand: a time limit, a cache time, two instances, nothing public.

To run the whole loop in a few minutes, a reviewer's fixes becoming the starter's next version, follow the walkthrough [each fix becomes where the next app starts](../examples/walkthroughs/story-25-alice-bob-hardened.md).

Starters are an option, switched off unless you switch them on. They come with confighub mini from 0.10.7-mini.21; the output on this page is from 0.10.7-mini.23.

You need an unpacked confighub mini package ([install confighub mini](install-mini.md)), a terminal, and Python 3 for the Vercel and author's-kit examples. Everything runs on your machine; no account is used and nothing is sent anywhere.

## Words used on this page

- **A hub** is one running ConfigHub. `cub` is ConfigHub's command-line tool, and `cub mini` is the set of commands confighub mini adds to it.
- **Connecting an app** is running `cub mini adopt FOLDER`. It reads the app's settings files (such as `.env`, `.env.staging` and `.env.production`) and keeps three copies of the settings in the hub: **the base**, the shared settings, where a change is made once; **staging**, which gets a change to the base at once; and **live**, the copy for production, which gets a change only when you approve it. Your files are not changed.
- **A change order** is a proposed change that waits until a person approves it with `cub mini approve`, or refuses it. Most change orders are for the live copy; the ones in [keep a starter in your hub](#keep-a-starter-in-your-hub-with-versions-you-approve) are for a starter.
- **A Space** is a folder in the hub, and **a Unit** is one piece of configuration in a Space. A name such as `menu-live` is a Space; a name such as `pattern-web/web-service` is the Unit `web-service` in the Space `pattern-web`.
- **A revision** is one saved state of a Unit. The hub numbers every change to a Unit as its next revision. A starter's **version** is the number in its own file. They are counted separately.

## What a starter is

A starter is one short YAML file for one kind of app. It says three things:

- how to recognize that kind of app from the files in its folder, such as `package.json` and `.env`;
- the settings an app of that kind should have, with a value and a reason for each;
- what else to set up: production behind your approval, always; and, for an app that a hosting service such as Vercel runs, what delivers production's settings there. On this page such a service is called a **provider**.

Here is a starter for a team's Node APIs:

```yaml
starter: team-api
version: 1
about: One of the team's Node APIs, with its settings in .env.
after: [web]
looks_for:
  files: [package.json, .env]
owns: [API_]
defaults:
  - key: API_TIMEOUT_SECONDS
    value: "10"
    reason: A request stops after ten seconds, so one slow caller cannot hold every worker.
  - key: API_CACHE_SECONDS
    value: "60"
    reason: Answers are cached for a minute, so a change is seen within a minute.
wires:
  approval: live
```

`owns` lists the settings the starter may set: here, every setting whose name starts with `API_`. `wires` says what else to set up; `approval: live` is in every starter and means that the live copy gets a change only when a person approves it. `after: [web]` is explained in [two starters on one app](#two-starters-on-one-app).

A starter holds no program, no template and no expression: what it sets is written in it. A starter for a provider names a separate program, an add-on, which does the delivering ([a new provider](#a-new-provider-an-add-on-and-a-starter)). Its fields:

| Field | What it holds |
|---|---|
| `starter` | Its name: lowercase letters, digits and dashes. |
| `version` | A whole number. Raise it when you change the file. |
| `about` | One line: the kind of app it is for. |
| `looks_for` | What must be in the app's folder for the starter to fit: `files` (all of these), `any_file` (one of these), `files_matching` (a name pattern such as `*.tfvars`), `absent` (none of these), `keys` (a key a settings or JSON file must set), `provider` (an add-on's name, below), or `gitops` (`argocd` or `flux`). |
| `owns` | The settings it may set: the start of their names, ending in `_`, `/`, `.` or `-`, such as `API_`, or whole names, such as `PORT`. |
| `defaults` | Each setting it sets: `key`, `value` (in quotes when it is a number or `true`), and `reason`. |
| `describes` | One line for each setting it owns and gives no default, such as `SITE_URL`, which each site sets for itself. |
| `wires` | `approval: live`, always. A starter for a provider adds `reader: live`, a key that can only read production, and `delivery: {addon: NAME, target: TARGET}`, the add-on that delivers and the provider's environment it delivers to, such as `production`. |
| `after` | Optional: one starter, written as a list of one, such as `[web]`, whose settings this one's go on top of. Where both set a value, this one's wins. |

`cub mini adopt` refuses a file that breaks a rule before it writes anything, and names the rule it breaks: a setting without a reason, a setting it does not own, or a default that looks like a password, for example.

## Where the idea comes from

Starters borrow their main ideas from [Spring Boot](https://spring.io/projects/spring-boot)'s starters and its [auto-configuration](https://docs.spring.io/spring-boot/reference/features/developing-auto-configuration.html), and we are grateful to the Spring team for them. Here is what each idea became:

| In Spring Boot | In a ConfigHub starter |
|---|---|
| A starter: one dependency that brings what a kind of app needs | One file that gives a kind of app the settings it needs |
| Auto-configuration applies only when its conditions hold, such as a class being on the classpath | `looks_for`: the files a folder must have for the starter to fit |
| Back-off: a bean or property you define yourself wins over the default | Your values win: a value you already set is never replaced |
| Ordering between auto-configurations (`@AutoConfigureAfter`) | `after:`, the starters this one comes after |
| The condition evaluation report, which says why each auto-configuration did or did not apply | `cub mini adopt` lists every starter it considered and why each one did or did not fit |
| Configuration properties under a prefix, each one described | `owns:`, the prefix of the settings a starter may set, and a reason for each value |

Two things are different. Spring Boot applies its auto-configuration every time an app starts; a starter writes its settings once, when you connect the app, and after that the hub holds them, so a new version of the starter comes to an app as a proposal, never as a rewrite. And because production's copy changes only when a person approves it, a starter can set up production's settings but cannot change them on its own.

## Switch starters on

`cub mini adopt` uses starters only when you switch them on, with the environment variable `CUB_MINI_STARTERS=on`, or when your hub already keeps starters in a Space named `starters`. Otherwise it connects an app as [an app you already have](journeys/existing-app.md) shows.

The package has five starters: `web`, for a small web service with a `.env`, `app.env` or compose file; `vercel`, for an app on Vercel; `parameter-store`, for an app that reads AWS Parameter Store; and `kustomize-argocd` and `kustomize-flux`, for a Kustomize repository that Argo CD or Flux deploys. The `vercel` and `parameter-store` starters run only against a stand-in: a small program in the package that answers as Vercel or AWS would, and keeps the settings in a local file. They use no account.

In a terminal, with `MINI` the folder of the unpacked package, such as `~/.confighub/mini/confighub-mini-0.10.7-mini.23-darwin-arm64`:

```bash
export PATH="$MINI/bin:$PATH"
export CUB_MINI_STARTERS=on
```

The steps below also need a hub. If none is running, start one with `cub mini install` ([install confighub mini](install-mini.md)). The first `cub mini adopt` with starters on puts the package's five starters into your hub, as version 1, and prints the one line that approves them; until you run it, adopt uses the package's own files. After that the hub is where adopt reads starters from, and no folder is needed. To switch starters off again, `unset CUB_MINI_STARTERS` and delete the Space with `cub space delete starters --recursive`; apps you connected keep the settings they have.

## Connect a small web service

The whole path for this starter, from connecting the app to moving it to a shared hub and deleting it, is one page with every command: [the web starter's walkthrough](../examples/walkthroughs/starter-web.md).

The folder `menu` holds a small web service's settings. To make it:

```bash
mkdir menu
printf 'PORT=5000\nLOG_LEVEL=warn\nMENU_SOURCE=kitchen.json\n' > menu/.env
printf 'MENU_SOURCE=kitchen-staging.json\n' > menu/.env.staging
printf 'LOG_LEVEL=error\n' > menu/.env.production
```

1. See what adopt would do, without changing anything:

   ```bash
   cub mini adopt menu --dry-run
   ```

   With starters on, the output starts with each starter it considered, and why it fits or not. A test that "did not hold" is the first thing the starter looks for that the folder lacks:

   ```
   Starters considered: 5, each with the first test that did not hold, or why it was chosen.
     kustomize-argocd, version 1: does not fit: none of kustomization.yaml, base/kustomization.yaml.
     kustomize-flux, version 1: does not fit: none of kustomization.yaml, base/kustomization.yaml.
     parameter-store, version 1: does not fit: no --provider-root: a parameter-store starter runs only against a marked stand-in.
     vercel, version 1: does not fit: no .vercel/project.json: the folder is not linked to a vercel project.
     web, version 1: fits, and is the one used: .env is there.
   …
   ```

   The rest of the output is the plan shown in the next step, and ends by saying that nothing was changed.

2. Connect it:

   ```bash
   cub mini adopt menu
   ```

   The first lines are the plan, printed before anything is written:

   ```
   Starter: web (version 1, web.yaml): A small web service whose settings are in a .env, app.env or compose file, made from adopt's starter pattern.
     It fits: .env is there.
     Sets REPLICAS=2, as a setting: Two instances, so that one can restart without the service going down.
     Sets RELEASE=none, as a setting: Nothing is released until a copy names a release.
     Sets PUBLIC=false, as a setting: A service is private until someone decides it is public.
     Leaves PORT alone: it is set already, PORT=5000, by you, in .env.
     Leaves LOG_LEVEL alone: it is set already, LOG_LEVEL=warn, by you, in .env.
     Leaves LOG_LEVEL alone in live: it is set already, LOG_LEVEL=error, by you, in .env.production.
     Wires: puts menu-live behind your approval, as adopt does; delivery is left to you.
   …
   ConfigHub now keeps menu's settings, from .env, with .env.staging for staging and .env.production for production. Your files are unchanged.
   …
     Production has its own settings from .env.production: LOG_LEVEL=error. The shared settings reach production only after you approve them: run cub mini waiting.
   …
   ```

   The starter added three settings, each with its reason. It left your port and your two log levels alone, and said who set each one and where. `delivery is left to you` means the starter sets up nothing that sends production's settings anywhere; you run the app from them as you do now.

   The `web` starter is the one `cub mini adopt` has always used, written as a starter file. The hub keeps its settings in the Unit `pattern-web/web-service`, which the output calls a starter pattern, and the app's copies are made from it.

3. Approve production's settings. This is the only approval the app needs. Adopt named the waiting change order `menu-base/adopt`; `cub mini waiting` lists every change order that waits.

   ```bash
   cub mini approve menu-base/adopt
   ```

   It shows what production would get and asks you first:

   ```
   A change to production waits for your approval: menu's settings, from .env, with .env.staging for staging and .env.production for production. It was made just now; its name is menu-base/adopt.
     Approving it changes production:
       PORT: 8080 → 5000
       MENU_SOURCE: (not set) → kitchen.json
     Production keeps its own value for these, so approving does not change them there:
       LOG_LEVEL=error
   …
   Approved menu-base/adopt.
   ```

   Until you approved, production held the starter's settings, including its usual `PORT=8080`, and its own log level. Approving gave it your shared values, `PORT=5000` and `MENU_SOURCE`, and production kept its own `LOG_LEVEL=error`.

`cub mini receipts menu --setup` shows each setting, who set it, and why, as the hub holds it:

```
  Starter: web, version 1, connected menu; its defaults are kept in pattern-web/web-service, which the app is made from.
    LOG_LEVEL=warn in menu-base and menu-staging: the starter backed off: set by a person in the app's own file, .env.
    LOG_LEVEL=error in menu-live: the starter backed off: set by a person in the app's own file, .env.production.
    PORT=5000 in menu-base, menu-live and menu-staging: the starter backed off: set by a person in the app's own file, .env.
    PUBLIC=false in menu-base, menu-live and menu-staging: set by the starter web, version 1: A service is private until someone decides it is public.
…
```

"The starter backed off" means it left a value alone because a person had set it.

## Connect an app on Vercel: one command and one approval

For an app that a provider runs, the starter also sets up what delivers production's settings to the provider. Here the provider is the package's Vercel stand-in, which keeps a project's settings in a file and needs no Vercel account.

The folder `shop` is linked to a Vercel project: its `.vercel/project.json` names the project, and its `.env` sets `LOG_LEVEL=warn`. The folder `shop-project` is the stand-in project. It holds `SHOP_CURRENCY=EUR` for Vercel's preview environment, which becomes staging, and for production, and `EDGE_REGION=fra1` for production only. To make both folders:

```bash
mkdir -p shop/.vercel shop-project/bin
printf '{"projectId":"prj_shop","orgId":"team_shop"}\n' > shop/.vercel/project.json
printf 'LOG_LEVEL=warn\n' > shop/.env
printf 'ConfigHub CLI contract stand-in v1\n' > shop-project/.vercel-contract-stand-in
cp "$MINI/examples/extensions/delivery/vercel-standin" shop-project/bin/vercel
cat > shop-project/state.json <<'EOF'
{"envs": [
 {"id": "env_currency_preview", "key": "SHOP_CURRENCY", "value": "EUR", "type": "encrypted", "visibility": "config", "target": ["preview"]},
 {"id": "env_currency_production", "key": "SHOP_CURRENCY", "value": "EUR", "type": "encrypted", "visibility": "config", "target": ["production"]},
 {"id": "env_region_production", "key": "EDGE_REGION", "value": "fra1", "type": "encrypted", "visibility": "config", "target": ["production"]}],
 "writes": 0, "redeploys": 0,
 "deployments": {"preview": {"SHOP_CURRENCY": "EUR"}, "production": {"SHOP_CURRENCY": "EUR", "EDGE_REGION": "fra1"}}}
EOF
```

The file `.vercel-contract-stand-in` marks the folder as a stand-in; the add-on refuses to write to a folder without it. `state.json` is where the stand-in keeps the project's settings.

1. Read the project's settings into the app's folder, with the Vercel add-on, a small program in the package that moves settings between a hub and Vercel. `VERCEL_STANDIN_AUTH=owner` signs in to the stand-in as its owner; the other options name the stand-in's folder, the app's folder, and the project:

   ```bash
   VERCEL_STANDIN_AUTH=owner python3 "$MINI/examples/extensions/delivery/vercel.py" import --provider-root shop-project --dir shop --project prj_shop --scope team_shop --deployment shop.vercel.invalid
   ```

   It writes `shop/.env.staging` from the project's preview settings and `shop/.env.production` from its production settings, and prints `Imported environment files; owner can now run cub mini adopt.`

2. Connect the app. This is the one command:

   ```bash
   cub mini adopt shop --provider-root shop-project
   ```

   ```
   Starter: vercel (version 1, vercel.yaml): An app deployed by Vercel, whose settings are its project's environment variables.
     It fits: .env.production is there; .vercel/project.json links a vercel project, and shop-project is its stand-in.
     Sets EDGE_CACHE_SECONDS=60, as a setting: Pages are cached at the edge for a minute, so a change to a setting is seen within a minute of delivery.
     Sets EDGE_REGION=iad1 (not in live, which set it already), as a setting: Functions run in Vercel's default region, stated so that a copy cannot move away from its database unnoticed.
     Sets EDGE_MAX_DURATION=10, as a setting: A function stops after ten seconds, the Hobby plan's limit, so a slow request fails the same way in every copy.
     Leaves EDGE_REGION alone in live: it is set already, EDGE_REGION=fra1, by you, in .env.production.
     Wires: puts shop-live behind your approval, and opens the order shop-live/connect that you approve before anything is delivered.
     Wires: makes the reader key shop-delivery, which can read shop-live and nothing else, for delivery.
     Wires: names the vercel add-on as what delivers shop-live to production: after you approve, its apply reads the approved revision with the reader key.
   …
     Production has what the folder held. It is not delivered until you approve the order shop-live/connect: cub mini approve shop-live/connect
   …
   ```

   The starter set three settings, each with its reason. It set the region `iad1` in the base and staging, and left production's region in Frankfurt (`fra1`), as the project had it. It also made a reader key, a sign-in that can read production and nothing else, for the add-on to deliver with, and opened a change order, `shop-live/connect`, for your approval.

3. Approve production. This is the one approval:

   ```bash
   cub mini approve shop-live/connect
   ```

   ```
   A change to production waits for your approval: Connect the existing app without changing its running configuration. It was made just now; its name is shop-live/connect.
     It changes no setting. Once you approve it, production can be delivered as it is now: revision 4 of app.
   Approved shop-live/connect. Production can now be delivered as it was when you read it.
   ```

   `app` is the Unit that holds the app's settings in each copy, and revision 4 is the state of production you read and approved.

4. Deliver it. Adopt wrote the reader key to `~/.confighub/keys/shop-delivery.jwk`. The first command signs in with it, in a `cub` configuration of its own (`CUB_CONFIG`), so that the add-on runs with that key and not yours. The second applies the approved revision to the stand-in project:

   ```bash
   CUB_CONFIG="$PWD/reader-shop" cub auth login --new-context --private-key="$HOME/.confighub/keys/shop-delivery.jwk" --server "$(cub context get -o jq=.coordinate.serverURL)" > /dev/null
   CUB_CONFIG="$PWD/reader-shop" VERCEL_STANDIN_AUTH=owner python3 "$MINI/examples/extensions/delivery/vercel.py" apply --provider-root shop-project --target production --space shop-live --unit app --project prj_shop --scope team_shop --deployment shop.vercel.invalid --dir shop --receipt shop-receipt.json
   ```

   ```
   {"contract": "confighub.delivery-receipt/v1", "provider": "vercel-cli-stand-in", "target": "production", "space": "shop-live", "unit": "app", "revision": 4, "sha256": "9e14d628498ddd2060156dcbea4fe04a73a57abd62b64efe9250ebe90f193277", "result": "applied"}
   ```

   The output is the add-on's receipt: it read revision 4 of production, the one you approved, and applied it to the stand-in. `sha256` is a fingerprint of what it delivered. The stand-in project's production in `shop-project/state.json` now holds the currency and region it had, your log level, and the starter's cache time and time limit. Nothing was sent to Vercel.

## What a starter never does

- **It never replaces a value you set.** A value in the app's files, or one someone set in the hub, stays as it is. The plan says each value it left alone, who set it and where.
- **It never writes again on its own.** A starter writes when the app is connected, and when you take a newer version of it, and at no other time. Connecting the same app again writes nothing, and says so: `Starter: menu was connected with web, version 1, already; connecting it again writes nothing.` A later change you or an agent make to the app is never redone or undone by the starter.
- **It never delivers production without you.** Production is behind your approval in every starter. A starter that delivers to a provider opens a change order that waits for you before anything is delivered.
- **It never holds a password.** A default that looks like a password, a token or a key is refused before anything is written.

After a starter has written its settings, they belong to you and your team, to change with `cub` like any other setting. A newer version of the starter changes only a value that still holds the starter's earlier value.

## Keep a starter in your hub, with versions you approve

A starter file on one person's machine is easy to change by accident, and each person may have a different copy. You can keep it in the hub instead, so that everyone connects apps with the same one, and each version of it is one you approved.

1. Switch starters on with `export CUB_MINI_STARTERS=on` and run `cub mini adopt` once, as [above](#switch-starters-on) says. The hub then has the Space `starters`, the rule `workflows/starters-approval` that names you as the approver, and the package's starters as version 1. Approve them with the line adopt printed, which looks like this:

   ```bash
   cub variant approve starters --change-order starters/package-starters-v1 --note "Read them"
   ```

   It prints `Recorded pass Approval attestation … in starters`. An attestation is ConfigHub's record of an approval: who gave it, with the note, for which revision. From now on, `cub mini adopt` uses the starters the hub holds and needs no folder.

2. Put your team's starter in the hub. Write `team-api.yaml` anywhere, as above, then three ordinary `cub` commands: put the file in as a Unit of data, propose it as version 1 with a change order, and approve it:

   ```bash
   cub unit create --space starters team-api team-api.yaml --toolchain AppConfig/YAML --change-desc "The team's starter for its APIs, version 1"
   cub changeorder create --space starters team-api-v1 --in-scope-space starters --change-workflow workflows/starters-approval --description "Version 1 of the team-api starter"
   cub variant approve starters --change-order starters/team-api-v1 --note "Read it: the team's settings for an API"
   ```

   The starter is kept as data, so one default and its reason can be read, changed and asked about with `cub`: `cub unit list --space starters --where-data "defaults.*.key = 'API_TIMEOUT_SECONDS'"` names the starters that set that key.

3. Connect an app. The folder `orders` has a `package.json`, a `.env` with `LOG_LEVEL=warn` and `API_CACHE_SECONDS=30`, and a `.env.production` with `LOG_LEVEL=error`:

   ```bash
   mkdir orders
   printf '{"name":"orders","version":"1.0.0"}\n' > orders/package.json
   printf 'LOG_LEVEL=warn\nAPI_CACHE_SECONDS=30\n' > orders/.env
   printf 'LOG_LEVEL=error\n' > orders/.env.production
   cub mini adopt orders
   ```

   ```
   Starter: team-api (version 1, starters/team-api revision 2): One of the team's Node APIs, with its settings in .env.
     Kept in the hub: version 1 is starters/team-api revision 2, approved by admin@local.confighub.dev.
     It fits: package.json is there; .env is there.
     Sets API_TIMEOUT_SECONDS=10, as a setting: A request stops after ten seconds, so one slow caller cannot hold every worker.
     Leaves API_CACHE_SECONDS alone: it is set already, API_CACHE_SECONDS=30, by you, in .env.
     Wires: puts orders-live behind your approval, as adopt does; delivery is left to you.
     Order: web (version 1, web.yaml), then team-api: team-api is after web, so its defaults go on top of web's; it fits this app too.
     Sets PORT=8080, by web: Every small web service listens on one port, the same in every copy.
     Sets REPLICAS=2, by web: Two instances, so that one can restart without the service going down.
     Sets RELEASE=none, by web: Nothing is released until a copy names a release.
     Sets PUBLIC=false, by web: A service is private until someone decides it is public.
     Leaves LOG_LEVEL alone for web: it is set already, LOG_LEVEL=warn, by you, in .env.
     Leaves LOG_LEVEL alone for web: it is set already, LOG_LEVEL=error, by you, in .env.production.
   …
   ```

   The starter came from the hub: its version 1 is revision 2 of the Unit `starters/team-api`. Both starters set settings here, as [two starters on one app](#two-starters-on-one-app) explains; `web` left the log level alone in the base and in production. The `admin@local.confighub.dev` it names is the sign-in that `cub mini install` makes for you. Approve production's settings with `cub mini approve orders-base/adopt`, as for the menu service.

### How a team's fixes become the next version

Say the team finds that every API should refuse a request larger than 64 KiB. Someone adds that setting with its reason under `defaults`, raises `version` to 2, and proposes it in the hub. The new default, in the starter file:

```yaml
  - key: API_MAX_REQUEST_BYTES
    value: "65536"
    reason: A request larger than 64 KiB is refused before it is read, which stopped last month's flood of oversized uploads.
```

```bash
cub unit update --space starters team-api team-api-v2.yaml --change-desc "Version 2: a limit on request size"
cub changeorder create --space starters team-api-v2 --in-scope-space starters --change-workflow workflows/starters-approval --description "Version 2 of the team-api starter"
cub variant approve starters --change-order starters/team-api-v2 --note "Read it: every API should refuse oversized requests"
```

To change one default that exists, with its reason, one command is enough, because the starter is data: `cub function set --space starters --unit team-api --toolchain AppConfig/YAML --change-desc WHY -- set-yq '.version = 2 | (.defaults[] | select(.key == "API_TIMEOUT_SECONDS") | .value) = "5"'`. Then the change order and approval are the same two lines.

Anyone the hub lets change the Space `starters` can propose a version. Only a person the rule names can approve it, and an agent's key never can.

**The next app starts from version 2.** A new app, `billing`, with a `package.json` and a `.env` that sets `LOG_LEVEL=info`, connected after the approval, gets the new setting with no one typing it:

```
Starter: team-api (version 2, starters/team-api revision 3): One of the team's Node APIs, with its settings in .env.
…
  Sets API_MAX_REQUEST_BYTES=65536, as a setting: A request larger than 64 KiB is refused before it is read, which stopped last month's flood of oversized uploads.
…
```

**An app connected earlier takes version 2 and keeps its own values.** Running `cub mini adopt orders` again offers it the new version:

```
Starter: team-api, version 2, is newer than version 1, which orders was connected with. It writes once, in pattern-team-api/team-api-service, what version 2 changes where the Unit still holds the starter's earlier value, and changes no value anyone else set.
  Starter team-api, version 2, wrote API_MAX_REQUEST_BYTES=65536 in pattern-team-api/team-api-service (it held version 1): A request larger than 64 KiB is refused before it is read, which stopped last month's flood of oversized uploads.
  pattern-team-api/team-api-service now holds version 2. orders takes it by cub mini upgrade pattern-team-api/team-api-service --change-desc WHY, which keeps every value set by a person; staging then by cub mini promote orders-staging, and live by a change order you approve.
```

Two Units are involved. `starters/team-api` holds the starter file. `pattern-team-api/team-api-service` holds the settings the starter gives, and every app the starter connects is made from it. Version 2 wrote its new setting into the second; the output ends with the commands that bring it to the app. `WHY` stands for your reason. Run them:

```bash
cub mini upgrade pattern-team-api/team-api-service --change-desc "orders takes version 2 of the team's starter"
cub mini promote orders-staging --change-desc "Staging takes version 2"
```

The base and staging of `orders` now have the new limit. Its own `API_CACHE_SECONDS=30` is still 30. Production gets the new limit only through a change order you approve, as every change to production does; `cub mini receipts orders --setup` names the command that makes it.

**Which app is on which version.** ConfigHub calls each connected app a Component, and records on it the starters it was connected with. One command lists them:

```bash
cub component list -o jq='.[] | "\(.Component.Slug): \(.Component.Annotations["confighub-mini.starter"]) from \(.Component.Annotations["confighub-mini.starter-source"]); order: \(.Component.Annotations["confighub-mini.starter-order"])"'
```

```
…
orders: team-api@2 from starters/team-api@3; order: web@1 then team-api@2
billing: team-api@2 from starters/team-api@3; order: web@1 then team-api@2
```

Both apps are on version 2 of `team-api`, which is revision 3 of the Unit `starters/team-api`, on top of version 1 of `web`.

## Two starters on one app

An app can fit two starters. The `orders` folder above fits both `web`, which looks for a `.env`, and `team-api`, which looks for a `package.json` and a `.env`. Two starters apply to one app only when one names the other in its `after` line. `team-api` says `after: [web]`, so the app takes both: the `web` settings beneath, and the team's on top. The plan's `Order:` line says so, and every setting is credited to the starter that set it (`by web`).

When two starters fit and neither names the other, adopt uses one: a starter that lists files under `files`, which must all be there, wins over one that lists them under `any_file`, which needs only one. A chain of three or more starters, each after the next, is not supported.

## A new provider: an add-on and a starter

To connect apps that a provider the package does not know runs, you write two things, and confighub mini needs no change:

- **An add-on**: a program, in any language, that reads the provider's settings into an app's folder (`import`), delivers one approved revision to the provider (`apply`), and says whether the provider still has the approved settings (`compare`). Beside it is a short declaration, `addon.yaml`: the add-on's name, the file that shows an app's folder is linked to the provider, the file that marks the provider's stand-in, and where it can deliver.
- **A starter** that names the add-on, in `looks_for.provider` and `wires.delivery.addon`, and adds the settings, each with its reason.

Both go in the folder `CUB_MINI_STARTERS` names. Each add-on is a folder in its `addons` folder:

```
my-starters/
  netlify.yaml               the starter
  addons/
    netlify/
      addon.yaml             the add-on's declaration
      netlify                its program: import, apply and compare
```

The package's own Vercel and Parameter Store add-ons are built the same way, in `$MINI/starters/addons`. An add-on takes the provider's credential from the environment of the person who runs it; its declaration names none.

### Check a starter before anyone uses it

The package has a kit for a starter's author, `$MINI/examples/starter-check`, which needs Python 3, with a worked example for Netlify in `example-provider`: a starter and an add-on written in POSIX shell, run against a stand-in. The check reads a starter file as `cub mini adopt` does, tries it on made-up app folders with and without each thing it looks for, and then, on a hub of its own, checks the promises above: it keeps every value a person set, writes once, and changes no value when a newer version arrives. For a starter with an add-on beside it, it also runs the add-on's three commands. Last, it breaks each promise on purpose and checks that it notices.

```bash
cd "$MINI"
examples/starter-check/check examples/starter-check/example-provider/netlify.yaml
```

```
1. The file, read by cub mini's loader
  pass  the loader accepts the file
2. Test worlds
  pass  it fits a stand-in app where everything it looks for is present
  pass  it does not fit when file .env.production is absent
  pass  it does not fit when provider netlify is absent
…
3. The contract, on a hub of the check's own
  pass  a first app is connected with the starter, which writes its defaults into the hub
  pass  cub mini adopt connects the stand-in app with the starter
  pass  connecting keeps every value a person set in the app's files
…
4. The add-on netlify: its three commands, against its stand-in, read with the reader key adopt made
  pass  adopt made the reader key the add-on reads with
  pass  apply delivers the copy's head and writes its receipt
…
   Planted faults; each check must now fail:
  pass  planted: a condition report that differs from what adopt did is caught
  pass  planted: a person's value overwritten by the starter is caught
  pass  planted: the starter's values written again after a change are caught

PASS: netlify is accepted, fits its stand-in app and no other, and keeps the contract, and its add-on keeps the delivery contract.
```

It starts a hub of its own and removes it at the end. "The contract" in its output is the list of promises above; "the delivery contract" is the rules for an add-on's three commands. To check only the file, with no hub, add `--no-hub`. The kit's `README.md` lists what each part checks. The rules for an add-on's three commands are in [the delivery add-on contract](../examples/extensions/delivery/README.md).

## What this does not do yet

- Starters are an experiment. They are off by default, and the format may change in a later release.
- A starter looks for files, file name patterns, keys in a file, a provider's link, or an Argo CD or Flux source. A new kind of thing to look for, or a way of delivering other than an add-on, Argo CD or Flux, needs a change in confighub mini.
- A starter reads an app's settings only from the files `cub mini adopt` reads: `.env` and its staging and production files, `app.env`, a compose file's environment, `.env.example`, and Terraform var files.
- The Vercel and Parameter Store add-ons in the package run only against their stand-ins.

## Undo it

- **Switch starters off:** `unset CUB_MINI_STARTERS`, and `cub space delete starters --recursive` if the hub keeps starters. Apps already connected keep their settings.
- **Change a setting a starter gave:** change it like any other, for example `cub mini set APP KEY=VALUE --change-desc "WHY"`. The starter never sets it again.
- **Disconnect an app:** your files were never changed. `cub mini copy APP --to-dir DIR` writes the hub's copies out as plain files, with the reason for each value. Every way out is in [going back](journeys/going-back.md).
