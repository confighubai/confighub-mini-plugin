# A first run of confighub mini

This page is for someone trying confighub mini for the first time, on their own machine. confighub mini is a hub, ConfigHub made small enough to run on one machine, with no Docker, no cluster and no account. You install it, try one short story, put your agents' record into the hub if you have one, and tell us how it went.

The words on this page are explained in [the glossary](README.md#words).

## Install it

Type `/confighub:install-mini` in Claude Code, or follow [the install steps](install-mini.md) up to and including `cub space list`. With `/confighub:install-mini`, the hub is already running, and it printed the full path of its `cub`; to type `cub` yourself, put that folder first on your path: `export PATH="$HOME/.confighub/mini/confighub-mini-VERSION-OS-ARCH/bin:$PATH"`.

## Try one story

Each walkthrough shows every command and what it prints, and removes what it made at the end:

- [Run my app, and keep my changes when George updates it](../examples/walkthroughs/story-02-keep-your-changes.md): you change a start page someone else made, with a reason each time, and keep your changes through their next version. It is the package's `examples/startpage`.
- [The `cub mini` commands](../examples/walkthroughs/tool-cub-mini.md): the dozen commands a newcomer needs, on one small app.
- [Your first hour](../examples/walkthroughs/story-13-first-hour.md): production behind your approval, and an agent's own approval refused.

The package's `START-HERE.txt` lists more stories, and its `./verify` checks, on your machine, the size and speed claimed for confighub mini.

## Put your agents' record into the hub

If you have used the ConfigHub plugin in a repository, its record of what agents changed can go into the hub. Each recorded change becomes a revision, with the request or reason behind it.

1. Go to the repository, and see what would be written, without writing it:

   ```bash
   cub mini copy --from-record --dry-run
   ```

   In the repository from the [five-minute try](try-the-plugin.md#try-it-in-five-minutes), it printed:

   ```
   .env, as try-confighub-env:
     would make try-confighub-env-base, the file as it was before the first recorded change, and try-confighub-env-local
     would set CACHE off → on: Asked: Turn the cache on in .env for next week's sale. Don't commit. (agent session e7a0a61a, 27 October 2026 14:31)
     would set CACHE on → off: Asked: We're chasing a memory leak: turn the cache off and set debug logging. Don't commit. (agent session f3e8ff28, 27 October 2026 14:32)
     would set LOG_LEVEL warn → debug: Asked: We're chasing a memory leak: turn the cache off and set debug logging. Don't commit. (agent session f3e8ff28, 27 October 2026 14:32)
   ```

2. Write it:

   ```bash
   cub mini copy --from-record
   ```

   Each file becomes a Component. Its base is the file as it was before the first recorded change, and each recorded change is a revision of its local copy. Running it again writes only what was recorded since.

## Remove it

This removes the hub and its data:

```bash
cub mini uninstall --delete-data
```

## What to send back

- Your machine: the output of `uname -sm`, and the package you downloaded.
- The last lines `./verify` printed, if you ran it.
- Where you got stuck, had to guess, or read something twice.
- Anything that surprised you, good or bad.
