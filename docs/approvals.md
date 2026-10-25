# Approvals, on ConfigHub today

An agent can propose a change to production, and only the person you name can approve it. This works today on ConfigHub, hosted or on your own server (`cub server install`), with `cub` alone. Every command below was run, in order, on hosted ConfigHub and on a server of its own, both v0.9.0. confighub mini, when it is published, does the same on a laptop, and `cub mini require-approval` sets it up in one step.

The example is a Component `api`, its base Space `api-base`, and its live copy `api-live`, made from the base with `cub variant create`.

## 1. Require your approval for live, once

Find your user ID with `cub user list`. Then:

```bash
cub space create workflows
cub space update --patch api-live --label Stage=live
cub changeworkflow create --space workflows api-live-approval --stage live \
  --attestation-prerequisite approval \
  --attestation-prerequisite-from-user-ids approval=YOUR_USER_ID \
  --attestation-prerequisite-description "approval=read and approved by a person before it reaches api-live" \
  --stage-prerequisites live=approval
cub component update --patch api --change-workflow-required \
  --allowed-change-workflow workflows/api-live-approval
```

Several user IDs, separated by `;`, name several people who may approve.

## 2. Give the agent a key of its own

Signed in as you, an agent could approve. Give it a service account that may change the base and only read live:

```bash
cub serviceaccount create bot
cub space update api-base --permission Edit:serviceaccount:bot --permission EditChildren:serviceaccount:bot \
  --permission View:serviceaccount:bot --permission ViewChildren:serviceaccount:bot
cub space update api-live --permission View:serviceaccount:bot --permission ViewChildren:serviceaccount:bot
cub space update workflows --permission View:serviceaccount:bot --permission ViewChildren:serviceaccount:bot \
  --permission UseChildren:serviceaccount:bot
cub component update api --permission View:serviceaccount:bot
```

Make its key, and sign the agent in with it, in a cub configuration of its own, so that its sessions cannot use yours:

```bash
cub serviceaccount key add bot --generate bot
CUB_CONFIG=~/.confighub-bot cub auth login --private-key=$HOME/.confighub/keys/bot.jwk --server https://hub.confighub.com
```

Run the agent with `CUB_CONFIG=~/.confighub-bot`. On the same machine it could still read your own sign-in, so for a firm line, run it where only its key is, as in CI. `cub serviceaccount delete bot` takes the access away.

## 3. The agent proposes

```bash
cub function set --space api-base --unit api --change-desc "Four for the sale" set-replicas 4
cub changeorder create --space api-base sale-4 --component api \
  --change-workflow workflows/api-live-approval --description "Four for the sale"
```

Its own `cub variant approve` is refused, and so is a write to `api-live`.

## 4. You read it, approve it, and promote it

```bash
cub unit diff --space api-live api --with-unit api-base/api
cub variant approve api-base --change-order api-base/sale-4 --note "Checked: four is right for the sale"
cub variant promote api-live --change-order api-base/sale-4
```

Until you approve, the promotion is refused. An approval covers the exact revision: if the agent changes the value again, the new change waits for an approval of its own. Who approved, when and why is kept (`cub attestation list --space api-base`).

## In a pull request

Argo CD and Flux can deploy the approved copy from ConfigHub over its OCI gateway. Where a cluster still reads Git, the approved copy can be checked against the pull request's commit, and the result set as a commit status that branch protection can require; that check is a `cub mini` command, in the confighub mini package.

More on ChangeWorkflows, ChangeOrders and attestations: [docs.confighub.com](https://docs.confighub.com).
