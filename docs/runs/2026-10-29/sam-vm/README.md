# Sam's VM: a service that takes its settings from the hub, and agents with no SSH key

[Story 14](../../../vm.md), steps 1 to 5, run on 29 October 2026: the hub on a laptop (confighub mini, package 0.9.0-mini.5 with the `pull` commands built on it), Sam's API on a Linux VM (Ubuntu, `systemd` 259, an OrbStack machine on the same laptop, which reaches the laptop's loopback hub as `host.internal`). The service is a small Python HTTP server, started by `systemd` as a user service, that reads `api.env` and `config.toml` once at start and serves what it read.

What it shows:

- **The VM pulls, and nothing else writes its files.** `cub mini pull` runs on a `systemd` timer every 30 seconds, with a key that may read `api-live` and nothing else, writes the two files, and restarts the service only when one changed. The hub's own marker line is left out of the files.
- **The agent proposes and cannot approve, and cannot write live.** On a key of its own it changes the base, asks with a change order, is refused its own approval and its write to live, and has nothing to reach the VM with: a hub key in a configuration with nothing of Sam's in it, and no SSH key.
- **Only approved values reach the service.** The timeout Sam approves reaches the files within 30 seconds, with its reason beside it in the hub, and the service restarts. The rate limit he does not approve stays in the base; the service never sees it.
- **A hand edit on the VM does not stick.** The next pull names what differed and writes the hub's copy over it.
- **The VM's key is refused** a write to live, the base is not even visible to it, and so there is nothing to approve with.

`$` is Sam at his laptop, `$ B` the agent on its own key, `$ VM` on the VM. Two long shell lines that check the service and the last pull are shown by what they print. The hub was stopped and removed afterwards.

Found on the way: `cub function set ... set-string-path` on a settings file does nothing, silently, without `--toolchain` (the gap list, noted for cub's owners); `cub mini set KEY=VALUE` on a Component with two settings files added the key to both, so it now asks for `--unit`; a `.tar.xz` package needs `xz`, which a fresh Ubuntu does not have.

```

== 1. Sam's two files go into the hub as one Component, and live is made from the base
$ cat api/api.env api/config.toml
MODEL=small
TIMEOUT_SECONDS=30
LOG_LEVEL=info
[server]
port = 8080
rate_limit = 100

[features]
beta_search = false
$ cub mini install
==> Installing a ConfigHub server as processes on this machine
    server   http://127.0.0.1:26785 (ConfigHub build 687e8742c21f8d763951d1f29cae7ef003b51e13-mh1-1048285e5046)
    registry 127.0.0.1:29723
$ cub mini upload api
Space api-base (Create)
  Create    api
  Create    config

api is in the hub. It is not running anywhere: this hub has no cluster.
Bulk create operation completed:
  Success: 2 unit(s)

== 2. A key for the VM that may read live and nothing else; on the VM, cub pulls on a timer
$ cub mini pull-key vm api --variant live
The key vm may read api-live and nothing else: not write it, not change api-base, not approve.
Its private half is ~/.confighub-mini-item3/keys/vm.jwk; only its public half is in the hub.

On the machine that runs the service, with cub and cub mini installed and the key copied there:
  cub auth login --new-context --private-key=vm.jwk --server http://127.0.0.1:26785
  cub context rename "$(cub context get -o json | jq -r .name)" vm      # or leave the name cub gave it
  CUB_CONTEXT=vm cub mini pull api --variant live --dir /etc/api --restart "systemctl restart api" --timer 30s

Every 30 seconds it then writes api-live's files into that directory and restarts the service only when one changed.
To take the key's right away: cub mini revoke-agent vm

This hub listens on this machine only. A machine elsewhere reaches it only through a tunnel you open to it, or through a hub it can reach: copy the work up to one with cub mini copy and make the key there.
(the key is copied to the VM; this hub listens on the laptop only, and the VM reaches it as host.internal:26785, which OrbStack routes to the laptop)
$ VM cp (the key, from the laptop) ~/.confighub-vm/keys/vm.jwk; confighub-mini-app mini install-plugin ~/.confighub-vm
cub mini is now in /home/alexis/.confighub-vm, linked to /home/alexis/mini/confighub-mini-0.9.0-mini.5-linux-arm64; nothing was copied.
$ VM cub auth login --new-context --private-key=/home/alexis/.confighub-vm/keys/vm.jwk --server http://host.internal:26785; cub context rename paw-paw vm; cub context list
Token Status         valid until 2026-10-30T17:22:42Z
Successfully renamed context "paw-paw" to "vm"
Note: "vm" is now the current context
* CUB_CONTEXT, config.yaml    vm         http://host.internal:26785    Local           82dde854-7a06-471b-8931-68245fa69225@serviceaccount.confighub.dev
$ VM cat ~/.config/systemd/user/sam-api.service
[Unit]
Description=Sam's API

[Service]
ExecStart=/usr/bin/python3 /home/alexis/api-src/api.py
Environment=API_DIR=/home/alexis/api
Restart=on-failure
$ VM cub mini pull api --variant live --dir /home/alexis/api --restart "systemctl --user restart sam-api" --timer 30s
/home/alexis/.config/systemd/user/cub-mini-pull-api-live.service
  runs: /home/alexis/mini/confighub-mini-0.9.0-mini.5-linux-arm64/bin/cub mini pull api --variant live --dir /home/alexis/api --restart "systemctl --user restart sam-api"
/home/alexis/.config/systemd/user/cub-mini-pull-api-live.timer
  every 30s
The timer cub-mini-pull-api-live is running. What it did last: systemctl --user status cub-mini-pull-api-live.service
A user's timers stop at logout unless: loginctl enable-linger alexis
$ VM ls ~/api; cat ~/api/api.env; echo; cat ~/api/config.toml; systemctl --user is-active sam-api
api.env
config.toml
MODEL=small
TIMEOUT_SECONDS=30
LOG_LEVEL=info

[features]
  beta_search = false

[server]
  port = 8080
  rate_limit = 100
active
$ VM curl -s 127.0.0.1:8080     (the service, summarized)
the service serves: TIMEOUT_SECONDS 30  rate_limit 100  pid 3207

== What the VM's key cannot do: write live, see the base, approve
$ VM cub function set --space api-live --unit api --toolchain AppConfig/Env --change-desc "from the VM" set-string-path "*" TIMEOUT_SECONDS 1
Failed: failed to invoke function(s) on space 5eecda09-3259-4808-8d6a-8cf008c1bc0e: HTTP 403 for req PapySspkmZdcZLNyUeSHaxVeVGjZzlWa: permission denied
$ VM cub unit list --space api-base
Failed: space "api-base" not found
$ VM cub variant approve api-base --change-order api-base/rate-1000 --note "from the VM"
Failed: space "api-base" not found

== 3. Sam requires his approval for live, and gives the agent a key of its own
$ cub mini require-approval api --variant live --agent bot
api: a change reaches api-live only by a change order under workflows/api-live-approval, once approved by admin@local.confighub.dev.

== The agent, on its key: it changes the base and asks
$ B cub mini set api TIMEOUT_SECONDS=120 --variant base --unit api --change-desc Production waits longer for the large model
api-base
  Resource: NoSchema api
    ~ [Update] TIMEOUT_SECONDS
        30 → 120
Kept as yours: a later version will not overwrite it. Reason recorded: Production waits longer for the large model
$ B cub changeorder create --space api-base timeout-120 --component api --change-workflow workflows/api-live-approval --description Longer timeout for the large model
Successfully created changeorder timeout-120 (e9394911-7207-4cf1-a880-6ec74dae51e0)
$ B cub mini promote api-live --change-order api-base/timeout-120 --dry-run
cub mini: not promoted; the change order waits for:
  unable to promote to stage 'live', Variant 'base': requires approval: 1 Approval attestation(s) from eligible attesters; api revision 3 has 0 of 1
What it changes, value by value, before anyone approves it:
  cub unit diff --space api-live UNIT --with-unit api-base/UNIT
Someone the workflow names approves it, after reading it, with:
  cub variant approve api-base --change-order api-base/timeout-120 --note WHY

== What is refused: the agent approving its own change, and writing live itself
$ B cub variant approve api-base --change-order api-base/timeout-120 --note looks fine
Failed to approve in api-base: permission denied
Failed: approval failed in 1 space(s): api-base
$ B cub mini set api TIMEOUT_SECONDS=120 --variant live --unit api --change-desc skip the gate
cub mini: failed to invoke function(s) on space 5eecda09-3259-4808-8d6a-8cf008c1bc0e: HTTP 403 for req XwRzFxEEWufYGcsHhXmmcCVaQWNTevPw: permission denied

== What the agent has to reach the VM with
$ B ls $CUB_CONFIG $CUB_CONFIG/keys
claude-settings.json
config.yaml
functions.json
keys
plugins
tokens
bot.jwk
(a hub key, in a cub configuration with nothing of Sam's in it; the VM's address is nowhere in it, and it has no SSH key)

== Meanwhile the VM: nothing reached it
$ VM systemctl --user status cub-mini-pull-api-live.service --no-pager | grep "cub\[" | tail -3 | sed "s/.*cub\[[0-9]*\]: //"
api.env                  unchanged (revision 2)
config.toml              unchanged (revision 2)
Nothing changed; not restarted.
$ VM curl -s 127.0.0.1:8080     (the service, summarized)
the service serves: TIMEOUT_SECONDS 30  rate_limit 100  pid 3207

== 4. Sam approves the timeout, with why; it goes on to live
$ cub variant approve api-base --change-order api-base/timeout-120 --note Yes: the large model needs it
Recorded pass Approval attestation e9f5f7d2-7f22-40a3-9325-53e717f3caeb in api-base, covering 2 revision(s)
  you wrote part of the change on 1 of these units, so it does not count there for a prerequisite that excludes authors
$ cub mini promote api-live --change-order api-base/timeout-120
Updating api-live
api-live: updated. It is not delivered to a cluster
Done. Each Space kept its protected values.

== The VM, within 30 seconds: the file written, the service restarted
$ VM systemctl --user status cub-mini-pull-api-live.service --no-pager | grep "cub\[" | tail -3 | sed "s/.*cub\[[0-9]*\]: //"
api.env                  written: revision 3: Longer timeout for the large model
config.toml              unchanged (revision 2)
Restarting: systemctl --user restart sam-api
$ VM cat ~/api/api.env
MODEL=small
TIMEOUT_SECONDS=120
LOG_LEVEL=info
$ VM curl -s 127.0.0.1:8080     (the service, summarized)
the service serves: TIMEOUT_SECONDS 120  rate_limit 100  pid 3423

== The agent proposes a rate limit; Sam does not approve it
$ B cub mini set api server.rate_limit=1000 --variant base --unit config --change-desc Raise the rate limit for the batch job
api-base
  Resource: NoSchema config
    ~ [Update] server.rate_limit
        100 → 1000
Kept as yours: a later version will not overwrite it. Reason recorded: Raise the rate limit for the batch job
$ B cub changeorder create --space api-base rate-1000 --component api --change-workflow workflows/api-live-approval --description Rate limit 1000 for the batch job
Successfully created changeorder rate-1000 (392b71c0-3f7d-4e9e-b327-368abe12e683)
$ B cub mini promote api-live --change-order api-base/rate-1000 --dry-run
cub mini: not promoted; the change order waits for:
  unable to promote to stage 'live', Variant 'base': requires approval: 1 Approval attestation(s) from eligible attesters; config revision 3 has 0 of 1
What it changes, value by value, before anyone approves it:
  cub unit diff --space api-live UNIT --with-unit api-base/UNIT
Someone the workflow names approves it, after reading it, with:
  cub variant approve api-base --change-order api-base/rate-1000 --note WHY

== The VM, a minute later: the service never sees it
$ VM systemctl --user status cub-mini-pull-api-live.service --no-pager | grep "cub\[" | tail -3 | sed "s/.*cub\[[0-9]*\]: //"
api.env                  unchanged (revision 3)
config.toml              unchanged (revision 2)
Nothing changed; not restarted.
$ VM curl -s 127.0.0.1:8080     (the service, summarized)
the service serves: TIMEOUT_SECONDS 120  rate_limit 100  pid 3423
  rate_limit = 1000
  rate_limit = 100

== 5. An edit by hand on the VM is written over, and what differed is said
$ VM sed -i "s/^TIMEOUT_SECONDS=.*/TIMEOUT_SECONDS=5/" ~/api/api.env; grep TIMEOUT ~/api/api.env; sleep 33
TIMEOUT_SECONDS=5
$ VM systemctl --user status cub-mini-pull-api-live.service --no-pager | grep "cub\[" | tail -6 | sed "s/.*cub\[[0-9]*\]: //"
api.env                  changed by hand here since the last pull; the hub's copy is written over it:
                          here:    TIMEOUT_SECONDS=5
                          the hub: TIMEOUT_SECONDS=120
api.env                  written: revision 3: Longer timeout for the large model
config.toml              unchanged (revision 2)
Restarting: systemctl --user restart sam-api
$ VM curl -s 127.0.0.1:8080     (the service, summarized)
the service serves: TIMEOUT_SECONDS 120  rate_limit 100  pid 3580

== The record: live's revisions, with the reasons, and who approved
$ cub revision list api --space api-live
NUM    UNIT    SOURCE         CHANGESET    CHANGEORDERS            TAGS                             DESCRIPTION
3      api     UpgradeUnit                 api-base/timeout-120    api-base/timeout-120-co-end      Longer timeout for the large model
2      api     CloneUnit                                           api-base/timeout-120-co-start    Cloned from 3d440727-8d53-4c7e-b002-22528c40b5a...
1      api     CloneUnit                                                                            Empty revision preceding the unit's first content
$ cub changeorder list --space api-base
NAME           SPACE       STATE       STAGE        COMPLETED    UPDATE-TYPE    DESCRIPTION                           ABORTED-REASON
rate-1000      api-base    New                      false        UpgradeUnit    Rate limit 1000 for the batch job
timeout-120    api-base    Released    Completed    true         UpgradeUnit    Longer timeout for the large model
```
