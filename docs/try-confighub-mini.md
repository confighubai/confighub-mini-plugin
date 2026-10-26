# Try confighub mini: a first run, about 15 minutes

This is for someone trying confighub mini for the first time, on their own machine, and telling us how it went. You need a Mac or Linux machine (ARM or Intel), `curl`, `xz` and `python3`. No Docker, no cluster, no account.

## 1. Install it, and start a hub

Follow [the install steps](install-mini.md) up to `cub space list`. Note how long `cub mini install` took.

## 2. Check what is claimed for it

From the package folder:

```bash
./verify
```

It checks, on your machine, the size and speed claimed for confighub mini, in a folder of its own, and removes what it made. About a minute.

## 3. A first story: an app you run, change, and keep your changes in

George made a start page for his team; you run your own copy, change it, and keep your changes when George updates his.

```bash
cd examples/startpage
./startpage
./startpage set theme dark "Easier on my eyes"
./startpage remove links.wiki "We do not use the wiki"
cp georges-next-version/startpage.yaml published/
./startpage update
./startpage why
```

`./startpage` opens your page in the browser. The `cp` is George publishing his next version. `update` shows what you would take from it and what you keep, and asks before taking it; `why` lists what you changed and why. `examples/startpage/README.md` tells the whole story.

## 4. Optional: an agent that proposes and a person who approves

The [approval steps](approvals.md) work on this hub as they do on hosted ConfigHub. It takes about 5 minutes.

## 5. Remove it

```bash
cub mini uninstall --delete-data
```

## What to send back

- Your machine: the output of `uname -sm`, and the package you downloaded.
- How long `cub mini install` took, and the last lines `./verify` printed.
- Where you got stuck, had to guess, or read something twice.
- Anything that surprised you, good or bad.
