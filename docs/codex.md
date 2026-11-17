# In Codex

This page is for setting up the ConfigHub plugin in Codex. Codex runs only the hooks in its own configuration, not the hooks a plugin carries. So installing the plugin in Codex records nothing until you run one setup command. That command also installs the shared app workflow for ordinary development requests.

## Set it up

1. Find a copy of the plugin: the one Claude Code installed, or a clone of this repository. From that copy, run:

   ```
   plugins/confighub/bin/confighub mini codex-setup
   ```

2. In Codex, type `/hooks` and approve the plugin's hooks. Repeat setup after an update and review the changed definitions in a fresh session.

Codex can work on a scoped proposal key with a separate launcher ([setup and limits](approvals.md#codex-sessions-on-the-proposal-key)).

On a Mac with no hub configuration, ask Codex to “Build me a small web app using ConfigHub.” The approved hook starts the local hub and tells you when it is ready. Other requests keep their usual behavior. If the hook cannot start the hub, it gives you the command to run in your own terminal.

Use normal app requests after setup; see [how the agent chooses a useful step and attributes ConfigHub actions](agent-workflow.md).

For what is recorded, refused or left to a person, see the [client capability matrix](how-it-works.md#client-capabilities).

## Try a change and start a second app

On macOS, with plugin 0.99.0 and mini.17, adopting a new local app with an env file also prepares a preview and a scoped launcher. Use the launcher the setup prints to open a fresh session for the app.

1. Ask, “Try a warmer greeting in preview and show me what it serves over HTTP.” The agent pulls the preview settings and runs a separate copy of the app. Staging and production stay as they were. Ask for the actual response if you only see what the hub stored.
2. If you like it, ask, “Make that the shared greeting and put it in staging.” Use the exact approval command the agent gives you when you are ready for production to take it. Delivery to a running app needs a connected deployment path.
3. In a new folder, ask, “Build a second app using the first app’s setup.” Codex can find the local hub you already use. The second app starts with the shared greeting and gets its own first production review.

## Read the record

The record is the plugin's list of what agents changed, and why. To read it:

```
~/.codex/confighub/bin/confighub mini changes
```

## Remove it

`codex-setup --remove` takes out the hooks, program copy and installed app workflow. Setup refuses to overwrite a personal skill of the same name or an edited installed workflow; it reports the conflict before changing hooks. Removal keeps a personal or edited workflow while taking out the hooks and program copy.
