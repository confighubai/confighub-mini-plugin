# In Codex

This page is for setting up the ConfigHub plugin in Codex. Codex runs only the hooks in its own configuration, not the hooks a plugin carries. So installing the plugin in Codex records nothing until you run one setup command.

## Set it up

1. Find a copy of the plugin: the one Claude Code installed, or a clone of this repository. From that copy, run:

   ```
   plugins/confighub/bin/confighub mini codex-setup
   ```

2. In Codex, type `/hooks` and approve the plugin's hooks. You do this once.

## Read the record

The record is the plugin's list of what agents changed, and why. To read it:

```
~/.codex/confighub/bin/confighub mini changes
```

## Remove it

`codex-setup --remove` takes the hooks out again.
