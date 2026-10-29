# Sam's app platform on one hub: an agent's release to staging and live, and rolled back

[Story 16](../../../vm.md#an-app-platform-on-the-hub), steps 1 to 5, run on 29 October 2026 on the VM of [Sam's VM](../sam-vm/README.md): the hub on the laptop; on the Linux VM, staging and live copies of Sam's API as two `systemd` user services on two ports, each with a key that reads its variant and nothing else, each pulled by `cub mini pull` on a 30-second timer, with a deploy step as the restart hook that takes the release the settings name, checks it against the digest they name, unpacks it and restarts. A release is a tarball of the service's code in a directory on the VM, built by "the agent" with its own tools, named by its digest; the image registry of a cluster is the same thing with a cluster.

What it shows:

- **A service is a Component; staging and live are variants with values of their own**: staging's port and log level, live's timeout, each with its reason.
- **An agent proposes a release: the name and digest into the base, and a change order headed for staging.** It cannot approve it. Nothing moves until Sam does.
- **Staging takes it on Sam's approval, within 30 seconds**; the deploy step checks the digest and restarts; live does not move.
- **Live takes it on one more approval**, as a revision of live with the reason beside it.
- **Rollback is two commands**: the change order is given up with a reason, and demoted from live; live is restored to the revision before it, as a new revision, and the earlier release is running within 30 seconds. Staging keeps the new release.
- **A release the settings do not name by digest is refused** by the deploy step, and the hand edit that named it is written over at the next pull.

`$` is Sam at his laptop, `$ B` the agent on its own key, `$ VM` on the VM. Long shell lines that check the two services and the last pull are shown by what they print. The hub was stopped and removed afterwards.

Found on the way: a change order made with `--component` is headed for every Space of the Component, and is refused once staging and live are at different revisions; `--in-scope-space` names the one it is for, and `cub mini require-approval` now prints that form (the gap list, noted for cub's owners).

```

== 1. A service is a Component: its settings, the release's digest among them; staging and live are variants with values of their own
$ cat api/api.env
RELEASE=api-1.0.0
RELEASE_DIGEST=sha256:83df2c98fe99cfb6d8d326adc0361dd22614964a4737c4d93cb089a2b476d13a
MODEL=small
TIMEOUT_SECONDS=30
LOG_LEVEL=info
$ cub mini install
==> Installing a ConfigHub server as processes on this machine
    server   http://127.0.0.1:27685 (ConfigHub build 687e8742c21f8d763951d1f29cae7ef003b51e13-mh1-1048285e5046)
$ cub mini upload api
Space api-base (Create)
  Create    api
  Success: 2 unit(s)
  Success: 2 unit(s)
$ cub mini set api server.port=8081 --variant staging --unit config --change-desc Staging runs beside live on the one VM
api-staging
  Resource: NoSchema config
    ~ [Update] server.port
        8080 → 8081
Kept as yours: a later version will not overwrite it. Reason recorded: Staging runs beside live on the one VM
$ cub mini set api LOG_LEVEL=debug --variant staging --unit api --change-desc Staging logs everything
api-staging
  Resource: NoSchema api
    ~ [Update] LOG_LEVEL
        info → debug
Kept as yours: a later version will not overwrite it. Reason recorded: Staging logs everything
$ cub mini set api TIMEOUT_SECONDS=120 --variant live --unit api --change-desc Production waits longer for the large model
api-live
  Resource: NoSchema api
    ~ [Update] TIMEOUT_SECONDS
        30 → 120
Kept as yours: a later version will not overwrite it. Reason recorded: Production waits longer for the large model

== 2. The VM runs both: a key for each, cub pulling each on a timer, and a deploy step that takes the release the settings name
$ cub mini pull-key vm-staging api --variant staging
$ cub mini pull-key vm-live api --variant live
$ VM cp (the two keys, from the laptop) ~/.confighub-vm/keys/; confighub-mini-app mini install-plugin ~/.confighub-vm
cub mini is now in /home/alexis/.confighub-vm, linked to /home/alexis/mini/confighub-mini-0.9.0-mini.5-linux-arm64; nothing was copied.
$ VM cub auth login --new-context --private-key=/home/alexis/.confighub-vm/keys/vm-staging.jwk --server http://host.internal:27685; cub context rename NAME vm-staging
Token Status         valid until 2026-10-30T17:35:57Z
Successfully renamed context "doze-cub" to "vm-staging"
Note: "vm-staging" is now the current context
$ VM cub auth login --new-context --private-key=/home/alexis/.confighub-vm/keys/vm-live.jwk --server http://host.internal:27685; cub context rename NAME vm-live
Token Status         valid until 2026-10-30T17:35:58Z
Successfully renamed context "meadow-bear" to "vm-live"
Note: "vm-live" is now the current context
$ VM cat ~/deploy.sh
#!/bin/bash
# deploy.sh VARIANT: run by cub mini pull after a settings file changed.
set -e
v=$1; dir=/home/alexis/$v
release=$(grep "^RELEASE=" $dir/api.env | cut -d= -f2)
want=$(grep "^RELEASE_DIGEST=" $dir/api.env | cut -d= -f2)
have="sha256:$(sha256sum /home/alexis/releases/$release.tar.gz | cut -c1-64)"
[ "$have" = "$want" ] || { echo "deploy $v: $release has digest $have, the settings say $want; not deployed"; exit 1; }
mkdir -p $dir/app && tar -C $dir/app -xzf /home/alexis/releases/$release.tar.gz
echo "deploy $v: $release ($want) unpacked; restarting sam-api-$v"
systemctl --user restart sam-api-$v
$ VM ls ~/releases
api-1.0.0.tar.gz
api-1.1.0.tar.gz
$ VM CUB_CONTEXT=vm-staging cub mini pull api --variant staging --dir /home/alexis/staging --restart "/home/alexis/deploy.sh staging" --timer 30s | head -4
/home/alexis/.config/systemd/user/cub-mini-pull-api-staging.service
  runs: /home/alexis/mini/confighub-mini-0.9.0-mini.5-linux-arm64/bin/cub mini pull api --variant staging --dir /home/alexis/staging --restart "/home/alexis/deploy.sh staging"
/home/alexis/.config/systemd/user/cub-mini-pull-api-staging.timer
  every 30s
$ VM CUB_CONTEXT=vm-live cub mini pull api --variant live --dir /home/alexis/live --restart "/home/alexis/deploy.sh live" --timer 30s | head -4
/home/alexis/.config/systemd/user/cub-mini-pull-api-live.service
  runs: /home/alexis/mini/confighub-mini-0.9.0-mini.5-linux-arm64/bin/cub mini pull api --variant live --dir /home/alexis/live --restart "/home/alexis/deploy.sh live"
/home/alexis/.config/systemd/user/cub-mini-pull-api-live.timer
  every 30s
$ VM systemctl --user status cub-mini-pull-api-staging.service     (what the last pull printed)
api.env                  written: revision 3: Staging logs everything| Functions: set-string-path
config.toml              written: revision 3: Staging runs beside live on the one VM| Functions: set-int-path
Restarting: /home/alexis/deploy.sh staging
deploy staging: api-1.0.0 (sha256:83df2c98fe99cfb6d8d326adc0361dd22614964a4737c4d93cb089a2b476d13a) unpacked; restarting sam-api-staging
$ VM systemctl --user status cub-mini-pull-api-live.service     (what the last pull printed)
api.env                  written: revision 3: Production waits longer for the large model| Functions: set-string-path
config.toml              written: revision 2: Cloned from 23910939-6d0b-43c5-9759-6df4f1a1d7e5/config
Restarting: /home/alexis/deploy.sh live
deploy live: api-1.0.0 (sha256:83df2c98fe99cfb6d8d326adc0361dd22614964a4737c4d93cb089a2b476d13a) unpacked; restarting sam-api-live
$ VM curl -s 127.0.0.1:8081; curl -s 127.0.0.1:8080     (staging and live, summarized)
now: staging serves release api-1.0.0  health -  LOG_LEVEL debug  TIMEOUT_SECONDS 30  pid 5542
now: live serves release api-1.0.0  health -  LOG_LEVEL info  TIMEOUT_SECONDS 120  pid 5594

== 3. The agent builds 1.1.0 and proposes it as a release: the digest and nothing else, asked for staging
$ cub mini require-approval api --variant staging --agent bot
$ cub mini require-approval api --variant live
$ VM echo "(built by the agent with its own tools; not ours)"; sha256sum ~/releases/api-1.1.0.tar.gz | cut -c1-64
(built by the agent with its own tools; not ours)
6d510a8326fd92987197eb5e16d9145361f7377f4467a1abf79a637e0393149c
Kept as yours: a later version will not overwrite it. Reason recorded: Release 1.1.0: answers /health for the load balancer
Kept as yours: a later version will not overwrite it. Reason recorded: Release 1.1.0: answers /health for the load balancer
$ B cub changeorder create --space api-base release-1-1-0 --in-scope-space api-staging --change-workflow workflows/api-staging-approval --description Release 1.1.0 to staging: /health for the load balancer
Successfully created changeorder release-1-1-0 (1bc96566-44b4-4487-b694-bee0c0cbb349)
$ B cub mini promote api-staging --change-order api-base/release-1-1-0 --dry-run
cub mini: not promoted; the change order waits for:
  unable to promote to stage 'staging', Variant 'base': requires approval: 1 Approval attestation(s) from eligible attesters; api revision 4 has 0 of 1
$ B cub variant approve api-base --change-order api-base/release-1-1-0 --note ship it
Failed to approve in api-base: permission denied
Failed: approval failed in 1 space(s): api-base

== Staging takes it: Sam approves, the staging runtime pulls the release and deploys it; live does not move
$ cub variant approve api-base --change-order api-base/release-1-1-0 --note Tried it: the health check answers
Recorded pass Approval attestation c09f67c6-3eaa-4b08-a1ae-50927587464b in api-base, covering 2 revision(s)
  you wrote part of the change on 1 of these units, so it does not count there for a prerequisite that excludes authors
api-staging: updated. It is not delivered to a cluster
Done. Each Space kept its protected values.
$ VM systemctl --user status cub-mini-pull-api-staging.service     (what the last pull printed)
api.env                  written: revision 4: Release 1.1.0 to staging: /health for the load balancer
config.toml              unchanged (revision 3)
Restarting: /home/alexis/deploy.sh staging
deploy staging: api-1.1.0 (sha256:6d510a8326fd92987197eb5e16d9145361f7377f4467a1abf79a637e0393149c) unpacked; restarting sam-api-staging
$ VM curl -s 127.0.0.1:8081; curl -s 127.0.0.1:8080     (staging and live, summarized)
after staging: staging serves release api-1.1.0  health ok  LOG_LEVEL debug  TIMEOUT_SECONDS 30  pid 5754
after staging: live serves release api-1.0.0  health -  LOG_LEVEL info  TIMEOUT_SECONDS 120  pid 5594

== 4. Sam promotes to live: one approval, and the live runtime pulls it
$ cub changeorder create --space api-base release-1-1-0-live --in-scope-space api-live --change-workflow workflows/api-live-approval --description Release 1.1.0 to live
Successfully created changeorder release-1-1-0-live (654a8d17-84ff-42a7-97f4-1ef61943d24c)
$ cub variant approve api-base --change-order api-base/release-1-1-0-live --note A day on staging, no errors
Recorded pass Approval attestation 4f681266-3799-43d0-83c3-b2a15790c51a in api-base, covering 2 revision(s)
  you wrote part of the change on 1 of these units, so it does not count there for a prerequisite that excludes authors
api-live: updated. It is not delivered to a cluster
Done. Each Space kept its protected values.
$ VM systemctl --user status cub-mini-pull-api-live.service     (what the last pull printed)
api.env                  written: revision 4: Release 1.1.0 to live
config.toml              unchanged (revision 2)
Restarting: /home/alexis/deploy.sh live
deploy live: api-1.1.0 (sha256:6d510a8326fd92987197eb5e16d9145361f7377f4467a1abf79a637e0393149c) unpacked; restarting sam-api-live
$ VM curl -s 127.0.0.1:8081; curl -s 127.0.0.1:8080     (staging and live, summarized)
after live: staging serves release api-1.1.0  health ok  LOG_LEVEL debug  TIMEOUT_SECONDS 30  pid 5754
after live: live serves release api-1.1.0  health ok  LOG_LEVEL info  TIMEOUT_SECONDS 120  pid 5903
$ cub revision list api --space api-live
NUM    UNIT    SOURCE         CHANGESET    CHANGEORDERS                   TAGS                                DESCRIPTION
4      api     UpgradeUnit                 api-base/release-1-1-0-live    api-base/release-1-1-0-live-c...    Release 1.1.0 to live
3      api     Invoke                                                     api-base/release-1-1-0-live-c...    Production waits longer for the large model| Fu...
2      api     CloneUnit                                                                                      Cloned from 23910939-6d0b-43c5-9759-6df4f1a1d7e...
1      api     CloneUnit                                                                                      Empty revision preceding the unit's first content

== 5. Rollback: the release is given up on and taken back out of live, in one command each; live pulls the earlier release
$ cub changeorder update release-1-1-0-live --space api-base --aborted-reason 1.1.0 answers /health slowly under load; back to 1.0.0
Successfully updated changeorder release-1-1-0-live (654a8d17-84ff-42a7-97f4-1ef61943d24c)
$ cub variant demote api-live --change-order api-base/release-1-1-0-live
Restored 1 unit(s) to the revisions before change order release-1-1-0-live
Marked 1 unit(s) the change order carried nothing for as restored, without a new revision
$ VM systemctl --user status cub-mini-pull-api-live.service     (what the last pull printed)
api.env                  written: revision 5: Undo change order release-1-1-0-live
config.toml              unchanged (revision 2)
Restarting: /home/alexis/deploy.sh live
deploy live: api-1.0.0 (sha256:83df2c98fe99cfb6d8d326adc0361dd22614964a4737c4d93cb089a2b476d13a) unpacked; restarting sam-api-live
$ VM curl -s 127.0.0.1:8081; curl -s 127.0.0.1:8080     (staging and live, summarized)
after rollback: staging serves release api-1.1.0  health ok  LOG_LEVEL debug  TIMEOUT_SECONDS 30  pid 5754
after rollback: live serves release api-1.0.0  health -  LOG_LEVEL info  TIMEOUT_SECONDS 120  pid 6058
$ cub revision list api --space api-live
NUM    UNIT    SOURCE             CHANGESET    CHANGEORDERS                   TAGS                                DESCRIPTION
5      api     RestoreRevision                                                api-base/release-1-1-0-live-c...    Undo change order release-1-1-0-live
4      api     UpgradeUnit                     api-base/release-1-1-0-live    api-base/release-1-1-0-live-c...    Release 1.1.0 to live
3      api     Invoke                                                         api-base/release-1-1-0-live-c...    Production waits longer for the large model| Fu...
2      api     CloneUnit                                                                                          Cloned from 23910939-6d0b-43c5-9759-6df4f1a1d7e...
1      api     CloneUnit                                                                                          Empty revision preceding the unit's first content
$ cub changeorder list --space api-base
NAME                  SPACE       STATE       STAGE        COMPLETED    UPDATE-TYPE    DESCRIPTION                                           ABORTED-REASON
release-1-1-0         api-base    Released    Completed    true         UpgradeUnit    Release 1.1.0 to staging: /health for the load ...
release-1-1-0-live    api-base    Aborted     Completed    true         UpgradeUnit    Release 1.1.0 to live                                 1.1.0 answers /health slowly under load; back t...

== What is refused on the VM: a release the settings do not name by digest
$ VM sed -i "s/^RELEASE=.*/RELEASE=api-1.1.0/" ~/live/api.env; /home/alexis/deploy.sh live; echo "exit=$?"; sleep 33
deploy live: api-1.1.0 has digest sha256:6d510a8326fd92987197eb5e16d9145361f7377f4467a1abf79a637e0393149c, the settings say sha256:83df2c98fe99cfb6d8d326adc0361dd22614964a4737c4d93cb089a2b476d13a; not deployed
exit=1
$ VM systemctl --user status cub-mini-pull-api-live.service     (what the last pull printed)
                          here:    RELEASE=api-1.1.0
                          the hub: RELEASE=api-1.0.0
api.env                  written: revision 5: Undo change order release-1-1-0-live
config.toml              unchanged (revision 2)
Restarting: /home/alexis/deploy.sh live
deploy live: api-1.0.0 (sha256:83df2c98fe99cfb6d8d326adc0361dd22614964a4737c4d93cb089a2b476d13a) unpacked; restarting sam-api-live
$ VM curl -s 127.0.0.1:8081; curl -s 127.0.0.1:8080     (staging and live, summarized)
after the hand edit: staging serves release api-1.1.0  health ok  LOG_LEVEL debug  TIMEOUT_SECONDS 30  pid 5754
after the hand edit: live serves release api-1.0.0  health -  LOG_LEVEL info  TIMEOUT_SECONDS 120  pid 6220
```
