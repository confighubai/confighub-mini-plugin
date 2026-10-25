# Approvals, on ConfigHub today

An agent can propose a change to production, and only the person you name can approve it. It works on confighub mini on a laptop, and on ConfigHub, hosted or on your own server (`cub server install`), with `cub` alone. Every command below was run as written, on confighub mini and on hosted ConfigHub, both ConfigHub v0.9.0.

**Words used here.** A *Space* holds configuration, as *Units* (one per file or resource). A *Component* is one piece of software, such as `api`; its *base* is the version you change, and a *variant*, such as `live`, is a copy made from the base for one place it runs. A *change order* asks for a change to reach a variant; a *ChangeWorkflow* says what it needs first, here a person's approval, which ConfigHub keeps as an *attestation*.

## On confighub mini, from nothing: about 5 minutes

With confighub mini installed and a hub started ([install it](install-mini.md)), make a folder with one manifest:

```bash
mkdir api
cat > api/api.yaml <<'EOF2'
apiVersion: apps/v1
kind: Deployment
metadata: {name: api, namespace: shop}
spec:
  replicas: 2
  selector: {matchLabels: {app: api}}
  template:
    metadata: {labels: {app: api}}
    spec:
      containers:
      - {name: api, image: ghcr.io/example/shop-api:1.8.2}
EOF2
```

Put it in the hub as the Component `api`, with its base `api-base` and a live copy `api-live`, and require your approval for live. `--agent bot` also makes the agent a key of its own, in a `cub` configuration that holds nothing of yours:

```bash
cub mini upload api --variant live --namespace shop
cub mini require-approval api --variant live --agent bot
```

It prints the two settings the agent's sessions need, `CUB_CONFIG=~/.confighub-agent-bot CUB_CONTEXT=bot`, and a few lines to put in the agent's `CLAUDE.md` or `AGENTS.md` so that it asks rather than asking you for more access.

**The agent proposes.** In the agent's session, with those two settings (here given on each line, to try it by hand):

```bash
CUB_CONFIG=~/.confighub-agent-bot CUB_CONTEXT=bot cub function set --space api-base --unit api --change-desc "Four for the sale" set-replicas 4
CUB_CONFIG=~/.confighub-agent-bot CUB_CONTEXT=bot cub changeorder create --space api-base sale-4 --component api --change-workflow workflows/api-live-approval --description "Four for the sale"
```

If it tries to approve its own change (`cub variant approve`), or to write `api-live`, it is refused.

**You read it, approve it, and it goes on:**

```bash
cub mini promote api-live --change-order api-base/sale-4 --dry-run
cub variant approve api-base --change-order api-base/sale-4 --note "Checked: four is right for the sale"
cub mini promote api-live --change-order api-base/sale-4
```

The dry run says what waits, and for whom, and exits with status 1 while it waits. After your approval, `api-live` runs 4 replicas. A later change by the agent waits for an approval of its own.

## On hosted ConfigHub or your own server, with cub alone

The same, step by step, with `cub` alone. First the Component, its base and its live copy, from the folder above:

```bash
cub component create api
cub space create api-base --component api --variant base
cub unit create --space api-base api api/api.yaml
cub variant create live api-base
```

### 1. Require your approval for live, once

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

### 2. Give the agent a key of its own

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
CUB_CONFIG=~/.confighub-agent-bot cub auth login --private-key=$HOME/.confighub/keys/bot.jwk --server https://hub.confighub.com
```

Run the agent with `CUB_CONFIG=~/.confighub-agent-bot`, the same as on confighub mini. On the same machine it could still read your own sign-in, so for a firm line, run it where only its key is, as in CI. `cub serviceaccount delete bot` takes the access away.

### 3. The agent proposes

```bash
cub function set --space api-base --unit api --change-desc "Four for the sale" set-replicas 4
cub changeorder create --space api-base sale-4 --component api \
  --change-workflow workflows/api-live-approval --description "Four for the sale"
```

Its own `cub variant approve` is refused, and so is a write to `api-live`.

### 4. You read it, approve it, and promote it

```bash
cub unit diff --space api-live api --with-unit api-base/api
cub variant approve api-base --change-order api-base/sale-4 --note "Checked: four is right for the sale"
cub variant promote api-live --change-order api-base/sale-4
```

Until you approve, the promotion is refused. An approval covers the exact revision: if the agent changes the value again, the new change waits for an approval of its own. Who approved, when and why is kept (`cub attestation list --space api-base`).

## In a pull request

Argo CD and Flux can pull the approved copy straight from ConfigHub, over OCI. Where a cluster still deploys from Git, make the pull request check that its files are the approved copy. A pull request whose files differ from what was approved fails, and names each value that differs.

The order of things:

1. The change is made in the hub, approved and promoted, as above.
2. The approved copy is written out for Git and committed on a branch, by the person who approved it: `confighub-mini mini copy api --variant live --to-dir deploy/api` writes a folder for each Space, such as `deploy/api/api-live/`, and a `CHANGES.md` that says why each value is set. Argo CD or Flux deploys `deploy/api/api-live/`; the check reads all of `deploy/api`.
3. A pull request with that branch runs [the workflow](../approval-check/confighub-approval.yml), which compares `deploy/api` with the hub's copy of `api-live`, value by value, and sets the status "ConfigHub: api-live" on the commit.
4. Branch protection requires that status, so only the approved copy merges. A pull request made by hand, with values the hub has not approved, fails and names each value. To make such a change, make it in the hub, have it approved, and write it out again; `cub mini copy --from-git` takes a commit's values into the hub, each with the commit's message as its reason.

`confighub-mini` is the plugin's program, at `plugins/confighub-mini/bin/confighub-mini` in this repository; the workflow checks it out.

**Once, for the workflow.** The runner must reach the hub: hosted ConfigHub, or a server of your own. A confighub mini on a laptop cannot be reached from GitHub's runners. Give the workflow a service account that may only view the work:

```bash
cub serviceaccount create pr-check
cub space update api-base --permission View:serviceaccount:pr-check --permission ViewChildren:serviceaccount:pr-check
cub space update api-live --permission View:serviceaccount:pr-check --permission ViewChildren:serviceaccount:pr-check
cub component update api --permission View:serviceaccount:pr-check
cub serviceaccount key add pr-check --generate pr-check
gh secret set CONFIGHUB_KEY < ~/.confighub/keys/pr-check.jwk
gh variable set CONFIGHUB_SERVER --body https://hub.confighub.com
rm ~/.confighub/keys/pr-check.jwk
```

Then copy [the workflow](../approval-check/confighub-approval.yml) into `.github/workflows/`, and set its `COMPONENT`, `VARIANT` and `DIR`. It runs on every pull request, since a required status that never reports would hold other pull requests back, and it pins the plugin's version. **From a laptop instead:** where the runner cannot reach the hub, as with confighub mini, run the same check from your own machine, with the GitHub CLI signed in, and it sets the same status on the commit: `confighub-mini mini copy api --variant live --check-git deploy/api --github-status`. These steps were run against hosted ConfigHub: signed in with only that key, the check passed on the approved copy, failed on a commit with a value nobody approved ("Deployment/api/spec.replicas: 5 here, 2 in the hub"), and the key could not create anything. The workflow itself has run in a GitHub repository, setting the status on each commit.

More on ChangeWorkflows, ChangeOrders and attestations: [docs.confighub.com](https://docs.confighub.com).
