# Install confighub mini

confighub mini is ConfigHub, small, for one machine: the ConfigHub server and its PostgreSQL run as ordinary processes, with no Docker, no cluster and no account. There is a package for macOS and for Linux, each on ARM and on Intel, with `cub` inside. Each is about 45 to 70 MB.

## In one step, from Claude Code

With the ConfigHub plugin installed, type:

```
/confighub:install-mini
```

It finds the newest release, downloads the package for your machine, checks it against the release's `SHA256SUMS`, unpacks it, and starts a hub: about 25 seconds on a Mac. Run again, it starts the hub if it is stopped. In a terminal, or in Codex, `bin/confighub mini get` from the plugin does the same. Below are the same steps by hand.

## Download and unpack

```bash
V=0.9.0-mini.5
P=$(uname -s | tr A-Z a-z)-$(uname -m | sed 's/x86_64/amd64/; s/aarch64/arm64/')
curl -fLO https://github.com/confighubai/confighub-mini-plugin/releases/download/mini-v$V/confighub-mini-$V-$P.tar.xz
curl -fLO https://github.com/confighubai/confighub-mini-plugin/releases/download/mini-v$V/SHA256SUMS
grep " confighub-mini-$V-$P.tar.xz" SHA256SUMS | shasum -a 256 -c
tar xf confighub-mini-$V-$P.tar.xz
cd confighub-mini-$V-$P
```

On Linux it needs `curl` and `xz` (on Debian or Ubuntu, `apt-get install curl xz-utils`); without `shasum`, use `sha256sum -c` in its place.

The macOS programs are not signed yet. Downloaded with `curl`, as above, macOS does not hold them back. Downloaded through a browser, clear that once from the package folder: `xattr -dr com.apple.quarantine .`

## Start a hub

From the package folder, once, add the `cub mini` commands to the package's `cub`, and put it first on your path:

```bash
./bin/cub plugin install .
export PATH="$PWD/bin:$PATH"
```

Then:

```bash
cub mini install
cub space list
```

`cub mini install` starts the server and its PostgreSQL, and signs `cub` in to the new hub as a new context, in about 10 seconds. With no `cub` context before, the hub's becomes the current one, as above. If you already use `cub`, your current context is kept, and `cub mini install` prints the line that reaches the hub, such as `cub --context star-paw space list`; `cub mini install --use` makes the hub current instead.

`START-HERE.txt` in the package lists ten stories to run on it.

To remove the hub and its data: `cub mini uninstall --delete-data`.

## In a container or a CI job

PostgreSQL will not run as root, nor as a user ID with no account, so run confighub mini as an ordinary user. On a machine or CI runner that runs as an ordinary user, the steps above work as written. In a container, this Dockerfile makes a plain Debian image with confighub mini in it, checked against `SHA256SUMS`:

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

```bash
docker build -t agent-sandbox .
docker run --rm --network none agent-sandbox sh -c 'cub mini install && cub space list'
```

- **No network after the download.** A hub starts and works with the network off, as in the `docker run` above.
- **Where its data is.** Each hub keeps its data under `~/.confighub/servers/`. Set `CUB_CONFIG=DIR` to keep the hub and `cub`'s settings in a folder of your choice instead, such as the task's workspace, so they stay with it or go with it.
- **Telling the agent.** `cub --help` does not list plugin commands, so tell the agent `cub mini` is there. One line in its `CLAUDE.md` or `AGENTS.md` is enough: *This is a sandbox. Its cub has the cub mini commands (cub mini --help): the first one that needs a hub starts a hub of your own here, which is thrown away with the sandbox.*
- **What it adds.** The image grows by about 300 MB once unpacked; each hub then uses about 30 MB of disk and 140 to 190 MB of memory.

## What it holds

Each package's `provenance.json` names the ConfigHub release it was built from, and the PostgreSQL build inside it, with its SHA-256. Approvals, ChangeWorkflows and the rest are ConfigHub's own; the steps for approvals are in [approvals.md](approvals.md).
