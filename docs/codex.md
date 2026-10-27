# In Codex

Codex runs only the hooks in its own configuration, not those a plugin carries, so installing the plugin in Codex records nothing. From a copy of the plugin, the one Claude Code installed or a clone of this repository, run:

```
plugins/confighub/bin/confighub mini codex-setup
```

Then type `/hooks` in Codex to approve its hooks, once. Read the record with `~/.codex/confighub/bin/confighub mini changes`. `codex-setup --remove` takes it out again.
