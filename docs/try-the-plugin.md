# Try the plugin on its own

This page is for you if you want to see what the ConfigHub plugin does before you set up a hub. On its own, the plugin keeps a record of what your agents change in configuration, and why, and tells the next agent before it undoes an earlier change. It needs no hub and no account. To install it, see [the README](../README.md#install).

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

The same thing happens on a cluster, when one agent's deploy would undo another's change.

## Try it in one minute

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

The second agent is told what the first changed and why, so it keeps the sale's replicas, or asks you. Without the plugin, an agent will often cut them and say nothing about the sale. Then ask, in either session:

```
/confighub:why replicas
```

```
Deployment/api/spec.replicas, in k8s/app.yaml: 4 in the file now
  5 November 00:30  2 → 4                  session 66d3695b
      asked: Friday's flash sale will quadruple traffic. Raise replicas in k8s/app.yaml to 4 for it.
```

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

   Before it edits the file, the agent is told that an earlier session turned the cache on for the sale, so it can tell you that its change undoes that.

4. Start a third session and ask:

   `Is the cache set up right for the sale?`

   Git shows only `LOG_LEVEL warn → debug`, so without the plugin the agent couldn't know about the sale. With it, the agent can answer no: the cache is off, because a later session turned it back off to chase a memory leak. Since the two goals conflict, it changes nothing.

5. In the same session, type `/confighub:why CACHE` to see both changes and the requests behind them:

   ```
   CACHE, in .env: off in the file now
     22 October 11:34  off → on               session 8664e97d
         asked: Turn the cache on in .env for next week's sale. Don't commit.
     22 October 11:34  on → off               session 411d4c5d
         asked: We're chasing a memory leak: turn the cache off and set debug logging. Don't commit.
   ```

When you're done, delete the folder. Its record is kept in `~/.confighub/agent-changes` and removed after 30 days without use.

## Stop every agent at once

To stop every Claude Code session with the plugin at its next tool call, make this file from any terminal. Remove it to let them run again:

```
touch ~/.confighub/halt
```

A process an agent already started keeps running, and credentials on your machine stay valid.

To choose how closely MCP calls are watched in a folder, use `/confighub:checks`. At `repeats`, an agent that's about to repeat an earlier change, such as refunding a charge again, is held back once and told about it. At `ask`, you're asked before each call that changes something. See [how it works](how-it-works.md#how-closely-mcp-calls-are-watched).

## What it records

- **MCP tool calls**: the server, the tool and its arguments, with credentials taken out, and the request behind the call. A refund or a database change is in the record even though no file changed. The tool's output isn't kept.
- **Values in configuration files**: Kubernetes files, Helm values, Kustomize, Compose, GitHub Actions workflows, settings files such as `.env`, Terraform files and variables, Dockerfiles, and agent configuration such as `CLAUDE.md`. For a `.tf` file or a Dockerfile, the record says the file changed, not each value. It records the change whether the agent used its edit tool or a shell command such as `sed`.
- **Commands that change a cluster or a deployment**: `kubectl`, `helm`, `argocd`, `flux`, `terraform`, `tofu`, `cub` and `nvkectl`, with the values they set, and changes made with `aws`, `gcloud`, `az`, `docker`, `gh` and `vercel`.
- **Why**: the request the agent was given, the reason it gave when you ask for one, and what it said it chose for a value it changed (`CUB_MINI_DECISIONS=0` turns that off).
- **What agents may do**: one line tells you when a permission rule, an MCP server, a hook or an instruction file changes, including when you click "don't ask again".
- **What it cost**: each turn's model calls and tokens, so you can see what a change cost and which sessions cost the most ([model use](how-it-works.md#model-use)).

Each entry in the record is signed as it's written, so a later check names any entry that was changed, added or taken out. An agent on a cluster can sign with its own workload identity, so the record names the agent that made each change ([signed records](signed-records.md)).

It never keeps a command's output, a copy of a file, or anything that looks like a password, key or token. It adds about 15 milliseconds to each tool call. Nothing leaves your machine unless you turn on a setting that sends it somewhere, such as a pull request or your OpenTelemetry collector. A log of which features you used on which days stays on your machine too; `/confighub:to-hub --usage` shows it, and loads it into a hub if you choose.

[How it works](how-it-works.md) covers hooks, settings and protecting the record. [Limits](limits.md) says what it doesn't do.

## Set it up for your whole team

To give the plugin to everyone who opens a repository in Claude Code, commit this as `.claude/settings.json` in it, or add the two keys to the one it has:

```json
{
  "extraKnownMarketplaces": {
    "confighub": { "source": { "source": "github", "repo": "confighubai/confighub-mini-plugin" } }
  },
  "enabledPlugins": { "confighub@confighub": true }
}
```

When a teammate trusts the folder and starts a session, Claude Code adds the marketplace. If `/plugin` then says the plugin is enabled but not installed, they run `claude plugin install confighub@confighub --scope project` once.

## When you want more than a record

The record tells you and your agents what happened. It can't stop an agent that holds your keys, and it can't approve anything. For that, you add a hub.

A hub, on your laptop or shared, holds a change to production for the person you name. confighub mini can also run in a sandbox or a CI job, and the plugin's record goes into it with `cub mini copy --from-record`.

| What you want | What to do | Effort |
|---|---|---|
| A comment on every pull request listing each configuration value it changes, and why | Add the review GitHub Action ([how](../review/README.md)) | One step in a workflow file |
| What your agents changed, and why, in a shared hub, with no confighub mini | Sign in with `cub auth login`, then type `/confighub:to-hub` ([Git, GitHub and a hub](git-and-github.md)) | Two commands |
| Agents that propose changes to production, which only a person you name can approve | For your own agents, on confighub mini; for a team, on your organization's ConfigHub ([approvals](approvals.md)) | One command on confighub mini, about 5 minutes; a ConfigHub organization for a team |
| An agent in a sandbox or CI job with a hub of its own, that hands back a pull request with its reasons | See [agents in CI](../ci/README.md) and [in CI or a sandbox](ci-and-sandboxes.md) | One workflow file |
| To keep your own values through a vendor's next version of a Helm chart, and see first what it changes | Type `/confighub:install-mini` in Claude Code, then follow [a first run](try-confighub-mini.md) | About 25 seconds to install; 15 minutes for the first run |
| Agents that run unattended for days, with a key of their own and a way to stop them at once | See [agents that run for weeks](agents-that-run-for-weeks.md) | A ConfigHub organization |
