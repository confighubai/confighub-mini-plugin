# Try confighub mini: a first run, about 15 minutes

This walkthrough is for someone trying confighub mini for the first time, on their own machine. You install it, run a short story in which you change an app and keep your changes through its next version, and then tell us how it went.

[ConfigHub](https://docs.confighub.com) keeps your configuration with the reason each value is set. A *hub* is one running ConfigHub server with its database. *confighub mini* is ConfigHub made small enough to run a hub on one machine.

## What you need

- A Mac or a Linux machine, ARM or Intel.
- `curl`, `xz` and `python3`.

You need no Docker, no cluster and no account.

## Step 1: Install confighub mini and start a hub

Follow [the install steps](install-mini.md) up to and including `cub space list`.

Note how long `cub mini install` took. We ask for it at the end.

## Step 2: Check the claims made for it

From the package folder, run:

```bash
./verify
```

It checks, on your machine, the size and speed claimed for confighub mini. It works in a folder of its own, and removes what it made when it is done. It takes about a minute.

Note the last lines it prints. We ask for them at the end.

## Step 3: Change an app, and keep your changes through its next version

In this story, George made a start page for his team. You run your own copy of it and change it. Then George publishes a new version, and you keep your changes when you take it.

1. From the package folder, go to the example:

   ```bash
   cd examples/startpage
   ```

2. Open your page:

   ```bash
   ./startpage
   ```

   Your start page opens in the browser.

3. Change the theme, and give your reason:

   ```bash
   ./startpage set theme dark "Easier on my eyes"
   ```

4. Remove a link, and give your reason:

   ```bash
   ./startpage remove links.wiki "We do not use the wiki"
   ```

5. Play George, publishing his next version:

   ```bash
   cp georges-next-version/startpage.yaml published/
   ```

6. Take George's new version:

   ```bash
   ./startpage update
   ```

   You see what you would take from George's version, and what of yours you keep. It asks before it takes anything.

7. See what you changed:

   ```bash
   ./startpage why
   ```

   You see each change you made, with the reason you gave.

`examples/startpage/README.md` tells the whole story.

## Step 4 (optional): An agent proposes, and a person approves

In this step an agent proposes a change, and only you can approve it. Follow [the approval steps](approvals.md). They work on this hub as they do on hosted ConfigHub. This takes about 5 minutes.

## Step 5: Remove it

This removes the hub and its data:

```bash
cub mini uninstall --delete-data
```

## What to send back

- Your machine: the output of `uname -sm`, and the package you downloaded.
- How long `cub mini install` took, and the last lines `./verify` printed.
- Where you got stuck, had to guess, or read something twice.
- Anything that surprised you, good or bad.
