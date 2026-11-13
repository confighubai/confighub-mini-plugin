# Four examples you can run

Four short examples of what a hub on your laptop does for an app's settings, each run with one command:

- **`r1`:** a service on a Linux VM. Staging takes a change at once, live waits for your approval, and you roll it back the same way.
- **`r2`:** a second app that reuses the first app's settings and keeps its own values when the first changes.
- **`r3`:** copying an app from one hub to another, and back out to plain files.
- **`r4`:** a small program that reads one approved version of an app's settings, with a key that can do nothing else.

None of them needs Kubernetes. Each makes hubs of its own on your machine and removes them when it's done. Each prints `PASS` for each thing it checks, or stops with an error; `--out FILE` saves the result as JSON. They run on confighub mini, and `r4` also works with your organization's ConfigHub.

## What you need

Python 3.12 or newer, Git, and a confighub mini package (the next step gets it). For `r1`, you also need a Mac with OrbStack and a Linux machine in it with Python 3 and user systemd. The examples make their own hub configurations and keys, and leave your own sign-in alone.

## Run it

1. Get the packages, as below.
2. Run the command for `r1`, `r2`, `r3` or `r4`.

### Get the packages

From this folder:

```sh
python3 get-packages.py --vm my-vm
. ./.confighub-example-env
```

Replace `my-vm` with the name of your Linux machine in OrbStack. To run only `r2` to `r4`, leave out `--vm`. The downloader checks the published SHA-256 hashes and writes only quoted local package paths. It refuses to replace an existing environment file; choose another `--env PATH` for another run. You can instead set `CONFIGHUB_MINI_PACKAGE` and `VM_SERVICE_LINUX_PACKAGE` to unpacked packages yourself.

## r1: change, approve, recover and roll back a running service

```sh
python3 run.py r1 --vm my-vm --out "$HOME/r1-result.json"
```

The example starts isolated staging and live HTTP services on that VM. Staging takes a smaller request limit while live keeps answering the original request. The proposer cannot approve or write live. You review and approve the hardening in your terminal, then separately approve its rollback. The initial baseline is a scripted setup fixture.

The checks include a deliberate restart failure, an outstanding-restart receipt that survives a file-only pull, successful recovery, and the service's loaded revision and content hash. Rollback needs a new approval. Declining approval leaves live at its previous behavior until the example cleans up. Approval is in your terminal; there is no approval prompt inside the coding agent's chat.

For an automated check, explicitly select scripted approval:

```sh
python3 run.py r1 --vm my-vm --scripted --out "$HOME/r1-scripted.json"
```

With `--scripted`, the script approves, not you. This VM example creates its own service copies; it does not attach to or modify your existing application.

## r2: use a setup again without losing your own values

```sh
python3 run.py r2 --out "$HOME/r2-result.json"
```

The first app supplies a logging setting and reason. The second keeps its own port, region and local credential. An upstream update changes the inherited setting while those choices survive. Live stays unchanged until a separate change order is approved; the exported setup excludes the credential.

This checks the stored configuration, and the script approves. It doesn't start a second service, or carry reasons into newly generated Kubernetes manifests.

## r3: copy between hubs and return to plain files

```sh
python3 run.py r3 --out "$HOME/r3-result.json"
```

Two local hubs exercise the copy/connect path. The app keeps its values, protection and reasons; a parent update leaves the local port choice intact. Returning to plain files produces native settings files and `CHANGES.md`, with no owner key.

This uses one owner and two local hubs. It doesn't cover signing up for hosted ConfigHub, two people sharing one hub, full historical revision/cost replay, or a service running after the move. For a team, use a shared hub: hosted ConfigHub or the enterprise edition, where many people share one organization.

## r4: read a pinned revision from a small extension

```sh
python3 run.py r4 --out "$HOME/r4-result.json"
```

The [snapshot extension](../extensions/config-snapshot/README.md) uses a key limited to the app's live variant. It writes a versioned JSON snapshot and checks that retrying the same revision gives the same bytes. The check also tries, and is refused, reading base, writing live and approving.

The reader needs no owner key. It signs in the ordinary `cub` way; it isn't a new SDK.

## Inspect and clean up

By default every example removes its own hubs, keys and workspace on success or failure. `r1` also removes its own systemd services and timers; it leaves the existing VM running. Result files remain where you requested them.

For `r2` to `r4`, add `--keep` to retain the workspace. The runner prints its exact inspection and cleanup commands:

```sh
python3 run.py r2 --keep
python3 run.py cleanup "$HOME/.confighub-roadmap-PRINTED-ID"
```

Cleanup accepts only a workspace created by this runner and removes only the hubs in its marker. A failed cleanup retains the workspace, returns failure and records an incomplete result. Use a new `--out` filename for each run.

## What you see when it passes

Lines such as:

```text
PASS new pattern revision waits for its own approval
PASS approved pattern reaches live with recipient values kept
PASS retrying the same revision is idempotent
```

## What it checks

Each section above names its assertions and limits. A failed assertion stops the example, exits nonzero and attempts cleanup. A scripted approval does not count as a real person's acceptance.

The words on this page, such as *hub*, *base* and *change order*, are explained in [the glossary](../../docs/README.md#words).
