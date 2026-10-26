# `cub mini` and plain `cub`

confighub mini is ConfigHub, smaller: the same server and the same `cub`. The `cub mini` commands are a thin layer on top. Each is one of `cub`'s own commands with the rest of the request filled in, except where the table says `cub` has nothing yet. So everything shown with `cub mini` can be done with plain `cub`, and works the same on the company's ConfigHub.

| `cub mini` | Plain `cub` | What `cub mini` fills in |
|---|---|---|
| `cub mini install` | `cub server install` | The server and its PostgreSQL run as processes on this machine, with no Docker and no Kubernetes |
| `cub mini upload FOLDER --variant V` | `cub component create`, `cub space create`, `cub unit create`, `cub variant create` (or `cub variant upload`) | The Component is named after the folder, the base and the copy are made, and the copy is aimed at the hub's cluster when there is one |
| `cub mini set COMPONENT FUNCTION ARG --variant V` | `cub function set --space COMPONENT-V --unit UNIT FUNCTION ARG` | The Space and Unit are found, the value is marked as kept so a later version does not replace it, and the reason is recorded beside it |
| `cub mini promote COMPONENT-V` | `cub variant promote COMPONENT-V`, then `cub release publish COMPONENT-V` | The preview shows each value taken and kept, and the result is released to the cluster |
| `cub mini require-approval COMPONENT --variant V --agent NAME` | `cub changeworkflow create`, `cub component update`, `cub serviceaccount create` and `key add`, and permissions on each Space | The whole gate in one step, the agent's own `cub` configuration, and its Claude Code settings ([approvals](approvals.md), where the same steps are shown with plain `cub`) |
| `cub mini copy --to-dir`, `--from-git`, `--to-file`, `--from-file` | Nothing yet | The work written out as plain files with a `CHANGES.md` that says why each value is set, and back in from Git with each commit's reason; and moved between hubs |
| `cub mini connect`, `offer`, `offers` | Nothing yet | The company's ConfigHub made the parent of a confighub mini's work, and changes offered up to it |

Where `cub` has nothing yet, the command is the working example of what `cub` could gain.
