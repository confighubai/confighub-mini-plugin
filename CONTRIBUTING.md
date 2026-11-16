# Contribute to ConfigHub for coding agents

The quickest contribution is to try a [walkthrough](examples/walkthroughs/README.md) and tell us where you got stuck. [Open an issue](https://github.com/confighubai/confighub-mini-plugin/issues/new) with your operating system, agent and plugin versions, the guide you followed, what you expected, and the smallest example that shows what happened. Remove credentials, private settings and customer data from commands and output before posting.

- **Fix a guide or example.** Open a pull request. If a command changes, run it on the released package and say which version you used. A stand-in, a simulated reader and a real provider run are different kinds of evidence.
- **Share a starter.** Start from [the starter author guide](docs/write-a-starter.md). It shows the example and the command that checks detection, protects existing values and tests the cub plugin, if there is one. Include the YAML, a small app or fixture, and the check result in an issue. You don't need a provider account to start.
- **Propose a plugin change.** Open an issue with the behavior you want and a small example. The release generates `plugins/confighub/`; edits to that directory here won't carry into the next release.

For documentation changes, run these checks from the repository root. They use Python 3 and don't start a hub:

```sh
python3 -I .github/tools/check-links.py .
python3 -I .github/tools/lint-walkthroughs.py examples/walkthroughs
python3 -I .github/tools/llms-txt.py . | diff -u llms.txt -
```

## What's in this repository

| Folder | What it is |
|---|---|
| `plugins/confighub/` | The Claude plugin. Each release builds it, so please don't edit it here |
| `.claude-plugin/`, `.agents/` | The marketplace files Claude Code and Codex read |
| `docs/` | The guides |
| `review/` | A GitHub Action that comments on each pull request with every setting it changes, and why |
| `approval-check/` | A pull-request check that the settings match what the hub approved, for branch protection |
| `ci/` | GitHub Actions jobs that run a coding agent in CI |
| `examples/` | Runnable examples, such as a service on a Linux VM |
| `gitops/` | A small `docker` wrapper for kind clusters on OrbStack |
| `evaluate/` | Runs our evaluation of the Claude plugin with your own models |
| `entire-plugin.yml` | Installs the Claude plugin into the CLI of [Entire](https://entire.io), if you use it |
| `AGENTS.md`, `llms.txt` | What an AI agent should read first, and every page listed for AI agents |
