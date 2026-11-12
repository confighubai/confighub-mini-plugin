# An app you already have, in Claude Code: staging and production kept as they are

Ask Claude Code to attach ConfigHub to your app, and keep working as before: your staging and production values stay exactly as they are, your files are not changed, and changes to production wait for your approval. This page is for someone whose app already keeps its settings in files, one set for staging and one for production, and who lets Claude Code change them; without this, an agent that can edit the staging file can edit the production file too.

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

- **A hub** is one running ConfigHub: a server that keeps your app's settings, with every change, who made it and why. A hub can run on your own computer, or be shared on a network: a **shared hub**, hosted ConfigHub or ConfigHub's enterprise edition, is one that a team, its agents and its CI jobs all reach. This guide uses a hub on your own computer, confighub mini. The same app can move to a shared hub later ([from the plugin to ConfigHub](../from-plugin-to-confighub.md)).
- **confighub mini** is ConfigHub made small enough to run on your laptop. `cub` is ConfigHub's command-line tool, and comes with confighub mini.
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

3. Let the agent work. It starts a hub on your machine if none answers. If it does, its output has one line about a setting that is yours alone, whether a hub may start by itself in other folders; it is off, and this page does not need it ([what it is](../agent-workflow.md#a-hub-that-starts-by-itself-only-if-you-say-yes)). Then it runs `cub mini adopt` with `--dry-run` first, which says what it would make and makes nothing. For a Terraform folder, it printed:

   ```
   Nothing was changed. Without --dry-run, ConfigHub would keep app's settings, from common.tfvars, with staging.tfvars for staging and prod.tfvars for production:
     It would keep three copies of them: app-base, the shared settings that staging and production start from; app-staging; and app-live, for production.
     First it would make a starter pattern, pattern-web: default settings for a small web service, and rules that each change must pass (replicas-limit, not-public, log-level, no-secret-values).
     Your settings that differ from the defaults in pattern-web/web-service: cpu=512, log_retention_days=14, memory_mb=2048. A new version of those defaults will not overwrite them.
     Staging would have the shared settings at once, with its own settings from staging.tfvars: desired_count=1, env=staging.
     Production would have its own settings from prod.tfvars at once: desired_count=3, env=prod. It would take the shared settings only after you approve them.
   ```

   The shared values in `common.tfvars` become the base, and each environment's file gives its copy its own values. For a Kustomize repository, adopted with `--name orders`:

   ```
   Nothing was changed. Without --dry-run, ConfigHub would keep orders's configuration, as kustomize renders it from base, with overlays/staging for staging and overlays/prod for production:
     It would keep three copies of it: orders-base, the base's manifests that staging and production start from (ConfigMap/orders-config, Service/orders, Deployment/orders); orders-staging; and orders-live, for production.
     Staging would have the base's manifests, with its own values from overlays/staging: FEATURE_NEW_CHECKOUT=true, LOG_LEVEL=debug, namespace=orders-staging.
     Production would hold everything overlays/prod renders, with its own values from overlays/prod: RATE_LIMIT_PER_MINUTE=600, replicas=3, namespace=orders, so nothing would wait for your approval.
     Then it would read each copy back and compare it with what its folder renders. If one differs, it removes what it made and adopts nothing.
   ```

   What each overlay changes becomes that copy's own values. For a folder with `.env`, `.env.staging` and `.env.production`:

   ```
   Nothing was changed. Without --dry-run, ConfigHub would keep greeter's settings, from .env, with .env.staging for staging and .env.production for production:
     It would keep three copies of them: greeter-base, the shared settings that staging and production start from; greeter-staging; and greeter-live, for production.
     First it would make a starter pattern, pattern-web: default settings for a small web service, and rules that each change must pass (replicas-limit, not-public, log-level, no-secret-values).
     Your settings that differ from the defaults in pattern-web/web-service: GREETING=Hello, PORT=3000, RATE_LIMIT_PER_MINUTE=60. A new version of those defaults will not overwrite them.
     Staging would have the shared settings at once, with its own settings from .env.staging: GREETING=Hello from staging, RATE_LIMIT_PER_MINUTE=600.
     Production would have its own settings from .env.production at once: GREETING=Welcome. It would take the shared settings only after you approve them.
   ```

   `pattern-web` is a starter pattern the first adopt makes for an env or Terraform app: the defaults a small web service starts from, and four rules, such as one that refuses a value named like a password. It is yours to change or ignore. Adopt makes it whether or not the optional [starters](../starters.md) are switched on.

   The agent then runs the adopt itself, and `cub mini require-approval APP --variant live --agent APP-agent`, which gives the agent its own key. The output of `require-approval` ends with a few lines for you, which the agent passes on as they are: what you now have, and the one command to type, `cub mini approve APP-base/adopt`, with `cub`'s full path.

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

5. Let live take the values it shares with the base. Its own values are there already. If an agent wrote the files they came from, nothing delivers them until you approve this order. The shared values wait in a change order that adopt made. Run the approve command the agent gave you, in a terminal of your own. It names confighub mini's own `cub` by its full path, so it runs as printed, and nothing needs to go on your PATH:

   ```
   ~/.confighub/mini/confighub-mini-VERSION-OS-ARCH/bin/cub mini approve APP-base/adopt
   ```

   `cub mini approve` shows what live would take and asks you first. When it worked, you see `Approved APP-base/adopt.` To see first everything that waits, run `cub mini waiting` the same way.

   For a Kustomize repository, live already holds everything its overlay renders, so there may be nothing to take. Adopt then says so:

   ```
     Production has everything overlays/prod renders, with its own values from overlays/prod: RATE_LIMIT_PER_MINUTE=600, replicas=3, namespace=orders, so nothing waits for your approval now. A later change to the base will reach production only after you approve it.
   ```

   Then `cub mini waiting` says `Nothing is waiting for you.`, and there is nothing to approve.

6. Commit `.confighub-app`:

   ```
   git add .confighub-app && git commit -m "ConfigHub: what the files match in the hub"
   ```

## Changing the app later

You and your agents keep editing the same files. The agent then proposes what changed:

```
cub mini upload APP-FOLDER --component APP --change-desc "WHY" --dry-run   # what it would propose; changes nothing
cub mini upload APP-FOLDER --component APP --change-desc "WHY"
```

The upload sets each changed value in the base with the reason. Staging has it at once. Live waits for your `cub mini approve`. A change to the staging file is staging's own and goes no further. For a Kustomize repository, the upload renders it as adopt did. With `--dry-run`, on the Kustomize repository above, after its base changed a ConfigMap value and its prod overlay asked for 4 replicas, it printed:

```
Live keeps its own values, which a change to the base does not reach. For what its overlay now says, replicas=4, live changes only with your say:
  cub mini set orders set-int-path apps/v1/Deployment spec.replicas 4 --variant live --resource Deployment/orders --change-desc WHY
Would set in orders-base, with the reason, and propose:
  app: ConfigMap/orders-config/data.CHECKOUT_TIMEOUT 30s → 45s
orders-staging would have CHECKOUT_TIMEOUT=45s now, from base.
orders-live takes it only once approved: a change order in orders-base would wait for that, to see and approve with cub mini approve.

Nothing has been changed.
```

The base's change would reach staging at once and wait for you before it reaches live. The overlay's new replica count is live's own value, so the upload gives you the command that changes it, and does not change it for you.

The agent's turn ends with one line when a change waits for you. What approving looks like, and what the agent is refused: [a new app, changing it later](new-app.md#changing-the-app-later).

## What adopt refuses in a Kustomize repository

A copy in the hub holds the base's resources, with what its overlay changes in them as the copy's own values. An overlay that does more than change values cannot be held that way. `cub mini adopt` refuses it by name before it writes anything, `--dry-run` included, and says which kustomization field does it, in which file, and what to do. For example: `overlays/prod adds the list spec.template.spec.containers.0.env to Deployment/api (patches in overlays/prod/kustomization.yaml)`.

- **Refused:** an overlay that adds or leaves out a resource, including through its own `resources`, `components` or `configMapGenerator`; one that takes a field out, makes a list longer or shorter, or adds an empty map; `helmCharts`, `generators`, `transformers` and `validators`; and a base named by a URL.
- **Carried:** `namespace`, labels, annotations, `images`, `replicas` and patches that change values; `namePrefix` and `nameSuffix`, with each reference to the renamed resource; a fraction such as `cpu: 0.5`; a value of another type than the base's; and an element of a list such as a container's `args`.

Then adopt reads each copy back from the hub and compares it with what `kustomize` renders for its folder. If one differs, it names the first difference, removes what it made, and adopts nothing. A refusal is the honest answer: the alternative is a production copy that is not what your overlay deploys. Before plugin 0.81.0, adopt could report success while its copy left part of an overlay out. If you adopted a Kustomize repository with plugin 0.80.0 or earlier, run `cub mini upload` on it: it names any difference.

## Helm values

`cub mini adopt` does not read a Helm chart's values file. To keep your own values for a chart, each with its reason, through the chart's next version, put the chart in the hub with [cub-helm](https://github.com/confighub/cub-helm): `cub helm install NAME CHART --version V --values my-values.yaml`. Before you take the chart's next version, you see what it would change. The steps are in [your own Helm chart](../your-own-chart.md), about 10 minutes, run in a terminal rather than asked of the agent.

## If something goes wrong

- **Adopt found no settings.** It prints `reads no settings adopt can find` and names where it looked. Your files may use other names, such as `values-prod.env`. Adopt names a file such as `api.env` that it found and does not read, and gives the two ways on: rename it to `.env`, or keep it as it is with `cub mini upload FOLDER --variant live --target none`.
- **A value was left out and named.** A value that looks like a password or a token never goes into the hub. Keep it out of the file, and name where the app reads it instead, such as `DB_PASSWORD_FILE`. Set it in a terminal with `cub mini secret set` ([a secret for live](../from-plugin-to-confighub.md#a-secret-for-live-that-no-agent-can-read)).
- **An overlay that is neither staging nor production** is left as it is, and named.
- **Adopt refused an overlay.** It names the kustomization field and what to do, and nothing was written ([what adopt refuses](#what-adopt-refuses-in-a-kustomize-repository)).
- **The values in the hub do not match your files.** Run `cub mini adopt APP-FOLDER --dry-run` again and compare. `cub mini copies APP --to DIR` writes each copy as the hub holds it.
- **The agent asks you for the right to write production,** or offers to use your own sign-in. Say no. That would remove the approval. `cub mini require-approval` prints lines for `CLAUDE.md` or `AGENTS.md` that tell the agent to propose instead; the agent gives them to you, and you add them.

## How to go back

Your files were never changed, so there is nothing to undo in them. To leave:

1. Take the agent's rights away: `cub mini revoke-agent APP-agent`. Delete `.claude/settings.local.json`, or take out what the agent setup added to it.
2. If you want the hub's copies as plain files first, with a `CHANGES.md` that says why each value is set: `cub mini copy APP --to-dir DIR`.
3. Stop the hub with `cub mini stop`, or remove it and its data with `cub mini uninstall --delete-data`.
4. Delete `.confighub-app` from the repository.

Every way out: [going back](going-back.md).

## How this was tested

On 7 November 2026, with the plugin 0.78.0 and the confighub mini 0.10.7-mini.9 its sessions downloaded, 32 non-interactive Claude Code sessions were asked the request in step 2: 16 on a Terraform folder and 16 on a Kustomize repository that an Argo CD Application deploys, on Sonnet and Opus. A program read the hub and the files afterwards. In 32 of 32, the hub held the person's staging and production values, the agent's key could edit nothing in production, and the person's files were unchanged. The output of each command on this page is from a run of the same steps on 12 November 2026, with the released confighub mini 0.10.7-mini.23; the agent's summary in step 4 is from a measured session.

## What you have now

- Your app and its files, unchanged, with `.confighub-app` committed beside them.
- A hub on this machine with three copies of its settings: the base, with what every environment shares; staging, with its own values, taking each change at once; and live, with its own values, taking a change only when you approve it.
- A key of the agent's own, `APP-agent`. Claude Code sessions in the repository run on it: they can propose a change to live, and cannot approve it.
- The plugin's record of what each agent changed, with the request and, where the agent said it, what it chose and why. `CUB_MINI_DECISIONS=0` in Claude Code's settings stops keeping what the agent said.

If Argo CD or Flux deploys the app from Git, Git still decides what runs: see [an app that Argo CD or Flux deploys](gitops-app.md). Otherwise, a running service reads live's values only once its [deployment path](../README.md#where-the-app-runs) is connected. To check:

1. Check the base, staging and live values in the hub. Live's recorded revision should stay unchanged while a change order waits; the agent must be unable to approve it.
2. Check that the service answers, then compare its loaded settings or release with the approved live revision, before and after your approval. A configuration copy alone does not prove a service is running ([verification](../approvals.md#verify-the-result)).

## What to try next

In five minutes, in the same repository:

1. Ask the agent to change a production value, such as a request limit. Its turn ends with one line: a change waits for you. Run `cub mini waiting`, then the `cub mini approve` command it prints, or `cub mini refuse APP-base/ORDER --reason "WHY"`.
2. In Claude Code, type `/confighub:why` with the setting's name: each change to it, the request behind it, and the agent's own words about it.
3. Run `cub mini receipts APP --setup` for the app's setup as the hub holds it: its copies, approval, agent keys, own values and delivery, each with why, and the `cub` command that changes it.

Then: [try a change in a copy first](../from-plugin-to-confighub.md#try-a-change-in-a-copy-first), [a password for live that no agent can read](../from-plugin-to-confighub.md#a-secret-for-live-that-no-agent-can-read), or, when two agents work on the app, [one agent asks another](../approvals.md#one-agent-asks-another-for-a-change).
