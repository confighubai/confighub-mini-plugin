# ConfigHub for AI agents: the ConfigHub plugin and confighub mini

You are in Claude Code, making a new app or changing one you have. Install the plugin, and the app gets what a platform used to give you, around it:

- **A new app:** ask for it with "a staging and a production setup". The agent writes it and leaves a staging copy that takes changes at once and a live copy that changes only when you approve, on a hub it starts on your machine: 75 seconds, in 16 of 16 measured sessions. A second app "like the first" starts from it. [How to ask](#or-ask-for-the-app).
- **An app you have:** a folder with `.env.staging`, Terraform var files, or a Kustomize repository that Argo CD or Flux deploys. "Attach ConfigHub to this app" keeps your values exactly as they are and puts production behind your approval: 32 of 32 sessions.

Your agent makes the platform; the hub keeps it. From the first session, each value an agent sets is also recorded with your request behind it, in your files and in the services your production lives in (Vercel, Supabase, Fly, Railway, GitHub, AWS SSM, `terraform apply`, `kubectl`, `helm`), so the next agent is told why before it changes it, and you stop re-explaining. In simulated weeks with people new to ConfigHub, no agent undid an earlier change silently ([the runs](docs/evidence.md)). One page shows it in real runs: [ConfigHub for AI agents](https://confighub.github.io/helm-expt/ai-agents/).

## Install

In a terminal:

```
claude plugin marketplace add confighubai/confighub-mini-plugin
claude plugin install confighub@confighub
```

Then, in any Claude Code session, you can ask:

```
/confighub:changes              what the agent changed, and why
/confighub:why replicas         every recorded change to one value, and why
/confighub:inventory            what this repository deploys, and what deploys it
/confighub:permissions          what your agents may run, which rules were used, and a narrower set
/confighub:checks               how closely MCP tool calls are watched: off, log, warn, repeats or ask
/confighub:to-hub               the same record, MCP calls too, into the ConfigHub your cub is signed in to
```

There is no account to create and no server to run. The plugin is MIT-licensed.

### Or ask for the app

In an empty folder, with the plugin installed, ask Claude Code:

```
vibe code me a baseline app using ConfigHub: a small web service with a health endpoint,
a configurable greeting, and a staging and a production setup
```

The agent writes the app, starts confighub mini on your machine if no hub answers, and ends with the three copies and the command that approves a change to live. Before you run that command, run the `export PATH=...` line the agent gives you in the same terminal: `cub` comes with confighub mini and is not on your path yet. Ask for a second app "like the first" and it starts from the first's base. [Step by step](docs/journeys/new-app.md).

For Codex CLI, run `plugins/confighub/bin/confighub mini codex-setup` from this checkout, then review `/hooks`. Repeat after updates.

Codex can use a scoped proposal key with a separate launcher; [setup and limits](docs/approvals.md#codex-sessions-on-the-proposal-key).

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

Already use [Entire](docs/entire.md)? `entire plugin install https://github.com/confighubai/confighub-mini-plugin` adds the same record as `entire confighub`.

## What this is

This is the way in to [ConfigHub](https://docs.confighub.com) for people who work with AI agents; the plugin and this repository are MIT-licensed. ConfigHub keeps configuration with every change, who made it and why, and lets a person approve what reaches production. There are three parts:

| Part | What it is | How you start |
|---|---|---|
| **The ConfigHub plugin**, for Claude Code and Codex | Records what agents change in configuration, and why, and tells the next agent before it undoes a change | Two commands, [above](#install) |
| **confighub mini** | A hub of your own: ConfigHub itself, packaged lean, as two processes on your laptop, in an agent's sandbox or in a CI job. No Docker, no cluster, no account, and it works with the network off. A download of 48 to 73 MB | `/confighub:install-mini` in Claude Code |
| **`cub mini`** | A plugin for `cub`, ConfigHub's command-line tool, that fills in the rest of each request so the commands stay short. What you learn with it works unchanged on your organization's ConfigHub | Comes with confighub mini |

It solves four problems: agents undo each other's changes ([step by step](#the-problem-it-solves)); nothing stands between an agent and production, since a rule in `CLAUDE.md` is only a request, while with a hub the agent proposes on a key of its own and only the person you name approves ([approvals](docs/approvals.md)); nobody knows what a repository deploys before they change it; and a vendor's next version overwrites your changes. Each step from the plugin to your organization's ConfigHub is [one team's path, step by step](docs/from-plugin-to-confighub.md).

## The problem it solves

Here is what happens without the plugin.

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
- **Why**: the request the agent was given, and the reason it gave, when you ask agents to give one.
- **What agents may do**: one line tells you when a permission rule, an MCP server, a hook or an instruction file changes, including when you click "don't ask again".
- **What it cost**: each turn's model calls and tokens, so you can see what a change cost and which sessions cost the most ([model use](docs/how-it-works.md#model-use)).

Each turn of the record is signed when it ends, so you can check later that nobody changed it. An agent on a cluster can sign with its own workload identity, so the record names the agent that made each change ([signed records](docs/signed-records.md)).

In Codex, completed MCP calls are recorded too; at `ask`, write calls are refused with an explanation. Failed calls and `apply_patch` undo protection have [client limits](docs/runs/2026-11-09/codex-mcp/README.md).

It never keeps a command's output, a copy of a file, or anything that looks like a password, key or token. It adds about 15 milliseconds to each tool call. Nothing leaves your machine unless you turn on a setting that sends it somewhere, such as a pull request or your OpenTelemetry collector. Explicit Vercel read-back calls its CLI when you request `changes --why NAME --vercel production` ([how it works](docs/runs/2026-11-09/vercel-readback/README.md)). A log of which features you used on which days stays here too, and `/confighub:to-hub --usage` shows it and loads it into a hub if you choose.

[How it works](docs/how-it-works.md) covers hooks, settings and protecting the record; [limits](docs/limits.md) says what remains unproved.

## When you want more than a record

The record tells you and your agents what happened. It cannot stop an agent that holds your keys, and it cannot approve anything. For that, you add a hub.

A hub keeps your configuration with every change, who made it and why, and holds a change to production for the person you name. confighub mini is ConfigHub small enough for every agent to have one, on your laptop, in a sandbox or in a CI job; the plugin's record goes into it with `cub mini copy --from-record`.

| What you want | What to do | Effort |
|---|---|---|
| A comment on every pull request listing each configuration value it changes, and why | Add the review GitHub Action ([how](review/README.md)) | One step in a workflow file |
| What your agents changed, and why, in your organization's ConfigHub, with no hub on your laptop | Sign in with `cub auth login`, then type `/confighub:to-hub` ([Git, GitHub and a hub](docs/git-and-github.md)) | Two commands |
| Agents that propose changes to production, which only a person you name can approve | For your own agents, on confighub mini; for a team, on your organization's ConfigHub ([approvals](docs/approvals.md)) | One command on confighub mini, about 5 minutes; a ConfigHub organization for a team |
| An agent in a sandbox or CI job with a hub of its own, that hands back a pull request with its reasons | See [agents in CI](ci/README.md) and [in CI or a sandbox](docs/ci-and-sandboxes.md) | One workflow file |
| To keep your own values through a vendor's next version of a Helm chart, and see first what it changes | Type `/confighub:install-mini` in Claude Code, then follow [a first run](docs/try-confighub-mini.md) | About 25 seconds to install; 15 minutes for the first run |
| Agents that run unattended for days, with a key of their own and a way to stop them at once | See [agents that run for weeks](docs/agents-that-run-for-weeks.md) | A ConfigHub organization |

What you learn on your laptop works on your organization's ConfigHub too ([how the commands map](docs/cub-mini-and-cub.md)).

## Documentation

[Guides](docs/README.md): [a new app](docs/journeys/new-app.md), [an app you have](docs/journeys/existing-app.md), [Argo CD or Flux](docs/journeys/gitops-app.md), and [software with ConfigHub inside](docs/journeys/bundled.md). [`llms.txt`](llms.txt) indexes the pages for agents. Report [issues](https://github.com/confighubai/confighub-mini-plugin/issues) with the command and its output.

## License

MIT ([LICENSE](LICENSE)). The program is built with Go and open-source modules, whose licenses are in [`plugins/confighub/THIRD_PARTY_LICENSES.txt`](plugins/confighub/THIRD_PARTY_LICENSES.txt).
