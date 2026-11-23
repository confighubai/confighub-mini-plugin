<!-- walkthrough
id: story-26-staging-in-your-own-app
starts_with: both
story: "26. Staging and production, seen in the app on your laptop"
needs: [Claude Code with the ConfigHub plugin, cub mini package, Python 3, curl]
budget_seconds: 180
-->
# See staging and production in the app that runs on your laptop

Maya builds a small app on her laptop: a Vite or Next.js app, or a Python app with a `Procfile`. Its settings are in `.env`. She wants her coding agent to try changes in staging and see them in the running app, while production changes wait for her. Here the app is a few lines of Python that shows one setting, `BANNER`, on a page, so you need nothing but Python. The [guide to an app you already have](../../docs/journeys/existing-app.md) covers the same commands for a Node app.

## Quick start

You need: Claude Code with the [ConfigHub plugin](../../README.md#install), and an app that runs on your laptop with its settings in `.env` or `.env.local`.

| | By hand | Ask your agent |
|---|---|---|
| Connect the app | `/confighub:staging` in the app's folder | You type it yourself. |
| Change staging and see it | `cub mini set shop BANNER=autumn --variant staging --change-desc "WHY"`, then `cub mini preview --staging` | "Try the autumn banner in staging, and show me the app running with it." |
| See production before you approve | `cub mini preview --production` | "Make the banner say winter in production. I'll approve it." |
| Approve, and see it again | `cub mini approve shop`, then `cub mini preview --production` | You approve it yourself. |

Your app runs the way it already does, with each copy's settings passed in. Your files are not changed.

Without ConfigHub: your agent edits `.env` and restarts the dev server, so staging and production are the same file, and nothing waits for you.

## Deeper dive

The rest of this page is the full version: every command with what it prints, how to stop what runs, what an agent leaves to you, and how this was tested.

<details>
<summary>Show the full walkthrough</summary>

## Human

### What you need

Claude Code with the ConfigHub plugin, an unpacked [confighub mini package](../../docs/install-mini.md) 0.11.1-mini.31 or later, Python 3 and `curl`, on macOS or Linux. No account. A *hub* is ConfigHub running on your computer. It keeps a staging and a production copy of the app's settings, each change with its reason.

### Steps

1. Set up a terminal. `CUB_CONFIG` gives this walkthrough a `cub` configuration of its own, so your own settings are not touched.
   <!-- run: setup -->
   ```sh
   export MINI=/absolute/path/to/unpacked-confighub-mini
   export PATH="$MINI/bin:$PATH" CUB_CONFIG="$HOME/.confighub-walkthrough"
   unset CUB_CONTEXT
   "$MINI/bin/confighub-mini-app" mini install-plugin "$CUB_CONFIG" >/dev/null
   ```
2. Make the app. It reads `BANNER` from its environment first and from `.env` second, as Vite, Next.js and python-dotenv do. It keeps a secret in `.env` too, which never goes into the hub. The `Procfile` says how it runs.
   <!-- run: app files -->
   ```sh
   mkdir -p ~/walkthrough/shop && cd ~/walkthrough/shop
   printf 'BANNER=summer\nSECRET_KEY=change-me-locally\n' > .env
   printf 'web: python3 app.py\n' > Procfile
   cat > app.py <<'EOF'
   import os, http.server
   env = dict(l.strip().split("=", 1) for l in open(".env") if "=" in l)
   banner = os.environ.get("BANNER") or env.get("BANNER")
   class Page(http.server.BaseHTTPRequestHandler):
       def do_GET(self):
           self.send_response(200); self.end_headers(); self.wfile.write(f"banner={banner}\n".encode())
   http.server.HTTPServer(("127.0.0.1", int(os.environ.get("PORT", "8000"))), Page).serve_forever()
   EOF
   ```
3. Connect it. `/confighub:staging` gives the app a staging and a production copy of its settings in a hub on this computer. The secret stays in `.env`. The last line says how to see each copy in the running app.
   <!-- run: connect -->
   ```sh
   claude -p "/confighub:staging"
   ```
   ```text
   shop now has a staging and a production copy of its settings, in a hub on this machine. Your files are unchanged.
   Staging takes your agent's changes at once. Your agent can only propose changes to production; they wait for you.
   …
   ```
4. Change staging. Your agent changes it on its own key at once; here you make the same change.
   <!-- run: staging -->
   ```sh
   cub mini set shop BANNER=autumn --variant staging --change-desc "Try the autumn banner"
   ```
   ```text
   Saved in shop-staging, with the reason: Try the autumn banner. A later version of what shop-staging is made from will not overwrite this value.
   ```
5. See staging in the running app. `cub mini preview --staging` names the command before it runs it, here the `web:` line of the `Procfile`, and passes staging's settings as environment variables. It prints the address. Open it, or read it with `curl`.
   <!-- run: staging-preview -->
   ```sh
   cub mini preview --staging | tee staging.txt
   sleep 2; curl -fsS "$(sed -nE 's/^Staging is running at ([^,]+),.*/\1/p' staging.txt)"
   ```
   ```text
   Running python3 app.py, the web line of the Procfile, with staging's 2 settings as environment variables; your files are not changed.
   banner=autumn
   ```
6. Propose a production change. Your agent can only propose it; it waits for you, and production keeps its value.
   <!-- run: propose -->
   ```sh
   cub mini set shop BANNER=winter --variant live --change-desc "Winter banner"
   cub mini waiting
   ```
7. See production before you approve. `cub mini preview --production` runs the app on this computer with what was approved for production. A change that still waits is not in it. Production itself is unchanged.
   <!-- run: production-before -->
   ```sh
   cub mini preview --production -- python3 app.py | tee production.txt
   sleep 2; curl -fsS "$(sed -nE 's/^Your app is running at ([^ ]+) on this machine.*/\1/p' production.txt)"
   ```
   ```text
   banner=summer
   ```
8. Approve it. `cub mini approve shop` shows the change and asks; answer `y`.
   <!-- run: approve -->
   ```sh
   cub mini approve shop
   ```
   ```text
       BANNER: summer → winter
   Applied the reviewed change to shop-live.
   ```
9. See production again. Run it the same way, and the page shows what you approved.
   <!-- run: production-after -->
   ```sh
   cub mini preview --production --stop
   cub mini preview --production -- python3 app.py | tee production.txt
   sleep 2; curl -fsS "$(sed -nE 's/^Your app is running at ([^ ]+) on this machine.*/\1/p' production.txt)"
   ```
   ```text
   banner=winter
   ```
10. Stop both runs. Your agent finds them too, in a fresh chat, with `cub mini preview --status`.
    <!-- run: stop -->
    ```sh
    cub mini preview --staging --stop
    cub mini preview --production --stop
    rm staging.txt production.txt
    ```
    ```text
    The app run with staging's settings is stopped.
    Your app run on this machine with production's settings is stopped. Production itself is unchanged.
    ```

### Undo it

`cub mini uninstall --name mini --delete-data` removes the hub and everything in it; then delete `~/walkthrough` and `~/.confighub-walkthrough`. The app's files were never changed.

### What you have now

The app on your laptop runs with staging's settings or with production's approved ones, whichever you ask for, and your `.env` is as you wrote it. Each change has its reason in the hub, and production changed only when you said yes.

## Agent

For an AI agent doing this for a person.

- The person types `/confighub:staging`; you cannot. After it, work in a fresh session, on the key it gives you.
- Change staging with `cub mini set APP KEY=VALUE --variant staging --change-desc "WHY"`, then run `cub mini preview --staging` and give the person the address it prints.
- Propose a production change with `--variant live`, and hand the person `cub mini approve APP` for their own terminal. They can run `cub mini preview --production` before and after.
- Never approve production, never edit `.env` to make a change, and never print a secret's value.
- When the person is done, stop what you started with `cub mini preview --staging --stop`.

## Testing

<!-- agent-task: staging after=connect -->
> Try the autumn banner in staging, and show me the app running with it.

<!-- agent-check staging: cub unit data --space shop-staging app | grep -qx 'BANNER=autumn' && cub unit data --space shop-live app | grep -qx 'BANNER=summer' && grep -qx 'BANNER=summer' .env && cub mini preview --status | grep -q 'Staging is running' -->
<!-- agent-check-a staging: grep -qx 'BANNER=summer' .env -->
<!-- next-step boundary=same-tier when "did not change": see production too | Production kept its banner and waits for your yes. Want to run the app with production's settings now, and again after you approve? -->

This proves: an app that runs on the laptop is connected without a change to its files; the agent's staging change is seen in the running app; a production change waits, the person sees production before and after approving it, and the app's own files and secret stay as they were.

**What ran.** This path ran in our release check for confighub mini 0.11.1-mini.31, on a real local hub on a Mac, with three apps: one shaped like a Vite app, one shaped like a Next.js app with its settings only in `.env.local`, and a Python app with a `Procfile`. The `vite` and `next` commands were small stand-ins that read the environment first and the file second, as the real ones do. The check confirmed that the agent's key changed staging and the page served its value, that production's run served the value before the approval and the approved value after it, that a fresh session found and stopped both runs, that each app's files were byte for byte unchanged, and that no secret appeared in any output. Real Vite, Next.js and Flask were not run, and no real agent session asked for the run: the agent's commands ran on its key from a script.

</details>
