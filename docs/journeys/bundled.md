# Software that comes with ConfigHub inside it

This page is for someone who was given an app, a Helm chart or a platform by someone else, a vendor, a platform team or a colleague, and wants to change it to suit them without losing those changes at the next version. The way in is for that software to come with a hub inside it, so that each change you make is kept with its reason and the next version arrives with your changes kept. This page says plainly what of that exists today, and what does not.

## Words used on this page

- **A hub** is one running ConfigHub: a server that keeps configuration with every change, who made it and why. **confighub mini** is ConfigHub made small enough to run on one machine, as two processes, with no Docker and no account. It is small enough, 44 to 67 MB, to travel inside an app's download.
- **The base** is the configuration as its author ships it. **Your copy** is made from the base, and keeps what you change as your own when the base changes.

## What exists today

| What you were given | What you can do today | Where |
|---|---|---|
| An app that starts its own hub | Change it, including things its author never meant to be changed, each with a reason, and take the author's next version with your changes kept. You see first what you would take and what you keep | An example in the confighub mini package, `examples/startpage`; [below](#an-app-that-starts-its-own-hub) |
| A platform given to customers | Each customer keeps a value they had to pin, such as a GPU driver, through the platform's next version, and sees what the new version would change first | An example in the confighub mini package, `examples/gpu-platform` ([below](#a-platform-given-to-customers)) |
| A vendor's Helm chart | You add the hub yourself: your values kept through the chart's next version, with what it changes shown first | [Your own Helm chart](../your-own-chart.md) |
| An app's setup someone shared as a file | Make your own app from it, with its staging and live copies and the reason for each value | [An app from a setup someone shared](../from-plugin-to-confighub.md#an-app-from-a-setup-someone-shared) |

## What does not exist yet

- **No published way for a vendor to put a hub inside their software.** The two examples above build it in themselves. There is no contract or library a host program can use to do the same.
- **No hub that starts when it is first needed and stops when it is idle,** with no step for the person. The examples start their hub on first run.

If your vendor's software has none of this, the second and third ways in still work for it: [an app you already have](existing-app.md) and [your own Helm chart](../your-own-chart.md).

## An app that starts its own hub

George made a start page for his team. You run your own copy. The example carries no setup of its own: it uses the confighub mini it came in, and starts a hub the first time you run it. You never type a `cub` command.

1. Install confighub mini, if you have not: type `/confighub:install-mini` in Claude Code ([install](../install-mini.md)).

2. From the package's folder, `~/.confighub/mini/confighub-mini-VERSION-PLATFORM`, go to the example and open your page:

   ```bash
   cd examples/startpage
   ./startpage
   ```

   The page opens in your browser. The first time takes about ten seconds.

3. Change it, with a reason each time:

   ```bash
   ./startpage set theme dark "Easier on my eyes"
   ./startpage remove links.wiki "We do not use the wiki"
   ```

4. George publishes his next version. In the example, you stand in for him:

   ```bash
   cp georges-next-version/startpage.yaml published/
   ```

5. Take it:

   ```bash
   ./startpage update
   ```

   Before anything changes, you see what George changed, what you take, and what you keep, with his new value beside each thing you keep. The example's own README shows:

   ```
     George changed   columns: 3 -> 4
     George added     links.status: https://status.example.com
     You keep         links.wiki taken out   (George now has: https://wiki.example.com/new-home)
     You keep         title: Support start page   (George now has: Team start page 2)

   Take George's update? [y/N]
   ```

   Say no, and nothing changes.

6. See what you changed, and why:

   ```bash
   ./startpage why
   ```

The full walk-through, about two minutes, is step 3 of [a first run](../try-confighub-mini.md#step-3-change-an-app-and-keep-your-changes-through-its-next-version), and the example's `README.md`.

## A platform given to customers

The package's `START-HERE.txt` lists `examples/gpu-platform`: a platform team gives customers NVIDIA's GPU Operator. A customer keeps the driver version they pinned, with the reason "A driver change drains every GPU node. We change it only in a maintenance window.", and takes the operator's next version, shown first what it would take and keep. It needs no GPU, no cluster and no Docker, and Helm only to render the chart. Its README, sections 1 to 4, takes about three minutes.

## How to go back

The start page's hub is one more context in your own `cub`, and your current context is not changed. To remove it and its data, run `cub mini uninstall --delete-data`, then delete the package folder ([going back](going-back.md)).

## How this was tested

Both examples ship in the confighub mini package. The package's story checks run them, and passed before the release of confighub mini 0.10.7-mini.11.
