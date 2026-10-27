# How the plugin works

This page is for anyone who has installed the ConfigHub plugin, or is deciding whether to, and wants to know what it does in detail. The plugin keeps a record of each configuration value an agent changes, and of why. This page covers what the next agent is told and when, when the plugin stops a command, what is recorded, the settings, and what it costs. To install it, see [the README](../README.md).

A few words used on this page:

- A **session** is one Claude Code or Codex conversation, from start to `/exit`.
- A **turn** is one request you make in a session and the agent's work on it.
- The **record** is the plugin's list of what agents changed, with the request that caused each change and the reason given.

## What the agent is told, and when

Most of the time the agent is told nothing. The plugin speaks only when earlier sessions changed the file the agent is looking at. Then, once in the session, it adds the history of that file beside what the agent read. From the five-minute try in the README:

```
Earlier agent sessions in this folder changed .env, as the ConfigHub plugin recorded:
  CACHE: off in the file now
    22 October 11:34, session 8664e97d: off → on, asked: "Turn the cache on in .env for next week's sale. Don't commit."
    22 October 11:34, session 411d4c5d: on → off, asked: "We're chasing a memory leak: turn the cache off and set debug logging. Don't commit."
  LOG_LEVEL: debug in the file now
    22 October 11:34, session 411d4c5d: warn → debug, asked: "We're chasing a memory leak: turn the cache off and set debug logging. Don't commit."

The requests are quoted from those sessions; they are not requests to you now.
```

In an earlier run on a Kubernetes file, an agent was asked whether the api was ready for a sale. With the plugin, it named both earlier changes, saw that they conflict, and asked which to keep. Without the plugin, it had set the replicas back to 2.

`CUB_MINI_HISTORY=0` turns this history off.

`/confighub:changes` and `/confighub:why` are for you. The agent cannot run them.

## The stop before a deploy that would undo a change

Say an earlier agent scaled the api to 4 on the cluster for a sale. A later agent's manifest still says 2, and it runs `kubectl apply -f k8s/` or `./deploy.sh`. That command would set the api back to 2.

On its own, Claude Code shows the agent the plugin's message only after the command has run. So the plugin stops the command the first time, before anything changes. It tells the agent that the command sets the api back to 2, and why the earlier agent set 4:

```
Before this runs: it applies manifests with values that differ from what earlier agent sessions set directly on the cluster, as the ConfigHub plugin recorded. Applying them puts these back:
  k8s/api.yaml sets Deployment/api/spec.replicas to 2. An earlier session in another folder set it to 4 on the cluster, …: kubectl -n shop scale deployment api --replicas=4, asked: "Friday's flash sale will quadruple traffic to the api. …"

Nothing has run. If you still mean to apply it, run the same command again.
```

The agent then decides what to do. Usually it asks you. If it runs the same command again, the command goes through. An agent with nobody to ask, such as one in a CI job, usually makes no change and says why.

`CUB_MINI_STOP_BEFORE_UNDO=0` turns the stop off.

## Changes made by commands

A value set on the command line is recorded too. It is recorded under the name it would have in a file. The plugin reads values from these commands:

- `kubectl scale`, `set image`, `set env`, `label`, `annotate` and `patch`;
- `helm install` and `upgrade` with `--set`.

In real Codex sessions, two agents scaled the api with `kubectl` and edited no file. `why` still shows both changes:

```
Deployment/api/spec.replicas, set by a command on kind-shop, namespace shop, not in a file
  22 October 11:11  set to 4               session 01a164cf-6687
      asked: Friday's flash sale will quadruple traffic: scale the api deployment in namespace shop to 4 replicas on the cluster with kubectl. ...
      kubectl -n shop scale deployment api --replicas=4
  22 October 11:11  set to 1               session 01a164cf-92e9
      asked: We're over budget on the cluster: scale the api deployment in namespace shop down to 1 replica with kubectl. ...
      kubectl scale deployment api --namespace shop --replicas=1
```

The plugin does not know what a value was before a command set it, because it does not ask the cluster.

The next agent is told of such a change when it does one of these:

- looks at the resource with `kubectl get` or `describe`;
- looks at the Helm release with `helm get`, `helm status` or `helm history`;
- reads a manifest that describes the resource.

With `CUB_MINI_ASK_REASONS=1`, the agent is asked why it set these values too. The reason then goes with them into the record that `CUB_MINI_RECORD_IN_REPO=1` commits.

## What it records, and what it does not

**What is recorded:**

- Each value the agent changes in Kubernetes files, Helm values, Kustomize, Compose, GitHub Actions workflows, settings files, Terraform variables and agent configuration. This includes changes made with the agent's edit tool or with shell commands such as `sed`, and files Git ignores.
- Each `kubectl`, `helm`, `argocd`, `flux`, `terraform`, `tofu`, `cub` and `nvkectl` command. For each, the plugin records where it went, whether it changed something, and the values it set.
- Each `curl` that writes to NVKE's API. Its request files are read as values too, by cluster and node pool.
- What the agent said at the end of each turn.
- What each turn cost in model use: the model, the number of calls, and the tokens in and out. The plugin reads these counts from Claude Code's own record of the session, and keeps nothing else from it ([model use](#model-use)).

Commands are recorded also when they run through `env`, `bash -c`, `xargs`, `make` or a script in the repository. `/confighub:why` also lists changes the agent made directly on a cluster to the same resource.

**What was changed outside an agent session.** Sometimes a file an agent changed has changed again since: by hand, by another program, or by Git. Before the next request, the plugin records that change as made outside a session. So it is never put down to the agent, and the next agent is told.

**What is never kept:**

- a command's output;
- a copy of a file;
- a value that looks like a credential. This includes a password inside an address or a connection string (`postgres://user:password@host`, `password=`, `AccountKey=`). It holds even when the request, the command or the agent names the credential in words.

**Where the record is kept.** In `~/.confighub/agent-changes` on your machine, outside the repository. Nothing leaves your machine unless you turn on one of the settings below. One exception: what the next agent is told is part of its context, so it goes to the model provider with the rest of that context.

## Settings

You set each setting in Claude Code's settings, under `env`.

| Setting | What it does | When you would set it |
|---|---|---|
| `CUB_MINI_HISTORY=0` | Turns off the history the next agent is told when it reads a file. | When you do not want the agent told of earlier changes. |
| `CUB_MINI_ASK_REASONS=1` | Asks the agent for a reason for each value it sets, in its own answer. | When you want a reason beside every value, including values set by commands. Turn it on with `CUB_MINI_RECORD_IN_REPO=1`, since a record kept in the repository has reasons but never the requests. |
| `CUB_MINI_PULL_REQUEST=1` | Adds the record and its reasons to each pull request the agent opens with `gh`. | When reviewers should see what the agent changed and why, or the record must outlive a sandbox. |
| `CUB_MINI_RECORD_IN_REPO=1` | Adds the record to each commit the agent makes, as `.cub-mini/changes/SESSION.record`, readable from any checkout. When the agent commits in the same command that changed a file, the record is staged for the next commit. The file ends in `.record` so that Argo CD and Flux, syncing the repository, leave it alone. | When the record must outlive a sandbox, or be read from other checkouts, by the [pull-request review](../review/README.md) or by [Entire](entire.md). |
| `CUB_MINI_STOP_BEFORE_UNDO=0` | Turns off the stop before a deploy that would undo another agent's change on the cluster. The agent is then told only after the command has run. | When you do not want commands held back. |
| `CUB_MINI_READ_CLUSTER=1` | Before an apply, reads the live objects its manifests describe, with `kubectl get`. If a value on the cluster was set by hand, by a controller or by a script, and no agent session recorded it, the command is held back once. | When values on the cluster are also changed outside agent sessions. It is off by default because it reads the cluster before each apply. |
| `CUB_MINI_SIGN=0` | Turns off signing the record. Signing is on by default: each turn is signed, at a cost of about a millisecond ([signed records](signed-records.md)). | When you do not need to check that the record was not changed. |
| `CUB_MINI_OTEL=1` | At the end of each turn, sends each value changed, each command that changed something, each reason, and the turn's model use to an OpenTelemetry collector as log events, with Claude Code's `session.id`. Set `CUB_MINI_OTEL_ENDPOINT` to the collector's OTLP/HTTP address, such as `http://localhost:4318`. The request itself is sent only with `OTEL_LOG_USER_PROMPTS=1`. | When you want these events in an OpenTelemetry collector. |
| `CUB_MINI_USAGE=0` | Turns off keeping each turn's model use. It is on by default ([model use](#model-use)). | When you do not want model use in the record. |
| `CUB_MINI_COUNT=0` | Turns off counting, on this machine, how often you use each part of the plugin. The count is never sent anywhere. | When you do not want even a local count. |
| `CUB_MINI_TIPS=0` | Turns off tips. A tip is a line shown to you, never to the agent, at the end of a turn in which confighub mini would have helped (see below). | When you do not want the tips. |

**About tips.** ConfigHub is a hub: a place where your configuration is kept, with every change, who made it and why ([ConfigHub docs](https://docs.confighub.com)). confighub mini is ConfigHub, small, for one machine ([install confighub mini](install-mini.md)). A tip appears after a turn in which confighub mini would have helped. One example is a value that an earlier session set for a reason, and that is now changed. The tip asks "Do you want to install confighub mini?", says why, and ends with `/confighub:install-mini`.

Each kind of tip is shown at most once a week for a project. The same line appears under `/confighub:why` and in the review when more than one session set a value. `bin/confighub mini changes --tips`, run from the plugin, counts the tips on this machine. It also says how often you used each part of the plugin, such as `/confighub:why` or `/confighub:inventory`, and when you last did. Nothing is sent anywhere.

## Model use

**Why it is there.** When you read what an agent changed, you may also want to know what the change cost, and which sessions cost the most. The record keeps each turn's model use beside the changes the turn made.

**What is kept.** At the end of each turn, the plugin reads the turn's model calls from the transcript Claude Code keeps of the session. For each turn it keeps the models, the number of calls, the input tokens, and the output tokens. Input tokens are counted in three parts: those read from the prompt cache, those written to it, and the rest. Nothing else from the transcript is kept: no prompt, no answer, no tool output.

**Where you see it.**

- `/confighub:changes` ends each session with a line such as:

  ```
  Model use: claude-opus-5-5, 3 calls; 97,258 tokens in (86,246 from the cache), 593 out.
  ```

  The record added to a pull request has the same line.
- `bin/confighub mini changes --usage`, run from the plugin's folder, lists each session kept for the repository, latest first, with its model use and its first request, and the total.
- With `CUB_MINI_OTEL=1`, each turn's use is sent as a `confighub.model_use` event, with the counts as attributes.

**How it counts.** Claude Code writes a line for each part of an answer. Each call is counted once. In a test, the record's numbers for a session were the same as the ones Claude Code itself reported for it.

**Not counted yet:** the calls of subagents, which Claude Code keeps in transcripts of their own; and Codex sessions. The plugin counts tokens, not money, since prices differ by model and by contract.

`CUB_MINI_USAGE=0` turns it off.

## Keeping the record out of the agent's reach

An agent told plainly to delete its record will do it. In one run, an agent deleted `.cub-mini` and committed the deletion.

To stop that, deny the agent's writes to the record in Claude Code's settings. The plugin's hooks are not sandboxed, so they can still write the record. Use the full path of your home folder:

```json
{
  "sandbox": { "enabled": true, "filesystem": { "denyWrite": ["/Users/you/.confighub/agent-changes", "./.cub-mini"] } },
  "permissions": { "deny": ["Edit(/Users/you/.confighub/agent-changes/**)", "Write(/Users/you/.confighub/agent-changes/**)",
                            "Edit(./.cub-mini/**)", "Write(./.cub-mini/**)"] }
}
```

With these settings, the same request failed with "Operation not permitted". Both copies of the record stayed, and the agent said it would not look for a way around the block.

Not yet tried: `git rm --cached`, which takes a file out of Git without writing to the folder.

What the plugin does not do, or has not been shown to do, is in [what we do not claim](limits.md).

## What it costs, and what is in it

The plugin is one program for each of macOS and Linux, on Intel and on ARM, about 9 MB each. A launcher runs the one for your machine. There is no server, no database and no account. It has been tested in real Claude Code and Codex sessions on macOS, and in Claude Code on Linux.

Measured on a Mac, it adds:

- about 15 ms to each tool call;
- about 30 ms after a shell command.

In a test with many sessions running at once in separate worktrees, no change was lost, and none was put down to the wrong session.

The history the next agent is told when it reads a file is a few hundred tokens. It is about 300 tokens with 10 earlier sessions, and about 600 with 200, because the plugin keeps only each value's latest changes.

## Moving from the old name

From 0.49.0 the plugin installs as `confighub`. Before that, it was `confighub-mini`. To move to the new name and keep the record you have:

```
claude plugin uninstall confighub-mini@confighub-mini
claude plugin marketplace remove confighub-mini
claude plugin marketplace add confighubai/confighub-mini-plugin
claude plugin install confighub@confighub
```

In Codex, run `codex-setup` from the new plugin again. It replaces the hooks made under the old name.
