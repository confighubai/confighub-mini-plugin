# Using ConfigHub in Codex CLI

Codex runs hooks configured in its own settings directory rather than plugin-bundled hooks. One setup command installs the ConfigHub binary (`~/.codex/confighub/bin/confighub`), hooks, and shared app workflow into Codex.

## Set it up

1. **Install hooks and workflow** (paste in Terminal from any folder; requires Git and Codex CLI):

   ```sh
   git clone --depth 1 --branch v0 https://github.com/confighubai/confighub-mini-plugin.git "$HOME/confighub-mini-plugin" &&
     "$HOME/confighub-mini-plugin/plugins/confighub/bin/confighub" mini codex-setup
   ```

2. **Approve hooks once in Codex CLI:** open `codex`, run `/hooks`, review and approve the ConfigHub hooks, then start a **fresh `codex` session** in your project folder.

**What to try first:**
- **Plugin only (no server):** [Remember why a setting changed in five minutes](try-the-plugin.md#try-it-in-five-minutes).
- **Local hub + live preview:** [Run a preview of an existing app](journeys/existing-app.md#run-a-preview-of-my-app) or follow [the preview and second-app steps below](#try-a-change-and-start-a-second-app).

<details>
<summary><strong>Updating or removing the Codex integration</strong></summary>

- **Update to the latest `v0` release:**
  ```sh
  git -C "$HOME/confighub-mini-plugin" fetch origin refs/tags/v0 &&
    git -C "$HOME/confighub-mini-plugin" switch --detach FETCH_HEAD &&
    "$HOME/confighub-mini-plugin/plugins/confighub/bin/confighub" mini codex-setup
  ```
  Then review any changed hooks in `/hooks` and start a fresh session.
- **Uninstall:** Run `"$HOME/confighub-mini-plugin/plugins/confighub/bin/confighub" mini codex-setup --remove`. This removes the hooks, `~/.codex/confighub` binary copy, and unmodified app workflow (any custom or edited personal skill is preserved).
</details>

---

## Try a change and start a second app

**You** choose what to share and decide separately about production. **Your agent** checks the preview, makes the greeting a shared staging setting at your request, and verifies the second app’s response.

If you just want a preview of an existing Node app, ask for a change you can keep. Say yes to the local setup offer. Codex checks the running page and gives you the address in this chat. A fresh chat in the same folder can find it again.

When you create or attach an app on macOS, ConfigHub prepares a local hub, a preview slot, and a **scoped `run-codex` launcher** for that folder. Running `run-codex` starts Codex on the app's proposal key—so the agent can update `preview` and `staging` freely while the hub refuses any attempt by the agent to self-approve `live` ([scoped Codex key details](approvals.md#codex-sessions-on-the-proposal-key)).

1. **Attach or create your first app** in an ordinary `codex` session:
   - Empty Git folder: `Build me a small web app using ConfigHub.`
   - Existing Node app: `Attach ConfigHub to this app so I can try a preview.`
2. **Open the app’s scoped session** in Terminal using the `run-codex` path printed at the end of Step 1, then ask:
   ```text
   Try a warmer greeting in preview.
   ```
   The agent starts an isolated local preview process and prints its `http://127.0.0.1:...` URL while keeping your `.env` files, `staging`, and `live` unchanged.
3. **Promote when ready:** Ask `Make that the shared greeting and put it in staging. Show me what the first app serves there.` When you want production to take it, run the printed `cub mini approve` command in your own terminal.
4. **Start a second app from the first:** Open a normal `codex` session (not the first app's scoped `run-codex` launcher) in a **new Git folder** and ask:
   ```text
   Build a second app using the first app’s ConfigHub setup. Let it inherit the greeting. Run the second app with its staging settings and show me its response.
   ```
   Check that both staging apps serve the same greeting and the second app has no greeting in its own settings file. Its production approval is separate.

See [normal app workflow behavior](agent-workflow.md) and the [client capability matrix](how-it-works.md#client-capabilities) for details on what Codex hooks record vs. refuse.

## Read the record

Inspect what Codex sessions changed and why from your Terminal inside any project folder (`codex-setup` places the CLI at `~/.codex/confighub/bin/confighub`):

```sh
~/.codex/confighub/bin/confighub mini changes
```

For `.env` files, this compares before/after values and shows the prompt behind each edit—even when the repo has no Git commits or Codex edited the file via Python.
