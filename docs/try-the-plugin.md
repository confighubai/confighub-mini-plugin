# Try the plugin on its own

Ask your agent to change one setting, then open a fresh session and see whether it can explain the change. You need Git and Claude Code or Codex. The record stays on your computer. No hub or ConfigHub account is needed.

## Try it in five minutes

**You** install the plugin, open the sample folder and ask two questions in separate sessions. **Your agent** makes the edit, then uses the record to explain it in the next session.

1. **Claude Code:** if you haven’t installed the plugin, run these in Terminal. **Codex:** use the [copyable Codex setup](codex.md#set-it-up) and approve its hooks instead.

   ```sh
   claude plugin marketplace add confighubai/confighub-mini-plugin
   claude plugin install confighub@confighub
   ```

2. Create a throwaway Git folder with a sample setting. Then start a fresh session in that folder with `claude` or `codex`.

   ```sh
   mkdir try-confighub && cd try-confighub && git init -q &&
     printf 'CACHE=off\n' > .env && git add -f .env
   ```

3. Ask **“Turn the cache on in `.env` for next week’s sale. Don’t commit.”** Allow the edit if your agent asks.
4. Start another fresh session in the same folder and ask **“Why is the cache on?”** Look for both the change from `off` to `on` and the request about the sale. To check the record yourself, type `/confighub:why CACHE` in Claude Code or run the [Codex record command](codex.md#read-the-record) in the project.

[What fresh sessions recovered in this test](evidence.md#two-first-actions-in-fresh-sessions). You can delete the sample folder when you’re done. The local record expires after 30 days without use.

The [full plugin walkthrough](../examples/walkthroughs/tool-plugin.md) shows the output, what happens when a later agent turns the cache off, and how to add a hub when you need one.

## The problem it solves

Without the Claude plugin:

1. You ask an agent to give the api 4 replicas, because Friday's sale will bring four times the usual traffic.
2. Later, in another session, you ask an agent to cut costs. It sets the api to 1 replica.
3. Nobody committed in between, so Git shows only this:

```
$ git diff k8s/api.yaml
-  replicas: 2
+  replicas: 1
```

The 4, and the reason for it, are gone. Nothing tells you or the next agent that the sale needed them.

With the Claude plugin, the second agent was told about the 4 before it made its change, and it said so:

> **This change undoes an earlier one.** The file already had an uncommitted change that raised replicas from 2 to 4. A session earlier today made it, with this request: *"Friday's flash sale will quadruple traffic to the api: give it 4 replicas."* So 1 replica is below even the committed value of 2, and it would leave the api with a single pod on Friday.

The same thing happens on a cluster, when one agent's deploy would undo another's change.

## Stop every agent at once

To stop every Claude Code session with the Claude plugin at its next tool call, make this file from any terminal. Remove it to let them run again:

```
touch ~/.confighub/halt
```

A process an agent already started keeps running, and credentials on your machine stay valid. [Sam's bad afternoon](../examples/walkthroughs/story-19-recovery.md) shows what to do next: find the change and put it back.

To choose how closely MCP calls are watched in a folder, use `/confighub:checks`. At `repeats`, an agent that is about to repeat an earlier change, such as refunding a charge again, is held back once and told about it. At `ask`, you are asked before each call that changes something ([how it works](how-it-works.md#how-closely-mcp-calls-are-watched)).

## What it records

- **Values in configuration files**, such as Kubernetes files, Helm values, `.env` and Terraform variables, whether the agent used its edit tool or a shell command such as `sed`.
- **Commands and MCP tool calls that change something**, such as `kubectl`, `helm`, `terraform`, `cub` or a refund through a payments server, with the values they set and credentials taken out.
- **Why**: the request the agent was given, and what it said it chose for a value it changed.

Each entry is signed as it is written, so a later check names any entry that was changed, added or taken out ([signed records](signed-records.md)). It never keeps a command's output, a copy of a file, or anything that looks like a password, key or token, and nothing leaves your machine unless you turn on a setting that sends it somewhere. The whole list, every setting and what is never kept are in [how it works](how-it-works.md#what-it-records-and-what-it-does-not); [limits](limits.md) says what it does not do.

## Set it up for your whole team

To give the Claude plugin to everyone who opens a repository in Claude Code, commit this as `.claude/settings.json` in it, or add the two keys to the one it has:

```json
{
  "extraKnownMarketplaces": {
    "confighub": { "source": { "source": "github", "repo": "confighubai/confighub-mini-plugin" } }
  },
  "enabledPlugins": { "confighub@confighub": true }
}
```

When a teammate trusts the folder and starts a session, Claude Code adds the marketplace. If `/plugin` then says the Claude plugin is enabled but not installed, they run `claude plugin install confighub@confighub --scope project` once.

## When you want more than a record

The record tells you and your agents what happened. It cannot stop an agent that holds your keys, and it cannot approve anything. For that, you add a hub.

A hub, on your laptop or shared, holds a change to production for the person you name. The local hub can also run in a sandbox or a CI job, and the Claude plugin's record goes into it with `cub mini copy --from-record`.

| What you want | What to do |
|---|---|
| A comment on every pull request listing each configuration value it changes, and why | Add the review GitHub Action ([how](../review/README.md)): one step in a workflow file |
| What your agents changed, and why, in a shared hub, with no local hub | Sign in with `cub auth login`, then type `/confighub:to-hub` ([Git, GitHub and a hub](git-and-github.md)) |
| Agents that propose changes to production, which only a person you name can approve | One command on the local hub for your own agents; your organization's shared hub for a team ([approvals](approvals.md)) |
| An agent in a sandbox or CI job with a hub of its own, that hands back a pull request with its reasons | One workflow file ([agents in CI](../ci/README.md), [in CI or a sandbox](ci-and-sandboxes.md)) |
| To keep your own values through a vendor's next version of a Helm chart, and see first what it changes | Install the local hub with `bin/confighub mini get` from the Claude plugin, in a terminal ([install](install-mini.md)), then follow [a Helm chart you use, with your values](your-own-chart.md) |
| Agents that run unattended for days, with a key of their own and a way to stop them at once | A ConfigHub organization ([agents that run for weeks](agents-that-run-for-weeks.md)) |
