# A person approves an agent's change, with the hub's own approval

`cub mini require-approval api --variant live`, then an agent, with a key of its own that may change `api`'s base and read its live variant, makes a change and asks for it with a change order. The approval is ConfigHub's own: an Attestation of the exact revisions of the change, recorded with who, when and why; a ChangeWorkflow gates the live variant on one from the person named, and the Component takes a change only by a change order under it. One hub, on one machine; the package is minihub 0.38.0-dev; the hub was stopped and removed afterwards.

What it shows:

- The change waits, for the person and for the agent alike, and `cub mini promote` says what it waits for and how to approve it.
- The agent cannot approve its own change: its key has no right to approve.
- A colleague who may approve, but is not the person named, records an approval that does not count.
- The person's approval lets it through, and only it: the agent's next change waits for one of its own.

The run's script used `cub mini promote ... --yes`, a flag the command does not have; that step was run again by hand, without it, on the same hub, and its output is put in its place below. `cub mini promote` now names the change order in the command it suggests, where this run printed `cub variant approve SPACE --change-order SPACE/CHANGE-ORDER`.

```
== Set up: the work, api, and its live variant. You require your approval for live.
$ cub mini require-approval api --variant live --dry-run
api: a change reaches api-live only by a change order under workflows/api-live-approval, once approved by admin@local.confighub.dev.
Nothing was changed.
$ cub mini require-approval api --variant live
api: a change reaches api-live only by a change order under workflows/api-live-approval, once approved by admin@local.confighub.dev.
After a change to api-base, by an agent or anyone else, a change order asks for it:
  cub changeorder create --space api-base NAME --component api --change-workflow workflows/api-live-approval --description WHY
What waits, and for whom:
  cub mini promote api-live --change-order api-base/NAME --dry-run
Approving it, with why; it is recorded, and covers only what it was given:
  cub variant approve api-base --change-order api-base/NAME --note WHY
Then it goes on:
  cub mini promote api-live --change-order api-base/NAME

== An agent, with a key of its own, that may change the base and read live

== The agent changes the base, and asks
$ A cub function set --space api-base --unit api --change-desc Four for the sale set-replicas 4
Function(s) succeeded on unit api-base/api (a377ed65-b5e9-4fcc-987a-57baa76e4963)
Config data changed
Awaiting triggers...
$ A cub changeorder create --space api-base sale-4 --component api --change-workflow workflows/api-live-approval --description Four replicas for the sale
Successfully created changeorder sale-4 (1f60fb25-7d0c-45cb-b48c-9a00448278c1)

== What waits
$ cub mini promote api-live --change-order api-base/sale-4 --dry-run
cub mini: not promoted; the change order waits for:
  unable to promote to stage 'live', Variant 'base': requires approval: 1 Approval attestation(s) from eligible attesters; api revision 3 has 0 of 1
Someone the workflow names approves it with: cub variant approve SPACE --change-order SPACE/CHANGE-ORDER --note WHY
$ A cub mini promote api-live --change-order api-base/sale-4
cub mini: not promoted; the change order waits for:
  unable to promote to stage 'live', Variant 'base': requires approval: 1 Approval attestation(s) from eligible attesters; api revision 3 has 0 of 1
Someone the workflow names approves it with: cub variant approve SPACE --change-order SPACE/CHANGE-ORDER --note WHY

== The agent tries to approve it itself
$ A cub variant approve api-base --change-order api-base/sale-4 --note looks fine
Failed to approve in api-base: permission denied
Failed: approval failed in 1 space(s): api-base

== A colleague who may approve, but is not the one named
$ env CUB_CONTEXT=colleague cub variant approve api-base --change-order api-base/sale-4 --note fine by me
Recorded pass Approval attestation 6d7b922e-246a-40f4-932c-ddec0ceff751 in api-base, covering 1 revision(s)
$ cub mini promote api-live --change-order api-base/sale-4 --dry-run
cub mini: not promoted; the change order waits for:
  unable to promote to stage 'live', Variant 'base': requires approval: 1 Approval attestation(s) from eligible attesters; api revision 3 has 0 of 1
Someone the workflow names approves it with: cub variant approve SPACE --change-order SPACE/CHANGE-ORDER --note WHY

== You approve
$ cub variant approve api-base --change-order api-base/sale-4 --note Checked: four is right for the sale
Recorded pass Approval attestation a86e52e9-26c9-4a9c-891a-236f6f079945 in api-base, covering 1 revision(s)
Updating api-live
api-live: updated. It is not delivered to a cluster
Done. Each Space kept its protected values.
live now: replicas: 4
$ cub attestation list --space api-base
ATTESTATION-ID                          TYPE        RESULT    REVOKES    USER-ID                                 CREATED                              
6d7b922e-246a-40f4-932c-ddec0ceff751    Approval    Pass                 fd741fce-1eba-496d-a374-a9f47ecd0948    2026-10-20 14:33:51.231528 -0700 PDT    
a86e52e9-26c9-4a9c-891a-236f6f079945    Approval    Pass                 172341ec-a24e-4c47-86be-9b5c82dfddd8    2026-10-20 14:33:51.496905 -0700 PDT    

== The agent changes it again
$ A cub function set --space api-base --unit api --change-desc Six, to be safe set-replicas 6
Function(s) succeeded on unit api-base/api (a377ed65-b5e9-4fcc-987a-57baa76e4963)
Config data changed
Awaiting triggers...
$ A cub changeorder create --space api-base safe-6 --component api --change-workflow workflows/api-live-approval --description Six
Successfully created changeorder safe-6 (401a53c5-3e3c-44e1-9c60-4967acece5c1)
$ cub mini promote api-live --change-order api-base/safe-6 --dry-run
cub mini: not promoted; the change order waits for:
  unable to promote to stage 'live', Variant 'base': requires approval: 1 Approval attestation(s) from eligible attesters; api revision 4 has 0 of 1
Someone the workflow names approves it with: cub variant approve SPACE --change-order SPACE/CHANGE-ORDER --note WHY

== Without a change order
$ cub mini promote api-live --dry-run
cub mini: not promoted; the change order waits for:
  unable to promote to stage 'live', Variant 'base': requires approval: 1 Approval attestation(s) from eligible attesters; api revision 4 has 0 of 1
Someone the workflow names approves it with: cub variant approve SPACE --change-order SPACE/CHANGE-ORDER --note WHY
```
