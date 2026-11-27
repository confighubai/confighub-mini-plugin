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
<summary><strong>Using Codex CLI or standalone local hub?</strong></summary>

- **Codex CLI:** run `curl -sSfL https://raw.githubusercontent.com/confighubai/confighub-mini-plugin/main/install-codex.sh | bash`, then `/hooks` in Codex to approve ConfigHub hooks ([Codex setup](docs/codex.md#set-it-up)).
- **Standalone local hub (no coding agent):** [install `confighub mini` on its own](docs/install-mini.md).
</details>

## Try it

### Try one setting

1. In a throwaway Git folder, start a fresh `claude` (or `codex`) session:
   ```sh
   mkdir try-confighub && cd try-confighub && git init -q &&
     printf 'CACHE=off\n' > .env && git add -f .env
   ```
2. Ask: `Set CACHE=on in .env for Saturday’s sale. Leave it uncommitted.`
   Look for **ConfigHub plugin** at the end of the turn (`CACHE off → on`, quoting your request).
3. Open a fresh chat in the same folder and ask: `Why is the cache on?`
   It recovers `"for Saturday’s sale"` before you commit. ([Full five-minute guide](docs/try-the-plugin.md#try-it-in-five-minutes))

### Try a change in my app (local hub + preview)

In a Node app reading its heading from `.env`, ask your agent:

```text
Show me my app as it is and a local preview with the heading “Evening collection.” Give me both links and keep the preview running for tomorrow.
```

First local setup downloads the local hub once ([package size](docs/install-mini.md#the-current-release)) and runs two `127.0.0.1` processes (ConfigHub + PostgreSQL, no Docker); remove anytime with `cub mini uninstall --delete-data`. [Existing app guide](docs/journeys/existing-app.md#run-a-preview-of-my-app)

### Build my first app

In an empty Git folder, ask:

```text
Build a small Node app for my neighborhood market. Give it a heading I can change in .env, run it locally and give me the link.
```

Then ask for a preview heading or start a second app from the first. [New app guide](docs/journeys/new-app.md) · [Three things to try first](https://confighub.github.io/helm-expt/ai-agents/first-look.html)

## Add only what you need

| Moment | What you use | Guide |
|---|---|---|
| Inspect an unfamiliar repo (read-only) | `/confighub:inventory` | [Inventory](docs/inventory.md) |
| Review agent PRs on GitHub | [PR review Action](review/README.md) | [Git & GitHub](docs/git-and-github.md) |
| Staging + gated production (local hub) | `/confighub:staging` | [Vercel](docs/nextjs-on-vercel.md) · [Fly](docs/rails-on-fly.md) · [Heroku](docs/heroku.md) · [Unikraft](examples/walkthroughs/starter-unikraft.md) |
| Team, CI, or self-hosted SSO audit | Shared hub (`confighub.com` or Helm) | [Self-hosted Helm](docs/self-hosted-helm.md) · [PR audit hub](examples/walkthroughs/tool-record-pr-hub.md) |

See all 11 steps in [Add only what you need, step by step](docs/add-as-you-grow.md).

<details>
<summary><strong>Why durable config matters with coding agents</strong></summary>

1. **A fresh session can explain yesterday’s change.** If you turned on caching for a sale, your next agent finds that request alongside the edit.
2. **Prompts alone don’t protect production.** A hub gives the agent a scoped key: free to update `staging`, refused by the server if it tries to approve `live`.
3. **Templates rot after day one; linked setups stay live.** Shared fixes flow from a base or [starter](docs/starters.md) to every linked app while each keeps its own overrides ([Alice ships it, Bob hardens it](examples/walkthroughs/story-25-alice-bob-hardened.md) · [Why not just Git?](docs/why-durable-config.md)).

ConfigHub does not host or run your app—your cluster, VM, Vercel, or Fly.io still does. ([Product overview](https://confighub.github.io/helm-expt/ai-agents/))
</details>

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

`cub` is ConfigHub’s CLI; `cub mini` wraps common multi-step `cub` operations into single commands for local or shared hubs ([`cub mini` and plain `cub`](docs/cub-mini-and-cub.md)).

## Documentation & stacks

- **Browse:** [Docs index](docs/README.md) · [Walkthroughs](examples/walkthroughs/README.md) · [Security (plugin)](docs/security.md) · [Security (hub)](docs/security-hub.md) · [Limits](docs/limits.md) · [Instructions for AI agents](AGENTS.md)
- **Web guide:** [ConfigHub for Coding Agents](https://confighub.github.io/helm-expt/ai-agents/) · [Kubernetes Workshop](https://confighub.github.io/helm-expt/site/index.html)

<details>
<summary><strong>All supported runtimes, hosts &amp; integrations</strong></summary>

- **Hosts & runtimes:** [Web (`.env`)](examples/walkthroughs/starter-web.md) · [Vercel](examples/walkthroughs/starter-vercel.md) · [Next.js on Vercel](docs/nextjs-on-vercel.md) · [Heroku](docs/heroku.md) · [Rails on Fly](docs/rails-on-fly.md) · [AWS Parameter Store](examples/walkthroughs/starter-parameter-store.md) · [Argo CD](examples/walkthroughs/starter-kustomize-argocd.md) · [Flux](examples/walkthroughs/starter-kustomize-flux.md) · [Temporal worker](examples/walkthroughs/starter-temporal-worker.md) · [Daytona](examples/walkthroughs/starter-daytona.md) · [Unikraft](examples/walkthroughs/starter-unikraft.md) · [Linux VM](docs/vm.md) · [Bundled inside software](docs/journeys/bundled.md)
- **Integrations:** Git/GitHub, Vault, Sigstore, SPIFFE, OpenTelemetry, [Entire](docs/entire.md), MCP servers, [Codex](docs/codex.md) ([all integrations](docs/integrations.md))
</details>

## Open, and yours to extend

- **MIT-licensed plugin** ([LICENSE](LICENSE); third-party notices in [`plugins/confighub/THIRD_PARTY_LICENSES.txt`](plugins/confighub/THIRD_PARTY_LICENSES.txt); [contributing](CONTRIBUTING.md)).
- **Plain-YAML starters & open SDKs:** [Write a starter](docs/write-a-starter.md) · [UI](https://github.com/confighub/ui) · [Go SDK](https://github.com/confighub/sdk) · [JS SDK](https://github.com/confighub/js-sdk) · [Server docs](https://docs.confighub.com).
- **Standalone local hub binary:** Free, no account required — **[download the current release](docs/install-mini.md#the-current-release)**.
