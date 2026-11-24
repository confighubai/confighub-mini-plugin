<!-- walkthrough
id: starter-heroku
starts_with: both
starter: heroku   # no starter file: production and staging start from the apps' config vars
needs: [Claude Code with the ConfigHub plugin, cub mini package, Python 3, a hosted ConfigHub organization for step 9]
budget_seconds: 300
-->
# An app on Heroku, with production behind your approval
Connect an app that runs on Heroku as a staging app and a production app in a pipeline. Your agent changes staging, and the change reaches the staging app. A production change waits for you, and approving it puts it live on the production app. This page uses a stand-in for the `heroku` command, so it needs no Heroku account. The [Heroku guide](../../docs/heroku.md) is the short version for your real app.
## Quick start

You need: Claude Code with the [ConfigHub plugin](../../README.md#install), and your app's folder with a Git remote to the Heroku app (`heroku git:remote -a APP`). On a real app, the `heroku` command must be signed in.

| | By hand | Ask your agent |
|---|---|---|
| Connect the app | `/confighub:staging` in the app's folder | You type it yourself. |
| Send staging to the staging app | `cub mini deliver api --staging`, once | "Raise WEB_CONCURRENCY to 8 in staging for the checkout load test." |
| Approve production | `cub mini approve api` | "Raise WEB_CONCURRENCY to 8 in production too. Checkout times out under load." Then you approve it. |
| Undo | `cub mini rollback api --reason "The load test is over"`, then `cub mini approve api` | "Propose putting WEB_CONCURRENCY back. I'll approve it." |

Staging reaches the staging app after your one yes. Production keeps its value until you approve, and credentials and add-on settings stay on Heroku.

Without ConfigHub: your agent runs `heroku config:set` on the staging app and then on the production app, nothing waits for you, and the next session has no record of why.

## Deeper dive

The rest of this page is the full version: every command with what it prints, a stand-in for Heroku so you can try it without an account, the move to a shared hub, what an agent leaves to you, and how this was tested.

<details>
<summary>Show the full walkthrough</summary>

## Human
### What you need
Claude Code with the ConfigHub plugin, an unpacked [confighub mini package](../../docs/install-mini.md), and Python 3. Step 9 needs a sign-in to your organization's shared hub. Sending staging to the staging app (steps 4 and 5) needs confighub mini 0.11.1-mini.32 or later.
### Steps
1. Set up a terminal. `MINI` is the unpacked package. `CUB_CONFIG` gives this walkthrough a `cub` configuration of its own, so your own settings are not touched.
   <!-- run: setup -->
   ```sh
   export MINI=/absolute/path/to/unpacked-confighub-mini
   export PATH="$MINI/bin:$PATH" CUB_CONFIG="$HOME/.confighub-walkthrough"
   unset CUB_CONTEXT
   "$MINI/bin/confighub-mini-app" mini install-plugin "$CUB_CONFIG" >/dev/null
   ```
2. Make the app and a stand-in for Heroku. The stand-in is a small `heroku` command that keeps two apps in files: `shop-api`, production, and `shop-api-staging`, staging, in the pipeline `shop`. Each has three settings and a `DATABASE_URL` that its Postgres add-on sets; production also holds a payment key. The app's folder holds a `Procfile`, no settings file, and the Git remote `heroku git:remote` writes.
   <!-- run: app files -->
   ```sh
   mkdir -p ~/walkthrough/heroku/apps ~/walkthrough/bin ~/walkthrough/api && cd ~/walkthrough
   cat > bin/heroku <<'EOF'
   #!/usr/bin/env python3
   import json, os, sys
   d = os.path.expanduser("~/walkthrough/heroku/apps"); a = sys.argv[1:]
   app = lambda n: json.load(open(f"{d}/{n}.json"))
   name = a[a.index("-a") + 1] if "-a" in a else ""
   if a[0] == "apps:info":
       x = app(name); print(json.dumps({"app": {"name": name, "id": name}, "pipeline_coupling": {"stage": x["stage"], "pipeline": {"id": "shop", "name": "shop"}}}))
   elif a[0] == "config": print(json.dumps(app(name)["config"]))
   elif a[0] == "addons": print(json.dumps([{"config_vars": ["DATABASE_URL"]}]))
   elif a[0] == "pipelines:info": print(json.dumps({"apps": [{"name": f[:-5], "pipelineCoupling": {"stage": app(f[:-5])["stage"]}} for f in os.listdir(d)]}))
   elif a[0] == "config:set":
       x = app(name); x["config"].update(kv.split("=", 1) for kv in a[3:]); x["release"] += 1
       json.dump(x, open(f"{d}/{name}.json", "w")); print(f"done, v{x['release']}", file=sys.stderr)
   EOF
   chmod +x bin/heroku && export PATH="$HOME/walkthrough/bin:$PATH"
   echo '{"stage": "production", "release": 41, "config": {"APP_BANNER": "baseline", "WEB_CONCURRENCY": "4", "LOG_LEVEL": "info", "DATABASE_URL": "postgres://u:p@db/prod", "STRIPE_KEY": "sk_live_stand_in"}}' > heroku/apps/shop-api.json
   echo '{"stage": "staging", "release": 12, "config": {"APP_BANNER": "staging-teal", "WEB_CONCURRENCY": "2", "LOG_LEVEL": "debug", "DATABASE_URL": "postgres://u:p@db/stg"}}' > heroku/apps/shop-api-staging.json
   cd api && printf 'web: bundle exec puma -C config/puma.rb\n' > Procfile
   git init -q && git remote add heroku https://git.heroku.com/shop-api.git
   ```
3. Deploy it: connect the app. `/confighub:staging` reads the config vars into a hub on this computer. Production starts from the production app's and staging from the staging app's. Credentials, the add-on's `DATABASE_URL` and Heroku's own settings stay on Heroku and are only counted. Nothing on Heroku changes, and no settings file is written.
   <!-- run: deploy -->
   ```sh
   claude -p "/confighub:staging"
   ```
   ```text
   api now has a staging and a production copy of its settings, in a hub on this machine. Production starts from the 3 settings Heroku app shop-api holds for production, and staging from the 3 settings Heroku app shop-api-staging holds. Nothing on Heroku was changed, and no settings file was written in this folder.
   …
   Staging changes can reach Heroku app shop-api-staging, the staging app, and never production. To send them there from now on, say yes once, in a terminal of your own: cub mini deliver api --staging
   ```
4. Update it. Your agent changes staging at once. Here you make the same change it would make. Then say yes, once, to sending staging to the staging app. The question names the staging app and says it never sends to production. Answer `y`.
   <!-- run: update -->
   ```sh
   cub mini set api WEB_CONCURRENCY=8 --variant staging --change-desc "More workers for the checkout load test"
   cub mini deliver api --staging
   ```
   ```text
   Staging is live on Heroku app shop-api-staging: WEB_CONCURRENCY changed, and Heroku restarted the app (release v13). The app now holds staging's 3 settings (revision 6).
   ```
5. From now on, each staging change goes to the staging app in the same command, without asking you. Your agent may send it too. With nothing changed, nothing is set, so the app does not restart.
   <!-- run: update-again -->
   ```sh
   cub mini set api LOG_LEVEL=info --variant staging --change-desc "Debug logs fill the staging disk"
   ```
   ```text
   Staging is live on Heroku app shop-api-staging: LOG_LEVEL changed, and Heroku restarted the app (release v14). The app now holds staging's 3 settings (revision 7).
   ```
6. A production change waits for you. Your agent proposes it; here you do. Production in the hub and the production app keep their value until you approve. `cub mini waiting` shows what would change.
   <!-- run: propose -->
   ```sh
   cub mini set api WEB_CONCURRENCY=8 --variant live --change-desc "Checkout times out under load: 8 workers"
   cub mini waiting
   ```
   ```text
   ConfigHub: proposed new values for production's own WEB_CONCURRENCY. Production keeps its current values until you approve them. To see the change and approve it, in a terminal:
   ```
7. Approve it. `cub mini approve api` shows the change and asks. The first time, it also asks once whether approved settings go to the production app from now on. Answer `y` both times. Only `WEB_CONCURRENCY` is set on `shop-api`.
   <!-- run: approve -->
   ```sh
   cub mini approve api
   ```
   ```text
       WEB_CONCURRENCY: 4 → 8
   Live on Heroku app shop-api: WEB_CONCURRENCY changed, and Heroku restarted the app (release v42). The app now holds the 3 settings you approved.
   ```
8. Undo. A rollback is a change to production like any other: it waits, and approving it puts the old value live. `cub mini deliver api --compare` writes nothing and says whether the production app holds what you approved.
   <!-- run: undo -->
   ```sh
   cub mini rollback api --reason "The load test is over"
   cub mini approve api
   cub mini deliver api --compare
   ```
9. Move it to your team's shared hub. Sign in once; `auth login` opens a browser. The copy keeps every value and its reason. `TEAM_APP` starts with your user name, so it does not clash with a teammate's.
   <!-- run: move sign-in -->
   ```sh
   cub context create shared --server https://hub.confighub.com
   cub --context shared auth login
   export TEAM_APP="${WALKTHROUGH_PREFIX:-$USER-}api"
   cub --context shared mini copy --from-context "$(cub context get -o jq=.name)" api --name "$TEAM_APP"
   ```
10. Delete it from your own hub, now that the shared hub holds it. The Heroku apps keep the config vars they were last given.
    <!-- run: delete -->
    ```sh
    cub component delete --recursive --detach api
    ```
### Undo it
In the shared hub: `cub --context shared component delete --recursive --detach "$TEAM_APP"`. Here: `cub mini uninstall --name mini --delete-data`, then `rm -rf ~/walkthrough ~/.confighub-walkthrough`.
### What you have now
The staging app runs what your agent changed in staging. The production app runs only what you approved, and each value has its reason in the hub. Credentials and add-on settings never left Heroku.
### Leaving Heroku
To move production to Fly or Vercel, see the plan first, in your own terminal; it writes nothing. For Vercel, run `vercel link` in the app's folder first.

```sh
cub mini deliver api --fly FLYAPP --compare
cub mini deliver api --vercel PROJECT --compare
```

Run the line the plan gives to copy the credentials from Heroku, then the same command without `--compare`. Staging stays on the Heroku staging app. [Moving production to Fly or Vercel](../../docs/heroku.md#moving-production-to-fly-or-vercel) has the details.

## Agent
For trials, use the stand-in. **Deploy**: ask the person to type `/confighub:staging` in the app's folder; you cannot type it. **Update**: change staging with `cub mini set api KEY=VALUE --variant staging --change-desc "WHY"`. Once the person has said yes to the staging app, the change goes there in the same command. Before that, tell them the one command, `cub mini deliver api --staging`, for their own terminal. Propose production changes with `--variant live` and hand the person `cub mini approve api`. **Undo** with `cub mini rollback api --reason "WHY"` and hand over the approval. **Move** with step 9, and **delete** with step 10 only after the copy is confirmed. Never approve production, never move it with `--fly` or `--vercel`, never give the first yes for either app, never run `heroku config:set` yourself, and never put a credential in a setting.
## Testing
<!-- agent-task: deploy after=app -->
> My Rails API runs on Heroku as shop-api, with shop-api-staging as its staging app. Set it up so staging takes your changes and production waits for me.
<!-- agent-person deploy: claude -p "/confighub:staging" -->
<!-- agent-check deploy: cub unit data app --space api-live | grep -qx WEB_CONCURRENCY=4 && cub unit data app --space api-staging | grep -qx WEB_CONCURRENCY=2 && ! cub unit data app --space api-live | grep -q STRIPE_KEY -->
<!-- agent-task: update -->
> Raise WEB_CONCURRENCY to 8 in staging for the checkout load test.
<!-- agent-person update: cub mini deliver api --staging --yes -->
<!-- agent-check update: cub unit data app --space api-staging | grep -qx WEB_CONCURRENCY=8 && grep -q '"WEB_CONCURRENCY": "8"' ~/walkthrough/heroku/apps/shop-api-staging.json && grep -q '"WEB_CONCURRENCY": "4"' ~/walkthrough/heroku/apps/shop-api.json -->
<!-- agent-check-a update: grep -q '"WEB_CONCURRENCY": "8"' ~/walkthrough/heroku/apps/shop-api-staging.json -->
<!-- agent-task: undo -->
> Propose putting WEB_CONCURRENCY back in production. I'll approve it.
<!-- agent-check undo: cub mini waiting | grep -q 'WEB_CONCURRENCY' && grep -q '"WEB_CONCURRENCY": "8"' ~/walkthrough/heroku/apps/shop-api.json -->
<!-- agent-task: move -->
> Move the API to our shared hub. The shared context is named `shared`, and the destination is in `TEAM_APP`.
<!-- agent-check move: cub --context shared unit data app --space "$TEAM_APP-live" | grep -q WEB_CONCURRENCY -->
<!-- agent-task: delete -->
> Remove the API from the hub on this computer, now that the shared hub has it.
<!-- agent-check delete: ! cub component get api >/dev/null 2>&1 -->
<!-- next-step boundary=same-tier when "did not change": your real Heroku app | Production waited for your yes. Want to connect your real Heroku app the same way, with only what you approve reaching it? -->

This proves: the hub starts each copy from the Heroku app it belongs to and leaves credentials and add-on settings on Heroku; a staging change reaches the staging app after the person's one yes, and the next one in the same command; a production change waits, and approving it sets only that config var on the production app; a rollback goes live the same way.

**What ran, and what did not.** This path ran on a local hub against a stand-in `heroku` command, not a real Heroku account. The stand-in answers in the forms the Heroku command line's own source prints. The check covered connecting from a pipeline, the agent's key being refused the first yes for the staging app, the person's yes, a staging change carried on to the staging app with production unchanged, a production change that waits, approval, a second delivery that sets nothing, a setting changed on Heroku by hand, and a rollback. A setting written to an app Heroku does not couple as the pipeline's staging app is refused, production included. The stand-in on this page is shorter than the one the check used. Steps 4 and 5 need confighub mini 0.11.1-mini.32 or later. The move to a shared hub was not run for this page.

</details>
