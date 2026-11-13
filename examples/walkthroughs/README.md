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

## User stories

| Story | What you get | Starts with |
|---|---|---|
| [1. Dan: "I don't know what's wrong. Please fix it."](story-01-find-the-fault.md) | Find the fault in a customer's platform, keep the two changes they meant with their reasons, and hand it back as files for their Git | confighub mini |
| [2. George's colleague: "Run my app, and keep my changes when George updates it"](story-02-keep-your-changes.md) | Change an app someone else made, with a reason each time, and keep every change through their update | confighub mini |
| [7. The customer, months later: "Take the platform's next version, and keep the change we had to make"](story-07-next-version.md) | Take a platform's next version, about a hundred changes, and keep the one value you set on purpose, with its reason | confighub mini |
| [8. An agent's own configuration: "Give every team the assistant, and let each keep what it changed"](story-08-agent-config.md) | Each team keeps its own changes to a shared AI assistant through the next version, with the evaluation that explains them | confighub mini |
| [14. Sam's VM: a service that takes its settings from the hub](story-14-sam-vm.md) | A service's folder written only from approved settings; the agent holds a hub key and nothing that reaches the service | confighub mini |
| [16. Sam's app platform on one hub](story-16-app-platform.md) | An agent proposes a release, you approve it, the runtime takes it, and you roll it back in one command | confighub mini |
| [19. Sam's bad afternoon: stop it, find it, undo it](story-19-recovery.md) | One command stops every agent session and takes an agent's key away; then find its change and put it back | both |
| [20. Noor's staging: more memory, and production left alone](story-20-noors-staging.md) | An agent changes staging's own file; production changes only with your approval | confighub mini |
