# Install confighub mini

confighub mini is ConfigHub, small, for one machine: the ConfigHub server and its PostgreSQL run as ordinary processes, with no Docker, no cluster and no account. There is a package for macOS and for Linux, each on ARM and on Intel, with `cub` inside. Each is about 45 to 70 MB.

## Download and unpack

```bash
V=0.9.0-mini.1
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

## What it holds

Each package's `provenance.json` names the ConfigHub release it was built from, and the PostgreSQL build inside it, with its SHA-256. Approvals, ChangeWorkflows and the rest are ConfigHub's own; the steps for approvals are in [approvals.md](approvals.md).
