# If you use Entire

[Entire](https://entire.io) keeps each agent session with the commit it made. The plugin keeps why each configuration value is what it is. `entire confighub` asks the second from Entire's CLI, and says which of Entire's checkpoints holds each session:

```
entire plugin install https://github.com/confighubai/confighub-mini-plugin
entire confighub why replicas
```

| Command | What it answers |
|---|---|
| `entire confighub why VALUE` | Every recorded change to a value, and why, with the Entire checkpoint of each session |
| `entire confighub changes` | What an agent changed in its latest session (`--all` for every session) |
| `entire confighub review` | Each configuration value this branch changes, and why |

Entire asks you to confirm the install, since this repository is not in its plugin index. The checkpoint is found through the record kept in each commit, so turn on `CUB_MINI_RECORD_IN_REPO=1`. With both in one repository, every hook of each ran and exited cleanly, and each commit kept both tools' trailers. The plugin's review gives Entire's hooks in `.claude/settings.json` as one line, not one value each.
