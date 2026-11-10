# Four runnable product examples

These examples show what R1–R4 do today. R1 runs real HTTP services on an existing Linux VM. R2–R4 check configuration stored in isolated local hubs. They do not need Kubernetes. Each prints `PASS` or fails with a nonzero exit code; `--out` keeps a JSON result outside its temporary workspace.

- **Way in:** an app you already have, or software with ConfigHub inside it.
- **Stage:** confighub mini; R4 also works with your organization's ConfigHub.

## What it needs

Use Python 3.12 or newer, Git and a mini package. R1 also needs a Mac, OrbStack, and an existing Linux machine with Python 3 and user systemd. The examples create their own hub configurations and keys. They leave your normal sign-in alone.

## Run it

1. Get the packages as below.
2. Run the command for R1, R2, R3 or R4.

### Get the packages

From this directory:

```sh
python3 get-packages.py --vm sam-vm
. ./.confighub-example-env
```

Replace `sam-vm` with your existing OrbStack machine. To run only R2–R4, omit `--vm`. The downloader checks the published SHA-256 hashes and writes only quoted local package paths. It refuses to replace an existing environment file; choose another `--env PATH` for another run. You can instead set `CONFIGHUB_MINI_PACKAGE` and `VM_SERVICE_LINUX_PACKAGE` to unpacked packages yourself.

## R1: change, approve, recover and roll back a running service

```sh
python3 run.py r1 --vm sam-vm --out "$HOME/r1-result.json"
```

The example starts isolated staging and live HTTP services on that VM. Staging takes a smaller request limit while live keeps answering the original request. The proposer cannot approve or write live. You review and approve the hardening in your terminal, then separately approve its rollback. The initial baseline is a scripted setup fixture.

The checks include a deliberate restart failure, an outstanding-restart receipt that survives a file-only pull, successful recovery, and the service's loaded revision and content hash. Rollback needs a new approval. Declining approval leaves live at its previous behavior until the example cleans up. Approval is in your terminal; there is no approval prompt inside the coding agent's chat.

For an automated check, explicitly select scripted approval:

```sh
python3 run.py r1 --vm sam-vm --scripted --out "$HOME/r1-scripted.json"
```

This is a functional test, not evidence that an outside developer completed the journey or a person approved it. This VM example creates its own service copies; it does not attach to or modify your existing application.

## R2: use a setup again without losing your own values

```sh
python3 run.py r2 --out "$HOME/r2-result.json"
```

The first app supplies a logging setting and reason. The second keeps its own port, region and local credential. An upstream update changes the inherited setting while those choices survive. Live stays unchanged until a separate change order is approved; the exported setup excludes the credential.

This checks stored configuration and uses scripted approvals. It does not launch a second service, measure unaided human use or transfer reasons into newly generated Kubernetes manifests.

## R3: copy between hubs and return to plain files

```sh
python3 run.py r3 --out "$HOME/r3-result.json"
```

Two local hubs exercise the copy/connect path. The app keeps its values, protection and reasons; a parent update leaves the local port choice intact. Returning to plain files produces native settings files and `CHANGES.md`, with no owner key.

This uses one owner and two local hubs. It does not exercise cloud signup, two-person cloud sharing, full historical revision/cost replay, or a service running after the move. The current hosted cloud is single-user. Use a provisioned shared hub for a team journey.

## R4: read a pinned revision from a small extension

```sh
python3 run.py r4 --out "$HOME/r4-result.json"
```

The [snapshot extension](../extensions/config-snapshot/README.md) uses a key limited to the app's live variant. It writes a versioned JSON snapshot and checks that retrying the same revision gives the same bytes. The check also tries, and is refused, reading base, writing live and approving.

The reader needs no owner key. This is an interface example using ordinary `cub` authentication; it makes no claim about authenticated agent delegation or a new SDK.

## Inspect and clean up

By default every example removes its own hubs, keys and workspace on success or failure. R1 also removes its own systemd services and timers; it leaves the existing VM running. Result files remain where you requested them.

For R2–R4, add `--keep` to retain the workspace. The runner prints its exact inspection and cleanup commands:

```sh
python3 run.py r2 --keep
python3 run.py cleanup "$HOME/.confighub-roadmap-PRINTED-ID"
```

Cleanup accepts only a workspace created by this runner and removes only the hubs in its marker. A failed cleanup retains the workspace, returns failure and records an incomplete result. Use a new `--out` filename for each run.

## What you see when it passes

The engineering runs include:

```text
PASS new pattern revision waits for its own approval
PASS approved pattern reaches live with recipient values kept
PASS retrying the same revision is idempotent
```

## What it checks

Each section above names its assertions and limits. A failed assertion stops the example, exits nonzero and attempts cleanup. A scripted approval does not count as a real person's acceptance.

## Words used here

A **variant** holds one environment's settings. A **pattern** supplies shared settings while an app keeps its own choices. A **change order** proposes a revision; approval covers that revision. A **snapshot** is one pinned revision read by the extension.
