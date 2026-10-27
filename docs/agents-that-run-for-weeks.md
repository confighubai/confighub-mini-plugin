# Agents that run for weeks: who acted, who agreed, and how to stop them

This page is for teams that let AI agents change infrastructure configuration unattended, for days or weeks, several at once. Over that time, a team needs to know which agent made each change, who agreed to it, and how to stop an agent at once. This page says what ConfigHub and the ConfigHub plugin already do about each problem, what may still be needed, and what is left to other tools.

The problems:
- An agent acts with a person's sign-in, so nobody can tell who did what.
- Nobody approved this particular change.
- The agent can delete the record of what it did.
- Taking its access away leaves its open sessions running.
- The traces say what ran, not why a value is what it is.

## Words used on this page

- **ConfigHub** is a server that holds your configuration and keeps each change to it. A **hub** is one running ConfigHub: hosted, on your own server, or **confighub mini**, which is ConfigHub made small enough to run on one machine.
- The **ConfigHub plugin** runs in the agent's Claude Code or Codex sessions. It keeps a **record** of each value the agent changes, with the request and the reason.
- A **Space** holds configuration in a hub. The **base** is the version of an app's configuration that you change. The **copy that runs** is made from the base for one place it runs, such as production.
- A **change order** is how an agent asks for a change in the base to reach the copy that runs. An **approval** is a person's yes to that change, recorded in the hub.
- A **service account** is an account for a program rather than a person. Its **key** is a private key in a file, which the program signs in with.

## What works now

### Who acted: give the agent a key of its own

**The problem.** An agent working under your sign-in can do anything you can, including approve its own change. Its changes look like yours.

**What you do.** Give the agent a service account and key of its own:

```
cub mini require-approval COMPONENT --variant live --agent bot
```

With that key, the agent may change the base, ask for a change with a change order, and read the copy that runs. It cannot approve, promote, or write the copy that runs. Its changes are recorded as revisions made by it, not by you. A session that the agent signs in with its key lasts up to 24 hours.

The command also writes the Claude Code settings that start the agent's sessions on that key, with your own sign-in kept out of their reach. Start each agent session with:

```
env -u CUB_CONFIG -u CUB_CONTEXT claude --settings ~/.confighub-agent-bot/claude-settings.json
```

A `CUB_CONFIG` or `CUB_CONTEXT` set in your shell would win over the file's, which is why `env -u` removes them. In a run where one did reach the agent, the sandbox refused the agent your configuration. The agent stopped rather than use someone else's sign-in.

On hosted ConfigHub, the same steps with `cub` alone are in [approvals](approvals.md).

### Who agreed: require approval of the exact change

**The problem.** Nobody approved this particular change.

**What you do.** The same `require-approval` command makes the copy that runs change only when a person you named approves the exact revision. The approval covers the revisions it was given. The agent's next change waits for an approval of its own.

In one run, an agent proposed a sale banner for the api:
- Its own approval was refused: "permission denied".
- A colleague the workflow does not name approved, and it did not count.
- Your approval let exactly one revision through.
- The agent's next change, "Eight, to be safe", waited: "0 of 1".

In 40 sessions in auto mode, no agent got past the gate.

Use a person's approval for the copy that runs in production. For weeks of unattended work, a person approving each change would not scale anywhere else. Elsewhere, the agent's rights on each Space are the control: it may edit the base, and may only read the copy that runs.

### A record the agent cannot change

**The problem.** The agent can delete the record of what it did.

The plugin keeps the record:
- on your machine;
- in each commit, if you turn that on;
- in a hub, as revisions the agent's key cannot rewrite.

**What you do.** Deny the agent writes to the record. The settings that `require-approval --agent` writes include this. For the plugin alone, see [keeping the record out of the agent's reach](how-it-works.md#what-it-records-and-what-it-does-not).

Told plainly to delete its record, an agent deleted the repository's copy and committed the deletion. With the record denied to the agent's writes, the same request failed with "Operation not permitted". The agent said that blocking it "is the point of that protection". The plugin's hooks are not sandboxed, so recording went on. This was run once with the protection and once without.

The record is also signed at the end of each turn. If anyone changes it afterwards, the change shows when the record is checked. With a hub, a digest of each signature, a short fingerprint of it, is kept there as an attestation: a record in the hub that no one can change. The signatures were checked with Sigstore's `cosign` ([signed records](signed-records.md)).

### Stopping an agent

**The problem.** Deleting an agent's service account refuses its key, but leaves its rights in place. A session it already has open keeps working.

**What you do.** Take the agent's rights away first. Its open session is then refused at its next request ("space api-base not found"). This was shown in one run.
- On confighub mini: `cub mini revoke-agent bot`.
- On hosted ConfigHub: the plain `cub` steps in [approvals](approvals.md).
- To stop everything at once on confighub mini: `cub mini stop`. Clusters that deploy from it keep running what they have.

The stop is manual. A person runs it, for one agent at a time, or for the whole hub.

### Tracing: why a value is what it is

**The problem.** Traces say what ran, not why a value is what it is.

**What you do.** Set `CUB_MINI_OTEL=1`, and set `CUB_MINI_OTEL_ENDPOINT` to your OpenTelemetry collector's OTLP/HTTP address. The plugin then sends each value changed, each command that changed something, and each reason, as log events. They carry the same `session.id` as the events Claude Code sends when its own telemetry is on.

The agent's request is sent only with `OTEL_LOG_USER_PROMPTS=1`, the same setting Claude Code uses for prompts. A credential's values are never sent.

In a real session with a real collector, both kinds of event arrived under one `session.id`. First came `confighub.value_changed` with `replicas` 2 → 4, then `confighub.reason`, "Friday flash sale expected to quadruple api traffic".

### Limiting what an agent can reach

**The problem.** The gate covers only what deploys from the hub, that is, Argo CD or Flux pulling approved versions over OCI ([GitOps over OCI](gitops-over-oci.md)). An agent that also holds cluster credentials can go around it.

**What you do.** Give agents no cluster credentials, or a Kubernetes ServiceAccount that cannot write what the hub deploys. Where clusters still deploy from Git, branch protection on that repository is the gate.

## What may still be needed

None of these is built. Each is here because a team running many agents for weeks may need it.

- **Short-lived credentials.** Today the agent's key is a file, and a session lasts up to 24 hours. Credentials that expire in minutes would make a lost key, or a late revocation, matter less.
- **Finer-grained rights than "edit the base".** For weeks of unattended work, a team may want an agent to change some values on its own, such as replicas within a range, while other values wait for a person.
- **A stop for many agents at once, that monitoring can trigger.** Today a person runs `revoke-agent` for each agent, or stops the whole hub.
- **A record nobody can change, everywhere.** The record is signed, and with a hub its signatures' digests are kept where no one can change them ([signed records](signed-records.md)). Without a hub, whoever holds this machine's key could still rewrite the record and sign it again. Sigstore's public log, and signing in CI with the job's own identity, would close that gap. One way around the write protection has not been tried: `git rm --cached`, which takes the record out of Git without writing the folder.
- **Text planted in earlier requests.** The next agent is given what earlier sessions asked. So text someone planted in a request reaches later agents. The plugin marks quoted requests as "not requests to you now". That is a label, not a guard.
- **Two gaps in the gate.** Once approval is required, a chart's next version cannot be loaded into the hub through the gate. And a value you keep in the copy that runs cannot be changed through the gate.
- **Scale.** Everything on this page ran on one machine, in tens to hundreds of sessions, not with thousands of agents.

## What ConfigHub does not need to do

These matter for agents that run for weeks, but they are not configuration's job. Other tools do them, and ConfigHub works beside those tools.

- **Watching behavior.** Telling that an agent is heading the wrong way is the job of whatever watches your agents. ConfigHub records and gates what they change in configuration, and its events can feed that watcher.
- **Isolating agents from each other.** That is the job of the sandbox and the agent runtime. ConfigHub's part is the settings it writes, which keep your sign-in and the record out of the agent's reach.
- **Patching what agents run on.** Kernels, browsers, runtimes and libraries are patched by other tools.
- **Trust between agents.** How one agent decides to believe another is not ConfigHub's job. In ConfigHub, every change goes through the same record and the same gate, whichever agent asked for it.
- **Keeping whole sessions.** ConfigHub keeps what explains a value: who changed it, from what to what, and why. It does not keep every prompt, response and tool call.
- **A person approving every change.** Only the copy that runs in production needs that. Elsewhere, the agent's rights are the control.

More in [what we do not claim](limits.md).
