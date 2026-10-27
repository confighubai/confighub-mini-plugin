# The ConfigHub plugin for Claude Code and Codex

When an AI agent changes your configuration, such as the replicas in a Kubernetes file or a setting in `.env`, the plugin writes down what it changed and why. We call this the record. When a later agent opens the same file, or is about to deploy over the change, the plugin tells it what the earlier agent did and why, before it acts.

You don't change your prompts or add instructions. The record stays on your machine.

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
```

There is no account to create and no server to run. The plugin is MIT-licensed.

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

The same thing happens on a cluster. An agent asked only to deploy, or to add a setting and apply it, will quietly put back values that another agent changed for a reason. In our tests that happened three times in four. In the sale example, the api went back to 2 pods before the sale, and nobody was told. With the plugin it never happened silently. The plugin stopped the deploy once and said why the 4 was there. The agent then asked you, or, with nobody to ask, left the value alone and said why. [How we tested this](docs/evidence.md).

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

   Git shows only `LOG_LEVEL warn → debug`, so without the plugin the agent could not know about the sale. In our run it answered:

   ```
   No. `.env` currently has `CACHE=off`.

   How it got that way: The plugin's change log shows two earlier agent sessions this morning (22 Oct, 11:34) that worked against each other:
   1. Session `8664e97d` turned the cache on for next week's sale.
   2. Session `411d4c5d` then turned it back off to chase a memory leak. It also changed `LOG_LEVEL` from `warn` to `debug`.
   ...
   I haven't changed anything, because the two goals conflict. ...
   ```

5. In the same session, type `/confighub:why CACHE` to see both changes and the requests behind them:

   ```
   CACHE, in .env: off in the file now
     22 October 11:34  off → on               session 8664e97d
         asked: Turn the cache on in .env for next week's sale. Don't commit.
     22 October 11:34  on → off               session 411d4c5d
         asked: We're chasing a memory leak: turn the cache off and set debug logging. Don't commit.
   ```

When you are done, delete the folder. Its record is kept in `~/.confighub/agent-changes` and removed after 30 days without use.

## What it records

- **Values in configuration files**: Kubernetes files, Helm values, Kustomize, Compose, GitHub Actions workflows, settings files such as `.env`, Terraform variables, and agent configuration such as `CLAUDE.md`. It records the change whether the agent used its edit tool or a shell command such as `sed`.
- **Commands that change a cluster or a deployment**: `kubectl`, `helm`, `argocd`, `flux`, `terraform`, `tofu`, `cub` and `nvkectl`, with the values they set.
- **Why**: the request the agent was given, and the reason it gave, when you ask agents to give one.
- **What it cost**: each turn's model calls and tokens, so you can see what a change cost and which sessions cost the most ([model use](docs/how-it-works.md#model-use)).

Each turn of the record is signed when it ends, so you can check later that nobody changed it. An agent on a cluster can sign with its own workload identity, so the record names the agent that made each change ([signed records](docs/signed-records.md)).

It never keeps a command's output, a copy of a file, or anything that looks like a password, key or token. It adds about 15 milliseconds to each tool call. Nothing leaves your machine unless you turn on a setting that sends it somewhere, such as a pull request or your OpenTelemetry collector.

[How it works](docs/how-it-works.md) covers what the agent is told and when, every setting, and how to keep the record out of the agent's reach. [What we do not claim](docs/limits.md) covers what it does not do.

## When you want more than a record

The record tells you and your agents what happened. Some teams also want to keep certain values safe through later changes, and to approve what agents change before it reaches production. For that, you add a hub.

A hub is a place where your configuration is kept, with every change, who made it and why. ConfigHub is that hub. confighub mini is ConfigHub made small enough to run on your laptop, with no account and no Docker.

| What you want | What to do | Effort |
|---|---|---|
| A comment on every pull request listing each configuration value it changes, and why | Add the review GitHub Action ([how](review/README.md)). Nobody needs to install anything. | One step in a workflow file |
| To keep your own values when a vendor ships the next version of a Helm chart | Type `/confighub:install-mini` in Claude Code, then follow [a first run](docs/try-confighub-mini.md) | About 25 seconds to install; 15 minutes for the first run |
| Agents that propose changes to production, which only a person you name can approve | For your own agents, on confighub mini; for a team, on your organization's ConfigHub ([approvals](docs/approvals.md)) | One command on confighub mini; a ConfigHub organization for a team |
| Agents that run unattended for days, with a key of their own and a way to stop them at once | See [agents that run for weeks](docs/agents-that-run-for-weeks.md) | A ConfigHub organization |

confighub mini uses the same commands as ConfigHub, so what you learn on your laptop works the same on your company's ConfigHub ([how the commands map](docs/cub-mini-and-cub.md)). [From the plugin to ConfigHub](docs/from-plugin-to-confighub.md) follows one team through each step.

## Documentation

Every page, grouped by what you are doing, is listed in [docs/README.md](docs/README.md).

## License

MIT ([LICENSE](LICENSE)). The program is built with Go and open-source modules, whose licenses are in [`plugins/confighub/THIRD_PARTY_LICENSES.txt`](plugins/confighub/THIRD_PARTY_LICENSES.txt).
