# `cub mini` and plain `cub`

What you do with confighub mini on your laptop works the same on your company's ConfigHub, because it is the same ConfigHub server and the same `cub`, ConfigHub's command-line tool. Each `cub mini` command runs `cub`'s own commands and fills in the rest of the request for you. So, except where the table says "Nothing yet", you can do everything shown with `cub mini` in plain `cub`, on any ConfigHub. The table lists which `cub` commands each `cub mini` command stands for.

| `cub mini` | Plain `cub` | What `cub mini` fills in |
|---|---|---|
| `cub mini install` | `cub server install` | The server and its PostgreSQL run as processes on this machine, with no Docker and no Kubernetes |
| `cub mini upload FOLDER --variant V` | `cub component create`, `cub space create`, `cub unit create`, `cub variant create` (or `cub variant upload`) | The Component is named after the folder. The base and the copy are made. The copy is aimed at the hub's cluster, when there is one |
| `cub mini set COMPONENT FUNCTION ARG --variant V` | `cub function set --space COMPONENT-V --unit UNIT FUNCTION ARG` | The Space and Unit are found. The value is marked as kept, so a later version does not replace it. The reason is recorded beside it |
| `cub mini promote COMPONENT-V` | `cub variant promote COMPONENT-V`, then `cub release publish COMPONENT-V` | The preview shows each value taken and each value kept. The result is released to the cluster |
| `cub mini require-approval COMPONENT --variant V --agent NAME` | `cub changeworkflow create`, `cub component update`, `cub serviceaccount create` and `key add`, and permissions on each Space | The whole approval gate in one step, plus the agent's own `cub` configuration and its Claude Code settings. [Approvals](approvals.md) shows the same steps with plain `cub` |
| `cub mini copy --to-dir`, `--from-git`, `--to-file`, `--from-file` | Nothing yet | Writes the work out as plain files, with a `CHANGES.md` that says why each value is set. Reads it back in from Git, with each commit's reason. Moves it between hubs |
| `cub mini connect`, `offer`, `offers` | Nothing yet | Makes the company's ConfigHub the parent of a confighub mini's work, and offers changes up to it |

Where the table says "Nothing yet", plain `cub` has no equivalent, and only `cub mini` does it for now.

## Words used in the table

- A *hub* is one running ConfigHub server. *confighub mini* runs a hub on one machine.
- A *Space* holds configuration, as *Units*: one Unit per file or resource.
- A *Component* is one piece of software. Its *base* is the version you change. A *variant*, such as `live`, is a copy made from the base for one place it runs. Its Space is named `COMPONENT-V`, such as `api-live`.
- To *promote* a variant is to bring the base's changes into it. A *release* is a published version of a variant that a cluster pulls.
- A *ChangeWorkflow* says what a change needs before it reaches a variant, such as a person's approval. A *service account* is the identity an agent uses, with a key of its own.
