# The ConfigHub plugin for Claude Code and Codex

When an agent changes your configuration, the plugin keeps what it changed and why. When the next agent opens the same file, or is about to deploy over the change, it is told first. You change no prompts and add no instructions.

```
claude plugin marketplace add confighubai/confighub-mini-plugin
claude plugin install confighub@confighub
```

Then, in any session:

```
/confighub:changes              what the agent changed, and why
/confighub:why replicas         every recorded change to one value, and why
/confighub:install-mini         ConfigHub on this machine, in about 25 seconds, when you want more than a record
```

No account, no server. MIT.

## Git shows 2 → 1. Your agent set 4 in between.

One session is asked to give the api 4 replicas for Friday's sale. A later one is asked to trim it to 1 to save money. Nobody commits in between, so Git sees only this:

```
$ git diff k8s/api.yaml
-  replicas: 2
+  replicas: 1
```

With the plugin, the second agent was told about the 4, and why, before it acted. It said so:

> **This change undoes an earlier one.** The file already had an uncommitted change that raised replicas from 2 to 4. A session earlier today made it, with this request: *"Friday's flash sale will quadruple traffic to the api: give it 4 replicas."* So 1 replica is below even the committed value of 2, and it would leave the api with a single pod on Friday.

Later agents asked to deploy, in other worktrees and in CI, undid an earlier agent's change without a word in 144 of 190 runs without the plugin, and in none of 190 with it ([the evidence](docs/evidence.md)).

## Four ways in, shortest first

| You want | Do this | It takes |
|---|---|---|
| **To know what your agent changed, and have the next agent know** | Install the plugin, above | One minute; nothing else changes |
| **Every pull request to say what it changes in configuration, and why** | Add the review Action: `uses: confighubai/confighub-mini-plugin/review@v0` ([how](review/README.md)) | One YAML step; nobody installs anything |
| **To keep your own values through a vendor's next version, and approve what agents propose** | `/confighub:install-mini`, then [a first run](docs/try-confighub-mini.md) | 25 seconds to a hub on your laptop; 15 minutes for the first run |
| **Agents your team trusts to run unattended** | Your company's ConfigHub: an agent with a key of its own, your approval before production, a record you can check, and a stop that works at once ([how](docs/agents-that-run-for-weeks.md)) | A ConfigHub organization; [the steps](docs/approvals.md) are plain `cub` |

The plugin is the record. confighub mini is ConfigHub made small, for one machine. The company's [ConfigHub](https://docs.confighub.com) is where the work ends up. Each step uses ordinary ConfigHub commands, so nothing is a separate product, and the work moves up with you: `cub mini copy --from-record` puts the record into a hub, and `cub mini connect` makes the company's hub its parent ([`cub mini` as plain `cub`](docs/cub-mini-and-cub.md)).

## Try it in five minutes

You need Claude Code and Git. In an empty folder, make a repository with one settings file:

```
git init try-confighub && cd try-confighub && printf 'CACHE=off\nLOG_LEVEL=warn\n' > .env && git add . && git commit -qm start
```

Then three Claude Code sessions in `try-confighub`, one after another. In each, ask one thing, let it make the edit, and close it with `/exit`:

1. `Turn the cache on in .env for next week's sale. Don't commit.`
2. `We're chasing a memory leak: turn the cache off and set debug logging. Don't commit.`
3. `Is the cache set up right for the sale?`

Git shows only `LOG_LEVEL warn → debug`. The second session saw what it was undoing, and said so. The third, in a real run:

```
No. `.env` currently has `CACHE=off`.

How it got that way: The plugin's change log shows two earlier agent sessions this morning (22 Oct, 11:34) that worked against each other:
1. Session `8664e97d` turned the cache on for next week's sale.
2. Session `411d4c5d` then turned it back off to chase a memory leak. It also changed `LOG_LEVEL` from `warn` to `debug`.
...
I haven't changed anything, because the two goals conflict. ...
```

Then `/confighub:why CACHE`:

```
CACHE, in .env: off in the file now
  22 October 11:34  off → on               session 8664e97d
      asked: Turn the cache on in .env for next week's sale. Don't commit.
  22 October 11:34  on → off               session 411d4c5d
      asked: We're chasing a memory leak: turn the cache off and set debug logging. Don't commit.
```

When you are done, remove the folder. Its record, in `~/.confighub/agent-changes`, is removed after 30 days unused.

## What it does

- **Records** each value an agent changes in Kubernetes files, Helm values, Kustomize, Compose, GitHub Actions workflows, settings files, Terraform variables and agent configuration, and each `kubectl`, `helm`, `argocd`, `flux`, `terraform`, `tofu`, `cub` and `nvkectl` command that changes something, with the request that caused it and the reason given.
- **Tells the next agent**, once, when it opens a file or looks at a resource an earlier session changed.
- **Stops a deploy that would undo another agent's change on a cluster**, once, before it runs, with the reason. Run again, it goes through.
- **Never keeps** command output, file copies, or anything that looks like a credential.
- **Signs the record** at the end of each turn, so anyone can check nobody changed it since, with `--verify`, in the review, or with Sigstore's `cosign` ([signed records](docs/signed-records.md)).
- **Costs** about 15 ms a tool call. Nothing leaves your machine unless you turn a setting on.

The details, the settings, and keeping the record out of the agent's reach: [how it works](docs/how-it-works.md). What it does not do: [what we do not claim](docs/limits.md).

## Documentation

All of it, by what you are doing: [docs/](docs/README.md).

| Using the plugin | Adding a hub | Teams and production |
|---|---|---|
| [How it works](docs/how-it-works.md) | [Install confighub mini](docs/install-mini.md) | [Approvals](docs/approvals.md) |
| [The evidence](docs/evidence.md) | [A first run](docs/try-confighub-mini.md) | [Agents that run for weeks](docs/agents-that-run-for-weeks.md) |
| [The pull-request review](review/README.md) | [Your own Helm chart](docs/your-own-chart.md) | [Signed records](docs/signed-records.md) |
| [In CI or a sandbox](docs/ci-and-sandboxes.md) | [Flux and Argo CD deploying from it](docs/gitops-over-oci.md) | [Agents in CI](ci/README.md) |
| [In Codex](docs/codex.md) · [With Entire](docs/entire.md) | [`cub mini` as plain `cub`](docs/cub-mini-and-cub.md) | [What we do not claim](docs/limits.md) |

## License

MIT ([LICENSE](LICENSE)). The program is built with Go and open-source modules, whose licenses are in [`plugins/confighub/THIRD_PARTY_LICENSES.txt`](plugins/confighub/THIRD_PARTY_LICENSES.txt).
