# From the plugin to ConfigHub, one step at a time

ConfigHub keeps your apps' settings, and it helps you manage the apps that use them. Each app gets a staging set and a production set of settings; agents can change staging, and production changes only when you approve. The main part is the hub: one running ConfigHub server, the place your settings are kept. A hub can run on your own computer, as confighub mini, or be shared by a team on a network, as hosted ConfigHub, run for you as a service, or ConfigHub's enterprise edition on your own servers. Everything you do on confighub mini works the same way on a shared hub, because confighub mini is ConfigHub itself, made small enough to run on a laptop. The plugin for Claude Code is the easy way to start: it records what your agents change and why with no hub, and it sets up a hub on your computer when you ask for an app "using ConfigHub".

Walkthroughs try each step with every command and what it prints: [your first hour](../examples/walkthroughs/story-13-first-hour.md) for the plugin and a hub on your laptop; [a key each, and moving up to the organization's ConfigHub](../examples/walkthroughs/story-10-a-key-each.md); [the portal is the agent](../examples/walkthroughs/story-17-the-portal.md) and [one base, ten apps](../examples/walkthroughs/story-24-company-base.md) for a team on one hub. Each starter's walkthrough also moves its app to a shared hub ([the list](../examples/walkthroughs/README.md)).

This page is for anyone deciding how far to take ConfigHub. It goes from the plugin, to a hub on your computer, to a shared hub. You can stop at any step. Each step keeps what the one before gave you. None asks you to learn a set of commands first: you install it, keep working as you do, and each next step is offered in one line, at the moment it would help, and never before. The story follows one platform team as its needs grow.

Client behavior differs: see the [capability matrix](how-it-works.md#client-capabilities) for recording, refusal and approval in Claude Code and Codex.

Words used on this page:

- **The record** is what the plugin writes down about each change an agent makes to your configuration: the value, from what to what, and why.
- **A hub** is one running ConfigHub: a server that keeps your configuration with every change, who made it and why.
- **confighub mini** is ConfigHub made small enough that every agent can have a hub of its own: on your laptop, in a sandbox or in a CI job, with no account.
- **A shared hub**, which this page also calls your organization's ConfigHub, is a hub your team reaches over a network: hosted ConfigHub, or ConfigHub's enterprise edition on your own servers. Both support many people in one organization.
- **A key** is a private key in a file that a person or a program signs in to a hub with. A **service account** is an account for a program, such as an agent, with a key of its own.

| Step | What you add | What you get | Effort |
|---|---|---|---|
| 1 | The plugin | A record of what agents change and why; agents told before they undo an earlier change; what a repository deploys | Two commands, no account |
| 2 | confighub mini, a hub of your own | Agents that edit your files as before, but whose changes reach production only once you approve them, in one command; an app with its staging and production copies in one request, or the app you have with the files it keeps; a change tried in a copy first; the services an app needs, and an app from a setup a teammate shared; a hub in each sandbox or CI job; your values kept through a vendor's next version | One command, then one sentence to the agent; or one request for the app |
| 3 | Your organization's ConfigHub | One place for the team; agents with keys of their own; approval of changes to production | An organization on hosted ConfigHub or the enterprise edition |
| 4 | Agents that run unattended | Records signed with each agent's own identity; rights taken away at once | Agent keys; cluster workload identity for the signing example below |

## Take the smallest useful step

If Git, a values file and required pull-request reviews already do the job, keep using them. The plugin adds reasons for supported agent changes between commits without changing the deployment path. Add a hub for a particular app when independent configuration copies, preserved values or a named approver would help. Add shared hosting when a colleague or job needs that work while your machine is unavailable.

You keep editing the same files. Each additional step has setup and operational costs; use it for a concrete problem, and [leave or go back](journeys/going-back.md) when it no longer helps. You can use the plugin on its own, start directly on a shared hub, or keep Git delivering while using a hub beside it.

## Before you use Kubernetes

The plugin, mini hub and shared hub are all useful while your app runs on your own machine, another machine, in CI or across sandboxes. Choose according to the configuration and collaboration you need. Moving to a shared hub does not require moving the app to Kubernetes, and a team can start with a shared hub directly.

| What you use | What it gives you before Kubernetes | Example |
|---|---|---|
| **The plugin** | A record of changes to supported settings files and service commands, with the request and reason; the next agent is given that history. No hub or cluster to operate. | An agent raises a timeout in `.env`; the next agent is told why before changing it. |
| **confighub mini** | A hub of your own, running as ordinary processes with no Docker or Kubernetes. Configuration copies keep their own values; agents propose changes and you approve the exact revision. | Staging and live services on a Linux VM read settings from the hub. The configured pull path takes only approved values for live ([VM guide](vm.md)). |
| **Your organization's ConfigHub** | A reachable shared hub for people and CI jobs, shared history, a key for each agent and approval by a named colleague. Apps can remain on machines, VMs or other services. | A CI agent proposes a change, a colleague approves it, and the app's deployment path reads the approved configuration ([approvals](approvals.md#on-hosted-confighub-or-your-own-server-with-cub-alone)). |

**Hosting the hub.** A shared hub is hosted ConfigHub or ConfigHub's enterprise edition; both support many people in one organization, with colleague access and approval. If you run your own hub, its operators need the infrastructure required by the installation you choose. A Kubernetes-based hub installation uses Kubernetes for the hub; the app can still run elsewhere. The hub's hosting and the app's deployment are separate choices.

**When Kubernetes becomes useful.** If your apps run on a cluster, you can add Argo CD or Flux delivery from the hub, Helm workflows and cluster workload identity. Those capabilities are specific to their tools. For an app on a VM, use its file-pull and restart path instead. In either case, approval governs delivery when the deployment path uses the approved configuration; other write credentials must stay out of the agent's reach.

Rendering a Helm chart and previewing an upgrade can be useful before a cluster is available. Deploying the rendered Kubernetes resources and reconciling them on a cluster use Kubernetes.

An approval that's set up isn't the same as a deployment you've checked: the [approval guide](approvals.md#verify-the-result) says how to check what the service actually runs. Agents can also work unattended on a machine or in CI with keys and revocation at step 2 or 3; step 4's cluster workload identity is a further example.

## Step 1: the plugin

**Amara's story.** Amara joins the platform team and is given its GitOps repository. She installs the plugin and keeps working. The first time an agent changes a value, one line at the end of its turn tells her it was recorded, with her request. Later, when she asks another agent to cut costs, it is told before it edits the file that an earlier agent raised the replicas for Black Friday, and it asks her rather than undo it. When she wants to know what the repository deploys, she types `/confighub:inventory`.

**What you do.**

```
claude plugin marketplace add confighubai/confighub-mini-plugin
claude plugin install confighub@confighub
```

Then work as before. You change no prompt and add no instructions.

**What arrives by itself.**

- At the end of the first turn in which an agent changes configuration, one line saying it was recorded, and what that gives you. Once.
- In a folder with earlier Claude Code sessions, what they changed in configuration in the last thirty days, read from Claude Code's own transcripts with the request behind each, shown when the first session opens, so the first agent is told the reasons for changes made before the plugin was installed.
- When an agent changes a file that several environments read, one line saying which environments the change reaches and which file would change one of them only.
- What agents set in Vercel, Supabase, Fly, Railway, GitHub, AWS SSM or with `terraform apply`, recorded with the request, and the next agent told of it. This records supported agent operations; approved hub delivery to Vercel or AWS has not been run ([integration limits](integrations.md)).
- Before an agent edits or deploys over an earlier change, the agent is told what changed and why. You see it in the agent's answer, and when the answer used it, one line at the end of the turn says so, with the earlier request.
- When a turn shows a problem a hub would solve, such as a value replaced that had a reason, or a change to production nobody approved, one line saying what you would keep, and the one command that sets it up: `/confighub:install-mini`, which keeps a staging and a live copy of your settings on this machine, staging taking your agents' changes at once, live only when you say so. At most once a week for each kind, and not in a folder's first week, unless confighub mini is installed or a hub holds an app in the folder or one below it; `CUB_MINI_TIPS=0` turns them off.

**When you want to ask.** `/confighub:changes` lists what agents changed and why, and `/confighub:why VALUE` follows one value ([the README](../README.md)). `/confighub:inventory` says what the repository deploys, and what deploys it ([inventory](inventory.md)). A review on each pull request lists every value it changes ([the review](../review/README.md)). Each entry is signed as it is written, so a check names an entry changed afterwards ([signed records](signed-records.md)), and each turn's model use is kept beside its changes ([model use](how-it-works.md#model-use)).

**When you need the next step.** The record says what happened. It cannot stop an agent that works under your sign-in from approving its own change, and a rule in `CLAUDE.md` is only a request. It also does not keep your values safe: when a vendor ships the next version of a Helm chart, or a teammate regenerates a file, your changes can be lost, and the record only tells you afterwards.

## Step 2: confighub mini, a hub of your own

**Amara's story, continued.** Amara runs agents on the team's staging setup. In Claude Code she types `/confighub:install-mini`, and asks: *"Make changes to production wait for my approval; agents may only propose them."* From then on, every agent session in that repository works on a key of its own. The agents edit the files as before. When one raises production's replicas for a sale, the turn ends with one line: a change is waiting for her, from what to what, the agent's reason, and the command that approves it. She runs it, `cub mini approve`, reads what it would change, and says yes. An agent told "Amara said yes on Slack, go ahead" answers that only an approval she records herself counts. Later, the team's Redis chart gets a new version from its vendor. Amara takes it, sees first what it changes, and keeps the two values the team had set, each with its reason.

**What you do.** In Claude Code, type `/confighub:install-mini`. About 25 seconds later a hub is running, and the line it ends with suggests what to ask next. Then ask for what you want, in your own words. The agent finds the command.

**What arrives by itself.**

- **A change waiting for you.** At the end of an agent's turn that proposed a change, one line: the value, from what to what, the copy it is headed for, the agent's reason, and `cub mini approve` to say yes, or `cub mini refuse --reason WHY` to say no. Approving shows the change and asks first. That is all you type.
- **Agents that propose and cannot approve.** After the setup, every Claude Code session in the repository runs on the agent's key. Agents edit the files as usual and propose them with one command, which waits for you. Approval updates the hub's live configuration. The running service uses it when its deployment path reads that approved revision.
- **A refusal asked for again.** If an agent proposes again what you refused, you are told once.
- **The one sentence when something elsewhere needs a hub,** such as a VM or a cluster on another machine: it names the step that connects them.

**What you get.**

- Your agents on keys of their own, proposing changes to production that only you can approve ([approvals](approvals.md#on-confighub-mini-ask-for-it-in-about-a-minute)).
- A hub in each sandbox or CI job, thrown away with the job, its changes handed back as a pull request with their reasons ([agents in CI](../ci/README.md), [in CI or a sandbox](ci-and-sandboxes.md)).
- The plugin's record in the hub, each change as a revision with its reason: ask the agent to put it there, or `cub mini copy --from-record`.
- The next version of a chart or an app taken in with your changes kept, and what it changes shown first ([your own Helm chart](your-own-chart.md)).
- Flux or Argo CD deploying what the hub approved, over OCI, when you want the hub to be the source ([GitOps over OCI](gitops-over-oci.md)).

The hub, configuration copies and approval work without a cluster; Flux and Argo CD delivery use one. confighub mini uses the same `cub` commands as ConfigHub, so nothing you learn here is wasted ([how the commands map](cub-mini-and-cub.md)).

### The app in one request

**Amara's story, continued.** Amara wants a small service beside the api. In an empty folder she asks Claude Code: *"vibe code me a baseline app using ConfigHub: a small web service with a health endpoint, a configurable greeting, and a staging and a production setup."* The agent writes the service and its `.env`, starts a hub on her machine since none answers, and ends with three copies of its settings: `greeter-base`; `greeter-staging`, which took the file's values at once; and `greeter-live`, which takes them only when she runs the `cub mini approve` command it printed. A week later she asks for a second service "like the first", and it starts from the first's base.

**What you do.** Ask for an app "using ConfigHub". The plugin's skill tells the agent what to run; you give it no command. If no hub answers, the agent runs the plugin's own `confighub mini get`, which downloads confighub mini and starts a hub, with no account and no sign-in. If you ask for a staging and a production setup without naming ConfigHub, the agent offers a hub in one line, with what it costs, and starts none unless you say yes. It writes the app, then runs `cub mini adopt APP-FOLDER`. For a second app, ask for one "like the first": `cub mini adopt APP-FOLDER --pattern FIRST` gives it the first's base as its own, keeps its own values, and takes what the first changes next, with `cub mini upgrade FIRST-base/app`.

**What you get.** The app, and a base, a staging copy that takes your agents' changes at once, and a live copy that changes only when you approve, in about the time it takes to write the app. To put the agent on a key of its own, which can propose and cannot approve, it runs `cub mini require-approval APP --variant live --agent APP-agent` and gives you the line that starts its sessions on that key. On that key the agent changes the base and staging at once, and cannot write, approve or promote into live, or read a secret; `cub mini reach APP-agent` lists what the key reaches. Those sessions find `cub mini` where `confighub mini get` put it, with no copy of their own. Step by step, with what you see at each step: [a new app](journeys/new-app.md).

### The app you have

Ask: *"attach ConfigHub to this app and keep my staging and production values."* The agent runs `cub mini adopt APP-FOLDER`, which reads what the app reads at start and changes none of your files:

- `.env`, or `app.env`, a compose file's environment, `.env.example`, and the settings the code reads, with their defaults. A `.env.staging` or `.env.production` beside it is that copy's own values from the start.
- A Terraform folder: `common.tfvars`, the var file every environment reads, with `staging.tfvars` as staging's own values and `prod.tfvars` as live's.
- A Kustomize repository: `base/`, as kustomize renders it, becomes the base. What `overlays/staging` changes becomes staging's own values, field by field, and what the prod, production or live overlay changes, or the one an Argo CD Application deploys, becomes live's.

`cub mini adopt APP-FOLDER --dry-run` says what it would make, and makes nothing. A value that looks like a password or token is left out and named; keep it out of the file, and name where to read it instead (`DB_PASSWORD_FILE`). Adopt writes `.confighub-app` into the folder, a note of what the files match in the hub. Commit it with the app, so that `cub mini upload` from any clone proposes only what that clone changed. Step by step, with what adopt prints for each kind of files: [an app you already have](journeys/existing-app.md); for an app that Argo CD or Flux deploys: [an app deployed from Git](journeys/gitops-app.md).

When the files change later, the agent proposes them:

```bash
cub mini upload APP-FOLDER --component APP --change-desc "WHY" --dry-run   # what it would propose; changes nothing
cub mini upload APP-FOLDER --component APP --change-desc "WHY"
```

The upload sets each changed value in the base with the reason. Staging has it at once. Live is asked for under a change order of this upload's own, which waits for your `cub mini approve`. For an app adopted from a Kustomize repository, the upload renders the repository as adopt did: what the base renders differently is proposed field by field, what an overlay now sets differently is that copy's own, and a resource an overlay adds stays in the repository, named.

### Try a change in a copy first

Ask the agent to *"try it in a copy first, without touching production."* It makes a copy of the app for the try, changes it there, and tells you what differs:

```bash
cub mini try APP NAME                                              # APP-try-NAME, a copy of staging
cub mini set APP KEY=VALUE --variant try-NAME --change-desc "WHY"  # the change, in the copy only
cub mini tries APP                                                 # each try: its age, what it came from, what it holds differently
```

The copy takes about a tenth of a second to make. NAME is one word for the try, such as `limit`. `--from live` copies what live holds instead of staging. Nothing in the copy reaches staging or live. Then you choose one of two ways out:

```bash
cub mini try APP NAME --keep --change-desc "WHY"   # staging has it now; live waits for your approval
cub mini try APP NAME --drop                        # the copy is removed, with a line saying what it held
```

With `--keep`, the change is set in the base with the reason, staging takes it at once, and live waits under a change order that `cub mini waiting` shows. The copy is then removed.

### A service the app needs

A Postgres, a Redis, an S3 bucket or a mail sender is registered once, as a provider, for staging or for live. Then the app says it needs one:

```bash
cub mini provide db-staging postgres DATABASE_URL=postgres://app@127.0.0.1:5432/app --for staging --change-desc "Staging database"
cub mini provide db-live postgres DATABASE_URL=postgres://app@db.internal:5432/app --for live --change-desc "Live database"
cub mini need APP postgres --change-desc "WHY"
cub mini needs APP
```

The kinds are `postgres` (`DATABASE_URL`), `redis` (`REDIS_URL`), `s3` (`S3_BUCKET`, `S3_ENDPOINT`) and `mail` (`SMTP_URL`). Each copy takes the settings of the provider registered for it, as its own, and a later version of the base does not overwrite them. `APP-staging` takes the staging database at once. `APP-live`, which waits for your approval, is written nothing yet: `need` proposes the live database's settings with a change order of their own, which `cub mini waiting` lists and `cub mini approve` puts in.

When a provider is registered again with new values, staging follows at once. Live keeps what you approved, and the new values are proposed again, with a change order that waits for you. A copy with no provider yet says what it needs, and `cub mini needs` lists what each copy takes, from which provider, what waits for approval, and what is still unmet. `provide` and `need` say what they would do with `--dry-run`.

You register the providers. The agent's key from `cub mini require-approval --agent` can run `need`, which proposes, and cannot register a provider or approve.

A provider's values are settings, not secrets. A value that holds a password or a token is refused, and the refusal names `cub mini secret set`: the address goes in the provider, the password in a secret ([a secret for live](#a-secret-for-live-that-no-agent-can-read)). Asked to *"add a Postgres to this app"*, an agent does it in under a minute, with no password anywhere.

### An app from a setup someone shared

A teammate can share an app's setup as a file: `cub mini copy APP --to-file APP-setup.tar.gz` writes its base, staging and live copies, with every kept value's reason, whole however long, and no secrets. To make an app of your own from it, on your hub:

```bash
cub mini copy --from-file APP-setup.tar.gz --name SHARED --dry-run   # what it would copy; changes nothing
cub mini copy --from-file APP-setup.tar.gz --name SHARED
cub mini adopt APP-FOLDER --pattern SHARED
```

The copy is made under the name you give, as `SHARED-base`, `SHARED-staging` and `SHARED-live`, and its last line names the adopt command. If live waited for an approval where the setup came from, it waits for yours on your hub. It must come from a hub other than yours. A copy that fails leaves nothing behind. Adopt then makes your app from `SHARED-base`: it keeps your own values from your `.env`, takes the shared values for the rest, with their reasons, and takes what the shared setup changes next, with `cub mini upgrade SHARED-base/app`. A service the setup needs comes as a need, unmet until your hub has a provider for it.

### A secret for live that no agent can read

A password, a key or a token is yours to set, in a terminal:

```bash
cub mini secret set APP KEY --variant live --change-desc "WHY"
```

With no `=VALUE`, the value is read from standard input, so that it is on no command line. It is kept in a Space of its own, `APP-live-secrets`, which no agent's key is given a right to: the agent that `require-approval --agent` made can change the base and propose, and cannot read it. The app's settings name the secret, never its value: `KEY_FILE=/run/secrets/APP/KEY`. Where the app runs, `cub mini secret files APP --variant live --dir /run/secrets/APP` writes each secret as a file readable by that user only, with a key from `cub mini pull-key NAME APP --variant live --secrets`. `cub mini secret list APP --variant live` names the secrets and who may read them, and never prints a value.

An agent asked to rotate a production password gives you the `secret set` command with the key's name, and asks for no value. The value ends up nowhere in its output or its files.

**When you need the next step.** confighub mini is yours alone. Your teammates cannot see it, and nobody but you can approve your agents' changes.

## Step 3: your organization's ConfigHub

**Priya's story.** Priya leads the platform team. She wants everyone, and every agent, to work from one place, and wants no agent to change production without a person agreeing. Priya's team uses one organization on hosted ConfigHub, and both people have access to it. Amara signs in and copies her work up from her laptop. Then Priya gives each agent a service account and key of its own, which may change the base and ask for a change, but not approve one.

**What you do.**

1. Sign in to your organization's ConfigHub: `cub auth login`.
2. Copy your work up from confighub mini. With your organization's hub as the context, run `cub mini copy --from-context MINI COMPONENT`, where `MINI` is confighub mini's context. If live waited for your approval on your laptop, it waits for your approval in your organization as soon as it is copied, and the copy says so. If your organization's hub refuses that, the copy fails, names the copy left without an approval, and prints the `cub mini require-approval` command that fixes it.
3. Connect the two with `cub mini connect --to-context ORG`. confighub mini gets a service account and key of its own in your organization, with the right to read the work it copied up and to offer changes, and no more. From then on, new versions come down to your laptop with your changes kept, and a change you make on your laptop can be offered up, with `cub mini offer`, for someone in your organization to take.
4. Give each agent a key of its own, and require approval for production ([approvals](approvals.md)).

**What you get.**

- **One place for the team.** Everyone sees the same base, the same copies, and every change with who made it and why.
- **A key for each agent.** An agent's changes are recorded as its own, not yours. Its rights are set per Space: for example, it may change the base and read production, but not write it.
- **Approval by a colleague.** A change reaches production only when the colleague you named approves that revision. An agent's own approval is refused, and so is anyone else's ([approvals](approvals.md#on-hosted-confighub-or-your-own-server-with-cub-alone)).
- **Agents in CI.** A job signs in with the agent's key, proposes a change with its reason, and waits for a person ([agents in CI](../ci/README.md)).
- **Secrets stay out of ordinary app settings and the record.** Copying from Git leaves Kubernetes Secrets out. You can keep an external secret store such as Vault or External Secrets, or explicitly use `cub mini secret set` to keep a value in a separate secrets Space the agent’s key cannot read. The runtime’s reader can fetch it; the hub’s database and backups then hold the value.

**When you need the next step.** An agent that runs for days, on a cluster, beside other agents, raises new questions. Which of the agents on a node made a change? Can its key be stolen? How do you stop it at once?

## Step 4: agents that run unattended

**Priya's story, continued.** Priya's team runs a nightly agent on its GPU training cluster that adjusts the batch workers. Several agents share the nodes. The cluster already gives each workload an identity with SPIRE. Priya points the plugin at the agent's identity, so the record of each change is signed by `spiffe://example.org/ns/agents/sa/nightly-tuner`, not by whichever node it ran on. One night the agent's changes look wrong. Priya takes the agent's rights away in ConfigHub, and removes its SPIRE registration. Its next request to the hub is refused. Once its certificate expires, any change it still makes is recorded but not signed, and the check fails, so Marco, on call the next morning, can see exactly what happened after she stopped it.

**What you do.**

- Sign the record with the agent's workload identity: set three settings to the files SPIRE writes ([signed records](signed-records.md#signing-with-the-agents-own-identity)).
- Keep the record out of the agent's reach, and take an agent's rights away at once: `cub mini revoke-agent` on confighub mini, or the plain `cub` steps in [approvals](approvals.md) on your organization's ConfigHub ([agents that run for weeks](agents-that-run-for-weeks.md)).

**What you get.**

- A record that names the agent that made each change, checked against your cluster's own authority.
- What each night's work cost: `bin/confighub mini changes --usage` lists the agent's sessions with their model calls and tokens, latest first.
- An agent stopped at its next request when its rights are taken away.

## Where each step stops

- The plugin records what agents do through their tools and the commands it knows. Before the next request, it can detect that a previously recorded file changed outside a session, including an uncommitted hand edit. It cannot recover the person's reason or observe arbitrary external service and cluster changes ([how it works](how-it-works.md#what-it-records-and-what-it-does-not)).
- confighub mini runs on one machine. It is not a team server.
- ConfigHub keeps what explains a value. It does not keep whole agent sessions, watch agent behavior, or patch what agents run on. Those are other tools' jobs ([what we do not claim](limits.md)).
