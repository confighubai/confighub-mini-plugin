# Starters: the settings a kind of app starts with

A starter gives any kind of app a good starting setup, much like Spring Boot's starters. It is one short file, written for one kind of app, that lists the settings an app of that kind should start with, a value for each, and the reason for that value. When you connect an app of that kind to a hub, the app gets those settings, except where you have set a value yourself. A starter is easy to make: you can read one in a minute, there is no program to write, and one command checks it before anyone uses it. When your team fixes a setting, the fix becomes the starter's next version, so every new app starts with it.

ConfigHub keeps your apps' settings, with every change, who made it and why, and holds a change to production until a person approves it. A hub is one running ConfigHub server. It can run on your own computer, as confighub mini, or be shared by a team on a network; this page uses confighub mini. This page is for someone who gives each new app of one kind the same settings by hand: a time limit, a cache time, two instances, nothing public.

To run the whole loop in a few minutes, a reviewer's fixes becoming the starter's next version, follow the walkthrough [each fix becomes where the next app starts](../examples/walkthroughs/story-25-alice-bob-hardened.md).

Starters are an option, switched off unless you switch them on. They come with confighub mini ([the current release](install-mini.md#the-current-release)).

You need an unpacked confighub mini package ([install confighub mini](install-mini.md)), a terminal, and Python 3 for the author's kit. Everything runs on your machine; no account is used and nothing is sent anywhere.

The words on this page, such as *hub*, *base* and *change order*, are explained in [the glossary](README.md#words).

**Connecting an app** is running `cub mini adopt FOLDER`: it reads the app's settings files, such as `.env`, `.env.staging` and `.env.production`, and keeps a base, a staging copy and a production copy of them in the hub, without changing your files. A starter's **version** is the number in its own file, and is counted apart from the hub's revisions.

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

In a terminal, with `MINI` the folder of the unpacked package, such as `~/.confighub/mini/confighub-mini-VERSION-OS-ARCH`:

```bash
export PATH="$MINI/bin:$PATH"
export CUB_MINI_STARTERS=on
```

The steps below also need a hub. If none is running, start one with `cub mini install` ([install confighub mini](install-mini.md)). The first `cub mini adopt` with starters on puts the package's five starters into your hub, as version 1, and prints the one line that approves them, which is yours to run, not an agent's, even when an agent ran the adopt; until you run it, adopt uses the package's own files. After that the hub is where adopt reads starters from, and no folder is needed. To switch starters off again, `unset CUB_MINI_STARTERS`, and delete the Component's two Spaces and the Component with `cub space delete starters-approved --recursive`, `cub space delete starters-base --recursive` and `cub component delete starters`; apps you connected keep the settings they have.

## What connecting an app shows

Each starter's walkthrough connects an app with it, delivers it, changes it, undoes the change, moves it to a shared hub and deletes it, with every command and what it prints: [web](../examples/walkthroughs/starter-web.md), [vercel](../examples/walkthroughs/starter-vercel.md), [parameter-store](../examples/walkthroughs/starter-parameter-store.md), [kustomize-argocd](../examples/walkthroughs/starter-kustomize-argocd.md) and [kustomize-flux](../examples/walkthroughs/starter-kustomize-flux.md). This section explains what `cub mini adopt` prints when starters are on.

**Which starter fits, and why.** `cub mini adopt FOLDER --dry-run` starts with each starter it considered, and the first test that did not hold, much as Spring Boot's condition report does:

```
Starters considered: 5, each with the first test that did not hold, or why it was chosen.
  kustomize-argocd, version 1: does not fit: none of kustomization.yaml, base/kustomization.yaml.
  kustomize-flux, version 1: does not fit: none of kustomization.yaml, base/kustomization.yaml.
  parameter-store, version 1: does not fit: no --provider-root: a parameter-store starter runs only against a marked stand-in.
  vercel, version 1: does not fit: no .vercel/project.json: the folder is not linked to a vercel project.
  web, version 1: fits, and is the one used: .env is there.
```

**The plan, before anything is written.** Then adopt prints what the starter will do, one line each:

```
Starter: web (version 1, web.yaml): A small web service whose settings are in a .env, app.env or compose file, made from adopt's starter pattern.
  It fits: .env is there.
  Sets REPLICAS=2, as a setting: Two instances, so that one can restart without the service going down.
  Leaves PORT alone: it is set already, PORT=5000, by you, in .env.
  Leaves LOG_LEVEL alone in live: it is set already, LOG_LEVEL=error, by you, in .env.production.
  Wires: puts menu-live behind your approval, as adopt does; delivery is left to you.
```

- `Sets` is a setting the starter gives, with its reason.
- `Leaves ... alone` is a value you set already, with who set it and where. The starter never replaces it.
- `Wires` is what else it sets up. Production is always behind your approval. `delivery is left to you` means it sets up nothing that sends production's settings anywhere; you run the app from them as you do now.

For an app that a provider runs, such as Vercel, the `Wires` lines also say how production is delivered: a change order, such as `shop-live/connect`, that you approve before anything is delivered; a reader key that can read production and nothing else; and the add-on that delivers the revision you approved with that key, and writes a receipt naming it.

The `web` starter is the one `cub mini adopt` has always used, written as a starter file. The hub keeps its settings in the Unit `pattern-web/web-service`, which the output calls a starter pattern, and the app's copies are made from it.

**What the hub holds afterwards.** `cub mini receipts APP --setup` shows each setting, who set it, and why:

```
  Starter: web, version 1, connected menu; its defaults are kept in pattern-web/web-service, which the app is made from.
    LOG_LEVEL=error in menu-live: the starter backed off: set by a person in the app's own file, .env.production.
    PUBLIC=false in menu-base, menu-live and menu-staging: set by the starter web, version 1: A service is private until someone decides it is public.
…
```

"The starter backed off" means it left a value alone because a person had set it.

## What a starter never does

- **It never replaces a value you set.** A value in the app's files, or one someone set in the hub, stays as it is. The plan says each value it left alone, who set it and where.
- **It never writes again on its own.** A starter writes when the app is connected, and when you take a newer version of it, and at no other time. Connecting the same app again writes nothing, and says so: `Starter: menu was connected with web, version 1, already; connecting it again writes nothing.` A later change you or an agent make to the app is never redone or undone by the starter.
- **It never delivers production without you.** Production is behind your approval in every starter. A starter that delivers to a provider opens a change order that waits for you before anything is delivered.
- **It never holds a password.** A default that looks like a password, a token or a key is refused before anything is written.

After a starter has written its settings, they belong to you and your team, to change with `cub` like any other setting. A newer version of the starter changes only a value that still holds the starter's earlier value.

## Keep a starter in your hub, with versions you approve

A starter file on one person's machine is easy to change by accident, and each person may have a different copy. You can keep it in the hub instead, so that everyone connects apps with the same one, and each version of it is one you approved.

1. Switch starters on with `export CUB_MINI_STARTERS=on` and run `cub mini adopt` once, as [above](#switch-starters-on) says. The hub then keeps the starters the way ConfigHub keeps an app: a Component `starters`, whose base, the Space `starters-base`, is where a version is proposed, and whose approved Variant, the Space `starters-approved`, is where a version waits for your approval and is read from. The rule `workflows/starters-approved-approval` names you as the approver, and the package's starters are there as version 1. Approve them with the line adopt printed, which looks like this:

   ```bash
   cub variant approve starters-approved --all --note "Read them"
   ```

   It prints `Recorded pass Approval attestation … in starters`. An attestation is ConfigHub's record of an approval: who gave it, with the note, for which revision. From now on, `cub mini adopt` uses the starters the hub holds and needs no folder.

2. Put your team's starter in the hub. Write `team-api.yaml` anywhere, as above, then three ordinary `cub` commands: put the file in as a Unit of data, propose it as version 1 with a change order, and approve it:

   ```bash
   cub unit create --space starters-base team-api team-api.yaml --toolchain AppConfig/YAML --change-desc "The team's starter for its APIs, version 1"
   cub changeorder create --space starters-base team-api-v1 --in-scope-space starters-approved --change-workflow workflows/starters-approved-approval --description "Version 1 of the team-api starter"
   cub mini approve starters-base/team-api-v1 --note "Read it: the team's settings for an API"
   ```

   The starter is kept as data, so one default and its reason can be read, changed and asked about with `cub`: `cub unit list --space starters-approved --where-data "defaults.*.key = 'API_TIMEOUT_SECONDS'"` names the starters that set that key.

3. Connect an app. The folder `orders` has a `package.json`, a `.env` with `LOG_LEVEL=warn` and `API_CACHE_SECONDS=30`, and a `.env.production` with `LOG_LEVEL=error`:

   ```bash
   mkdir orders
   printf '{"name":"orders","version":"1.0.0"}\n' > orders/package.json
   printf 'LOG_LEVEL=warn\nAPI_CACHE_SECONDS=30\n' > orders/.env
   printf 'LOG_LEVEL=error\n' > orders/.env.production
   cub mini adopt orders
   ```

   ```
   Starter: team-api (version 1, starters-approved/team-api revision 3): One of the team's Node APIs, with its settings in .env.
     Kept in the hub: version 1 is starters-approved/team-api revision 3, approved by admin@local.confighub.dev.
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

   The starter came from the hub: its version 1 is a revision of the Unit `starters-approved/team-api`. Both starters set settings here, as [two starters on one app](#two-starters-on-one-app) explains; `web` left the log level alone in the base and in production. The `admin@local.confighub.dev` it names is the sign-in that `cub mini install` makes for you. Approve production's settings with `cub mini approve orders-base/adopt`.

### How a team's fixes become the next version

Say the team finds that every API should refuse a request larger than 64 KiB. Someone adds that setting with its reason under `defaults`, raises `version` to 2, and proposes it in the hub. The new default, in the starter file:

```yaml
  - key: API_MAX_REQUEST_BYTES
    value: "65536"
    reason: A request larger than 64 KiB is refused before it is read, which stopped last month's flood of oversized uploads.
```

```bash
cub unit update --space starters-base team-api team-api-v2.yaml --change-desc "Version 2: a limit on request size"
cub changeorder create --space starters-base team-api-v2 --in-scope-space starters-approved --change-workflow workflows/starters-approved-approval --description "Version 2 of the team-api starter"
cub mini approve starters-base/team-api-v2 --note "Read it: every API should refuse oversized requests"
```

To change one default that exists, with its reason, one command is enough, because the starter is data: `cub function set --space starters-base --unit team-api --toolchain AppConfig/YAML --change-desc WHY -- set-yq '.version = 2 | (.defaults[] | select(.key == "API_TIMEOUT_SECONDS") | .value) = "5"'`. Then the change order and approval are the same two lines. The approval promotes it into `starters-approved`, the way a change to an app goes from staging to production.

Anyone the hub lets change the Space `starters-base` can propose a version. Only a person the rule names can approve it, and an agent's key never can.

**The next app starts from version 2.** A new app, `billing`, with a `package.json` and a `.env` that sets `LOG_LEVEL=info`, connected after the approval, gets the new setting with no one typing it:

```
Starter: team-api (version 2, starters-approved/team-api revision 4): One of the team's Node APIs, with its settings in .env.
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

Two Units are involved. `starters-approved/team-api` holds the starter file. `pattern-team-api/team-api-service` holds the settings the starter gives, and every app the starter connects is made from it. Version 2 wrote its new setting into the second; the output ends with the commands that bring it to the app. `WHY` stands for your reason. Run them:

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
orders: team-api@2 from starters-approved/team-api@4; order: web@1 then team-api@2
billing: team-api@2 from starters-approved/team-api@4; order: web@1 then team-api@2
```

Both apps are on version 2 of `team-api`, which is a revision of the Unit `starters-approved/team-api`, on top of version 1 of `web`.

**Every app at once.** With many apps made from the starter, one command takes the version through all of them: each app's base takes it, each app's staging takes it at once, and each app's production gets a change order of its own, behind that app's own approval.

```bash
cub mini upgrade pattern-team-api/team-api-service --change-desc "Take version 2 everywhere" --fleet
```

Each app keeps the values it set itself. `cub mini waiting` lists each production order, and approving one reaches that app and no other.

**Which apps are behind.** `cub mini receipts APP --setup` says which apps use the starter at which version, which keys each sets itself, and which are behind the newest version you approved.

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

- **Switch starters off:** `unset CUB_MINI_STARTERS`, and the Component's Spaces (`cub space delete starters-approved --recursive`, `cub space delete starters-base --recursive`, `cub component delete starters`) if the hub keeps starters. Apps already connected keep their settings.
- **Change a setting a starter gave:** change it like any other, for example `cub mini set APP KEY=VALUE --change-desc "WHY"`. The starter never sets it again.
- **Disconnect an app:** your files were never changed. `cub mini copy APP --to-dir DIR` writes the hub's copies out as plain files, with the reason for each value. Every way out is in [going back](journeys/going-back.md).
