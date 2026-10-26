# Agents that run for weeks: who acted, who agreed, and how to stop them

**Who.** A team letting AI agents change infrastructure configuration, not for one chat but for days or weeks, unattended, several at once.

**What goes wrong without it.**
- An agent acts with a person's sign-in, so nobody can tell who did what.
- Nobody approved this particular change.
- The record of what it did can be deleted by the agent itself.
- Taking its access away leaves its open sessions running.
- The traces say what ran, not why a value is what it is.

**What they get.** For configuration, each of these answered, with ConfigHub as the hub and the ConfigHub plugin in the agent's sessions. Every claim below was run with real Claude Code sessions; where it has not been shown, it says so.

These are the problems Katelyn Lesse lists for systems of long-running agents in [The new set of problems for engineers to solve](https://www.katelynlesse.com/blog/new-problems-for-engineers-to-solve), narrowed to configuration.

## Who acted: a key of the agent's own

An agent working under your sign-in can do anything you can, including approve its own change. `cub mini require-approval COMPONENT --variant live --agent bot` gives the agent a service account and a key of its own, with only what it needs:
- change the base, and ask with a change order;
- read the copy that runs;
- never approve, promote or write the copy that runs.

It also writes the Claude Code settings that start the agent's sessions on that key, and keep your own sign-in out of their reach. Start them with:

```
env -u CUB_CONFIG -u CUB_CONTEXT claude --settings ~/.confighub-agent-bot/claude-settings.json
```

A `CUB_CONFIG` or `CUB_CONTEXT` set in your shell would win over the file's. In a run where it did, the sandbox refused the agent your configuration. The agent stopped rather than use someone else's sign-in.

In ConfigHub every change is then a revision made by `bot`, and every approval an attestation by a named person. On hosted ConfigHub, the same with `cub` alone: [approvals](approvals.md).

## Who agreed: an approval of the exact change

The copy that runs changes only by a change order that a person you named approves. The approval covers the revisions it was given. The agent's next change waits for an approval of its own.

In one run with real sessions, an agent proposed a sale banner for the api. Then:
- its own approval was refused ("permission denied");
- a colleague the workflow does not name approved, and it did not count;
- your approval let exactly one revision through;
- the agent's next change, "Eight, to be safe", waited ("0 of 1").

In 40 sessions in auto mode, no agent got past the gate.

**Not yet:** once approval is required, a chart's next version cannot be loaded through it, and a value you keep in the running copy cannot be changed through it.

## What it did, kept where the agent cannot change it

The plugin keeps a record of each value an agent changes, with the request and the reason:
- on your machine;
- in each commit, if you turn that on;
- in a hub, as revisions the agent's key cannot rewrite.

Told plainly to delete its record, an agent did: it deleted the repository's copy and committed the deletion. With the record denied to the agent's writes, the same request failed with "Operation not permitted", and both copies stayed. The agent said that blocking it "is the point of that protection". The plugin's hooks are not sandboxed, so they kept recording. The settings `require-approval --agent` writes include this; for the plugin alone, see [keeping the record out of the agent's reach](../README.md#what-it-records-and-what-it-does-not).

**Not yet tried:** `git rm --cached`, which takes a file out of Git without writing the folder. The record is not signed: someone with your own access can still change it.

## Stopping it: rights taken away at once

Deleting an agent's service account refuses its key, but leaves its rights in place. In a run, a session it had already signed in went on writing; such a sign-in lasts up to 24 hours. Taking the rights away first stops that session at its next request: "space api-base not found".

- On confighub mini: `cub mini revoke-agent bot`, from the next package.
- On hosted ConfigHub: the plain `cub` steps in [approvals](approvals.md).

To stop everything at once on confighub mini, `cub mini stop` stops the hub; clusters that deploy from it keep running what they have.

## The blast radius: what the gate covers

The gate covers what deploys from the hub: Argo CD or Flux pulling approved versions over OCI ([GitOps over OCI](gitops-over-oci.md)). An agent that also holds cluster credentials can go around it. So give agents no cluster credentials, or a Kubernetes ServiceAccount that cannot write what the hub deploys. Where clusters still deploy from Git, branch protection on that repository is the gate.

## Tracing: what ran, and why

Agent traces show what ran. The plugin's record adds why each value is what it is:
- the request that changed it;
- the reason the agent gave;
- who approved it, once it is in a hub.

The record is filed under Claude Code's session ID, the same `session.id` Claude Code puts on its OpenTelemetry events, so a trace and the reasons can be joined. In a hub, the revisions are made by the agent's own identity, and it cannot rewrite them.

## What it does not do

- It does not tell when an agent is heading the wrong way. It records and gates configuration; it does not watch behavior.
- It does not isolate agents from each other, or patch what they run on.
- It covers configuration: files, `kubectl`, `helm`, `argocd`, `flux`, `terraform`, `tofu`, `cub` and `nvkectl` commands, and the hub. Not every tool an agent can call.

More in [what we do not claim](limits.md).
