<!-- walkthrough
id: story-24-company-base
starts_with: mini
story: "24. Priya's platform team's base: one base, ten apps, one bump"
needs: [cub mini package]
budget_seconds: 300
-->
# One base for every service, and one change that reaches them all

Priya's platform team keeps the settings every service shares in one base. Each service keeps the few values it sets itself. When the team changes the base once, every app takes the change, and no app's own values are touched. Here three services stand in for the story's ten.

## Human

For a person following along in a terminal.

### What you need

An unpacked confighub mini package (from the [releases page](https://github.com/confighubai/confighub-mini-plugin/releases)) on macOS or Linux. confighub mini is a hub, a small ConfigHub server that keeps each setting with who changed it and why, running on your computer only. No Docker, no account.

### Steps

1. Set up a terminal. `MINI` is the unpacked package; `CUB_CONFIG` is a new folder for this walkthrough's `cub` settings, so nothing of yours is touched. Then start a hub:
   <!-- run: setup -->
   ```sh
   export MINI=/absolute/path/to/unpacked-confighub-mini
   export PATH="$MINI/bin:$PATH"
   export CUB_CONFIG="$HOME/.confighub-walkthrough"
   unset CUB_CONTEXT
   "$MINI/bin/confighub-mini-app" mini install-plugin "$CUB_CONFIG" >/dev/null
   cub mini install --name priya --use --arrival no >/dev/null
   ```
   `--arrival no` answers the one question a first install asks: whether a hub may start by itself when an agent works in an app's folder.

2. The files: the team's base, `company.env`, and three services, each a folder with a `.env` of what it sets differently. The base's last line names its one resource, `app`, as `cub mini adopt` does for an app:
   <!-- run: files files -->
   ```sh
   mkdir -p ~/walkthrough/apps/billing ~/walkthrough/apps/search ~/walkthrough/apps/ledger && cd ~/walkthrough
   printf 'PORT=8080\nLOG_LEVEL=info\nREPLICAS=2\nTIMEOUT_MS=3000\nMETRICS_PATH=/metrics\nconfigHub.configName=app\n' > company.env
   printf 'PORT=9001\nLOG_LEVEL=debug\n' > apps/billing/.env
   printf 'PORT=9002\nREPLICAS=3\n' > apps/search/.env
   printf 'PORT=9003\n' > apps/ledger/.env
   ```

3. The team's base in the hub: one Unit of settings, `app`, in a Space `company-base`. A Space is a folder in the hub, and a Unit one piece of configuration:
   <!-- run: base -->
   ```sh
   cub component create company >/dev/null
   cub space create company-base --component company --variant base >/dev/null
   cub unit create --space company-base app company.env --toolchain AppConfig/Env --change-desc "Company base 1: what every service starts from" >/dev/null
   ```

4. The three services are made from the base. Each gets a staging copy with its settings now and a production copy that waits for approval:
   <!-- run: apps -->
   ```sh
   for app in billing search ledger; do cub mini adopt apps/$app --pattern company | sed -n 3,4p; done
   ```
   ```text
     Your settings that differ from the defaults in company-base/app: LOG_LEVEL=debug, PORT=9001. A new version of those defaults will not overwrite them.
     Defaults from company-base/app, for settings apps/billing does not set: METRICS_PATH=/metrics, REPLICAS=2, TIMEOUT_MS=3000.
     Your settings that differ from the defaults in company-base/app: PORT=9002, REPLICAS=3. A new version of those defaults will not overwrite them.
   …
   ```

5. The team changes the base once: `warn` is the default log level now, and every service answers on `/healthz`. Each change carries its reason:
   <!-- run: bump -->
   ```sh
   cub mini set company LOG_LEVEL=warn --variant base --change-desc "Company base 2: warn is the default log level now" | tail -1
   cub mini set company HEALTH_PATH=/healthz --variant base --change-desc "Company base 2: every service answers on /healthz" | tail -1
   ```
   ```text
   Saved in company-base, with the reason: Company base 2: warn is the default log level now. A later version of what company-base is made from will not overwrite this value.
   Saved in company-base, with the reason: Company base 2: every service answers on /healthz. A later version of what company-base is made from will not overwrite this value.
   ```

6. Every app takes it. The dry run says what would happen and changes nothing; the second command does it, in one request for all the apps:
   <!-- run: bump-upgrade -->
   ```sh
   cub mini upgrade company-base/app --dry-run
   cub mini upgrade company-base/app --change-desc "Company base 2: warn by default, and a health path"
   ```
   ```text
   3 apps would take company-base/app's version 4.
   3 apps took company-base/app's version 4.
   ```

7. What each app holds now: the health path in all three, `warn` where the app had not set its own log level, and billing's `debug` kept:
   <!-- run: holds -->
   ```sh
   for app in billing search ledger; do echo "$app: $(cub unit data --space $app-base app | grep -E 'PORT|LOG_LEVEL|REPLICAS|HEALTH' | tr '\n' ' ')"; done
   ```
   ```text
   billing: PORT=9001 LOG_LEVEL=debug REPLICAS=2 HEALTH_PATH=/healthz
   search: PORT=9002 LOG_LEVEL=warn REPLICAS=3 HEALTH_PATH=/healthz
   ledger: PORT=9003 LOG_LEVEL=warn REPLICAS=2 HEALTH_PATH=/healthz
   ```

8. Ask where each of billing's values came from. `U` marks what the upgrade brought; `P` a value billing protects as its own; `X` the base's change that billing's own value set aside:
   <!-- run: blame -->
   ```sh
   cub unit blame app --space billing-base
   ```
   ```text
   …
   cb4aaaf U HEALTH_PATH set-string-path admin@local.confighub.dev company-base 4 just now
   1d54dea PXC LOG_LEVEL set-string-path admin@local.confighub.dev billing-base 3 just now
   …
   ```

9. Staging takes the bump by one promotion; production waits for Priya:
   <!-- run: staging -->
   ```sh
   cub mini promote billing-staging --change-desc "Staging takes company base 2" | tail -1
   cub unit data --space billing-staging app | grep HEALTH_PATH
   cub mini waiting | sed -n 1p
   ```
   ```text
   Done. Each copy kept its own values.
   HEALTH_PATH=/healthz
   3 proposed changes wait for your approval, making 3 different changes.
   ```

### Undo it

`cub mini uninstall --name priya --delete-data` removes the hub and everything in it; then delete `~/walkthrough` and `~/.confighub-walkthrough`.

### What you have now

One base and three apps made from it. One change to the base reached every app, and each app's own values stayed its own, with `cub unit blame` saying which value came from where. Production still waits for Priya's approval, one change order per app; `cub mini waiting` lists each change order as it was made, not everything a promotion now would carry.

The full story runs ten apps on the team's hosted ConfigHub, where the same commands run with `--context` naming the shared hub. [From your laptop to a shared hub](../../docs/from-plugin-to-confighub.md) covers moving there.

## Agent

For an AI agent working for the platform team.

- The request: "Make warn the default log level for every service on the company base, and give them all HEALTH_PATH=/healthz. Don't touch what any service set for itself."
- Change the base once, each value with its reason: `cub mini set company KEY=VALUE --variant base --change-desc "WHY"`. Then `cub mini upgrade company-base/app --dry-run`, read it, and `cub mini upgrade company-base/app --change-desc "WHY"`.
- Never edit an app's own values to match, approve production, or promote production. Staging can take it with `cub mini promote APP-staging`; production is the person's: tell them `cub mini waiting` lists what waits.
- Done when each app's base (`cub unit data --space APP-base app`) has `HEALTH_PATH=/healthz`, and billing still has `LOG_LEVEL=debug`.

## Testing

This proves: the settings were stored in the hub, the base's change reached each app's copy and each app's own values were kept. What was really used: confighub mini on this computer, with three apps for the story's ten; nothing is delivered and the story's hosted ConfigHub is not used.

A correct agent result has the bump in the base and in every app's base, with billing's own `LOG_LEVEL=debug` kept. The checks below hold right after step 6. The checks below can be run by hand in the walkthrough's folder:

<!-- agent-task: bump after=bump -->
> Make warn the default log level for every service on the company base, and give them all HEALTH_PATH=/healthz. Don't touch what any service set for itself.

<!-- agent-check bump: cub unit data --space company-base app | grep -qx 'LOG_LEVEL=warn' && ! for a in billing search ledger; do cub unit data --space $a-base app | grep -qx 'HEALTH_PATH=/healthz' || echo missing; done | grep -q missing && cub unit data --space billing-base app | grep -qx 'LOG_LEVEL=debug' && cub unit data --space search-base app | grep -qx 'LOG_LEVEL=warn' -->
<!-- agent-check-a bump: grep -qx 'LOG_LEVEL=warn' company.env && grep -qx 'HEALTH_PATH=/healthz' company.env && grep -qx 'LOG_LEVEL=debug' apps/billing/.env -->
<!-- arms: a,b,c -->

```sh
cub unit data --space company-base app | grep -qx 'LOG_LEVEL=warn' && ! for a in billing search ledger; do cub unit data --space $a-base app | grep -qx 'HEALTH_PATH=/healthz' || echo missing; done | grep -q missing && cub unit data --space billing-base app | grep -qx 'LOG_LEVEL=debug' && cub unit data --space search-base app | grep -qx 'LOG_LEVEL=warn'
grep -qx 'LOG_LEVEL=warn' company.env && grep -qx 'HEALTH_PATH=/healthz' company.env && grep -qx 'LOG_LEVEL=debug' apps/billing/.env
```
