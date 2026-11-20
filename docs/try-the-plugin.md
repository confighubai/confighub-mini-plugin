# Try the plugin on its own

Give your next session the reason for an uncommitted edit. The plugin records the change on your machine. You need Git and Claude Code or Codex. No server or ConfigHub account is required.

## Try it in five minutes

Use your own Git app or the sample below. **You** ask for an edit, then open a fresh chat. **Your agent** edits the setting and later reads the record to explain why.

1. **Install the plugin** (skip if already installed):

   **Claude Code:**
   ```sh
   claude plugin marketplace add confighubai/confighub-mini-plugin
   claude plugin install confighub@confighub
   ```
   *(Using **Codex CLI**? Follow the [one-command Codex setup](codex.md#set-it-up) and approve `/hooks` instead.)*

   If Claude Code says the marketplace’s “network source differs,” run `claude plugin marketplace list`. If `confighub` points to the older skills repository, follow its [one-time migration](https://github.com/confighub/confighub-skills#moving-an-older-installation), then retry the install.

2. **Open a fresh session in your app folder** so the plugin is active. Pick a non-secret setting you actually want to change and give the reason in your request. To try the example without changing your app, create this sample folder and start a fresh session there:

   ```sh
   mkdir try-confighub && cd try-confighub && git init -q &&
     printf 'CACHE=off\n' > .env && git add -f .env
   ```

3. **Ask for the edit.** Here’s the request for the sample folder. In your own app, use the setting and reason you picked.

   ```text
   Turn the cache on in .env for next week's sale. Don't commit.
   ```

4. **Open a fresh session** in the same folder and ask:

   ```text
   Why is the cache on?
   ```

### What you should see

Even though nobody made a Git commit, the fresh session recovers both the previous value (`off → on`) and your reason about next week's sale.

You can also inspect the record directly:
- **In Claude Code:** type `/confighub:why CACHE`
- **In Terminal (Codex):** run `~/.codex/confighub/bin/confighub mini changes`

```text
CACHE: on in .env
  off → on
  asked: "Turn the cache on in .env for next week's sale. Don't commit."
```

If you used the sample, you can delete `try-confighub` when you're done.

**Want to see a change running?** In an existing Node app with a heading read from `.env`, ask “Try the heading ‘Evening collection’ in a preview I can keep until tomorrow. Leave my usual app alone.” Your agent offers to attach the app locally. Say yes. On first use it downloads mini, then checks the page and gives you its address in this chat. When you come back, ask “Where’s the preview, and what does it say?” [Run a preview of my app](journeys/existing-app.md#run-a-preview-of-my-app).

See [measured session timings](evidence.md#two-first-actions-in-fresh-sessions) or the [full plugin walkthrough](../examples/walkthroughs/tool-plugin.md).

---

## Why Git alone misses this

Suppose Session 1 raises `replicas` from `2` to `4` for Friday's flash sale without committing, and Session 2 is asked to cut costs and sets `replicas: 1`. Comparing the original file with the final one shows `2 → 1`. The intermediate value and the sale request are missing from that diff.

On a supported Claude Code edit, a later session can see this warning before changing the value:

> **This change undoes an earlier one.** The file already had an uncommitted change that raised replicas from 2 to 4. A session earlier today made it, with this request: *"Friday's flash sale will quadruple traffic to the api: give it 4 replicas."*

Codex can recover the same history. Its hooks record `apply_patch` edits **after** they run. The [capability table](how-it-works.md#client-capabilities) identifies which operations get a warning or can be refused. [See the measured runs](evidence.md).

## What it records (and never records)

- **Recorded:** Changed keys in `.env`, Kubernetes manifests, Helm values, Kustomize, Compose, GitHub Actions, and Terraform files; state-changing CLI commands (`kubectl`, `helm`, `terraform`, `vercel`, `fly`, `aws ssm`, `cub`) and MCP tool calls; the user request and the agent's stated rationale. Each entry is cryptographically signed ([signed records](signed-records.md)).
- **Never recorded:** Command outputs, full file copies, or anything resembling a password, secret, key, or connection-string credential. Nothing leaves your machine unless you opt in ([all details](how-it-works.md#what-it-records-and-what-it-does-not) · [what we do not claim](limits.md)).

<details>
<summary><strong>Emergency stop &amp; MCP tool guardrails</strong></summary>

- **Pause all Claude Code sessions at their next tool call:**
  ```sh
  touch ~/.confighub/halt   # remove the file to resume
  ```
  See [Sam's bad afternoon](../examples/walkthroughs/story-19-recovery.md) for full incident recovery.
- **Control MCP write calls:** Use `/confighub:checks` (`log`, `warn`, `repeats`, or `ask`) in Claude Code to hold back duplicate side effects (like double refunds) or require human confirmation ([how MCP checks work](how-it-works.md#how-closely-mcp-calls-are-watched)).
</details>

<details>
<summary><strong>Share plugin setup with your team via Git</strong></summary>

Add these keys to `.claude/settings.json` in your repository so teammates opening the project in Claude Code get the marketplace automatically:

```json
{
  "extraKnownMarketplaces": {
    "confighub": { "source": { "source": "github", "repo": "confighubai/confighub-mini-plugin" } }
  },
  "enabledPlugins": { "confighub@confighub": true }
}
```

If `/plugin` reports the plugin is enabled but not yet installed, run `claude plugin install confighub@confighub --scope project` once.
</details>

## When you want more than a local record

A record informs you and your agents, but an agent running with your credentials can still touch production. Add a **hub** when you want hard environment boundaries:

| Goal | Next step |
|---|---|
| Comment changed config values + reasons on every GitHub PR | Add the one-step [PR review Action](../review/README.md) |
| Review a proposed production change | [See what you are approving](approvals.md) |
| Keep your overrides cleanly across upstream Helm chart upgrades | Install the local hub ([install](install-mini.md)) and see [your own Helm chart](your-own-chart.md) |
| Run agents in CI or sandboxes with disposable hubs | See [agents in CI](../ci/README.md) and [CI & sandboxes](ci-and-sandboxes.md) |
| Share records, keys, and approvals across teammates | Connect to [a shared hub](git-and-github.md) or see [unattended agents](agents-that-run-for-weeks.md) |
