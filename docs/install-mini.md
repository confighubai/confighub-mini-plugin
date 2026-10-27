# Install confighub mini

This page is for an engineer who wants to run ConfigHub on their own machine, to try it or to give an agent a hub of its own. It shows how to install confighub mini in one step from Claude Code, by hand, and in a container or CI job.

## What you are installing

[ConfigHub](https://docs.confighub.com) keeps your configuration, such as Kubernetes manifests and Helm values, with the reason each value is set. It also controls how a change reaches your clusters, for example by requiring a person's approval.

A *hub* is one running ConfigHub server, with the database that holds your configuration. *confighub mini* is ConfigHub made small enough to run a hub on one machine. The ConfigHub server and its PostgreSQL database run as ordinary processes. You need no Docker, no cluster and no account.

You work with a hub through `cub`, ConfigHub's command-line tool. The package includes `cub`.

There is a package for macOS and one for Linux, each for ARM and for Intel. Each package is about 44 to 67 MB.

## Install in one step, from Claude Code

With [the ConfigHub plugin](../README.md) installed, type this in a Claude Code session:

```
/confighub:install-mini
```

It does the following, in about 25 seconds on a Mac:

1. It finds the newest release.
2. It downloads the package for your machine.
3. It checks the package against the release's `SHA256SUMS`.
4. It unpacks the package.
5. It starts a hub.

If you run it again, it starts the hub if the hub is stopped.

When it is done, it prints the line that puts the package's `cub` on your `PATH`, and what to do next: put a repository's record into the hub with `cub mini copy --from-record` ([how](try-confighub-mini.md#step-4-put-your-agents-record-into-the-hub)), or follow [a first run](try-confighub-mini.md).

In a terminal, or in Codex, run `bin/confighub mini get` from the plugin. It does the same.

## Install by hand

These are the same steps the one-step install takes.

On Linux you need `curl` and `xz`. On Debian or Ubuntu, install them with `apt-get install curl xz-utils`.

1. Set the version, and work out the package name for your machine. Run the next steps in the same shell, since they use `V` and `P`:

   ```bash
   V=0.9.0-mini.5
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

   The macOS programs are not signed yet. macOS holds back unsigned programs downloaded through a browser, and this command releases them. Programs downloaded with `curl`, as above, are not held back.

6. Add the `cub mini` commands to the package's `cub`, and put the package's `cub` first on your path. You do this once:

   ```bash
   ./bin/cub plugin install .
   export PATH="$PWD/bin:$PATH"
   ```

7. Start a hub:

   ```bash
   cub mini install
   ```

   This starts the ConfigHub server and its PostgreSQL, in about 10 seconds. It also signs `cub` in to the new hub, as a new *context*. A context is a named server and sign-in that `cub` can talk to.

   - If you had no `cub` context before, the hub's context becomes the current one.
   - If you already use `cub`, your current context is kept. `cub mini install` prints the line that reaches the hub, such as `cub --context star-paw space list`. To make the hub's context the current one instead, run `cub mini install --use`.

8. Check that `cub` reaches the hub:

   ```bash
   cub space list
   ```

   This lists the hub's Spaces. A *Space* is where ConfigHub keeps a set of configuration. If you kept your earlier context, use the line `cub mini install` printed instead.

The package's `START-HERE.txt` lists ten stories you can run on the hub. For a guided first run, see [Try confighub mini](try-confighub-mini.md).

To remove the hub and its data:

```bash
cub mini uninstall --delete-data
```

## In a container or a CI job

PostgreSQL will not run as root. It also will not run as a user ID that has no account. So run confighub mini as an ordinary user.

On a machine or CI runner that runs as an ordinary user, the steps above work as written.

In a container, this Dockerfile makes a plain Debian image with confighub mini in it. It checks the package against `SHA256SUMS`, and runs as an ordinary user, `agent`:

```dockerfile
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl xz-utils \
 && rm -rf /var/lib/apt/lists/*
RUN useradd -m agent
USER agent
WORKDIR /home/agent
ARG V=0.9.0-mini.5
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

The features of a hub are ConfigHub's own, not a separate version of them. That includes approvals, and ChangeWorkflows, which say what a change needs before it goes ahead, such as a person's approval. The steps for approvals are in [approvals.md](approvals.md).
