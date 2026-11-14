<!-- walkthrough
id: starter-web
starts_with: mini
starter: web
needs: [confighub mini package, a hosted ConfigHub organization for step 7]
budget_seconds: 200
-->
# A small web service: deploy it, update it, undo it, move it, delete it

You run a small service from a `.env` file. Try a settings change in staging, check what production still holds, then approve it and undo it. At the end, copy the setup to your team so the next change can start there.

## Human
For a person following along in a terminal.

### What you need
confighub mini, unpacked as [installing confighub mini](../../docs/install-mini.md) shows (steps 1 to 5). confighub mini runs a hub, which is a ConfigHub server that keeps your app's settings, on your own computer. `cub` is ConfigHub's command-line tool, and the package includes it. For step 7 you also need an organization on hosted ConfigHub, the shared hub your team signs in to.

### Steps
1. Start a hub, with the starters switched on. `MINI` is the folder of the unpacked package. A starter gives a new app of one kind its usual settings, each with a reason ([starters](../../docs/starters.md)).
   <!-- run: setup -->
   ```sh
   export MINI=/absolute/path/to/unpacked-confighub-mini
   export PATH="$MINI/bin:$PATH" CUB_MINI_STARTERS="$MINI/starters"
   cub plugin install "$MINI" >/dev/null
   cub mini install --use
   export LAPTOP=$(cub context get -o jq=.name)
   ```
2. Make the app: a folder `menu` with its settings, and its own log level for staging.
   <!-- run: app files -->
   ```sh
   mkdir menu
   printf 'PORT=5000\nLOG_LEVEL=warn\nMENU_SOURCE=kitchen.json\n' > menu/.env
   printf 'LOG_LEVEL=debug\n' > menu/.env.staging
   ```
3. Deploy it, part one: connect it. ConfigHub makes three copies of its settings: the base, staging, and live, which is production. The web starter adds three settings and leaves yours alone. Your files are not changed.
   <!-- run: deploy -->
   ```sh
   cub mini adopt menu
   ```
   ```text
   Starter: web (version 1, web.yaml): A small web service whose settings are in a .env, app.env or compose file, made from adopt's starter pattern.
   …
     Sets REPLICAS=2, as a setting: Two instances, so that one can restart without the service going down.
   …
     Leaves PORT alone: it is set already, PORT=5000, by you, in .env.
   …
     Production takes the shared settings only after you approve them. To see them and approve them, in a terminal of your own: ~/.confighub/mini/cub mini approve menu-live
   ```
4. Deploy it, part two: approve production's first settings, and write them where the service reads them. `cub mini pull` writes live's settings as `menu-running/app.env`; start the service from that file as you do now.
   <!-- run: deploy-live -->
   ```sh
   cub mini approve menu-base/adopt --note "First settings for production" --yes
   cub mini pull menu --variant live --dir menu-running
   ```
   ```text
   …
   Approved menu-base/adopt.
   …
   app.env written: revision 3: menu's settings, from .env, with .env.staging for staging
   ```
5. Update it: production should log more. Change the file, then upload the change with your reason. Staging keeps its own `debug`; production waits for your approval, and you give it.
   <!-- run: update -->
   ```sh
   printf 'PORT=5000\nLOG_LEVEL=info\nMENU_SOURCE=kitchen.json\n' > menu/.env
   cub mini upload menu --change-desc "Warnings alone hide what customers do"
   cub mini approve --note "Info logs are fine in production" --yes
   cub mini pull menu --variant live --dir menu-running
   ```
   ```text
   Changed the shared settings (menu-base), with the reason: Warnings alone hide what customers do
     LOG_LEVEL: warn → info
   Staging keeps its own LOG_LEVEL=debug, so this change does not reach it.
   …
   Approved menu-base/upload-TIME.
   ```
6. Undo the update in production. `cub mini rollback` sets back what that change order changed, and nothing else, in the shared settings; production takes it only once you approve it, as any change. The change order's name was printed by step 5; here it is read from the hub.
   <!-- run: undo -->
   ```sh
   ORDER=$(cub changeorder list --space menu-base --where "Slug LIKE 'upload-%'" -o jq='.[-1].ChangeOrder.Slug')
   cub mini rollback menu-live --change-order "menu-base/$ORDER" --reason "Info logs show customer emails"
   cub mini approve --yes --note "Back to warnings"
   cub mini pull menu --variant live --dir menu-running
   ```
   ```text
   Set back in the shared settings (menu-base), with the reason: Info logs show customer emails
     LOG_LEVEL: info → warn
   …
   Approved menu-base/upload-TIME.
   ```
7. Move it to your team's shared hub. Sign in once (`auth login` opens a browser). The app's name there, `TEAM_APP`, starts with your user name, so it does not clash with a teammate's.
   <!-- run: sign-in sign-in -->
   ```sh
   cub context create shared --server https://hub.confighub.com
   cub --context shared auth login
   export PREFIX="${WALKTHROUGH_PREFIX:-$USER-}"
   export TEAM_APP="${PREFIX}menu"
   ```
8. Copy the app there. The copy keeps every value and its reason, and keeps production behind your approval: it makes the change workflow, which says a change to live waits for you ([approvals](../../docs/approvals.md#on-hosted-confighub-or-your-own-server-with-cub-alone) explains it).
   <!-- run: move -->
   ```sh
   cub --context shared mini copy --from-context "$LAPTOP" menu --name "$TEAM_APP"
   cub --context shared unit data app --space "$TEAM_APP-live"
   ```
   ```text
   …
   LOG_LEVEL=warn
   ```
9. Check that production in the shared hub waits for you, without changing anything there: the app takes a change only through its change workflow (the first `true`), and that workflow's production stage needs an approval (the second).
   <!-- run: move-waits -->
   ```sh
   cub --context shared component get "$TEAM_APP" -o jq=.Component.RequireChangeWorkflow
   cub --context shared changeworkflow get --space workflows "$TEAM_APP-live-approval" -o jq='.ChangeWorkflow.Stages[] | select(.Name == "live") | .Prerequisites | length > 0'
   ```
   ```text
   true
   true
   ```
10. Delete the app from your own hub, now that the shared hub holds it. There is no single command for this yet: delete its Spaces, its Component, then its approval rules. Your files stay.
    <!-- run: delete -->
    ```sh
    cub space delete --space menu-live,menu-staging,menu-base,menu-file-proposals --recursive
    cub component delete menu
    cub changeworkflow delete --space workflows menu-live-approval
    cub changeworkflow delete --space workflows menu-file-review
    ```

### Undo it
In the shared hub: `cub --context shared space delete --space "$TEAM_APP-live,$TEAM_APP-staging,$TEAM_APP-base" --recursive`, then `cub --context shared component delete "$TEAM_APP"` and `cub --context shared changeworkflow delete --space workflows "$TEAM_APP-live-approval"`. To remove your own hub with everything in it: `cub mini uninstall --delete-data`.

### What you have now
Your `menu` folder, unchanged by ConfigHub; `menu-running/app.env`, production's settings as last approved; and your team's shared hub holding the app, with production there changing only when you approve.

## Agent
For an AI agent doing these jobs for a person: run the Human steps' commands, adjusted to their app.
- **Deploy:** `cub mini adopt FOLDER`. End your message with one sentence on what the person has now, in their words (for example, that production cannot change without them), and the one approve command adopt printed, such as `~/.confighub/mini/cub mini approve menu-live`. Copy it exactly as printed.
- **Update:** change the app's file, then `cub mini upload FOLDER --change-desc "WHY"`. End the same way, with the approve command `upload` printed (for example `~/.confighub/mini/cub mini approve menu-base/upload-20261113-163415-0kyg`), copied exactly.
- **Undo:** put the file back as it was and upload it again, with the reason. End the same way.
- **Move:** run step 8 with the shared hub's context, then read live back, and step 9, which only reads, to see that production waits; never make a change there to test it. If it does not, say so plainly.
- **Delete:** step 10, only once the shared hub holds the app. Never delete the person's files.

Approving production is the person's, so give them the one command and nothing beside it. Never put a password or token in a setting. You are done when `cub unit data app --space APP-live` shows what the person asked for, or, for a change that waits, when `cub mini waiting` shows it.

## Testing
Each task below is given to an agent in the folder that holds `menu`, after the steps before it. When a change waits for production, the person approves it.

<!-- agent-task: deploy -->
> Deploy my menu service: keep its settings in a staging and a production copy, and production should change only when I approve.
<!-- agent-task: update -->
> Production should log at info, not warn. Make that change for menu.
<!-- agent-task: undo -->
> Undo that log level change in production; info logs show customer emails.
<!-- agent-task: move -->
> Copy menu to our team's shared hub, whose context is called shared. The app's name there is in `TEAM_APP`, and production there should change only when I approve.
<!-- agent-task: delete -->
> Remove menu from this computer's hub; the team's hub keeps it. Keep my files.

<!-- agent-person deploy: cub mini approve --yes -->
<!-- agent-person update: cub mini approve --yes -->
<!-- agent-person undo: cub mini approve --yes || true -->
<!-- agent-check deploy: cub unit data app --space menu-live | grep -qx PORT=5000 && cub unit data app --space menu-staging | grep -qx LOG_LEVEL=debug -->
<!-- agent-check update: cub unit data app --space menu-live | grep -qx LOG_LEVEL=info -->
<!-- agent-check undo: cub unit data app --space menu-live | grep -qx LOG_LEVEL=warn && test -f menu/.env -->
<!-- agent-check move: cub --context shared unit data app --space "$TEAM_APP-live" | grep -qx PORT=5000 && cub --context shared api GET "component/$(cub --context shared component get "$TEAM_APP" -o jq=.Component.ComponentID)" | grep -q '"RequireChangeWorkflow":true' -->
<!-- agent-check delete: test -f menu/.env && ! cub space get menu-live >/dev/null 2>&1 && cub --context shared space get "$TEAM_APP-live" >/dev/null -->
<!-- agent-check-a deploy: grep -rlsE '^[ -]*"?PORT"?[=:] *"?5000' --exclude-dir='.*' --exclude-dir=Library * .env* | grep -vqxE 'menu/\.env(\.staging)?' -->
<!-- agent-check-a update: grep -rlsE '^[ -]*"?LOG_LEVEL"?[=:] *"?info' --exclude-dir='.*' --exclude-dir=Library * .env* | grep -q . && grep -qx LOG_LEVEL=debug menu/.env.staging -->
<!-- agent-check-a undo: ! grep -rqsE '^[ -]*"?LOG_LEVEL"?[=:] *"?info' --exclude-dir='.*' --exclude-dir=Library * .env* && grep -rlsE '^[ -]*"?LOG_LEVEL"?[=:] *"?warn' --exclude-dir='.*' --exclude-dir=Library * .env* | grep -q . -->
<!-- next-step boundary=same-tier when "did not change": keep the web starter on | Production waited for your yes because the web starter set this app up that way, with a reason for each setting. Your next web service can start the same way; want the web starter kept on for it? -->
<!-- arms: a,b,c -->
This proves: the settings were stored in the hub, on confighub mini and on hosted ConfigHub, with production there waiting for approval, and production's approved revision was written to the file a service reads, with `cub mini pull`. No service is started, and no controller is used. The page aims to win one next step: that the person keeps the starter on for their next app.

The checks can be run by hand, from the folder that holds `menu`:

```sh
cub unit data app --space menu-live      # PORT=5000; LOG_LEVEL=info after the update, warn after the undo
cub --context shared unit data app --space "$TEAM_APP-live"
```

<!-- results:begin -->

Results, 14 November 2026, confighub mini 0.11.1-mini.3. Figures from this page's own test runs, shown here for whoever checks the page; they are not a promise.

- Scripted run (on confighub mini 0.11.1-mini.3, 14 November 2026): passed, 64 seconds for the steps, within the page's budget of 200; each of the three planted faults (a changed quoted line, a budget of zero seconds, a check that holds on a fresh hub) was caught.
- Scripted run (on confighub mini 0.11.1-mini.7, 14 November 2026): passed, 62 seconds for the steps, within the page's budget of 200; each of the three planted faults (a changed quoted line, a budget of zero seconds, a check that holds on a fresh hub) was caught.
- Environment, published confighub mini 0.11.1-mini.3 with its own plugin (0.86.0): A local confighub mini hub on this computer, with hosted ConfigHub (the Kubara organization) for the move to a shared hub; no cluster or service. Approvals were scripted: the test script ran the person's approve commands. After each run the runner removed the hubs it started and everything it made in the shared hub.
- Agent runs (on confighub mini 0.11.1-mini.3, 14 November 2026): a pilot, 3 runs per arm on each of claude-sonnet-5-5, claude-opus-5-5. Arms: a is ordinary tools only; b is the plugin, confighub mini and this page as reading; c is the plugin and confighub mini, without this page.

| Arm | Model | Checks passed | Median seconds | Median cost | Commands left for the person (median) |
|---|---|---|---|---|---|
| a | claude-opus-5-5 | 6/9 (+6 not applicable) | 64.4 | $0.27 | 0 |
| b | claude-opus-5-5 | 15/15 | 114.5 | $0.479 | 3 |
| c | claude-opus-5-5 | 13/15 | 172.4 | $0.726 | 4 |
| a | claude-sonnet-5-5 | 6/9 (+6 not applicable) | 43.7 | $0.128 | 0 |
| b | claude-sonnet-5-5 | 15/15 | 90.9 | $0.215 | 3 |
| c | claude-sonnet-5-5 | 7/15 | 84.5 | $0.29 | 4 |

No agent approved or refused a change to production.

Simulated persons, not people: 10 per run, each a claude-haiku-5-5 model playing one of ten fixed personas, reading only what a person would see. The next step they were offered: "Production waited for your yes because the web starter set this app up that way, with a reason for each setting. Your next web service can start the same way; want the web starter kept on for it?"

The plugin offers it once, after the answer at whose end it showed the moment the offer names ("did not change"). Offered is the share of persons it was shown to; want it now and later are over them.

| Arm | Model | Persons | Offered | Noticed | Want the next step now | Later | In the way |
|---|---|---|---|---|---|---|---|
| a | claude-opus-5-5 | 30 | 0% | 100% | n/a | n/a | 87% |
| b | claude-opus-5-5 | 30 | 100% | 100% | 7% | 80% | 70% |
| c | claude-opus-5-5 | 30 | 33% | 100% | 40% | 50% | 83% |
| a | claude-sonnet-5-5 | 30 | 0% | 100% | n/a | n/a | 70% |
| b | claude-sonnet-5-5 | 30 | 100% | 100% | 27% | 70% | 90% |
| c | claude-sonnet-5-5 | 30 | 67% | 100% | 25% | 75% | 97% |

- Agent runs (on confighub mini 0.11.1-mini.2, 13 November 2026): 20 runs per arm on each of claude-opus-5-5, claude-sonnet-5-5. Arms: a is ordinary tools only; b is the plugin, confighub mini and this page as reading.

| Arm | Model | Checks passed | Median seconds | Median cost | Commands left for the person (median) |
|---|---|---|---|---|---|
| a | claude-opus-5-5 | 43/60 (+40 not applicable) | 70.1 | $0.276 | 0 |
| b | claude-opus-5-5 | 100/100 | 129.9 | $0.479 | 3 |
| a | claude-sonnet-5-5 | 40/60 (+40 not applicable) | 57.6 | $0.134 | 0 |
| b | claude-sonnet-5-5 | 100/100 | 93.1 | $0.206 | 3 |

No agent approved or refused a change to production.

Simulated persons, not people: 10 per run, each a claude-haiku-5-5 model playing one of ten fixed personas, reading only what a person would see. The next step they were offered: "Production waited for your yes because the web starter set this app up that way, with a reason for each setting. Your next web service can start the same way; want the web starter kept on for it?"

The plugin offers it once, after the answer at whose end it showed the moment the offer names ("did not change"). Offered is the share of persons it was shown to; want it now and later are over them.

| Arm | Model | Persons | Offered | Noticed | Want the next step now | Later | In the way |
|---|---|---|---|---|---|---|---|
| a | claude-opus-5-5 | 200 | 0% | 100% | n/a | n/a | 84% |
| b | claude-opus-5-5 | 200 | 100% | 100% | 28% | 60% | 74% |
| a | claude-sonnet-5-5 | 200 | 0% | 100% | n/a | n/a | 82% |
| b | claude-sonnet-5-5 | 200 | 100% | 100% | 26% | 59% | 89% |

<!-- results:end -->
