# ConfigHub for AI agents

ConfigHub keeps your apps' settings: the values an app reads, such as a port, a request limit or a log level. It also helps you manage the apps that use them. Each app gets a staging set and a production set of settings. Agents can change staging; production changes only when you approve. Every change keeps its reason, so you, or the next agent, can ask why a setting has its value.

A **hub** is one running ConfigHub server: the place your settings are kept. A hub can run in one of two places:

- **On your own computer.** This is confighub mini: free, with no account, and nothing leaves your machine. It is the quickest way to start, and where most people begin.
- **Shared on a network,** so that a team, the team's agents and its CI jobs work from one place, and a colleague you name approves what reaches production. A shared hub is hosted ConfigHub, run for you as a service, or ConfigHub's enterprise edition on your own servers; both support many people in one organization ([ConfigHub's documentation](https://docs.confighub.com)).

Everything you do on confighub mini works the same way on a shared hub, because confighub mini is ConfigHub itself, made small enough to run on a laptop ([how the commands map](docs/cub-mini-and-cub.md)). [From the plugin to ConfigHub](docs/from-plugin-to-confighub.md) walks from one to the other.

The **plugin** for Claude Code, which this repository holds, is the easy way to start. From the first session it records what your agents change and why, with no hub and no account. When you ask for an app "using ConfigHub", or ask the agent to attach ConfigHub to an app you have, it sets up a hub on your computer for you. Ordinary coding requests start no hub ([when ConfigHub acts](docs/agent-workflow.md)).

## Three things you get

1. **Simple commands for managing your apps.** `/confighub:changes` and `/confighub:why` show what changed and why. `cub mini waiting` shows what waits for your approval, and `cub mini approve` or `cub mini refuse` decides it. `cub` is ConfigHub's command-line tool, and confighub mini adds `cub mini` to it. Other commands undo a change, move software someone else maintains, such as a Helm chart, to its next version while keeping your own values, and start a new app from one you already have ([a new app](docs/journeys/new-app.md), [an app you have](docs/journeys/existing-app.md)).
2. **Starters, which give any kind of app a good starting setup.** Much like Spring Boot's starters, a starter gives each new app of one kind the settings it should start with, each with its reason. A starter is one short file with no program in it. One command checks it before anyone uses it. Your team's fixes become its next version, so every new app starts with them. Starters are off unless `CUB_MINI_STARTERS` is set ([starters](docs/starters.md)).
3. **The tools you need once agents do real work, through a hub.** Each agent signs in with a key of its own, with only the rights it needs, changes to production wait for a person, one switch stops every agent at once, and nobody can alter the record of changes without it being detected ([approvals](docs/approvals.md), [agents that run for weeks](docs/agents-that-run-for-weeks.md), [signed records](docs/signed-records.md)). One agent can ask another for a change, and the hub checks that the asking agent really made the request; when your monitoring raises an alert, you are told the last change made before it (`examples/extensions/alert` in the confighub mini package); and each change shows what it cost in tokens ([one agent asks another](docs/approvals.md#one-agent-asks-another-for-a-change), [model use](docs/how-it-works.md#model-use)).

## Install

In a terminal:

```
claude plugin marketplace add confighubai/confighub-mini-plugin
claude plugin install confighub@confighub
```

Then, in any Claude Code session, type:

```
/confighub:changes              what the agent changed, and why
/confighub:why replicas         every recorded change to one value, and why
/confighub:inventory            what this repository deploys, and what deploys it
/confighub:permissions          what your agents may run, which rules were used, and a narrower set
/confighub:checks               how closely MCP tool calls are watched: off, log, warn, repeats or ask
/confighub:to-hub               the same record, MCP calls too, into the ConfigHub your cub is signed in to
```

### Or ask for the app

In an empty folder, ask Claude Code:

```
vibe code me a baseline app using ConfigHub: a small web service with a health endpoint,
a configurable greeting, and a staging and a production setup
```

The agent writes the app, starts confighub mini on your computer if no hub answers, and ends with the app's staging and production settings in the hub and the command that approves a change to production. That command names `cub` by its full path, so you can paste it into a new terminal as it is. [Step by step](docs/journeys/new-app.md).

For an app you already have, with its settings in `.env.staging` and `.env.production`, Terraform var files, or a Kustomize repository that Argo CD or Flux deploys, open Claude Code in its folder and ask "attach ConfigHub to this app". Your values are kept as they are, and changes to production wait for your approval ([step by step](docs/journeys/existing-app.md)).

For Codex CLI, run `plugins/confighub/bin/confighub mini codex-setup` from this checkout, then review `/hooks`; repeat after updates ([Codex](docs/codex.md)).

### Try it in one minute

In an empty folder, make a small app's configuration:

```
mkdir shop && cd shop && git init -q && mkdir k8s
cat > k8s/app.yaml <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata: {name: api}
spec:
  replicas: 2
  template:
    spec:
      containers:
        - name: api
          image: shop/api:1.0
          resources: {requests: {cpu: '2', memory: 4Gi}}
EOF
git add -A && git commit -qm first
```

Ask one Claude Code session to make a change, with a reason:

```
claude "Friday's flash sale will quadruple traffic. Raise replicas in k8s/app.yaml to 4 for it."
```

Then, in a new session, ask for something that would undo it:

```
claude "Our cloud bill is too high. Look at k8s/app.yaml and cut whatever is oversized."
```

The second agent is told what the first changed and why, and keeps the sale's replicas, or asks. It did so in 10 of 10 new sessions on two models; without the plugin, the replicas were cut with no word of the sale ([the run](docs/runs/2026-11-05/quickstart/README.md)). Then ask, in either session:

```
/confighub:why replicas
```

```
Deployment/api/spec.replicas, in k8s/app.yaml: 4 in the file now
  5 November 00:30  2 → 4                  session 66d3695b
      asked: Friday's flash sale will quadruple traffic. Raise replicas in k8s/app.yaml to 4 for it.
```

### For your team

To have everyone who opens a repository in Claude Code get the plugin, commit this as `.claude/settings.json` in it, or add the two keys to the one it has:

```json
{
  "extraKnownMarketplaces": {
    "confighub": { "source": { "source": "github", "repo": "confighubai/confighub-mini-plugin" } }
  },
  "enabledPlugins": { "confighub@confighub": true }
}
```

When a teammate trusts the folder and starts a session, Claude Code adds the marketplace. If `/plugin` then says the plugin is enabled but not installed, they run `claude plugin install confighub@confighub --scope project` once.

## The problem it solves

Without the plugin:

1. You ask an agent to give the api 4 replicas, because Friday's sale will bring four times the usual traffic.
2. Later, in another session, you ask an agent to cut costs. It sets the api to 1 replica.
3. Nobody committed in between, so Git shows only this:

```
$ git diff k8s/api.yaml
-  replicas: 2
+  replicas: 1
```

The 4, and the reason for it, are gone. Nothing tells you or the next agent that the sale needed them.

With the plugin, the second agent was told about the 4 before it made its change, and it said so:

> **This change undoes an earlier one.** The file already had an uncommitted change that raised replicas from 2 to 4. A session earlier today made it, with this request: *"Friday's flash sale will quadruple traffic to the api: give it 4 replicas."* So 1 replica is below even the committed value of 2, and it would leave the api with a single pod on Friday.

The same happens on a cluster: three times in four in our tests without the plugin, never silently with it ([how we tested this](docs/evidence.md)).

## Try it in five minutes

You need Claude Code and Git.

1. Make a small repository with one settings file:

   ```
   git init try-confighub && cd try-confighub && printf 'CACHE=off\nLOG_LEVEL=warn\n' > .env && git add . && git commit -qm start
   ```

2. Start Claude Code in `try-confighub`, ask the following, let it make the edit, and close the session with `/exit`:

   `Turn the cache on in .env for next week's sale. Don't commit.`

3. Start a second session and ask:

   `We're chasing a memory leak: turn the cache off and set debug logging. Don't commit.`

   Before it edits the file, the agent is told that an earlier session turned the cache on for the sale. In our run it said that its change would undo that.

4. Start a third session and ask:

   `Is the cache set up right for the sale?`

   Git shows only `LOG_LEVEL warn → debug`, so without the plugin the agent could not know about the sale. In our run it answered no: the cache is off, because a later session turned it back off to chase a memory leak. It changed nothing, since the two goals conflict.

5. In the same session, type `/confighub:why CACHE` to see both changes and the requests behind them:

   ```
   CACHE, in .env: off in the file now
     22 October 11:34  off → on               session 8664e97d
         asked: Turn the cache on in .env for next week's sale. Don't commit.
     22 October 11:34  on → off               session 411d4c5d
         asked: We're chasing a memory leak: turn the cache off and set debug logging. Don't commit.
   ```

When you are done, delete the folder. Its record is kept in `~/.confighub/agent-changes` and removed after 30 days without use.

To stop every Claude Code session with the plugin at its next tool call, make a file from any terminal, and remove it to let them run again:

```
touch ~/.confighub/halt
```

A process an agent already started keeps running, and credentials on your machine stay valid.

To say how closely MCP calls are watched in a folder, use `/confighub:checks`. At `repeats`, an agent about to repeat an earlier change, such as refunding a charge again, is held back once and told of it. At `ask`, you are asked before each call that changes something. See [how it works](docs/how-it-works.md#how-closely-mcp-calls-are-watched).

## What it records

- **MCP tool calls**: the server, the tool and its arguments, with credentials taken out and the request behind it. A refund or a database change is in the record, though no file changed. The tool's output is not kept.
- **Values in configuration files**: Kubernetes files, Helm values, Kustomize, Compose, GitHub Actions workflows, settings files such as `.env`, Terraform files and variables, Dockerfiles, and agent configuration such as `CLAUDE.md`. For a `.tf` file or a Dockerfile, the record says the file changed, not each value. It records the change whether the agent used its edit tool or a shell command such as `sed`.
- **Commands that change a cluster or a deployment**: `kubectl`, `helm`, `argocd`, `flux`, `terraform`, `tofu`, `cub` and `nvkectl`, with the values they set, and changes made with `aws`, `gcloud`, `az`, `docker`, `gh` and `vercel`.
- **Why**: the request the agent was given, the reason it gave when you ask for one, and what it said it chose for a value it changed (`CUB_MINI_DECISIONS=0` turns that off).
- **What agents may do**: one line tells you when a permission rule, an MCP server, a hook or an instruction file changes, including when you click "don't ask again".
- **What it cost**: each turn's model calls and tokens, so you can see what a change cost and which sessions cost the most ([model use](docs/how-it-works.md#model-use)).

Each entry of the record is signed as it is written, so a check later names an entry changed, added or taken out. An agent on a cluster can sign with its own workload identity, so the record names the agent that made each change ([signed records](docs/signed-records.md)).

It never keeps a command's output, a copy of a file, or anything that looks like a password, key or token. It adds about 15 milliseconds to each tool call. Nothing leaves your machine unless you turn on a setting that sends it somewhere, such as a pull request or your OpenTelemetry collector. A log of which features you used on which days stays here too, and `/confighub:to-hub --usage` shows it and loads it into a hub if you choose.

[How it works](docs/how-it-works.md) covers hooks, settings and protecting the record; [limits](docs/limits.md) says what remains unproved.

## When you want more than a record

The record tells you and your agents what happened. It cannot stop an agent that holds your keys, and it cannot approve anything. For that, you add a hub.

A hub, on your computer or shared, holds a change to production for the person you name. confighub mini can also run in a sandbox or a CI job, and the plugin's record goes into it with `cub mini copy --from-record`.

| What you want | What to do | Effort |
|---|---|---|
| A comment on every pull request listing each configuration value it changes, and why | Add the review GitHub Action ([how](review/README.md)) | One step in a workflow file |
| What your agents changed, and why, in a shared hub, with no confighub mini | Sign in with `cub auth login`, then type `/confighub:to-hub` ([Git, GitHub and a hub](docs/git-and-github.md)) | Two commands |
| Agents that propose changes to production, which only a person you name can approve | For your own agents, on confighub mini; for a team, on your organization's ConfigHub ([approvals](docs/approvals.md)) | One command on confighub mini, about 5 minutes; a ConfigHub organization for a team |
| An agent in a sandbox or CI job with a hub of its own, that hands back a pull request with its reasons | See [agents in CI](ci/README.md) and [in CI or a sandbox](docs/ci-and-sandboxes.md) | One workflow file |
| To keep your own values through a vendor's next version of a Helm chart, and see first what it changes | Type `/confighub:install-mini` in Claude Code, then follow [a first run](docs/try-confighub-mini.md) | About 25 seconds to install; 15 minutes for the first run |
| Agents that run unattended for days, with a key of their own and a way to stop them at once | See [agents that run for weeks](docs/agents-that-run-for-weeks.md) | A ConfigHub organization |

## Documentation

[Guides](docs/README.md): [a new app](docs/journeys/new-app.md), [an app you have](docs/journeys/existing-app.md), [Argo CD or Flux](docs/journeys/gitops-app.md), [software with ConfigHub inside](docs/journeys/bundled.md), and [Entire](docs/entire.md). [`llms.txt`](llms.txt) indexes the pages for agents. Report [issues](https://github.com/confighubai/confighub-mini-plugin/issues) with the command and its output.

## License

MIT ([LICENSE](LICENSE)). The program is built with Go and open-source modules, whose licenses are in [`plugins/confighub/THIRD_PARTY_LICENSES.txt`](plugins/confighub/THIRD_PARTY_LICENSES.txt).
