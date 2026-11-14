<!-- walkthrough
id: story-02-keep-your-changes
starts_with: mini
story: "2. George's colleague: "Run my app, and keep my changes when George updates it""
needs: [confighub mini package, python3]
budget_seconds: 180
-->
# Run a colleague's app, change it, and keep your changes when he updates it

For anyone who runs an app someone else made. George made a start page for his team. You run your own copy, change it with a reason each time, and then take George's next version: you get his improvements, and your changes stay. You never see Helm, Git or the hub that came with the app.

## Human

### What you need

An unpacked confighub mini package, 0.11.1-mini.2 or later ([installing confighub mini](../../docs/install-mini.md#install-by-hand-without-the-plugin)), and `python3`. No Docker, no cluster and no account. A *hub* is ConfigHub running on your computer; the start page starts one by itself the first time it runs.

### Steps

1. Say where the unpacked package is:

   <!-- run: package files -->
   ```sh
   export MINI=/absolute/path/to/unpacked-confighub-mini
   ```

2. Set up a terminal for this walkthrough. `cub` is ConfigHub's command-line tool. `CUB_CONFIG` gives this walkthrough a `cub` configuration of its own, so your own `cub` settings are not touched:

   <!-- run: setup -->
   ```sh
   export PATH="$MINI/bin:$PATH"
   export CUB_CONFIG="$HOME/.confighub-walkthrough"
   unset CUB_CONTEXT
   confighub-mini-app mini install-plugin "$CUB_CONFIG"
   ```

3. Copy George's start page into a folder of your own:

   <!-- run: copy files -->
   ```sh
   mkdir -p ~/walkthrough && cp -R "$MINI/examples/startpage" ~/walkthrough/ && cd ~/walkthrough/startpage
   ```

4. Open it. It starts its hub the first time, in about 20 seconds, and opens the page in your browser: George's title, three links, a light background.

   <!-- run: keep-open -->
   ```sh
   ./startpage
   ```

   ```text
   Your page: ~/walkthrough/startpage/page.html
   ```

5. Make it yours. Each change says what, to what, and why. The footer is something George never planned for anyone to change:

   <!-- run: keep-change -->
   ```sh
   ./startpage set theme dark "Easier on my eyes"
   ./startpage set footer "Support desk, floor 3" "So people can find us"
   ./startpage remove links.wiki "We do not use the wiki"
   ```

   ```text
   theme is now dark. It stays that way when George's next version arrives.
   …
   footer is now Support desk, floor 3. It stays that way when George's next version arrives.
   …
   links.wiki is gone. It stays gone when George's next version arrives.
   ```

6. George improves his page: a new title, four columns, the wiki moved, and a status link. He puts his new version where his colleagues get it from, which here is a folder:

   <!-- run: keep-george -->
   ```sh
   cp georges-next-version/startpage.yaml published/
   ```

7. Look at his update before taking it. You see what George changed, what you would take, and what you keep, with his new value beside it. It then asks whether to take it; `echo n` answers no for you, so nothing changes yet:

   <!-- run: keep-look -->
   ```sh
   echo n | ./startpage update
   ```

   ```text
   George changed title: Team start page -> Team start page 2
   George changed columns: 3 -> 4
   George added links.status: https://status.example.com
   You keep links.wiki taken out (George now has: https://wiki.example.com/new-home)
   Take George's update? [y/N] Nothing has changed. Run this again when you want it.
   ```

8. Take it. `--yes` answers the question for you:

   <!-- run: keep-take -->
   ```sh
   ./startpage update --yes
   ```

   ```text
   …
   Done.
   ```

   Your page now has George's four columns and status link, and still your dark theme, your footer, and no wiki.

9. Later, someone asks why the page looks like this. The app lists each of your changes with its date and the reason you gave: `theme: Easier on my eyes`, `footer: So people can find us`, and `links.wiki taken out: We do not use the wiki`.

   <!-- run: keep-why -->
   ```sh
   ./startpage why
   ```

### Undo it

This removes the hub with everything in it, and the walkthrough's folder and `cub` configuration:

<!-- run: undo -->
```sh
cub mini uninstall --delete-data
cd ~ && rm -rf ~/walkthrough "$CUB_CONFIG"
```

### What you have now

Nothing left behind. While it ran, you had George's improvements and all three of your changes, each with its reason, including one George never offered as a setting. The full story adds a second app joining the same hub, George renaming a setting you changed, and the laptop crashing with nothing lost. [Software with ConfigHub inside](../../docs/journeys/bundled.md) shows how to build an app like this.

## Agent

For an AI agent doing this for a person.

- **The request:** "Run George's start page for me, make it dark because it's easier on my eyes, put 'Support desk, floor 3' in the footer so people can find us, then take George's newest version without losing my changes."
- **What to run:** in a copy of `$MINI/examples/startpage`, use the app's own commands, in this order: `./startpage`, `./startpage set theme dark "Easier on my eyes"`, `./startpage set footer "Support desk, floor 3" "So people can find us"`, `cp georges-next-version/startpage.yaml published/`, `./startpage update` (show the person the preview), then `./startpage update --yes`. Tell the person what George changed, what they kept, and that `./startpage why` lists their reasons.
- **Never:** edit `published/startpage.yaml` or `page.html` by hand to fake a change; the hub holds the person's copy, and a hand edit is lost at the next update. Never take the update without first showing the preview.
- **Done when:** `./startpage why` lists both reasons, and the person's copy in the hub has `theme: dark`, the footer, and `columns: 4`.

## Testing

The scripted run follows the Human steps on a hub of its own and compares the quoted output. A correct agent result leaves the person's copy, `startpage-mine`, with the dark theme and the footer kept and George's four columns taken, each change with its reason. The checks below can be run by hand, from the start page's folder, after the steps:

This proves: stored. The colleague's copy and George's update are kept in a hub on this computer, and the app draws its page from it; no service runs. The next step this aims to win: keeping the hub on for the next update. Tested on the checksum-verified published confighub mini 0.11.1-mini.2 with the plugin 0.85.0, 14 November 2026: environment, local hub and local files (no cluster); approval, no approval step.

<!-- agent-task: keep -->
> George's start page app is in this folder: run it. Make it dark because it's easier on my eyes, put "Support desk, floor 3" in the footer so people can find us, then take George's newest version (in its georges-next-version folder) without losing my changes.

<!-- agent-check keep: d=$(find . -name .my-settings.yaml | head -1) && grep -q '^theme: dark' "$d" && grep -q '^footer: Support desk, floor 3' "$d" && grep -q '^columns: 4' "$d" && cd "$(dirname "$d")" && ./startpage why | grep -q 'theme: Easier on my eyes' -->
<!-- agent-check-a keep: f=$(grep -rl --include='*.yaml' '^columns: 4' . | head -1) && grep -q '^theme: dark' "$f" && grep -q '^footer: Support desk, floor 3' "$f" -->
<!-- agent-tools: ./startpage -->
<!-- arms: a,b -->
<!-- next-step when "recorded": keep it for George's next update | George will update the app again. Keep your changes and their reasons in a hub, so the next update keeps them too? -->

```sh
d=$(find . -name .my-settings.yaml | head -1)
grep -E '^(theme|footer|columns):' "$d"
(cd "$(dirname "$d")" && ./startpage why)
```

<!-- results:begin -->

Results, 14 November 2026, confighub mini 0.11.1-mini.2. Figures from this page's own test runs, shown here for whoever checks the page; they are not a promise.

- Scripted run: passed, 59 seconds for the steps, within the page's budget of 180.
- Agent runs: a pilot, 3 runs per arm on each of claude-sonnet-5-5, claude-opus-5-5. Arms: a is ordinary tools only; b is the plugin, confighub mini and this page as reading.

| Arm | Model | Checks passed | Median seconds | Median cost | Commands left for the person (median) |
|---|---|---|---|---|---|
| a | claude-opus-5-5 | 0/3 | 30.5 | $0.236 | 0 |
| b | claude-opus-5-5 | 3/3 | 41.7 | $0.169 | 0 |
| a | claude-sonnet-5-5 | 0/3 | 15.3 | $0.096 | 0 |
| b | claude-sonnet-5-5 | 3/3 | 43.2 | $0.096 | 0 |

No agent approved or refused a change to production.

Simulated persons, not people: 10 per run, each a claude-haiku-5-5 model playing one of ten fixed personas, reading only what a person would see. The next step they were offered: "George will update the app again. Keep your changes and their reasons in a hub, so the next update keeps them too?"

The plugin offers it once, after the answer at whose end it showed the moment the offer names ("recorded"). Offered is the share of persons it was shown to; want it now and later are over them.

| Arm | Model | Persons | Offered | Noticed | Want the next step now | Later | In the way |
|---|---|---|---|---|---|---|---|
| a | claude-opus-5-5 | 30 | 0% | 100% | n/a | n/a | 100% |
| b | claude-opus-5-5 | 30 | 0% | 100% | n/a | n/a | 37% |
| a | claude-sonnet-5-5 | 30 | 0% | 100% | n/a | n/a | 100% |
| b | claude-sonnet-5-5 | 30 | 0% | 100% | n/a | n/a | 90% |

<!-- results:end -->
