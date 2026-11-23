# Walkthroughs

Each walkthrough shows one job, the commands to run, and what to expect. The tables say what you need to start.

Each walkthrough has three parts:

- **Human**, for you: the steps to follow in a terminal, what each one prints, and how to undo it.
- **Agent**, for an AI agent doing the job for you: what you would ask, what it runs, and what it must never do, such as approve a change to production.
- **Testing**, for checking that the walkthrough still works: the request given to an agent, and the commands that show whether the job was done.

Start with your app’s starter or pick one of the six examples below. [Install the local hub](../../docs/install-mini.md) if the walkthrough calls for it.

## Start here: starters

A starter gives a new app of one kind its usual settings, each with a reason ([starters](../../docs/starters.md)). Start with the walkthrough for your stack. Its Testing section says which steps ran on a real service, which ran locally and what still needs to be tried.

| Starter | What you get | Starts with |
|---|---|---|
| [web: a small web service with a `.env`](starter-web.md) | Try a change in staging, approve it for production, then undo it | the local hub |
| [kustomize-argocd: a Kustomize app that Argo CD deploys](starter-kustomize-argocd.md) | Try sending approved settings to Argo CD on a local cluster | the local hub |
| [parameter-store: an app that reads AWS Parameter Store](starter-parameter-store.md) | Try the local example. Testing also records delivery to real AWS from a shared hub | the local hub |
| [vercel: an app on Vercel](starter-vercel.md) | Send approved settings to a Hobby project, or try it locally without a Vercel account | the local hub |
| [heroku: an app on Heroku in a pipeline](starter-heroku.md) | Connect from the apps' config vars, send staging to the staging app, and approve production onto the production app, with a stand-in for Heroku | both |
| [kustomize-flux: a Kustomize app that Flux deploys](starter-kustomize-flux.md) | Try sending approved settings to Flux on a local cluster | the local hub |
| [daytona: your app in your sandbox](starter-daytona.md) | Run your own app in your Daytona sandbox with staging's settings, with production behind your approval | `/confighub:staging` |
| [temporal-worker: Activity retries](starter-temporal-worker.md) | See a local Temporal worker use a new retry limit, then go back to the old one | the local hub |
| [unikraft: your service on Unikraft Cloud](starter-unikraft.md) | Connect the service your app already runs as, and approve each production change there | `/confighub:staging` |
| [stripe, supabase & resend: add-on starters](starter-addons-stripe-supabase-resend.md) | Keep Stripe test mode, Supabase pool/SSL limits, and Resend mail sandbox explicit in staging while gating live behind approval | the local hub |

For framework-specific guides, see [Next.js on Vercel](../../docs/nextjs-on-vercel.md), [Rails on Fly](../../docs/rails-on-fly.md) and [an app on Heroku](../../docs/heroku.md). Each guide says what ran and what you need to try it.

## Then these six

The clearest place to see what a hub adds: in each, an agent with ordinary tools fails or does more work where ConfigHub keeps production safe.

| Walkthrough | What you get | Starts with |
|---|---|---|
| [`cub mini`](tool-cub-mini.md) | The dozen `cub mini` commands a newcomer needs, on one small app, each next to the plain `cub` commands it stands for | the local hub |
| [13. Sam's first hour: from the page to a gate](story-13-first-hour.md) | The Claude plugin and a hub on your laptop, with no account: production behind your approval, and an agent's own approval refused | both |
| [22. Priya approves from Slack, and it counts](story-22-priya-slack.md) | Told in the Slack thread where the work was asked for; your Approve there hands you one command that records the approval as yours, and anyone else's press approves nothing (local Slack stand-in) | both |
| [21. Ana's service, sized by what it used](story-21-ana-sized.md) | A new service measured as it runs, at a stated load, and its CPU and memory proposed from that, with the measurement as the reason; production changes only with your approval | the local hub |
| [9. Dan at ACME: "What is where, and what is running?"](story-09-git-hub-and-running.md) | Git, the hub and the cluster side by side, each difference sorted, and the app handed back to Git without a restart | the local hub |
| [24. Priya's platform team's base: one base, ten apps, one bump](story-24-company-base.md) | One change to a shared base reaches every app, and each app keeps the values it set itself | the local hub |

## More tools

| Tool | What you get | Starts with |
|---|---|---|
| [The Claude plugin](tool-plugin.md) | What your agents changed in configuration and why, the warning before one undoes another, and each `/confighub:` command; then the step to a hub | the Claude plugin |
| [What your GitOps repository deploys](tool-inventory.md) | Before you change a platform team's repository: what deploys each chart and app, for which clusters, which file holds each cluster's values, and what nothing deploys. It reads files only, with no cluster, account or hub | the Claude plugin |

## More user stories

| Story | What you get | Starts with |
|---|---|---|
| [1. Dan: "I don't know what's wrong. Please fix it."](story-01-find-the-fault.md) | Find the fault in a customer's platform, keep the two changes they meant with their reasons, and hand it back as files for their Git | the local hub |
| [2. George's colleague: "Run my app, and keep my changes when George updates it"](story-02-keep-your-changes.md) | Change an app someone else made, with a reason each time, and keep every change through their update | the local hub |
| [5. Steve's agent and Temporal: "Roll this out, and wait for me before production"](starter-temporal-worker.md#testing) | The Temporal rollout rehearsal waits for approval and verifies the approved policy after the worker restarts | the local hub |
| [3. Ivan's agents: "Give each run a hub of its own, and throw it away afterwards"](story-03-a-hub-per-agent-run.md) | An agent run in a sandbox starts a hub of its own from a file, leaves its fix as files for review, and the hub is deleted; the team's shared hub never changes | the local hub |
| [4. A preview on a hub of its own: "Show me what this branch would do to production, and let me see it running"](story-04-preview-a-change.md) | What a new version would do to production, then seen running with Argo CD on a local cluster, with nothing left behind | the local hub |
| [6. Ivan: "Show me what is actually running, and who changed what"](story-06-what-runs-and-why.md) | Which customer changed what, whether anyone said why, and who breaks the image rule, one command each across every customer | the local hub |
| [7. The customer, months later: "Take the platform's next version, and keep the change we had to make"](story-07-next-version.md) | Take a platform's next version, about a hundred changes, and keep the one value you set on purpose, with its reason | the local hub |
| [8. An agent's own configuration: "Give every team the assistant, and let each keep what it changed"](story-08-agent-config.md) | Each team keeps its own changes to a shared AI assistant through the next version, with the evaluation that explains them | the local hub |
| [10. Each person on a key of their own, and moving up to the organization's shared hub](story-10-a-key-each.md) | Three parties, a key each made by its holder, and everything outside each one's part refused | the local hub |
| [11. The whole path: from an agent in Claude Code to a bank's fleet](story-11-propose-not-approve.md) | An agent proposes a change to production and is refused when it tries to approve it; production changes only with your yes | both |
| [12. The devlab: one developer, a laptop, agents, and the hubs it connects to](story-12-laptop-connects-out.md) | A laptop hub that nothing connects to, and your work copied up to the team's hosted hub with its reasons | both |
| [14. Sam's VM: a service that takes its settings from the hub](story-14-sam-vm.md) | A service's folder written only from approved settings; the agent holds a hub key and nothing that reaches the service | the local hub |
| [15. The telling: the three things you are told](story-15-the-telling.md) | A change waiting for you, an agent proposing again what you refused, and a hub something elsewhere cannot reach: and nothing else | both |
| [16. Sam's app platform on one hub](story-16-app-platform.md) | An agent proposes a release, you approve it, the runtime takes it, and you roll it back with one command and your approval | the local hub |
| [17. The portal is the agent](story-17-the-portal.md) | What runs and why, what breaks a rule, what a key may change, and a new service from a tested one, each one question to the hub | both |
| [18. Ana asks for an app, and it fits the pattern](story-18-dev-intent.md) | A new app on the team's pattern, with rules that keep a value over the limit from reaching the service, and a second app made from the first | the local hub |
| [19. Sam's bad afternoon: stop it, find it, undo it](story-19-recovery.md) | One command stops every agent session and takes an agent's key away; then find its change and put it back | both |
| [20. Noor's staging: more memory, and production left alone](story-20-noors-staging.md) | An agent changes staging's own file; production changes only with your approval | the local hub |
| [23. Theo's first app: the setup travels with it from the first prompt](story-23-theo-first-app.md) | The reason for each setting an agent writes, kept with it from the first file, and where the app came from | the Claude plugin |
| [25. Alice ships it, Bob hardens it](story-25-alice-bob-hardened.md) | A reviewer's fixes become the starter's next version: the next app starts with them, the first app takes them | the local hub |
| [26. Staging and production, seen in the app on your laptop](story-26-staging-in-your-own-app.md) | Your agent's staging change, then a production change you approved, each seen in the app as it already runs, with its files unchanged | both |
