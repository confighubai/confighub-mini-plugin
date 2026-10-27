# Signed records: check that nobody changed them

**Who.** A team that relies on the record of what its agents changed, in a review, an audit or an incident, and needs to know it is the record as it was written.

**What goes wrong without it.** The record is a file. Anyone who can write the folder, an agent told to tidy up included, can change a value or a reason afterwards, and nothing shows it.

**What they get.** Each turn of the record is signed when it ends, linked to the turn before. A record changed afterwards, a signature taken out, or one altered, is named when anyone checks. Nothing is asked of you or the agent; it adds about a millisecond to the end of a turn.

## Checking

```
bin/confighub mini changes --verify
```

```
The records of /work/shop:
  ok   session 255c6769: 1 turn(s) signed, unchanged since (key e6ce0a1eb16e)
  ok   .cub-mini/changes/255c6769-eb67-4f4f-bdfd-a57103ecd696.record: signed, unchanged since (key e6ce0a1eb16e)
```

A record changed after it was signed is marked `NOT`, with the turn it no longer matches, and the command fails, so a CI job can stop on it.

**In the review.** The pull-request review opens with one line: `Records in the repository: 1 signed and unchanged.` A record in the repository changed after it was signed is named there, in bold.

## Checking with standard tools

Each signature is an in-toto statement in a DSSE envelope: the format Sigstore uses, and NVIDIA's AICR uses for its evidence. With the record kept in the repository (`CUB_MINI_RECORD_IN_REPO=1`), each `.cub-mini/changes/SESSION.record` has its signature beside it, `SESSION.record.intoto.json`, committed with it. Sigstore's `cosign` checks it with this machine's public key:

```
bin/confighub mini changes --signing-key > key.pem
cosign verify-blob-attestation --key key.pem --type https://confighub.com/agent-changes/record/v1 \
  --signature .cub-mini/changes/SESSION.record.intoto.json --insecure-ignore-tlog .cub-mini/changes/SESSION.record
```

In a real session's commit, cosign 3.1.3 printed `Verified OK`. `--insecure-ignore-tlog` is there because the signature is not in Sigstore's public log; see below.

## With a hub: a witness that cannot be changed

When changes are kept in a hub (`CUB_MINI_KEEP_IN_HUB=1`, with confighub mini), each kept change has, beside its revisions in ConfigHub, an attestation of type `AgentRecord`: the digest of the turn's signature and of the record it covers, the key, and the session. ConfigHub records it with its own time and never changes it. So the record cannot later be rewritten or backdated without it showing, even by whoever holds the key.

## What it proves, and what it does not

- **It proves** that the record has not changed since each turn was signed, and which key signed it.
- **It does not prove** that the hook saw everything the agent did: an agent that acts through something the plugin does not watch leaves nothing to sign.
- **The key** is made on your machine, in `~/.confighub/agent-changes/signing/`, the first time it is needed. Whoever can read it can sign. The settings `cub mini require-approval --agent` writes keep it, with the record, out of the agent's reach; the hub's witness covers the rest.
- **Not yet:** the digest in Sigstore's public log for open-source repositories; signing in CI with the job's own identity, with no key to keep; and `--verify` comparing the local record with the hub's attestations.

`CUB_MINI_SIGN=0` turns signing off.
