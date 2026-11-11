# In Codex

This page is for setting up the ConfigHub plugin in Codex. Codex runs only the hooks in its own configuration, not the hooks a plugin carries. So installing the plugin in Codex records nothing until you run one setup command. That command also installs the shared app workflow for ordinary development requests.

## Set it up

1. Find a copy of the plugin: the one Claude Code installed, or a clone of this repository. From that copy, run:

   ```
   plugins/confighub/bin/confighub mini codex-setup
   ```

2. In Codex, type `/hooks` and approve the plugin's hooks. Repeat setup after an update and review the changed definitions in a fresh session.

Codex can work on a scoped proposal key with a separate launcher ([setup and limits](approvals.md#codex-sessions-on-the-proposal-key)).

Use normal app requests after setup; see [how the agent chooses a useful step and attributes ConfigHub actions](agent-workflow.md).

For what is recorded, refused or left to a person, see the [client capability matrix](how-it-works.md#client-capabilities).

## Read the record

The record is the plugin's list of what agents changed, and why. To read it:

```
~/.codex/confighub/bin/confighub mini changes
```

## Remove it

`codex-setup --remove` takes out the hooks, program copy and installed app workflow. Setup refuses to overwrite a personal skill of the same name or an edited installed workflow; it reports the conflict before changing hooks. Removal keeps a personal or edited workflow while taking out the hooks and program copy.
