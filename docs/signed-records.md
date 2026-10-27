# Signed records: check that nobody changed them

This page is for a team that relies on the plugin's record of what its agents changed: in a review, an audit or an incident. The record is a file. Anyone who can write to its folder, including an agent told to tidy up, can change a value or a reason afterwards, and nothing would show it. Signing lets anyone check that the record is still as it was written.

The plugin signs each turn of the record when the turn ends. A **turn** is one request in a session and the agent's work on it. Each signature is linked to the turn before. If a record is changed afterwards, or a signature is taken out or altered, a check names it.

Nothing is asked of you or the agent. Signing adds about a millisecond to the end of a turn. `CUB_MINI_SIGN=0` turns it off.

## Checking the record

Run:

```
bin/confighub mini changes --verify
```

You will see something like:

```
The records of /work/shop:
  ok   session 255c6769: 1 turn(s) signed, unchanged since (key e6ce0a1eb16e)
  ok   .cub-mini/changes/255c6769-eb67-4f4f-bdfd-a57103ecd696.record: signed, unchanged since (key e6ce0a1eb16e)
```

A record changed after it was signed is marked `NOT`, with the turn it no longer matches. The command then fails, so a CI job can stop on it.

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

## With a hub: a witness that cannot be changed

ConfigHub is a hub: a place where your configuration is kept, with every change, who made it and why ([ConfigHub docs](https://docs.confighub.com)). A hub is a ConfigHub server. confighub mini is ConfigHub, small, for one machine ([install confighub mini](install-mini.md)). With confighub mini, `CUB_MINI_KEEP_IN_HUB=1` keeps changes in the hub.

Each change kept in the hub then has an attestation beside its revisions in ConfigHub. An attestation is a statement that ConfigHub stores; this one is of type `AgentRecord`. It holds:

- the digest of the turn's signature, and of the record it covers;
- the key;
- the session.

ConfigHub records the attestation with its own time, and never changes it. So nobody can later rewrite or backdate the record without it showing, not even whoever holds the key.

## What it proves, and what it does not

- **It proves** that the record has not changed since each turn was signed, and which key signed it.
- **It does not prove** that the hook saw everything the agent did. An agent that acts through something the plugin does not watch leaves nothing to sign.
- **The key** is made on your machine, in `~/.confighub/agent-changes/signing/`, the first time it is needed. Whoever can read the key can sign. The settings that `cub mini require-approval --agent` writes keep the key, with the record, out of the agent's reach. The hub's witness covers the rest.
- **Not yet:**
  - putting the digest in Sigstore's public log, for open-source repositories;
  - signing in CI with the job's own identity, with no key to keep;
  - `--verify` comparing the local record with the hub's attestations.
