# Agents that run for weeks: who acted, who agreed, and how to stop them

**Who.** A team letting AI agents change infrastructure configuration, not for one chat but for days or weeks, unattended, several at once.

**What goes wrong without it.**
- An agent acts with a person's sign-in, so nobody can tell who did what.
- Nobody approved this particular change.
- The agent can delete the record of what it did.
- Taking its access away leaves its open sessions running.
- The traces say what ran, not why a value is what it is.

**What they get.** For configuration, with ConfigHub as the hub and the ConfigHub plugin in the agent's sessions, in three parts:
- what works now, each with the run that showed it;
- what we might still need to build;
- what ConfigHub does not need to do, because it is another tool's job.

## What ConfigHub does now

| Problem | What ConfigHub does | Shown |
|---|---|---|
| Who acted | The agent has a service account and key of its own, with only the rights it needs. Its changes are revisions made by it, not by you | `require-approval --agent` |
| Who agreed | The copy that runs changes only when a person you named approves the exact revision | One run: the agent's own approval refused, an unnamed colleague not counted, one revision let through. 40 sessions in auto mode: none got past the gate |
| A record it cannot change | Told to delete its record, an agent did. With the record denied to its writes, the same request failed, and both copies stayed. Each turn is also signed, so a change by anyone afterwards shows, and a hub keeps each signature's digest where no one can change it | One run of each, in three settings; the signatures checked by Sigstore's `cosign` ([signed records](signed-records.md)) |
| Stopping it | `cub mini revoke-agent bot` takes its rights away, so a session it has open is refused at its next request | One run |
| Tracing | The record goes to your OpenTelemetry collector, under Claude Code's own `session.id` | One run, with a real collector |
| Blast radius | The gate covers what deploys from the hub: Argo CD or Flux pulling approved versions over OCI | [GitOps over OCI](gitops-over-oci.md) |

### Who acted: a key of the agent's own

An agent working under your sign-in can do anything you can, including approve its own change.
- `cub mini require-approval COMPONENT --variant live --agent bot` gives it a service account and key of its own.
- With that key it may change the base, ask with a change order, and read the copy that runs.
- It cannot approve, promote, or write the copy that runs.

The key is a private key in a file, and a session it signs in with lasts up to 24 hours.

`require-approval --agent` also writes the Claude Code settings that start the agent's sessions on that key, with your own sign-in kept out of their reach:

```
env -u CUB_CONFIG -u CUB_CONTEXT claude --settings ~/.confighub-agent-bot/claude-settings.json
```

A `CUB_CONFIG` or `CUB_CONTEXT` set in your shell would win over the file's. In a run where it did, the sandbox refused the agent your configuration, and the agent stopped rather than use someone else's sign-in. On hosted ConfigHub, the same steps with `cub` alone are in [approvals](approvals.md).

### Who agreed: an approval of the exact change

The approval covers the revisions it was given; the agent's next change waits for one of its own.

In one run, an agent proposed a sale banner for the api:
- its own approval was refused: "permission denied";
- a colleague the workflow does not name approved, and it did not count;
- your approval let exactly one revision through;
- the agent's next change, "Eight, to be safe", waited: "0 of 1".

A person approving each change is meant for the copy that runs in production. For weeks of unattended work it would not scale anywhere else. There, the agent's rights on each Space are the control: it may edit the base, and only read the copy that runs.

### A record it cannot change

The plugin keeps a record of each value an agent changes, with the request and the reason:
- on your machine;
- in each commit, if you turn that on;
- in a hub, as revisions the agent's key cannot rewrite.

Told plainly to delete its record, an agent deleted the repository's copy and committed the deletion. With the record denied to the agent's writes, the same request failed with "Operation not permitted", and the agent said that blocking it "is the point of that protection". The plugin's hooks are not sandboxed, so recording went on. The settings `require-approval --agent` writes include this; for the plugin alone, see [keeping the record out of the agent's reach](how-it-works.md#what-it-records-and-what-it-does-not).

Each turn of the record is also signed when it ends, so a change made afterwards, by anyone, shows when the record is checked; with a hub, each signature's digest is kept there as an attestation no one can change ([signed records](signed-records.md)).

### Stopping it

Deleting an agent's service account refuses its key, but leaves its rights in place, so a session it already has open keeps working. Taking the rights away first stops that session at its next request ("space api-base not found").
- On confighub mini: `cub mini revoke-agent bot`.
- On hosted ConfigHub: the plain `cub` steps in [approvals](approvals.md).
- To stop everything at once on confighub mini: `cub mini stop`. Clusters that deploy from it keep running what they have.

The stop is manual: a person runs it, for one agent at a time, or for the whole hub.

### Tracing

With `CUB_MINI_OTEL=1` and `CUB_MINI_OTEL_ENDPOINT` set to your collector's OTLP/HTTP address, the plugin sends each value changed, each command that changed something, and each reason, as log events. They carry the same `session.id` as the events Claude Code sends with its own telemetry on.

In a real session, both arrived at one collector under one `session.id`: `confighub.value_changed` with `replicas` 2 → 4, then `confighub.reason`, "Friday flash sale expected to quadruple api traffic". The request is sent only with `OTEL_LOG_USER_PROMPTS=1`, as Claude Code sends prompts. A credential's values are never sent.

### The blast radius

The gate covers what deploys from the hub. An agent that also holds cluster credentials can go around it. So give agents no cluster credentials, or a Kubernetes ServiceAccount that cannot write what the hub deploys. Where clusters still deploy from Git, branch protection on that repository is the gate.

## What we might need to do

None of these is built. Each is here because a team running many agents for weeks may need it.

- **Short-lived credentials.** Today the agent's key is a file, and a session lasts up to 24 hours. Credentials that expire in minutes would make a lost key, or a late revocation, matter less.
- **Finer-grained rights than "edit the base".** For weeks of unattended work, a team may want an agent allowed to change some values on its own, such as replicas within a range, while others wait for a person.
- **A stop for many agents at once, that monitoring can trigger.** Today a person runs `revoke-agent` for each agent, or stops the whole hub.
- **A record nobody can change, everywhere.** The record is signed, and with a hub its signatures' digests are kept where no one can change them ([signed records](signed-records.md)). Without a hub, whoever holds this machine's key could still rewrite and re-sign it; Sigstore's public log, and signing in CI with the job's own identity, would close that. Not tried: `git rm --cached`, which takes the record out of Git without writing the folder.
- **Closing memory as a way in.** The next agent is given what earlier sessions asked, so text someone planted in a request reaches later agents. The plugin marks quoted requests as "not requests to you now". That is a label, not a guard.
- **Two gaps in the gate:**
  - once approval is required, a chart's next version cannot be loaded through it;
  - a value you keep in the copy that runs cannot be changed through it.
- **Scale.** Everything above ran on one machine, in tens to hundreds of sessions, not thousands of agents.

## What ConfigHub does not need to do

These matter for agents that run for weeks, but they are not configuration's job. Other tools do them, and ConfigHub works beside them.

- **Watching behavior.** Telling that an agent is heading the wrong way is for whatever watches the agents. ConfigHub records and gates what they change in configuration, and its events can feed that watcher.
- **Isolating agents from each other.** That is the job of the sandbox and the agent runtime. ConfigHub's part is the settings it writes, which keep your sign-in and the record out of the agent's reach.
- **Patching what agents run on:** kernels, browsers, runtimes and libraries.
- **Trust between agents.** How one agent decides to believe another. In ConfigHub every change goes through the same record and the same gate, whichever agent asked for it.
- **Keeping whole sessions.** ConfigHub keeps what explains a value: who changed it, from what to what, and why. Not every prompt, response and tool call.
- **A person approving every change.** Only the copy that runs in production needs that; elsewhere, the agent's rights are the control.

More in [what we do not claim](limits.md).
