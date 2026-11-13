# Harden a service on a Linux VM, with production behind an approval

Sam already has an HTTP service running on a Linux VM. He tries a smaller request limit in staging, sees oversized requests refused there, and lets production take that exact change only after approval. The agent's proposal key cannot approve or write production; each running copy's reader key can read its settings and cannot write them.

- **Way in:** an app you already have, running without Kubernetes.
- **Stage:** confighub mini, with systemd on an existing Linux VM.

## What it needs

A Mac with OrbStack and an existing, running Linux machine with Python 3 and user systemd. `VM_SERVICE_MACHINE` defaults to `sam-vm`. Set `CONFIGHUB_MINI_PACKAGE` to the unpacked Mac package and `VM_SERVICE_LINUX_PACKAGE` to the unpacked Linux package for that machine's architecture. OrbStack's `/mnt/mac` filesystem shares the package with the VM. The VM reaches the laptop's loopback hub through OrbStack's `host.internal` routing.

## Run it

1. Point the check at the existing VM and the two unpacked packages:

   ```
   VM_SERVICE_MACHINE=sam-vm \
   CONFIGHUB_MINI_PACKAGE=/path/to/darwin-package \
   VM_SERVICE_LINUX_PACKAGE=/path/to/linux-package \
   VM_SERVICE_RESULT=/path/to/result.json python3 ./run
   ```

`run` starts a hub, installs `api.py` as two isolated user services, and runs the checks. It removes its own hub, files, services, timers and keys on success or failure. It leaves the existing VM and other services running. No Kubernetes or Docker is used.

### Have an agent build the app

With a package that includes the Codex launcher from `require-approval --agent`, add:

```
python3 ./run --agent --model MODEL --out /path/to/new-run-record
```

The runner sets up the pattern's initial settings, hub and scoped proposal key before the agent starts. Its trusted bootstrap approves the known initial settings as a scripted fixture; the later hardening has a separate proposal and approval. The first real Codex session writes the API from its request and the pattern's instructions; the runner deploys that code as staging and live. Two later sessions try the hardening in staging, then propose it for live. The agent gets no owner sign-in or VM login. Its Codex state is separate from yours, and native command sandboxes deny the owner configuration and the agent's login files. Its hooks keep the configuration history outside those command sandboxes.

Codex CLI must support native permission profiles and `--no-daemon`; this was developed against 0.163.0. It uses the existing file-based Codex login; it does not copy the person's Codex settings, plugins or other integrations. Model options go on the launcher or `--model` here. The recorded sessions are functional runs, not an evaluation of unaided first-time users.

### Approve in the same terminal

Add `--interactive` to read the exact proposal and answer the existing `cub mini approve` prompt in this terminal. The proposing agent has exited by then. The prompt runs in the owner process, outside the agent's credentials and sandbox. No approval token or callback is given to the agent. Saying no leaves live unchanged and removes the isolated example. Without a terminal, it refuses to guess. Without `--interactive`, the approval remains a scripted test and is recorded as such.

The VM services run with a private user namespace, no privilege escalation, no Unix-socket address family, and no access to OrbStack's `/mnt/mac` host mount. This separates generated app code from the host's files; it is not a production deployment policy.

## What you see when it passes

Each assertion prints `PASS`, including the two services answering requests, a staging request returning HTTP 413 while production still returns 200, and production returning 413 after approval. A JSON result records each assertion and whether the example completed.

From the engineering run on 9 November 2026:

```
PASS hardening changes real staging behaviour only
PASS the agent cannot approve its own proposal
PASS the agent cannot write live directly
PASS the pending proposal cannot be promoted
PASS production still accepts the original request
PASS the approved revision changes production behaviour
```

## What it checks

- Both staging and production serve real HTTP requests.
- An unchanged pull does not restart a service.
- Staging enforces its new request limit while production keeps its original behavior.
- The proposal key cannot approve itself or write production directly, and an unapproved proposal cannot be promoted.
- After approval, a deliberately failed restart leaves a retry owed; a file-only pull preserves that debt.
- A successful retry starts the approved configuration; the service reports the loaded revision and SHA-256.
- Rollback waits for a fresh approval and restores the original request behavior.
- The production reader cannot write the configuration it reads.

The default uses scripted calls under the agent's key and a scripted approval under the owner's key. `--agent` records the real sessions; `--interactive` uses a person's terminal prompt. Neither is approval inside a coding agent's chat UI. The VM runs on the development Mac; this is not a cloud deployment. The example does not change an existing user service: it brings up isolated copies of the example API.

The words on this page, such as *hub*, *base* and *change order*, are explained in [the glossary](../../docs/README.md#words).
