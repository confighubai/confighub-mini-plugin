# In Codex

This page is for setting up the ConfigHub plugin in Codex. Codex runs only the hooks in its own configuration, not the hooks a plugin carries. So installing the plugin in Codex records nothing until you run one setup command. That command also installs the shared app workflow for ordinary development requests.

## Set it up

1. With Git and the Codex CLI installed, paste this in Terminal. It downloads the released plugin into `~/confighub-mini-plugin` and installs its hooks and app workflow into Codex. You can run it from any folder.

   ```sh
   git clone --depth 1 --branch v0 https://github.com/confighubai/confighub-mini-plugin.git "$HOME/confighub-mini-plugin" &&
     "$HOME/confighub-mini-plugin/plugins/confighub/bin/confighub" mini codex-setup
   ```

2. In the Codex CLI, type `/hooks`, review and approve the ConfigHub hooks, then start a fresh session in your app’s folder.

The `v0` tag tracks the published plugin. To update an existing installation, run:

```sh
git -C "$HOME/confighub-mini-plugin" fetch origin refs/tags/v0 &&
  git -C "$HOME/confighub-mini-plugin" switch --detach FETCH_HEAD &&
  "$HOME/confighub-mini-plugin/plugins/confighub/bin/confighub" mini codex-setup
```

Review changed hooks in `/hooks` and start a fresh session.

To try it, [change one setting and recover its reason](try-the-plugin.md#try-it-in-five-minutes) or [run a preview of your app](journeys/existing-app.md#run-a-preview-of-my-app).

Codex can work on a scoped proposal key with a separate launcher ([setup and limits](approvals.md#codex-sessions-on-the-proposal-key)).

On a Mac with no hub configuration, ask “Build me a small web app using ConfigHub” or “Attach ConfigHub to this app so I can try a preview.” The approved hook starts the local hub. The five-minute cache example uses the plugin alone.

Use normal app requests after setup; see [how the agent chooses a useful step and attributes ConfigHub actions](agent-workflow.md).

For what is recorded, refused or left to a person, see the [client capability matrix](how-it-works.md#client-capabilities).

## Try a change and start a second app

On macOS, with plugin 0.99.0 and mini.17, adopting a new local app with an env file also prepares a preview and a scoped launcher. When the agent attaches the app, ask it for the full path to the app’s `run-codex` launcher. Run that command in Terminal to open the next session with the app’s permissions.

1. Ask, “Try a warmer greeting in preview and show me what it serves over HTTP.” The agent pulls the preview settings and runs a separate copy of the app. Staging and production stay as they were. Ask for the actual response if you only see what the hub stored.
2. If you like it, ask, “Make that the shared greeting and put it in staging.” Use the exact approval command the agent gives you when you are ready for production to take it. Delivery to a running app needs a connected deployment path.
3. For a second app, open an ordinary Codex session in a new Git folder. Ask, “Build a second app using the first app’s setup.” The first app’s limited session cannot attach another app. The second app uses the same hub, starts with the shared greeting and gets its own first production review.

## Read the record

The record is the plugin's list of what agents changed, and why. Run this in the project folder:

```
~/.codex/confighub/bin/confighub mini changes
```

For an env file, the record compares the settings before and after the edit. You can look up `CACHE` even if Codex used Python to rewrite the file and the repository has no commits.

## Remove it

`codex-setup --remove` takes out the hooks, program copy and installed app workflow. Setup refuses to overwrite a personal skill of the same name or an edited installed workflow; it reports the conflict before changing hooks. Removal keeps a personal or edited workflow while taking out the hooks and program copy.
