# If you use Entire

This page is for teams that use both [Entire](https://entire.io) and the ConfigHub plugin. Entire keeps each agent session with the commit it made. The plugin keeps why each configuration value is what it is. `entire confighub` lets you ask the plugin from Entire's CLI, and tells you which of Entire's checkpoints holds each session.

## Set it up

1. Install the plugin into Entire:

   ```
   entire plugin install https://github.com/confighubai/confighub-mini-plugin
   ```

   Entire asks you to confirm the install, because this repository is not in its plugin index.

2. Turn on `CUB_MINI_RECORD_IN_REPO=1` in the ConfigHub plugin's [settings](how-it-works.md#settings). This keeps the plugin's record in each commit, and the checkpoint is found through that record.

3. Ask about a value:

   ```
   entire confighub why replicas
   ```

## The commands

| Command | What it answers |
|---|---|
| `entire confighub why VALUE` | Every recorded change to a value, and why, with the Entire checkpoint of each session |
| `entire confighub changes` | What an agent changed in its latest session (`--all` for every session) |
| `entire confighub review` | Each configuration value this branch changes, and why |

## Using both in one repository

In a test with both in one repository, every hook of each tool ran and exited cleanly. Each commit kept both tools' trailers.

The plugin's [pull-request review](../review/README.md) shows Entire's hooks in `.claude/settings.json` as one line, not one value each.
