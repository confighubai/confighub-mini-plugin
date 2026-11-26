# Install confighub mini

The local hub is ConfigHub made small enough to run on one machine: a hub on your laptop, free, with no account, no Docker and no cluster. It keeps your app's settings with the reason for each value, and can make changes to production wait for your approval.

This page shows how to install it: in one step from Claude Code, on its own without the Claude plugin, and in a container or CI job. It is also the one page that says which versions are current; other pages link here rather than name a version.

## The current release

| What | Version |
|---|---|
| the local hub | 0.11.1-mini.41 |
| The ConfigHub server inside it | v0.11.1, the same version a shared hub on confighub.com runs |
| `cub`, ConfigHub's command-line tool, inside it | v0.11.1 |
| The download | Choose your platform in the [release assets](https://github.com/confighubai/confighub-mini-plugin/releases/tag/mini-v0.11.1-mini.41) to see its download size |

The Claude plugin's own version is on the [releases page](https://github.com/confighubai/confighub-mini-plugin/releases). `bin/confighub mini get` always gets the newest local hub.

## What you are installing

[ConfigHub](https://docs.confighub.com) keeps your configuration, such as Kubernetes manifests and Helm values, with the reason each value is set. It also controls how a change reaches your clusters, for example by requiring a person's approval.

A *hub* is one running ConfigHub server, with the database that holds your configuration. *the local hub* is ConfigHub made small enough to run a hub on one machine. The ConfigHub server and its PostgreSQL database run as ordinary processes. You need no Docker, no cluster and no account.

You work with a hub through `cub`, ConfigHub's command-line tool. The package includes `cub`.

There is a package for macOS and one for Linux, each for ARM and for Intel, on this repository's [releases page](https://github.com/confighubai/confighub-mini-plugin/releases). The sizes are in [the current release](#the-current-release).

## Install in one step, from Claude Code

With [the Claude plugin](../README.md) installed, open a Claude Code session in your app's folder, one that holds a settings file such as `.env`, and type:

```
/confighub:staging
```

When the local hub is not on your machine yet, it does the following:

1. It finds the newest release.
2. It downloads the package for your machine.
3. It checks the package against the release's `SHA256SUMS`.
4. It unpacks the package.
5. It starts a hub.

Then it gives the app a staging and a production copy of its settings in that hub. Staging takes your agent's changes at once, and production only what you approve. It asks nothing, and approves nothing. Where production's first settings wait for you, it ends with the one command that approves them, to run in a terminal of your own. Then start a new Claude Code session in the folder ([approvals](approvals.md#on-confighub-mini-ask-for-it)).

With the package already here, it downloads nothing, and starts the hub if the hub is stopped. To move to a newer release, see [below](#move-to-a-newer-confighub-mini).

For the record alone, with no app to connect, type `/confighub:to-hub --yes`. With no hub reachable, it starts one the same way, and copies the record into it.

In a terminal, or in Codex, run `bin/confighub mini get` from the plugin. It does steps 1 to 5. In a terminal, the first time on a machine, it asks one question before it starts the hub: whether a hub may start by itself for an app's settings files when an agent works in its folder ([what it does](agent-workflow.md#a-hub-that-starts-by-itself-only-if-you-say-yes)). Enter means no. The plugin on its own carries no server, so any `cub mini` command run as `bin/confighub mini COMMAND`, such as `bin/confighub mini install` or `bin/confighub mini need`, says it needs the local hub when none is downloaded, and names `confighub mini get`.

The one-step install needs nothing else on the machine: no `tar`, `xz` or `curl`, and no system certificates. It works on Linux distributions that use glibc, such as Debian, Ubuntu, Fedora, Rocky and Amazon Linux, including their slim images. Alpine uses musl, and the bundled PostgreSQL does not run on it, so the install stops before it downloads anything and says so. Use a glibc image instead. In a container, run it as a user that has an account, since PostgreSQL will not start for a user ID without one.

## Install by hand, without the plugin

These are the same steps the one-step install takes, and they need no plugin and no Claude Code.

On Linux you need `curl` and `xz`. On Debian or Ubuntu, install them with `apt-get install curl xz-utils`.

1. Set the version, and work out the package name for your machine. Run the next steps in the same shell, since they use `V` and `P`:

   ```bash
   V=0.11.1-mini.41
   P=$(uname -s | tr A-Z a-z)-$(uname -m | sed 's/x86_64/amd64/; s/aarch64/arm64/')
   ```

2. Download the package and the release's checksums:

   ```bash
   curl -fLO https://github.com/confighubai/confighub-mini-plugin/releases/download/mini-v$V/confighub-mini-$V-$P.tar.xz
   curl -fLO https://github.com/confighubai/confighub-mini-plugin/releases/download/mini-v$V/SHA256SUMS
   ```

3. Check the package against the checksums:

   ```bash
   grep " confighub-mini-$V-$P.tar.xz" SHA256SUMS | shasum -a 256 -c
   ```

   If your machine has no `shasum`, use `sha256sum -c` in its place.

4. Unpack the package, and go into its folder:

   ```bash
   tar xf confighub-mini-$V-$P.tar.xz
   cd confighub-mini-$V-$P
   ```

5. On macOS, if you downloaded the package through a browser rather than with `curl`, run this once in the package folder:

   ```bash
   xattr -dr com.apple.quarantine .
   ```

   These macOS binaries are unsigned. Check the archive against the release checksum in step 3 before clearing the browser download’s quarantine flag. Run the command only in the extracted package folder.

6. Add the `cub mini` commands to the package's `cub`, and put the package's `cub` first on your path. You do this once:

   ```bash
   ./bin/cub plugin install .
   export PATH="$PWD/bin:$PATH"
   ```

7. Start a hub:

   ```bash
   cub mini install
   ```

   The first time on a machine, it asks the one setup question first; Enter means no. This starts the ConfigHub server and its PostgreSQL. It also signs `cub` in to the new hub, as a new *context*. A context is a named server and sign-in that `cub` can talk to.

   - If you had no `cub` context before, the hub's context becomes the current one.
   - If you already use `cub`, your current context is kept. `cub mini install` prints the line that reaches the hub, such as `cub --context star-paw space list`. To make the hub's context the current one instead, run `cub mini install --use`.

8. Check that `cub` reaches the hub:

   ```bash
   cub space list
   ```

   This lists the hub's Spaces. A *Space* is where ConfigHub keeps a set of configuration. If you kept your earlier context, use the line `cub mini install` printed instead.

The package's `START-HERE.txt` lists ten stories you can run on the hub. For a guided first run, see [Try the local hub](try-confighub-mini.md); to learn the commands, the walkthrough [the `cub mini` commands](../examples/walkthroughs/tool-cub-mini.md).

## Move to a newer confighub mini

Run `bin/confighub mini get` from the Claude plugin in a terminal. It downloads the newest release, checks it against `SHA256SUMS`, and moves the hub onto it. Every Space, revision, change order still waiting and secret is kept. Each agent that `cub mini require-approval --agent` set up runs `cub mini` from the new package from then on, and its Claude Code settings may read it. Its last lines print the new `export PATH=...` line for its `cub`. `--version VERSION` gets one release in particular.

A repository's `.claude/settings.local.json` is not changed for you. When one runs its sessions as an agent, the move prints the new package's folder to add to that file's `sandbox.filesystem.allowRead`.

When the local hub installed is older than the one the Claude plugin was released with, the Claude plugin says so, at most once a day.

To move by hand, do steps 1 to 5 above with the new version. Then, in the new package's folder, swap the `cub mini` commands for its own, and put its `cub` first on your path:

```bash
./bin/cub plugin list
./bin/cub plugin uninstall confighub-mini-OLD-VERSION-PLATFORM
./bin/cub plugin install .
export PATH="$PWD/bin:$PATH"
```

Use the Claude plugin name `cub plugin list` shows. The next `cub mini` command moves your hub onto the new package's server. Your work, its history and your approvals are kept. A copy of the hub's data from before the move is kept in the hub's folder, as `pgdata-before-...`.

## Remove the hub

To remove the hub and its data:

```bash
cub mini uninstall --delete-data
```

## In a container or a CI job

PostgreSQL will not run as root. It also will not run as a user ID that has no account. So run the local hub as an ordinary user.

On a machine or CI runner that runs as an ordinary user, the steps above work as written.

In a container, this Dockerfile makes a plain Debian image with the local hub in it. It checks the package against `SHA256SUMS`, and runs as an ordinary user, `agent`:

```dockerfile
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl xz-utils \
 && rm -rf /var/lib/apt/lists/*
RUN useradd -m agent
USER agent
WORKDIR /home/agent
ARG V=0.11.1-mini.41
RUN P=linux-$(uname -m | sed 's/x86_64/amd64/; s/aarch64/arm64/') \
 && curl -fsSLO https://github.com/confighubai/confighub-mini-plugin/releases/download/mini-v$V/confighub-mini-$V-$P.tar.xz \
 && curl -fsSLO https://github.com/confighubai/confighub-mini-plugin/releases/download/mini-v$V/SHA256SUMS \
 && grep " confighub-mini-$V-$P.tar.xz" SHA256SUMS | sha256sum -c \
 && tar xf confighub-mini-$V-$P.tar.xz && rm confighub-mini-$V-$P.tar.xz SHA256SUMS \
 && mv confighub-mini-$V-$P confighub-mini \
 && confighub-mini/bin/cub plugin install ./confighub-mini >/dev/null \
 && rm -rf confighub-mini
ENV PATH=/home/agent/.confighub/plugins/confighub-mini/bin:$PATH
```

Build the image, then start a hub in it with the network off:

```bash
docker build -t agent-sandbox .
docker run --rm --network none agent-sandbox sh -c 'cub mini install && cub space list'
```

Things to know:

- **It needs no network after the download.** A hub starts and works with the network off, as in the `docker run` above.
- **Where the data is kept.** Each hub keeps its data under `~/.confighub/servers/`. To keep the hub and `cub`'s settings in a folder you choose instead, set `CUB_CONFIG=DIR`. For example, point it at the task's workspace, so the hub stays with the workspace or is removed with it.
- **Tell the agent that `cub mini` is there.** `cub --help` does not list plugin commands, so the agent will not find `cub mini` by itself. One line in its `CLAUDE.md` or `AGENTS.md` is enough: *This is a sandbox. Its cub has the cub mini commands (cub mini --help): the first one that needs a hub starts a hub of your own here, which is thrown away with the sandbox.*
- **What it costs.** The image grows by about 300 MB once the package is unpacked. Each hub then uses about 30 MB of disk, and 140 to 190 MB of memory.

## What the package contains

Each package has a `provenance.json` file. It names the ConfigHub release the package was built from, and the PostgreSQL build inside it, with that build's SHA-256.

The package includes its own `cub` ([which version](#the-current-release)), and every `cub mini` command runs that one, whichever `cub` comes first on your `PATH`. If you type plain `cub` commands with a `cub` of your own, use the same version. The commands on these pages use the flag names of ConfigHub v0.11, such as `--require-change-workflow`, which an older `cub` does not know, and a shared hub on confighub.com refuses a `cub` older than v0.11 as too old.

The features of a hub are ConfigHub's own, not a separate version of them. That includes approvals, and ChangeWorkflows, which say what a change needs before it goes ahead, such as a person's approval. The steps for approvals are in [approvals.md](approvals.md).

## Report a problem

Open an issue in [confighubai/confighub-mini-plugin](https://github.com/confighubai/confighub-mini-plugin/issues). It helps to include:

- the package folder's name, which gives its version and platform, such as `confighub-mini-0.11.1-mini.41-darwin-arm64`;
- what `cub version` prints, which names the hub's server version too;
- the command you ran, and what it printed.

Leave out keys, tokens and passwords. `cub version` prints none.
