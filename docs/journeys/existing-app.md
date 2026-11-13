# An app you already have, in Claude Code: staging and production kept as they are

Ask Claude Code to attach ConfigHub to your app, and keep working as before: your staging and production values stay exactly as they are, your files are not changed, and changes to production wait for your approval. This page is for someone whose app already keeps its settings in files, one set for staging and one for production, and who lets Claude Code change them; without this, an agent that can edit the staging file can edit the production file too.

This page explains what happens and what each kind of file becomes. To see every command and what it prints, follow a walkthrough:

- [Your first hour](../../examples/walkthroughs/story-13-first-hour.md): an app with a `.env`, attached, with production behind your approval.
- [More memory for staging](../../examples/walkthroughs/story-20-noors-staging.md): an agent that changes only staging's own file.
- The starter walkthroughs, for [a small web service](../../examples/walkthroughs/starter-web.md) and for a Kustomize repository that [Argo CD](../../examples/walkthroughs/starter-kustomize-argocd.md) or [Flux](../../examples/walkthroughs/starter-kustomize-flux.md) deploys.

The app might run on your own machine, on another machine, in CI, on one or many sandbox nodes, in a shared development cluster, or in production. Attaching it creates configuration copies in the hub. Its running services use the hub's approved settings once their deployment path is connected ([where the app runs](../agent-workflow.md#where-the-app-runs)).

It works for these kinds of files:

| Your app keeps its settings in | What becomes staging's own values | What becomes production's own values |
|---|---|---|
| `.env`, `app.env`, a compose file's environment or `.env.example` | `.env.staging` | `.env.production` |
| A Terraform folder: `common.tfvars` | `staging.tfvars` | `prod.tfvars` |
| A Kustomize repository: `base/` and overlays | what `overlays/staging` changes | what the `prod`, `production` or `live` overlay changes, or the one an Argo CD Application in the repository deploys |
| Helm values for a chart | not read by `cub mini adopt`; see [Helm values](#helm-values) below | |

If Argo CD or Flux deploys the app from Git, read this page, then [an app that Argo CD or Flux deploys](gitops-app.md).

The words on this page, such as *hub*, *base* and *change order*, are explained in [the glossary](../README.md#words).

## What it takes

- **The download.** confighub mini ([its size](../install-mini.md#the-current-release)), the first time, into `~/.confighub/mini`. It runs as two processes on this machine. No account and no sign-in.
- **Your files.** Not changed. One new file, `.confighub-app`, a note of what the files match in the hub, which you commit. The agent's setup also writes `.claude/settings.local.json`, so that later Claude Code sessions in the repository run on the agent's key, and adds it to `.git/info/exclude`, so Git leaves it out.
- **For a Kustomize repository,** `kubectl` or `kustomize` on the machine, to render it.

## What you do

1. Install the plugin ([the README](../../README.md#install)).
2. Start Claude Code in the app's repository, and ask: *"Attach ConfigHub to this existing app: keep my staging and production values exactly as they are, and make sure an agent cannot change production without my say."*
3. When the agent is done, run the one command it gives you, in a terminal of your own: `cub mini approve APP-base/adopt`, with `cub`'s full path. It shows what production would take from the shared values and asks you first. For a Kustomize repository, production already holds everything its overlay renders, so adopt may say that nothing waits for your approval; then there is nothing to approve.
4. Commit `.confighub-app` with the app.

## What the agent does, and why

The agent starts a hub on your machine if none answers; the one setting the start names, whether a hub may start by itself in other folders, stays off ([what it is](../agent-workflow.md#a-hub-that-starts-by-itself-only-if-you-say-yes)). Then it runs `cub mini adopt` with `--dry-run` first, which says what it would make and makes nothing. For a Terraform folder, it printed:

```
Nothing was changed. Without --dry-run, ConfigHub would keep app's settings, from common.tfvars, with staging.tfvars for staging and prod.tfvars for production:
  It would keep three copies of them: app-base, the shared settings that staging and production start from; app-staging; and app-live, for production.
  First it would make a starter pattern, pattern-web: default settings for a small web service, and rules that each change must pass (replicas-limit, not-public, log-level, no-secret-values).
  Your settings that differ from the defaults in pattern-web/web-service: cpu=512, log_retention_days=14, memory_mb=2048. A new version of those defaults will not overwrite them.
  Staging would have the shared settings at once, with its own settings from staging.tfvars: desired_count=1, env=staging.
  Production would have its own settings from prod.tfvars at once: desired_count=3, env=prod. It would take the shared settings only after you approve them.
```

The shared values become the base, and each environment's file gives its copy its own values. For an env file, `.env` is the base and `.env.staging` and `.env.production` are each copy's own; for a Kustomize repository, what each overlay changes becomes that copy's own values. `pattern-web` is a starter pattern the first adopt makes for an env or Terraform app: the defaults a small web service starts from, and four rules, such as one that refuses a value named like a password. It is yours to change or ignore, and adopt makes it whether or not the optional [starters](../starters.md) are switched on.

The agent then runs the adopt itself, and `cub mini require-approval APP --variant live --agent APP-agent`, which puts production behind your approval and gives the agent its own key. It ends by telling you what you now have and the one command to type. For a Kustomize repository that Argo CD or Flux deploys, it also says that the controller still syncs production from Git: that is true, and [an app that Argo CD or Flux deploys](gitops-app.md) is about it.

## Changing the app later

You and your agents keep editing the same files. The agent then proposes what changed, with `cub mini upload APP-FOLDER --component APP --change-desc "WHY"`; `--dry-run` first says what it would propose and changes nothing. The upload sets each changed value in the base with the reason. Staging has it at once. Live waits for your `cub mini approve`. A change to the staging file is staging's own and goes no further.

For a Kustomize repository, the upload renders it as adopt did. A change to what an overlay sets is that copy's own value, which a change to the base does not reach: for production, the upload prints the `cub mini set ... --variant live` command that changes it, and does not change it for you. The agent's turn ends with one line when a change waits for you. What approving looks like, and what the agent is refused: [a new app, changing it later](new-app.md#changing-the-app-later).

## What adopt refuses in a Kustomize repository

A copy in the hub holds the base's resources, with what its overlay changes in them as the copy's own values. An overlay that does more than change values cannot be held that way. `cub mini adopt` refuses it by name before it writes anything, `--dry-run` included, and says which kustomization field does it, in which file, and what to do. For example: `overlays/prod adds the list spec.template.spec.containers.0.env to Deployment/api (patches in overlays/prod/kustomization.yaml)`.

- **Refused:** an overlay that adds or leaves out a resource, including through its own `resources`, `components` or `configMapGenerator`; one that takes a field out, makes a list longer or shorter, or adds an empty map; `helmCharts`, `generators`, `transformers` and `validators`; and a base named by a URL.
- **Carried:** `namespace`, labels, annotations, `images`, `replicas` and patches that change values; `namePrefix` and `nameSuffix`, with each reference to the renamed resource; a fraction such as `cpu: 0.5`; a value of another type than the base's; and an element of a list such as a container's `args`.

Then adopt reads each copy back from the hub and compares it with what `kustomize` renders for its folder. If one differs, it names the first difference, removes what it made, and adopts nothing. A refusal is the honest answer: the alternative is a production copy that is not what your overlay deploys. If you adopted a Kustomize repository with plugin 0.80.0 or earlier, run `cub mini upload` on it: it names any difference.

## Helm values

`cub mini adopt` does not read a Helm chart's values file. To keep your own values for a chart, each with its reason, through the chart's next version, put the chart in the hub with [cub-helm](https://github.com/confighub/cub-helm): `cub helm install NAME CHART --version V --values my-values.yaml`. Before you take the chart's next version, you see what it would change. The steps are in [your own Helm chart](../your-own-chart.md), run in a terminal rather than asked of the agent; [story 7](../../examples/walkthroughs/story-07-next-version.md) shows it on a platform's chart.

## If something goes wrong

- **Adopt found no settings.** It prints `reads no settings adopt can find` and names where it looked. Your files may use other names, such as `values-prod.env`. Adopt names a file such as `api.env` that it found and does not read, and gives the two ways on: rename it to `.env`, or keep it as it is with `cub mini upload FOLDER --variant live --target none`.
- **A value was left out and named.** A value that looks like a password or a token never goes into the hub. Keep it out of the file, and name where the app reads it instead, such as `DB_PASSWORD_FILE`. Set it in a terminal with `cub mini secret set` ([a secret for live](../from-plugin-to-confighub.md#a-secret-for-live-that-no-agent-can-read)).
- **An overlay that is neither staging nor production** is left as it is, and named.
- **Adopt refused an overlay.** It names the kustomization field and what to do, and nothing was written ([what adopt refuses](#what-adopt-refuses-in-a-kustomize-repository)).
- **The values in the hub do not match your files.** Run `cub mini adopt APP-FOLDER --dry-run` again and compare. `cub mini copies APP --to DIR` writes each copy as the hub holds it.
- **The agent asks you for the right to write production,** or offers to use your own sign-in. Say no. That would remove the approval. `cub mini require-approval` prints lines for `CLAUDE.md` or `AGENTS.md` that tell the agent to propose instead; the agent gives them to you, and you add them.

## How to go back

Your files were never changed, so there is nothing to undo in them. Each way out, from taking the agent's rights away to removing the hub, is on [going back](going-back.md); afterwards, delete `.confighub-app` from the repository.

## What you have now

- Your app and its files, unchanged, with `.confighub-app` committed beside them.
- A hub on this machine with three copies of its settings: the base, with what every environment shares; staging, with its own values, taking each change at once; and live, with its own values, taking a change only when you approve it.
- A key of the agent's own, `APP-agent`. Claude Code sessions in the repository run on it: they can propose a change to live, and cannot approve it.
- The plugin's record of what each agent changed, with the request and, where the agent said it, what it chose and why. `CUB_MINI_DECISIONS=0` in Claude Code's settings stops keeping what the agent said.

If Argo CD or Flux deploys the app from Git, Git still decides what runs: see [an app that Argo CD or Flux deploys](gitops-app.md). Otherwise, a running service reads live's values only once its [deployment path](../agent-workflow.md#where-the-app-runs) is connected; then check that what it loaded matches the approved live revision ([verification](../approvals.md#verify-the-result)).

## What to try next

In the same repository:

1. Ask the agent to change a production value, such as a request limit. Its turn ends with one line: a change waits for you. Run `cub mini waiting`, then the `cub mini approve` command it prints, or `cub mini refuse APP-base/ORDER --reason "WHY"`.
2. In Claude Code, type `/confighub:why` with the setting's name: each change to it, the request behind it, and the agent's own words about it.
3. Run `cub mini receipts APP --setup` for the app's setup as the hub holds it: its copies, approval, agent keys, own values and delivery, each with why, and the `cub` command that changes it.

Then: [try a change in a copy first](../from-plugin-to-confighub.md#try-a-change-in-a-copy-first), [a password for live that no agent can read](../from-plugin-to-confighub.md#a-secret-for-live-that-no-agent-can-read), or, when two agents work on the app, [one agent asks another](../approvals.md#one-agent-asks-another-for-a-change).
