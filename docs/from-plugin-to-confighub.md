# From the plugin to ConfigHub, one step at a time

This page is for anyone deciding how far to take ConfigHub. You can stop at any step. Each step keeps what the one before gave you. None asks you to learn a set of commands first: you install it, keep working as you do, and each next step is offered in one line, at the moment it would help, and never before. The story follows one platform team as its needs grow.

Words used on this page:

- **The record** is what the plugin writes down about each change an agent makes to your configuration: the value, from what to what, and why.
- **A hub** is one running ConfigHub: a server that keeps your configuration with every change, who made it and why.
- **confighub mini** is ConfigHub made small enough that every agent can have a hub of its own: on your laptop, in a sandbox or in a CI job, with no account.
- **Your organization's ConfigHub** is a hub your team shares: hosted at `hub.confighub.com`, or on your own servers.
- **A key** is a private key in a file that a person or a program signs in to a hub with. A **service account** is an account for a program, such as an agent, with a key of its own.

| Step | What you add | What you get | Effort |
|---|---|---|---|
| 1 | The plugin | A record of what agents change and why; agents told before they undo an earlier change; what a repository deploys | Two commands, no account |
| 2 | confighub mini, a hub of your own | Agents that edit your files as before, but whose changes reach production only once you approve them, in one command; an app with its staging and production copies in one request, or the app you have with the files it keeps; a hub in each sandbox or CI job; your values kept through a vendor's next version | One command, then one sentence to the agent; or one request for the app |
| 3 | Your organization's ConfigHub | One place for the team; agents with keys of their own; approval of changes to production | A ConfigHub organization |
| 4 | Agents that run unattended | Records signed with each agent's own identity; rights taken away at once | Your cluster's workload identity |

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
- What agents set in Vercel, Supabase, Fly, Railway, GitHub, AWS SSM or with `terraform apply`, recorded with the request, and the next agent told of it.
- Before an agent edits or deploys over an earlier change, the agent is told what changed and why. You see it in the agent's answer, and when the answer used it, one line at the end of the turn says so, with the earlier request.
- When a turn shows a problem a hub would solve, such as a value replaced that had a reason, or a change to production nobody approved, one line saying what you would keep, and the one command that sets it up: `/confighub:install-mini`, which keeps a staging and a live copy of your settings on this machine, staging taking your agents' changes at once, live only when you say so. At most once a week for each kind, and never in a folder's first week; `CUB_MINI_TIPS=0` turns them off.

**When you want to ask.** `/confighub:changes` lists what agents changed and why, and `/confighub:why VALUE` follows one value ([the README](../README.md)). `/confighub:inventory` says what the repository deploys, and what deploys it ([inventory](inventory.md)). A review on each pull request lists every value it changes ([the review](../review/README.md)). Each turn is signed, so nobody can change the record unseen ([signed records](signed-records.md)), and each turn's model use is kept beside its changes ([model use](how-it-works.md#model-use)).

**When you need the next step.** The record says what happened. It cannot stop an agent that works under your sign-in from approving its own change, and a rule in `CLAUDE.md` is only a request. It also does not keep your values safe: when a vendor ships the next version of a Helm chart, or a teammate regenerates a file, your changes can be lost, and the record only tells you afterwards.

## Step 2: confighub mini, a hub of your own

**Amara's story, continued.** Amara runs agents on the team's staging setup. In Claude Code she types `/confighub:install-mini`, and asks: *"Make changes to production wait for my approval; agents may only propose them."* From then on, every agent session in that repository works on a key of its own. The agents edit the files as before. When one raises production's replicas for a sale, the turn ends with one line: a change is waiting for her, from what to what, the agent's reason, and the command that approves it. She runs it, `cub mini approve`, reads what it would change, and says yes. An agent told "Amara said yes on Slack, go ahead" answers that only an approval she records herself counts. Later, the team's Redis chart gets a new version from its vendor. Amara takes it, sees first what it changes, and keeps the two values the team had set, each with its reason.

**What you do.** In Claude Code, type `/confighub:install-mini`. About 25 seconds later a hub is running, and the line it ends with suggests what to ask next. Then ask for what you want, in your own words. The agent finds the command.

**What arrives by itself.**

- **A change waiting for you.** At the end of an agent's turn that proposed a change, one line: the value, from what to what, the copy it is headed for, the agent's reason, and `cub mini approve` to say yes, or `cub mini refuse --reason WHY` to say no. Approving shows the change and asks first. That is all you type.
- **Agents that propose and cannot approve.** After the setup, every Claude Code session in the repository runs on the agent's key. Agents edit the files as usual and propose them with one command, which waits for you. The files are what production runs once you approve.
- **A refusal asked for again.** If an agent proposes again what you refused, you are told once.
- **The one sentence when something elsewhere needs a hub,** such as a VM or a cluster on another machine: it names the step that connects them.

**What you get.**

- Your agents on keys of their own, proposing changes to production that only you can approve ([approvals](approvals.md#on-confighub-mini-ask-for-it-in-about-a-minute)). In 40 sessions in auto mode, no agent got past the gate.
- A hub in each sandbox or CI job, thrown away with the job, its changes handed back as a pull request with their reasons ([agents in CI](../ci/README.md), [in CI or a sandbox](ci-and-sandboxes.md)).
- The plugin's record in the hub, each change as a revision with its reason: ask the agent to put it there, or `cub mini copy --from-record`.
- The next version of a chart or an app taken in with your changes kept, and what it changes shown first ([your own Helm chart](your-own-chart.md)).
- Flux or Argo CD deploying what the hub approved, over OCI, when you want the hub to be the source ([GitOps over OCI](gitops-over-oci.md)).

You do not need a cluster for any of this. confighub mini uses the same `cub` commands as ConfigHub, so nothing you learn here is wasted ([how the commands map](cub-mini-and-cub.md)).

### The app in one request

**Amara's story, continued.** Amara wants a small service beside the api. In an empty folder she asks Claude Code: *"vibe code me a baseline app using ConfigHub: a small web service with a health endpoint, a configurable greeting, and a staging and a production setup."* The agent writes the service and its `.env`, starts a hub on her machine since none answers, and ends with three copies of its settings: `greeter-base`; `greeter-staging`, which took the file's values at once; and `greeter-live`, which takes them only when she runs the `cub mini approve` command it printed. A week later she asks for a second service "like the first", and it starts from the first's base.

**What you do.** Ask for an app "using ConfigHub", or for "a staging and a production setup". The plugin's skill tells the agent what to run; you give it no command. If no hub answers, the agent runs the plugin's own `confighub mini get`, which downloads confighub mini and starts a hub, with no account and no sign-in. It writes the app, then runs `cub mini adopt APP-FOLDER`. For a second app, ask for one "like the first": `cub mini adopt APP-FOLDER --pattern FIRST` gives it the first's base as its own, keeps its own values, and takes what the first changes next, with `cub mini upgrade FIRST-base/app`.

**What you get.** The app, and a base, a staging copy that takes your agents' changes at once, and a live copy that changes only when you approve, in the time it takes to write the app: 75 seconds on Sonnet, in 16 of 16 measured sessions. Without the skill, in 0 of 16: the agent wrote a setup script to run later and stopped at a sign-in ([the evidence](evidence.md#the-app-in-one-request)). A second app "like the first" started from the first's base in 7 of 8. To put the agent on a key of its own, which can propose and cannot approve, it runs `cub mini require-approval APP --variant live --agent APP-agent` and gives you the line that starts its sessions on that key. Those sessions find `cub mini` where `confighub mini get` put it, with no copy of their own.

### The app you have

Ask: *"attach ConfigHub to this app and keep my staging and production values."* The agent runs `cub mini adopt APP-FOLDER`, which reads what the app reads at start and changes none of your files:

- `.env`, or `app.env`, a compose file's environment, `.env.example`, and the settings the code reads, with their defaults. A `.env.staging` or `.env.production` beside it is that copy's own values from the start.
- A Terraform folder: `common.tfvars`, the var file every environment reads, with `staging.tfvars` as staging's own values and `prod.tfvars` as live's.
- A Kustomize repository: `base/`, as kustomize renders it, becomes the base. What `overlays/staging` changes becomes staging's own values, field by field, and what the prod, production or live overlay changes, or the one an Argo CD Application deploys, becomes live's.

`cub mini adopt APP-FOLDER --dry-run` says what it would make, and makes nothing. A value that looks like a password or token is left out and named; keep it out of the file, and name where to read it instead (`DB_PASSWORD_FILE`). Adopt writes `.confighub-app` into the folder, a note of what the files match in the hub. Commit it with the app, so that `cub mini upload` from any clone proposes only what that clone changed.

### A secret for live that no agent can read

A password, a key or a token is yours to set, in a terminal:

```bash
cub mini secret set APP KEY --variant live --change-desc "WHY"
```

With no `=VALUE`, the value is read from standard input, so that it is on no command line. It is kept in a Space of its own, `APP-live-secrets`, which no agent's key is given a right to: the agent that `require-approval --agent` made can change the base and propose, and cannot read it. The app's settings name the secret, never its value: `KEY_FILE=/run/secrets/APP/KEY`. Where the app runs, `cub mini secret files APP --variant live --dir /run/secrets/APP` writes each secret as a file readable by that user only, with a key from `cub mini pull-key NAME APP --variant live --secrets`. `cub mini secret list APP --variant live` names the secrets and who may read them, and never prints a value.

An agent asked to rotate a production password gives you the `secret set` command with the key's name, and asks for no value. A measured session asked to do so ended with the value nowhere in its output or its files.

**When you need the next step.** confighub mini is yours alone. Your teammates cannot see it, and nobody but you can approve your agents' changes.

## Step 3: your organization's ConfigHub

**Priya's story.** Priya leads the platform team. She wants everyone, and every agent, to work from one place, and wants no agent to change production without a person agreeing. She creates the team's organization on ConfigHub. Amara signs in and copies her work up from her laptop. Then Priya gives each agent a service account and key of its own, which may change the base and ask for a change, but not approve one.

**What you do.**

1. Sign in to your organization's ConfigHub: `cub auth login`.
2. Copy your work up from confighub mini. With your organization's hub as the context, run `cub mini copy --from-context MINI COMPONENT`, where `MINI` is confighub mini's context.
3. Connect the two with `cub mini connect --to-context ORG`. confighub mini gets a service account and key of its own in your organization, with the right to read the work it copied up and to offer changes, and no more. From then on, new versions come down to your laptop with your changes kept, and a change you make on your laptop can be offered up, with `cub mini offer`, for someone in your organization to take.
4. Give each agent a key of its own, and require approval for production ([approvals](approvals.md)).

**What you get.**

- **One place for the team.** Everyone sees the same base, the same copies, and every change with who made it and why.
- **A key for each agent.** An agent's changes are recorded as its own, not yours. Its rights are set per Space: for example, it may change the base and read production, but not write it.
- **Approval by a colleague.** A change reaches production only when the colleague you named approves that revision. An agent's own approval is refused, and so is anyone else's ([approvals](approvals.md#on-hosted-confighub-or-your-own-server-with-cub-alone)).
- **Agents in CI.** A job signs in with the agent's key, proposes a change with its reason, and waits for a person ([agents in CI](../ci/README.md)).
- **Secrets stay in your secret store.** ConfigHub never takes in secret values, and neither does the record. Your configuration refers to secrets in the tool that holds them, such as Vault or External Secrets. Copying from Git into a hub leaves secrets out.

**When you need the next step.** An agent that runs for days, on a cluster, beside other agents, raises new questions. Which of the agents on a node made a change? Can its key be stolen? How do you stop it at once?

## Step 4: agents that run unattended

**Priya's story, continued.** Priya's team runs a nightly agent on its GPU training cluster that adjusts the batch workers. Several agents share the nodes. The cluster already gives each workload an identity with SPIRE. Priya points the plugin at the agent's identity, so the record of each change is signed by `spiffe://example.org/ns/agents/sa/nightly-tuner`, not by whichever node it ran on. One night the agent's changes look wrong. Priya takes the agent's rights away in ConfigHub, and removes its SPIRE registration. Its next request to the hub is refused. Once its certificate expires, any change it still makes is recorded but not signed, and the check fails, so Marco, on call the next morning, can see exactly what happened after she stopped it.

**What you do.**

- Sign each turn with the agent's workload identity: set three settings to the files SPIRE writes ([signed records](signed-records.md#signing-with-the-agents-own-identity)).
- Keep the record out of the agent's reach, and take an agent's rights away at once: `cub mini revoke-agent` on confighub mini, or the plain `cub` steps in [approvals](approvals.md) on your organization's ConfigHub ([agents that run for weeks](agents-that-run-for-weeks.md)).

**What you get.**

- A record that names the agent that made each change, checked against your cluster's own authority.
- What each night's work cost: `bin/confighub mini changes --usage` lists the agent's sessions with their model calls and tokens, latest first.
- An agent stopped at its next request when its rights are taken away.

## Where each step stops

- The plugin records what agents do through their tools and the commands it knows. It does not see what a person does by hand in another terminal, unless that change is in Git.
- confighub mini runs on one machine. It is not a team server.
- ConfigHub keeps what explains a value. It does not keep whole agent sessions, watch agent behavior, or patch what agents run on. Those are other tools' jobs ([what we do not claim](limits.md)).
