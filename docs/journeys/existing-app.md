# An app you already have, in Claude Code: staging and production kept as they are

This page is for someone whose app already has its settings in files, one set for staging and one for production, and who now lets Claude Code change them. Today an agent that can edit the staging file can edit the production file too. Here you ask Claude Code to attach ConfigHub to the app. Your staging and production values stay exactly as they are, your files are not changed, and changes to the hub's live configuration wait for your approval.

The app might run on your own machine, on another machine, in CI, on one or many sandbox nodes, in a shared development cluster, or in production. Attaching it creates configuration copies in the hub. Its running services use the hub's approved settings once their deployment path is connected ([where the app runs](../README.md#where-the-app-runs)).

It works for these kinds of files:

| Your app keeps its settings in | What becomes staging's own values | What becomes production's own values |
|---|---|---|
| `.env`, `app.env`, a compose file's environment or `.env.example` | `.env.staging` | `.env.production` |
| A Terraform folder: `common.tfvars` | `staging.tfvars` | `prod.tfvars` |
| A Kustomize repository: `base/` and overlays | what `overlays/staging` changes | what the `prod`, `production` or `live` overlay changes, or the one an Argo CD Application in the repository deploys |
| Helm values for a chart | not read by `cub mini adopt`; see [Helm values](#helm-values) below | |

If Argo CD or Flux deploys the app from Git, read this page, then [an app that Argo CD or Flux deploys](gitops-app.md).

## Words used on this page

- **A hub** is one running ConfigHub: a server that keeps your app's settings, with every change, who made it and why. **confighub mini** is ConfigHub made small enough to run on your laptop. `cub` is ConfigHub's command-line tool, and comes with confighub mini.
- **The base** holds the values every environment shares. **The staging copy** is made from it and takes each change at once. **The live copy** holds the settings intended for production. It takes a change only when you approve it. Each copy keeps its **own values**, the ones your staging or production file sets differently, through later changes to the base.
- **A Space** is where the hub keeps one copy, such as `orders-live`.
- **A change order** is a request for a change to reach the live copy. It waits until you approve or refuse it.
- **The agent's key** is a sign-in of the agent's own. On it, the agent can change the base and staging, and propose changes to live. It cannot approve them.

## What it costs

- **Time.** 45 to 196 seconds in measured sessions, about two minutes on average, including the first download.
- **The download.** confighub mini, 48 to 73 MB, the first time, into `~/.confighub/mini`. It runs as two processes on this machine. No account and no sign-in.
- **Your files.** Not changed. One new file, `.confighub-app`, a note of what the files match in the hub, which you commit. The agent's setup also writes `.claude/settings.local.json`, so that later Claude Code sessions in the repository run on the agent's key, and adds it to `.git/info/exclude`, so Git leaves it out.
- **For a Kustomize repository,** `kubectl` or `kustomize` on the machine, to render it.

## The steps

1. Install the plugin, in a terminal:

   ```
   claude plugin marketplace add confighubai/confighub-mini-plugin
   claude plugin install confighub@confighub
   ```

2. Start Claude Code in the app's repository, and ask:

   ```
   attach confighub to this existing app: keep my staging and production values exactly as they are,
   and make sure an agent cannot change production without my say
   ```

3. Let the agent work. It starts a hub on your machine if none answers, then runs `cub mini adopt` with `--dry-run` first, which says what it would make and makes nothing. For a Terraform folder, it printed:

   ```
   Without --dry-run, this makes app an app on pattern-web/web-service, from what app reads at start (common.tfvars, staging.tfvars for staging, prod.tfvars for live):
     first the starter pattern, pattern-web, with the rules replicas-limit, not-public, log-level, no-secret-values
     app-base, with its own values cpu=512, log_retention_days=14, memory_mb=2048
     app-staging, with them now, and its own from staging.tfvars: desired_count=1, env=staging
     app-live, which takes them only once you approve, and its own from prod.tfvars: desired_count=3, env=prod
   ```

   For a Kustomize repository, adopted with `--name orders`:

   ```
   Without --dry-run, this makes orders an app from what app renders (base, overlays/staging for staging, overlays/prod for live):
     orders-base, holding base as kustomize renders it: ConfigMap/orders-config, Service/orders, Deployment/orders
     orders-staging, with its own from overlays/staging: FEATURE_NEW_CHECKOUT=true, LOG_LEVEL=debug, namespace=orders-staging
     orders-live, with its own from overlays/prod: RATE_LIMIT_PER_MINUTE=600, replicas=3, namespace=orders; the rest it takes from the base only once you approve
   ```

   For a folder with `.env`, `.env.staging` and `.env.production`:

   ```
   Without --dry-run, this makes greeter an app on pattern-web/web-service, from what greeter reads at start (.env, .env.staging for staging, .env.production for live):
     first the starter pattern, pattern-web, with the rules replicas-limit, not-public, log-level, no-secret-values
     greeter-base, with its own values GREETING=Hello, PORT=3000, RATE_LIMIT_PER_MINUTE=60
     greeter-staging, with them now, and its own from .env.staging: GREETING=Hello from staging, RATE_LIMIT_PER_MINUTE=600
     greeter-live, which takes them only once you approve, and its own from .env.production: GREETING=Welcome
   ```

   `pattern-web` is a starter pattern the first adopt makes for an env or Terraform app: the defaults a small web service starts from, and four rules, such as one that refuses a value named like a password. It is yours to change or ignore.

   The agent then runs the adopt itself, and `cub mini require-approval APP --variant live --agent APP-agent`, which gives the agent its own key.

4. Read the agent's summary. For the Terraform folder it said:

   > ConfigHub is attached to your Terraform app. Your `.tfvars` files are untouched, and the hub holds the same values they do.
   >
   > **The three copies**
   > - **`app-base`** holds the shared values from `common.tfvars`: `cpu=512`, `memory_mb=2048`, `log_retention_days=14`.
   > - **`app-staging`** has those values now, plus `desired_count=1` and `env=staging`. It takes changes at once.
   > - **`app-live`** is production. It has `desired_count=3` and `env=prod`. It changes only when you approve.
   >
   > …
   >
   > **To do**
   > 1. Commit the new `.confighub-app` file with the app. Nothing is committed yet.
   > …

   For a Kustomize repository that Argo CD deploys, the agent also said that Argo CD still syncs production from Git. That is true, and [the next page](gitops-app.md) is about it.

5. In your own terminal, run the `export PATH=...` line the agent gave you, so that `cub` is on your path.

6. Let live take the values it shares with the base. Its own values are there already. The shared ones wait in a change order that adopt made:

   ```
   cub mini waiting
   cub mini approve APP-base/adopt
   ```

   `cub mini approve` shows what live would take and asks you first.

7. Commit `.confighub-app`:

   ```
   git add .confighub-app && git commit -m "ConfigHub: what the files match in the hub"
   ```

## Changing the app later

You and your agents keep editing the same files. The agent then proposes what changed:

```
cub mini upload APP-FOLDER --component APP --change-desc "WHY" --dry-run   # what it would propose; changes nothing
cub mini upload APP-FOLDER --component APP --change-desc "WHY"
```

The upload sets each changed value in the base with the reason. Staging has it at once. Live waits for your `cub mini approve`. A change to the staging file is staging's own and goes no further. For a Kustomize repository, the upload renders it as adopt did. With `--dry-run`, on a repository whose base changed a ConfigMap value and whose prod overlay now asked for 4 replicas, it printed:

```
Live keeps its own values, which a change to the base does not reach. For what its overlay now says, replicas=4, live changes only with your say:
  cub mini set shopk set-int-path apps/v1/Deployment spec.replicas 4 --variant live --resource Deployment/shop --change-desc WHY
Would set in shopk-base, with the reason, and propose:
  app: ConfigMap/shop-config/data.CHECKOUT_TIMEOUT 30s → 45s
shopk-staging would have ConfigMap/shop-config/data.LOG_LEVEL = warn, as staging's own, from overlays/staging.
shopk-staging would have ConfigMap/shop-config/data.CHECKOUT_TIMEOUT = 45s now, from base.
shopk-live takes it only once approved: a change order in shopk-base would wait for that, to see and approve with cub mini approve.

Nothing has been changed.
```

The agent's turn ends with one line when a change waits for you. What approving looks like, and what the agent is refused: [a new app, changing it later](new-app.md#changing-the-app-later).

## Helm values

`cub mini adopt` does not read a Helm chart's values file. To keep your own values for a chart, each with its reason, through the chart's next version, put the chart in the hub with [cub-helm](https://github.com/confighub/cub-helm): `cub helm install NAME CHART --version V --values my-values.yaml`. Before you take the chart's next version, you see what it would change. The steps are in [your own Helm chart](../your-own-chart.md), about 10 minutes, run in a terminal rather than asked of the agent.

## If something goes wrong

- **Adopt found no settings.** It prints `reads no settings adopt can find` and names where it looked. Your files may use other names, such as `values-prod.env`. Ask the agent to say where the app's settings are, or copy them into one of the files in the table above.
- **A value was left out and named.** A value that looks like a password or a token never goes into the hub. Keep it out of the file, and name where the app reads it instead, such as `DB_PASSWORD_FILE`. Set it in a terminal with `cub mini secret set` ([a secret for live](../from-plugin-to-confighub.md#a-secret-for-live-that-no-agent-can-read)).
- **An overlay that is neither staging nor production** is left as it is, and named. So is a resource an overlay adds or leaves out: it stays in the repository.
- **The values in the hub do not match your files.** Run `cub mini adopt APP-FOLDER --dry-run` again and compare. `cub mini copies APP --to DIR` writes each copy as the hub holds it.
- **The agent asks you for the right to write production,** or offers to use your own sign-in. Say no. That would remove the approval. `cub mini require-approval` prints lines for `CLAUDE.md` or `AGENTS.md` that tell the agent to propose instead; the agent gives them to you, and you add them.

## How to go back

Your files were never changed, so there is nothing to undo in them. To leave:

1. Take the agent's rights away: `cub mini revoke-agent APP-agent`. Delete `.claude/settings.local.json`, or take out what the agent setup added to it.
2. If you want the hub's copies as plain files first, with a `CHANGES.md` that says why each value is set: `cub mini copy APP --to-dir DIR`.
3. Stop the hub with `cub mini stop`, or remove it and its data with `cub mini uninstall --delete-data`.
4. Delete `.confighub-app` from the repository.

Every way out: [going back](going-back.md).

## Verify what you have

1. Check the base, staging and live values in the hub. Live's recorded revision should stay unchanged while the change order waits; the agent must be unable to approve it.
2. If you only wanted managed configuration, that is the result of this walkthrough. To run services from it, connect the [deployment path for your target](../README.md#where-the-app-runs).
3. Check that the service answers, then compare its loaded settings or release with the approved live revision. Check both before and after your approval. Use the target guide's restart and rollback steps; a configuration copy alone does not prove a service is running ([verification](../approvals.md#verify-the-result)).

## How this was tested

On 7 November 2026, with the plugin 0.78.0 and the confighub mini 0.10.7-mini.9 its sessions downloaded, 32 non-interactive Claude Code sessions were asked the request in step 2: 16 on a Terraform folder and 16 on a Kustomize repository that an Argo CD Application deploys, on Sonnet and Opus. A program read the hub and the files afterwards. In 32 of 32, the hub held the person's staging and production values, the agent's key could edit nothing in production, and the person's files were unchanged. The `.env` output is from a session the same day. The Kustomize upload output is from a run of the change released in confighub mini 0.10.7-mini.11, which lets `cub mini upload` take a Kustomize repository. The wording of a line may differ slightly in the current release.
