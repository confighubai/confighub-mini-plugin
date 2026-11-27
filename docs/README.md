# Documentation

Start with the app you want to build or connect. ConfigHub keeps its setup and the reasons for each setting, so the next session, version, or app can start from it. Choose a [walkthrough](../examples/walkthroughs/README.md) for your stack, or install the Claude plugin and try a first app. [README](../README.md) · [Product overview](https://confighub.github.io/helm-expt/ai-agents/)

A **hub** is a ConfigHub server and database that stores your app's settings, the reason for each value, and who approved each change — on your laptop (`confighub mini`), hosted on confighub.com, or self-hosted in your cluster. Terms (*base*, *change order*, *Space*) are defined in [Words](words.md).

## Get started

| Page | What it's for |
|---|---|
| [Walkthroughs](../examples/walkthroughs/README.md) | End-to-end jobs with exact commands and expected output |
| [Try the Claude plugin on its own](try-the-plugin.md) | Record agent edits and reasons with no hub |
| [Install the local hub](install-mini.md) | Free single-machine hub on your laptop (no account, no Docker) |

### By stack or journey

| Page | What it's for |
|---|---|
| [A new app](journeys/new-app.md) | Build a new app with staging and gated production |
| [An app you already have](journeys/existing-app.md) | Attach `.env`, Terraform, Kustomize, or Helm files as-is |
| [An app that Argo CD or Flux deploys](journeys/gitops-app.md) | Hub beside Git, PR checks, or hub as OCI source |
| [A Next.js app on Vercel](nextjs-on-vercel.md) | Staging on Vercel with approved production delivery |
| [Rails on Fly](rails-on-fly.md) | Connect a running Fly app or share setup across apps |
| [An app on Heroku](heroku.md) | Pipeline-style staging/prod on Heroku and move to Fly/Vercel |
| [A first run of the local hub](try-confighub-mini.md) | Install, run one story, and load your agent record |

## Concepts

| Page | What it's for |
|---|---|
| [Add only what you need](add-as-you-grow.md) | Full 11-step progression from plugin to shared hub and GitOps |
| [Why not just Git, your host, or a rules file](why-durable-config.md) | What ConfigHub adds beyond Git, host dashboards, and `CLAUDE.md` |
| [When ConfigHub acts](agent-workflow.md) | When hooks stay quiet and when a hub is offered |
| [How the Claude plugin works](how-it-works.md) | Hook lifecycle, what is recorded, settings, and token cost |
| [Approvals](approvals.md) | Scoped agent proposals gated on human approval |
| [Starters](starters.md) | Shared team defaults where app overrides always win |
| [Write and check a starter](write-a-starter.md) | Author and test a 1-file YAML starter |
| [From your laptop to a shared hub](from-plugin-to-confighub.md) | Stepping from plugin to local hub to org hub |
| [Agents that run for weeks](agents-that-run-for-weeks.md) | Per-agent keys, exact-revision approval, instant revocation |
| [Signed records](signed-records.md) | Verifying tamper-evident agent change records |

## Reference

| Page | What it's for |
|---|---|
| [Words (Glossary)](words.md) | Every term (`hub`, `base`, `Space`, `change order`) defined once |
| [`cub mini` and plain `cub`](cub-mini-and-cub.md) | Mapping from each `cub mini` wrapper to plain `cub` |
| [What a repository deploys](inventory.md) | `/confighub:inventory` read-only GitOps map |
| [Working with the tools you already have](integrations.md) | Supported tools and current status |
| [Going back](journeys/going-back.md) | Exporting plain files and uninstalling each component |
| [For a security review (plugin)](security.md) | Plugin read/write/network scope and opt-out settings |
| [For a security review (hub)](security-hub.md) | Hub network surface, Postgres storage, redaction, teardown |
| [Self-hosting the hub in Kubernetes (Helm)](self-hosted-helm.md) | Packaged Helm chart with OIDC SSO, PVC, and `helm upgrade` |
| [Limits](limits.md) | What the plugin and local hub do not do yet |

## More tools, setups & testing

| Page | What it's for |
|---|---|
| [Codex](codex.md) | One-command setup for Codex CLI |
| [CI and sandboxes](ci-and-sandboxes.md) | Keeping agent records after disposable sandboxes exit |
| [Agents in CI](../ci/README.md) | GitHub Actions workflows for coding agents |
| [Git and GitHub](git-and-github.md) | In-repo records, `--commit-summary`, `--share-setup`, hub beside Git |
| [The pull-request review](../review/README.md) | PR comment listing every changed value and reason (no hub) |
| [Entire](entire.md) | `entire confighub why` paired with Entire checkpoints |
| [A service on a VM](vm.md) | Writing approved hub values to a VM service |
| [A Helm chart you use, with your values](your-own-chart.md) | Keeping custom values across vendor chart upgrades |
| [GitOps over OCI](gitops-over-oci.md) | Flux and Argo CD pulling approved OCI releases |
| [Software with ConfigHub inside](journeys/bundled.md) | Bundling a local hub inside distributed software |
| [Runnable examples](../examples/roadmap/README.md) | VM rollback, shared settings, hub export/import |
| [Extensions](../examples/extensions/config-snapshot/README.md) | Snapshot reader and experimental delivery plugin ([delivery](../examples/extensions/delivery/README.md)) |
| [Testing the Claude plugin and the local hub](testing.md) | Runnable checks, comparisons, and dated run records |
| [What agents did with and without the plugin](evidence.md) | Quoted real agent sessions |
| [Evaluate it yourself](../evaluate/README.md) | Run the same evaluation with your own models |

## Words

See the full glossary in [Words](words.md).

[`llms.txt`](../llms.txt) lists every page for AI agents.
