# Signed records: check that nobody changed them

This page is for a team that relies on the plugin's record of what its agents changed: in a review, an audit or an incident. The record is a file. Anyone who can write to its folder, including an agent told to tidy up, can change a value or a reason afterwards, and nothing would show it. Signing lets anyone check that the record is still as it was written.

The plugin signs each **entry** of the record as it writes it: each thing it notes, such as a value changed or a command run. Each signature is linked to the one before, and has a line in the folder's list of signatures, `signatures.jsonl`, beside the folder's **sessions** (one session is one Claude Code conversation; a **turn** is one request in it and the agent's work on it). If an entry is changed, added or taken out after it was signed, or a session is removed or cut back, a check names it.

Nothing is asked of you or the agent. Signing one entry takes about 0.2 milliseconds. `CUB_MINI_SIGN=0` turns it off.

## Checking the record

Run:

```
bin/confighub mini changes --verify
```

You will see something like:

```
The records of /work/shop:
  ok   session 255c6769: 1 turn signed, unchanged since (key e6ce0a1eb16e)
  ok   .cub-mini/changes/255c6769-eb67-4f4f-bdfd-a57103ecd696.record: signed, unchanged since (key e6ce0a1eb16e)
```

A record changed after it was signed is marked `NOT`, with the session, the file and the turn. The command then fails, so a CI job can stop on it. For example, for an entry written in after the record was signed, and for a session removed:

```
NOT  session s1: 1 entry after the last signature was never signed: the first is entry 8 of entries.jsonl, turn 2 (a change to k8s/api.yaml: Deployment/api/spec.replicas 6 to 20); written in after the record was signed, or left by a hook stopped before it could sign
NOT  session s1: removed: the folder's list of signatures has 7 signatures of it, the last at 11 November 12:01, and its record is gone
```

Two cases are marked `--` and do not fail the check. An entry from the last minute that is not signed yet is an unfinished write; after a minute it is marked `NOT`. A session with no signatures at all, made with `CUB_MINI_SIGN=0` or written in as a file, is marked `--` too.

`cub mini changes`, `/confighub:why` and the review show only entries a signature covers. `cub mini changes` says what it leaves out, in a line that starts `Not shown:`.

**In the pull-request review.** The [review](../review/README.md) comment opens with one line: `Records in the repository: 1 signed and unchanged.` If a record in the repository was changed after it was signed, the review names it there, in bold.

## Checking with standard tools

The signatures use open formats, so you can check them without the plugin:

- Each signature is an in-toto statement, a standard format for a signed claim about a file.
- The statement is wrapped in a DSSE envelope, a standard wrapper for a signed payload.
- This is the format that Sigstore, an open-source project for signing and checking software, uses.

To check a record with Sigstore's `cosign`:

1. Keep the record in the repository with `CUB_MINI_RECORD_IN_REPO=1`. Each `.cub-mini/changes/SESSION.record` then has its signature beside it, `SESSION.record.intoto.json`, committed with it.
2. Write out this machine's public key, and check the record against it:

   ```
   bin/confighub mini changes --signing-key > key.pem
   cosign verify-blob-attestation --key key.pem --type https://confighub.com/agent-changes/record/v1 \
     --signature .cub-mini/changes/SESSION.record.intoto.json --insecure-ignore-tlog .cub-mini/changes/SESSION.record
   ```

On a real session's commit, cosign printed `Verified OK`.

`--insecure-ignore-tlog` is there because the signature is not in Sigstore's public log. See "Not yet", below.

## With a hub: a copy to compare against

ConfigHub is a hub: a place where your configuration is kept, with every change, who made it and why ([ConfigHub docs](https://docs.confighub.com)). A hub is a ConfigHub server. confighub mini is ConfigHub, small, for one machine ([install confighub mini](install-mini.md)). With confighub mini, `CUB_MINI_KEEP_IN_HUB=1` keeps changes in the hub.

Each change kept in the hub then has an attestation beside its revisions in ConfigHub. An attestation is a statement that ConfigHub stores; this one is of type `AgentRecord`. It holds:

- the digest of the latest signature, and of the record it covers;
- the key;
- the session.

ConfigHub records the attestation with its own time, and never changes it. `--verify` does not read it. A record rewritten and signed again by whoever holds the key shows only when you compare it with the attestations the hub kept, and that comparison is done by hand today.

## Signing with the agent's own identity

On a laptop, the machine's key is enough: one person, one machine. An agent that runs unattended on a cluster is different. Several agents may share a node, and the platform team, not the agent, decides which of them may act. For that case, the record can be signed with the agent's own workload identity instead of the machine's key.

**Priya's story.** Priya runs the platform team for a GPU training cluster. Every night an agent, `nightly-tuner`, adjusts the batch workers. The cluster gives each workload an identity with SPIRE, and Priya points the plugin at the agent's.

1. **Which agent made this change?** One night the agent raises the workers from 4 to 6. In the morning Marco, who is on call, runs `--verify`. It names the agent, and checks that the cluster's own authority issued its identity:

   ```
   ok   session night-1: 1 turn signed, unchanged since, by spiffe://example.org/ns/agents/sa/nightly-tuner
   ```

2. **Priya withdraws the agent.** The agent's changes start to look wrong, so Priya removes its SPIRE registration. SPIRE stops renewing its certificate, and the certificate expires. The agent, still running, makes one more change, from 6 to 8. That change is recorded, with the request behind it, but it is not signed, and the check says why and fails:

   ```
   ok   session night-1: 1 turn signed, unchanged since, by spiffe://example.org/ns/agents/sa/nightly-tuner
   NOT  session night-2: not signed since 27 October 10:41: the workload identity expired at 2026-10-27T10:38:26Z
   ```

   The first night's turn still passes: a certificate is checked as of the time it signed, not as of today. The plugin never falls back to the machine's key, because a record signed by the machine would hide that the agent had lost its identity.

3. **Someone edits the record.** Marco changes the first night's 6 to a 5 in the file. The check names the turn that no longer matches, and fails.

**The words.** A workload identity is a short-lived certificate that a cluster gives a program. It names the program, not the machine it runs on. SPIFFE is the open standard for these identities, and SPIRE is its most widely used implementation. An identity is a URI such as `spiffe://example.org/ns/agents/sa/nightly-tuner`. The certificate that carries it is called an SVID, and it usually lives for an hour or less. SPIRE renews it for as long as the platform team allows. The trust bundle is the set of certificates of the authority that issues the identities; you check an identity against it.

**What you do.** Run [spiffe-helper](https://github.com/spiffe/spiffe-helper) beside the agent, so that SPIRE's files are written to a folder the agent's container can read, and set these in the agent's environment:

| Setting | What it is |
|---|---|
| `CUB_MINI_SIGNING_CERT` | The agent's certificate (its X.509 SVID), in PEM |
| `CUB_MINI_SIGNING_KEY` | Its private key, in PEM |
| `CUB_MINI_TRUST_BUNDLE` | The trust bundle, in PEM. Set it wherever you run `--verify` |

Each entry is then signed with the identity's key, and the signature carries the certificate, so anyone with the trust bundle can check the record.

**What it does not do.**

- **It does not sign the agent in to ConfigHub.** An agent that keeps its changes in a hub still signs in with its own ConfigHub key ([agents that run for weeks](agents-that-run-for-weeks.md)).
- **Withdrawing an identity is not instant.** It takes effect when the agent's current certificate expires.
- **The agent can read its own key.** The certificate's key is a file in the agent's pod. A program in the agent's container could sign anything with the agent's identity. So the signature shows which identity signed the record, not that the plugin saw everything the agent did.
- **Only certificates written to files are supported.** Reading them straight from SPIRE's Workload API, and JWT identities, are not.

This was run on a kind cluster with SPIRE 1.15.5 and spiffe-helper 0.10.1, with a two-minute certificate so the test could wait for it to expire.

## What it proves, and what it does not

- **It proves** that the record has not changed since each entry was written, by anyone without the key, and which key signed it.
- **It does not prove** that the hook saw everything the agent did. An agent that acts through something the plugin does not watch leaves nothing to sign.
- **The key** is made on your machine, in `~/.confighub/agent-changes/signing/`, the first time it is needed. Whoever can read the key, or run the hook, can make a record again and sign it. The settings that `cub mini require-approval --agent` writes keep the key, with the record, out of the agent's reach.
- **What a check on this machine cannot show.** Three alterations leave nothing on the machine to compare with, so `--verify` cannot name them:
  - the folder's whole record removed, with its list of signatures;
  - the latest turn taken out of the record together with its signatures and its lines in the list;
  - a record made again and signed by whoever holds the key.

  Each shows only against a copy kept elsewhere at the time: the hub's attestations, for changes kept in a hub; the record committed to the repository; or the changes sent to an OpenTelemetry collector. No command compares them today.
- **The plugin's own clean-up.** The plugin removes a session 30 days after its last write. A session whose last signature is more than 30 days old can be removed unseen in the same way.
- **A record made by plugin 0.80.0 or earlier** was signed at the end of each turn, and has no list of signatures. Its signed turns are checked as before. It cannot show a session removed, or cut back to an earlier turn. Entries after its last signature may be a turn that never ended: they are marked `--` for an hour, then `NOT`, and such a record cannot tell which.
- **Not yet:**
  - putting the digest in Sigstore's public log, for open-source repositories;
  - signing in CI with the job's own identity, such as GitHub Actions' OIDC token, with no key to keep;
  - `--verify` comparing the local record with the hub's attestations.
