# Build your app with your agent. Keep it easy to change.

Ask Claude or Codex to build an app, or start with one you already run. Try your next idea in a preview. Decide what goes live. When you build a second app, give it the setup that worked for the first.

ConfigHub remembers which settings worked, why you chose them, and which ones each app keeps for itself. Start on your laptop. There’s no platform to build first.

A **hub** is a ConfigHub server and database that stores your app’s settings, the reason for each value, and who approved each change — on your laptop (the local hub, `confighub mini`), hosted on confighub.com, or self-hosted in your own cluster.

**[Install the plugin](#install)** · [Start in my app](#try-one-setting) · [Build my first app](#build-my-first-app)

## Install

Run these two commands in Terminal for **Claude Code**, then open a fresh `claude` session in your app folder:

```sh
claude plugin marketplace add confighubai/confighub-mini-plugin
claude plugin install confighub@confighub
```

<details>
<summary><strong>Using the Codex CLI?</strong></summary>

With Git and Codex installed, run this one-liner in Terminal from any folder:

```sh
curl -sSfL https://raw.githubusercontent.com/confighubai/confighub-mini-plugin/main/install-codex.sh | bash
```

Then in Codex CLI, run `/hooks`, review and approve the ConfigHub hooks, and open a fresh session in your project folder. ([Codex setup, manual clone, and removal](docs/codex.md#set-it-up))
</details>

## Try one setting

In your app folder, ask **“What does ConfigHub remember about a setting we changed here, and why?”** If there’s a record, look for the key, the change and the request behind it. To start a record, ask for a change you already want, or try the five-minute cache example below. If your test app has `CACHE=off`, start at step 2.

1. Create a throwaway Git folder and start a fresh `claude` (or `codex`) session inside it:
   ```sh
   mkdir try-confighub && cd try-confighub && git init -q &&
     printf 'CACHE=off\n' > .env && git add -f .env
   ```
2. Paste this in the chat.

   ```text
   Set CACHE=on in .env for Saturday’s sale. Leave it uncommitted.
   ```

   Look for **ConfigHub plugin** at the end of the turn. It shows `CACHE off → on` and quotes your request.
3. Open a fresh chat in the same folder and ask **“Why is the cache on?”** It can tell you it was for Saturday’s sale, even before you commit.

[Full five-minute guide](docs/try-the-plugin.md#try-it-in-five-minutes) · [Next, run a preview of your app](#try-a-change-in-my-app)

## Try a change in my app

In a local Node web app that reads its heading from `.env`, paste this into your agent.

```text
Show me my app as it is and a local preview with the heading “Evening collection.” Give me both links and keep the preview running for tomorrow.
```

Say yes to local setup and compare the two headings. Once the hub has production history, you can also ask **“Open Friday’s production settings as a new preview.”** [Existing app guide](docs/journeys/existing-app.md#run-a-preview-of-my-app)

## Build my first app

In an empty Git folder, ask for the app you want. For one you can also preview locally, try this.

```text
Build a small Node app for my neighborhood market. Give it a heading I can change in .env, run it locally and give me the link.
```

Open your page. When you want to try a different heading, ask **“Show me ‘Evening market’ in a preview I can open again tomorrow.”** Your agent can offer to keep it in a local hub. [New app guide](docs/journeys/new-app.md)

[Three things to try first](https://confighub.github.io/helm-expt/ai-agents/first-look.html) includes copyable steps for both agents and a second app that inherits the first app’s greeting.

**Web guide:** [ConfigHub for Coding Agents](https://confighub.github.io/helm-expt/ai-agents/) · [Step 1: Plugin](https://confighub.github.io/helm-expt/ai-agents/plugin.html) · [Step 2: Mini Hub](https://confighub.github.io/helm-expt/ai-agents/mini.html) · [Starters & recipes](https://confighub.github.io/helm-expt/ai-agents/starters.html) · [Agent router (`llms.txt`)](https://confighub.github.io/helm-expt/ai-agents/llms.txt) · [Kubernetes Workshop](https://confighub.github.io/helm-expt/site/index.html)

*(Want the local hub CLI without a coding agent? [Install the local hub on its own](docs/install-mini.md).)*

## Choose where you are starting

| Starting point | What to ask your agent | Guide |
| --- | --- | --- |
| **Already building an app** *(plugin only)* | *“Turn the cache on in `.env` for Friday’s sale.”* Ask a fresh session why the cache is on. | [Try the plugin](docs/try-the-plugin.md#try-it-in-five-minutes) |
| **Already running an app** *(local hub + preview)* | *“Attach ConfigHub to this app so I can try a preview.”* Then ask: *“Try a warmer greeting in preview.”* Your existing files stay untouched. | [Attach an existing app](docs/journeys/existing-app.md#run-a-preview-of-my-app) |
| **Starting from scratch** *(new app + second app)* | *“Build a small greeting app using ConfigHub. Give it a configurable greeting and run it locally.”* Later, start a second app from the same setup. | [Build a new app](docs/journeys/new-app.md) · [Codex walkthrough](docs/codex.md#try-a-change-and-start-a-second-app) |

Reviewing agent pull requests on GitHub? Add the [PR config review Action](review/README.md) to comment every changed value and its recorded reason.

---

## Why durable config matters with coding agents

1. **A fresh session can explain yesterday’s change.** If you turned on caching for a sale, your next agent can find that request alongside the edit.
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
| Your app deploys to Vercel, Fly, Heroku or Unikraft Cloud | `/confighub:staging` in the app's folder, which starts from the settings the host holds (on Unikraft, `--unikraft SERVICE`) | Approving a production change puts it live; unapproved changes wait ([Next.js on Vercel](docs/nextjs-on-vercel.md), [Rails on Fly](docs/rails-on-fly.md), [Heroku](docs/heroku.md), [Unikraft](examples/walkthroughs/starter-unikraft.md)) |
| You run the app yourself | `/confighub:staging`, then `cub mini preview --staging` | Your app runs the way it already does, with staging's settings; your files are not changed ([an app you already have](docs/journeys/existing-app.md)) |
| You start a second app | `/confighub:start-from APP` or [starters](docs/starters.md) | New apps inherit proven defaults and reasons while keeping their own overrides |
| Your agent works in a Daytona sandbox | `/confighub:staging`, then `cub mini preview --staging --daytona SANDBOX` | Your app runs in the sandbox with staging's settings, with no credential or ConfigHub key there ([Daytona](examples/walkthroughs/starter-daytona.md)) |
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

- **By runtime / host:** [Web (`.env`)](examples/walkthroughs/starter-web.md) · [Vercel](examples/walkthroughs/starter-vercel.md) · [Next.js on Vercel](docs/nextjs-on-vercel.md) · [Heroku](docs/heroku.md) · [Rails on Fly](docs/rails-on-fly.md) · [AWS Parameter Store](examples/walkthroughs/starter-parameter-store.md) · [Argo CD](examples/walkthroughs/starter-kustomize-argocd.md) · [Flux](examples/walkthroughs/starter-kustomize-flux.md) · [Temporal worker](examples/walkthroughs/starter-temporal-worker.md) · [Daytona](examples/walkthroughs/starter-daytona.md) · [Unikraft](examples/walkthroughs/starter-unikraft.md) · [Linux VM](docs/vm.md) · [Bundled inside software](docs/journeys/bundled.md)
- **Integrations:** Git/GitHub, Vault, Sigstore, SPIFFE, OpenTelemetry, [Entire](docs/entire.md), MCP servers, and [Codex](docs/codex.md) ([all integrations](docs/integrations.md))
- **Core concepts & reference:** [Walkthroughs index](examples/walkthroughs/README.md) · [How the plugin works](docs/how-it-works.md) · [Measured results](docs/evidence.md) · [Approvals](docs/approvals.md) · [Starters](docs/starters.md) · [Signed records](docs/signed-records.md) · [Going back / uninstall](docs/journeys/going-back.md) · [What we do not claim (limits)](docs/limits.md) · [Full docs index](docs/README.md) · [Instructions for AI agents](AGENTS.md)

## Open, and yours to extend

- **MIT-licensed plugin** ([LICENSE](LICENSE); third-party notices in [`plugins/confighub/THIRD_PARTY_LICENSES.txt`](plugins/confighub/THIRD_PARTY_LICENSES.txt)). Note: `plugins/confighub/` is generated on release—open an [issue](https://github.com/confighubai/confighub-mini-plugin/issues/new) for plugin code changes, or send PRs to `docs/` and `examples/` ([contributing](CONTRIBUTING.md)).
- **Plain-YAML starters & open SDKs:** [Write a starter](docs/write-a-starter.md), or build on [the UI](https://github.com/confighub/ui), [Go SDK](https://github.com/confighub/sdk), [JS SDK](https://github.com/confighub/js-sdk), and [ConfigHub server docs](https://docs.confighub.com).
- **Standalone local hub binary:** Free, no account required—**[download the current release](docs/install-mini.md#the-current-release)**.
