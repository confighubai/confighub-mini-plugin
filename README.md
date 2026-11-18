# ConfigHub for your first app

Use ConfigHub with Claude Code or Codex to keep track of **why** settings changed across sessions, test config changes in a running local preview while production stays untouched, and reuse proven setups in your next app.

- **Plugin alone (`confighub`):** Records config edits, CLI commands, and the prompts behind them on your machine. Warns the next session before it silently undoes an earlier change. **No server, no account.**
- **Local hub (`cub mini`, optional):** Runs the ConfigHub server and PostgreSQL on `127.0.0.1` (no Docker, no account). Adds isolated previews, separate `staging` and `live` copies, and scoped agent keys that cannot approve their own production changes.

👉 **Prefer a single self-contained page?** Open **[Three things to try first](https://confighub.github.io/helm-expt/ai-agents/first-look.html)** (with a Claude Code / Codex toggle and copyable steps).

## Install

Run these two commands in Terminal for **Claude Code**, then open a fresh `claude` session:

```sh
claude plugin marketplace add confighubai/confighub-mini-plugin
claude plugin install confighub@confighub
```

<details>
<summary><strong>Using the Codex CLI?</strong></summary>

With Git and Codex installed, run this in Terminal from any folder:

```sh
git clone --depth 1 --branch v0 https://github.com/confighubai/confighub-mini-plugin.git "$HOME/confighub-mini-plugin" &&
  "$HOME/confighub-mini-plugin/plugins/confighub/bin/confighub" mini codex-setup
```

Then in Codex CLI, run `/hooks`, review and approve the ConfigHub hooks, and open a fresh session in your project folder. ([Codex setup and removal](docs/codex.md#set-it-up))
</details>

*(Want the local hub CLI without a coding agent? [Install the local hub on its own](docs/install-mini.md).)*

## Try one setting in two minutes

1. Create a throwaway Git folder and start a fresh `claude` (or `codex`) session inside it:
   ```sh
   mkdir try-confighub && cd try-confighub && git init -q &&
     printf 'CACHE=off\n' > .env && git add -f .env
   ```
2. Ask: **“Turn the cache on in `.env` for next week’s sale. Don’t commit.”**
3. Start a **new** session in the same folder and ask: **“Why is the cache on?”** (or type `/confighub:why CACHE` in Claude Code). Even with no Git commit, it recovers `off → on` and the sale request. ([Full five-minute guide](docs/try-the-plugin.md#try-it-in-five-minutes))

## Choose where you are starting

| Starting point | What to ask your agent | Guide |
| --- | --- | --- |
| **Already building an app** *(plugin only)* | *“Turn the cache on in `.env` for Friday’s sale.”* Check any value later with `/confighub:why CACHE`. | [Try the plugin](docs/try-the-plugin.md#try-it-in-five-minutes) |
| **Already running an app** *(local hub + preview)* | *“Attach ConfigHub to this app so I can try a preview.”* Then ask: *“Try a warmer greeting in preview.”* Your existing files stay untouched. | [Attach an existing app](docs/journeys/existing-app.md#run-a-preview-of-my-app) |
| **Starting from scratch** *(new app + second app)* | *“Build a small greeting app using ConfigHub. Give it a configurable greeting and run it locally.”* Later, start a second app from the same setup. | [Build a new app](docs/journeys/new-app.md) · [Codex walkthrough](docs/codex.md#try-a-change-and-start-a-second-app) |

Reviewing agent pull requests on GitHub? Add the [PR config review Action](review/README.md) to comment every changed value and its recorded reason.

---

## Why durable config matters with coding agents

1. **Agents change settings faster than humans read diffs.** A tweak meant for a debug run or a Friday sale gets silently reverted by the next session because Git only keeps committed values—not *why* a value was chosen.
2. **Prompts alone don’t protect production.** Telling an agent “ask before changing prod” in `AGENTS.md` fails if the agent runs with your credentials. A hub gives the agent a scoped key: free to update `staging`, refused by the server if it tries to approve `live`.
3. **Templates rot after day one; linked setups stay live.** When you build a second service (say `cart` after `shop`) from a shared base or [starter](docs/starters.md), shared fixes (`LOG_LEVEL=warn`) flow to both apps while `shop` keeps its own `DB_POOL_SIZE` and production overrides. ([Walkthrough: Alice ships it, Bob hardens it](examples/walkthroughs/story-25-alice-bob-hardened.md) · [Why not just Git, your host, or a rules file?](docs/why-durable-config.md))

ConfigHub does not host or run your app—your cluster, VM, Vercel, or Fly.io still does. It manages the configuration, reasons, and approval gates above them. ([Product overview](https://confighub.github.io/helm-expt/ai-agents/))

## Add only what you need, step by step

| When this happens | What you use | What you get |
|---|---|---|
| You open an unfamiliar repository | `/confighub:inventory` | What the repo deploys and what deploys it, before anyone edits a file ([inventory](docs/inventory.md)) |
| A teammate reviews an agent PR | [GitHub review Action](review/README.md) | Automatic PR comment showing each changed setting and its recorded reason |
| You want safe agent experiments | `/confighub:staging` (local hub) | Isolated preview + `staging` copy your agent edits freely; `live` gated behind your approval ([new app](docs/journeys/new-app.md)) |
| An upstream chart/version updates | Local hub | Preview incoming changes while preserving your overrides and reasons ([keep your changes](examples/walkthroughs/story-02-keep-your-changes.md), [Helm charts](docs/your-own-chart.md)) |
| Your app deploys to Vercel or Fly | Local hub + delivery | Approving a production order pushes it live; unapproved changes wait ([Next.js on Vercel](docs/nextjs-on-vercel.md), [Rails on Fly](docs/rails-on-fly.md)) |
| You start a second app | `/confighub:start-from APP` or [starters](docs/starters.md) | New apps inherit proven defaults and reasons while keeping their own overrides |
| Agents run in CI or sandboxes | Ephemeral hub per run | Isolated hub per job that outputs changes for human review ([hub per agent run](examples/walkthroughs/story-03-a-hub-per-agent-run.md), [CI](docs/ci-and-sandboxes.md)) |
| Teammates or long-running agents join | Shared hub (`confighub.com` or self-hosted) | Per-agent keys, instant revocation, named human approvers, signed records ([from laptop to shared hub](docs/from-plugin-to-confighub.md), [unattended agents](docs/agents-that-run-for-weeks.md)) |
| Clusters pull via Argo CD or Flux | GitOps over OCI | Clusters pull exact approved releases ([GitOps over OCI](docs/gitops-over-oci.md), [cluster drift vs. Git](examples/walkthroughs/story-09-git-hub-and-running.md)) |

## Commands in Claude Code

```text
/confighub:changes        what agents changed, and why
/confighub:why LOG_LEVEL  every change to one setting, and what was asked each time
/confighub:inventory      what this repository deploys, and what deploys it
/confighub:permissions    what your agents may run
/confighub:checks         how closely MCP tool calls are watched
/confighub:to-hub         copy the record into a hub
/confighub:staging        a staging and a production copy for this app
/confighub:start-from APP start this app from another app in the hub
```

`cub` is ConfigHub’s CLI; `cub mini` wraps common multi-step `cub` operations into single commands that work identically on a local or shared hub ([`cub mini` and plain `cub`](docs/cub-mini-and-cub.md)).

## Find your stack & documentation

- **By runtime / host:** [Web (`.env`)](examples/walkthroughs/starter-web.md) · [Vercel](examples/walkthroughs/starter-vercel.md) · [Next.js on Vercel](docs/nextjs-on-vercel.md) · [Rails on Fly](docs/rails-on-fly.md) · [AWS Parameter Store](examples/walkthroughs/starter-parameter-store.md) · [Argo CD](examples/walkthroughs/starter-kustomize-argocd.md) · [Flux](examples/walkthroughs/starter-kustomize-flux.md) · [Temporal worker](examples/walkthroughs/starter-temporal-worker.md) · [Daytona](examples/walkthroughs/starter-daytona.md) · [Unikraft](examples/walkthroughs/starter-unikraft.md) · [Linux VM](docs/vm.md) · [Bundled inside software](docs/journeys/bundled.md)
- **Integrations:** Git/GitHub, Vault, Sigstore, SPIFFE, OpenTelemetry, [Entire](docs/entire.md), MCP servers, and [Codex](docs/codex.md) ([all integrations](docs/integrations.md))
- **Core concepts & reference:** [Walkthroughs index](examples/walkthroughs/README.md) · [How the plugin works](docs/how-it-works.md) · [Measured results](docs/evidence.md) · [Approvals](docs/approvals.md) · [Starters](docs/starters.md) · [Signed records](docs/signed-records.md) · [Going back / uninstall](docs/journeys/going-back.md) · [What we do not claim (limits)](docs/limits.md) · [Full docs index](docs/README.md) · [Instructions for AI agents](AGENTS.md)

## Open, and yours to extend

- **MIT-licensed plugin** ([LICENSE](LICENSE); third-party notices in [`plugins/confighub/THIRD_PARTY_LICENSES.txt`](plugins/confighub/THIRD_PARTY_LICENSES.txt)). Note: `plugins/confighub/` is generated on release—open an [issue](https://github.com/confighubai/confighub-mini-plugin/issues/new) for plugin code changes, or send PRs to `docs/` and `examples/` ([contributing](CONTRIBUTING.md)).
- **Plain-YAML starters & open SDKs:** [Write a starter](docs/write-a-starter.md), or build on [the UI](https://github.com/confighub/ui), [Go SDK](https://github.com/confighub/sdk), [JS SDK](https://github.com/confighub/js-sdk), and [ConfigHub server docs](https://docs.confighub.com).
- **Standalone local hub binary:** Free, no account required—**[download the current release](docs/install-mini.md#the-current-release)**.
