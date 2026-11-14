# Walkthroughs

A walkthrough shows one job from start to finish, in one short page, with every command and what it prints. There is one for each tool, each starter and each user story.

Each walkthrough has three parts:

- **Human**, for you: the steps to follow in a terminal, what each one prints, and how to undo it.
- **Agent**, for an AI agent doing the job for you: what you would ask, what it runs, and what it must never do, such as approve a change to production.
- **Testing**, for checking that the walkthrough still works: the request given to an agent, and the commands that show whether the job was done.

To pick one: start with a tool's walkthrough to learn the commands. Pick a starter if you have an app of that kind and want it in ConfigHub. Pick a user story if it sounds like your situation. "Starts with" says what you need first: the plugin in Claude Code, confighub mini on your computer ([installing confighub mini](../../docs/install-mini.md)), or both.

## The tools

| Tool | What you get | Starts with |
|---|---|---|
| [`cub mini`](tool-cub-mini.md) | The dozen `cub mini` commands a newcomer needs, on one small app, each next to the plain `cub` commands it stands for | confighub mini |
| [The plugin](tool-plugin.md) | What your agents changed in configuration and why, the warning before one undoes another, and each `/confighub:` command; then the step to a hub | the plugin |

## Starters

A starter gives a new app of one kind its usual settings, each with a reason ([starters](../../docs/starters.md)). Each starter's walkthrough deploys an app, updates it, undoes the update, moves it to a shared hub, and deletes it.

| Starter | What you get | Starts with |
|---|---|---|
| [daytona: a sandbox experiment](starter-daytona.md) | Return a proposed change with its reason and leave production unchanged | confighub mini |
| [kustomize-argocd: a Kustomize app that Argo CD deploys](starter-kustomize-argocd.md) | Argo CD on a local kind cluster takes production from the hub with no pod restarted, and only what you approve | confighub mini |
| [kustomize-flux: a Kustomize app that Flux deploys](starter-kustomize-flux.md) | Flux on a local kind cluster takes production from the hub with no pod restarted, and only what you approve | confighub mini |
| [parameter-store: an app that reads AWS Parameter Store](starter-parameter-store.md) | Production's parameters written only from the revision you approved; the encrypted value never leaves Parameter Store (local stand-in) | confighub mini |
| [temporal-worker: Activity retries](starter-temporal-worker.md) | Observe the Temporal worker load an approved retry policy and roll it back | confighub mini |
| [unikraft: an incident banner](starter-unikraft.md) | Approve, roll back and move delivery of a banner on a disposable Unikraft Cloud service | confighub mini |
| [vercel: an app on Vercel](starter-vercel.md) | The Vercel project's production settings written only from the revision you approved (Hobby project or local stand-in) | confighub mini |
| [web: a small web service with a `.env`](starter-web.md) | Deploy, update, undo, move to a shared hub and delete, each with the commands it takes | confighub mini |

## User stories

| Story | What you get | Starts with |
|---|---|---|
| [1. Dan: "I don't know what's wrong. Please fix it."](story-01-find-the-fault.md) | Find the fault in a customer's platform, keep the two changes they meant with their reasons, and hand it back as files for their Git | confighub mini |
| [2. George's colleague: "Run my app, and keep my changes when George updates it"](story-02-keep-your-changes.md) | Change an app someone else made, with a reason each time, and keep every change through their update | confighub mini |
| 5. Steve's agent and Temporal: "Roll this out, and wait for me before production" | Not built yet: an agent rolls out a change through a Temporal workflow that waits for your approval before production | not built yet |
| [3. Ivan's agents: "Give each run a hub of its own, and throw it away afterwards"](story-03-a-hub-per-agent-run.md) | An agent run in a sandbox starts a hub of its own from a file, leaves its fix as files for review, and the hub is deleted; the team's hub never changes | confighub mini |
| [4. A preview on a hub of its own: "Show me what this branch would do to production, and let me see it running"](story-04-preview-a-change.md) | What a new version would do to production, then seen running with Argo CD on a local cluster, with nothing left behind | confighub mini |
| [6. Ivan: "Show me what is actually running, and who changed what"](story-06-what-runs-and-why.md) | Which customer changed what, whether anyone said why, and who breaks the image rule, one command each across every customer | confighub mini |
| [7. The customer, months later: "Take the platform's next version, and keep the change we had to make"](story-07-next-version.md) | Take a platform's next version, about a hundred changes, and keep the one value you set on purpose, with its reason | confighub mini |
| [8. An agent's own configuration: "Give every team the assistant, and let each keep what it changed"](story-08-agent-config.md) | Each team keeps its own changes to a shared AI assistant through the next version, with the evaluation that explains them | confighub mini |
| [9. Dan at ACME: "What is where, and what is running?"](story-09-git-hub-and-running.md) | Git, the hub and the cluster side by side, each difference sorted, and the app handed back to Git without a restart | confighub mini |
| [10. Each person on a key of their own, and moving up to the organization's ConfigHub](story-10-a-key-each.md) | Three parties, a key each made by its holder, and everything outside each one's part refused | confighub mini |
| [11. The whole path: from an agent in Claude Code to a bank's fleet](story-11-propose-not-approve.md) | An agent proposes a change to production and is refused when it tries to approve it; production changes only with your yes | both |
| [12. The devlab: one developer, a laptop, agents, and the hubs it connects to](story-12-laptop-connects-out.md) | A laptop hub that nothing connects to, and your work copied up to the team's hosted hub with its reasons | both |
| [13. Sam's first hour: from the page to a gate](story-13-first-hour.md) | The plugin and a hub on your laptop, with no account: production behind your approval, and an agent's own approval refused | both |
| [14. Sam's VM: a service that takes its settings from the hub](story-14-sam-vm.md) | A service's folder written only from approved settings; the agent holds a hub key and nothing that reaches the service | confighub mini |
| [15. The telling: the three things you are told](story-15-the-telling.md) | A change waiting for you, an agent proposing again what you refused, and a hub something elsewhere cannot reach: and nothing else | both |
| [16. Sam's app platform on one hub](story-16-app-platform.md) | An agent proposes a release, you approve it, the runtime takes it, and you roll it back with one command and your approval | confighub mini |
| [17. The portal is the agent](story-17-the-portal.md) | What runs and why, what breaks a rule, what a key may change, and a new service from a tested one, each one question to the hub | both |
| [18. Ana asks for an app, and it fits the pattern](story-18-dev-intent.md) | A new app on the team's pattern, with rules that keep a value over the limit from reaching the service, and a second app made from the first | confighub mini |
| [19. Sam's bad afternoon: stop it, find it, undo it](story-19-recovery.md) | One command stops every agent session and takes an agent's key away; then find its change and put it back | both |
| [20. Noor's staging: more memory, and production left alone](story-20-noors-staging.md) | An agent changes staging's own file; production changes only with your approval | confighub mini |
| 21. Ana's service, sized by what it used | Not built yet: a sandbox that measures what a new service uses, and sizes it from that | not built yet |
| [22. Priya approves from Slack, and it counts](story-22-priya-slack.md) | Told in the Slack thread where the work was asked for; your Approve there hands you one command that records the approval as yours, and anyone else's press approves nothing (local Slack stand-in) | both |
| [23. Theo's first app: the setup travels with it from the first prompt](story-23-theo-first-app.md) | The reason for each setting an agent writes, kept with it from the first file, and where the app came from | the plugin |
| [24. Priya's platform team's base: one base, ten apps, one bump](story-24-company-base.md) | One change to a shared base reaches every app, and each app keeps the values it set itself | confighub mini |
| [25. Alice ships it, Bob hardens it](story-25-alice-bob-hardened.md) | A reviewer's fixes become the starter's next version: the next app starts with them, the first app takes them | confighub mini |
