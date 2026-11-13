<!-- walkthrough
id: story-18-dev-intent
starts_with: mini
story: "18. Ana asks for an app, and it fits the pattern"
needs: [cub mini package]
budget_seconds: 240
-->
# A new app that fits the team's pattern, with rules an agent cannot break by accident

Ana asks her agent for a small notes API and does not want to think about environments or limits. What comes back fits what her team allows: the app's settings in a hub, a staging and a production copy, and rules that hold. When an agent breaks a rule, the value never reaches the service, and her first app becomes the starting point for her next.

## Human

For a person following along in a terminal.

### What you need

An unpacked confighub mini package (from the [releases page](https://github.com/confighubai/confighub-mini-plugin/releases)) on macOS or Linux. confighub mini is a hub, a small ConfigHub server that keeps each setting with who changed it and why, running on your computer only. No Docker, no account.

### Steps

1. Set up a terminal. `MINI` is the unpacked package; `CUB_CONFIG` is a new folder for this walkthrough's `cub` settings, so nothing of yours is touched. Then start a hub:
   <!-- run: setup -->
   ```sh
   export MINI=/absolute/path/to/unpacked-confighub-mini
   export PATH="$MINI/bin:$PATH"
   export CUB_CONFIG="$HOME/.confighub-walkthrough"
   unset CUB_CONTEXT
   "$MINI/bin/confighub-mini-app" mini install-plugin "$CUB_CONFIG" >/dev/null
   cub mini install --name ana --use --arrival no >/dev/null
   ```
   `--arrival no` answers the one question a first install asks: whether a hub may start by itself when an agent works in an app's folder.

2. Ana's agent wrote the notes API, with its settings in `.env`:
   <!-- run: app files -->
   ```sh
   mkdir -p ~/walkthrough/notes && cd ~/walkthrough
   printf 'PORT=3000\nLOG_LEVEL=info\n' > notes/.env
   ```

3. One command puts it on the team's pattern, `pattern-web`: default settings for a small web service, and rules each change must pass. A rule here is a validating Trigger, which ConfigHub runs on every change:
   <!-- run: adopt -->
   ```sh
   cub mini adopt notes | sed -n 1,4p
   cub mini approve notes-base/adopt --note "Ana's starting values" --yes >/dev/null
   ```
   ```text
   Made a starter pattern, pattern-web: default settings for a small web service (pattern-web/web-service), and rules that each change must pass (replicas-limit, not-public, log-level, no-secret-values). You can change it or ignore it.
   ConfigHub now keeps notes's settings, from .env. Your files are unchanged.
     It keeps three copies of them: notes-base, the shared settings that staging and production start from; notes-staging; and notes-live, for production.
     Your settings that differ from the defaults in pattern-web/web-service: PORT=3000. A new version of those defaults will not overwrite them.
   ```

4. The rules are ordinary ConfigHub, kept with the pattern:
   <!-- run: rules any-order -->
   ```sh
   cub trigger list --space pattern-web -o jq='.[].Trigger.Slug'
   ```
   ```text
   not-public
   no-secret-values
   log-level
   replicas-limit
   ```

5. An agent, on a key of its own, sets 50 replicas for staging. The value is kept in the hub, the agent is told it breaks a rule, and it is not released:
   <!-- run: break -->
   ```sh
   cub mini require-approval notes --variant live --agent bot >/dev/null
   cub --context bot mini set notes REPLICAS=50 --variant staging --change-desc "Handle the launch" | grep rules
   ```
   ```text
   This breaks the rules set for app (pattern-web/replicas-limit/vet-cel). The value is in the hub, and it will not be released or reach the service until it is fixed.
   ```

6. The machine that runs staging keeps what it has: `cub mini pull`, which writes a copy's settings into the service's folder, refuses:
   <!-- run: pull-refused -->
   ```sh
   cub mini pull notes --variant staging --dir ~/walkthrough/service || true
   ```
   ```text
   cub mini: notes-staging/app breaks the rules set for it (pattern-web/replicas-limit/vet-cel), so nothing was written and the service keeps what it has; fix the value in the hub
   ```

7. The agent asks Ana, who settles on 3. The next pull writes it:
   <!-- run: fix -->
   ```sh
   cub --context bot mini set notes REPLICAS=3 --variant staging --change-desc "Three for the launch, within the team's limit" >/dev/null
   cub mini pull notes --variant staging --dir ~/walkthrough/service
   grep REPLICAS service/app.env
   ```
   ```text
   app.env                  written: revision 4: Three for the launch, within the team's limit| Functions: set-string-path
   REPLICAS=3
   ```

8. Ana's second app, a blog, starts like the first. It is made from the notes app, keeps its own values, and takes what notes changes next:
   <!-- run: second-app -->
   ```sh
   mkdir blog && printf 'PORT=3001\nRELEASE=blog-1.0.0\n' > blog/.env
   cub mini adopt blog --pattern notes | sed -n 3,5p
   ```
   ```text
     Your settings that differ from the defaults in notes-base/app: PORT=3001, RELEASE=blog-1.0.0. A new version of those defaults will not overwrite them.
     Defaults from notes-base/app, for settings blog does not set: LOG_LEVEL=info, PUBLIC=false, REPLICAS=2.
     When notes's settings change, blog can take the change and keep its own values: cub mini upgrade notes-base/app --change-desc WHY
   ```

### Undo it

`cub mini uninstall --name ana --delete-data` removes the hub and everything in it; then delete `~/walkthrough` and `~/.confighub-walkthrough`.

### What you have now

Two apps on the team's pattern, each with staging and a production copy that changes only with Ana's approval; rules that kept a value over the limit from ever reaching a service; and a second app made from the first.

The full story asks for all of this in one request to an agent, which can also run in a sandbox of its own, and lets a reviewer read why the agent chose each value (`/confighub:why` in Claude Code). [A new app](../../docs/journeys/new-app.md) shows the one-request version with the plugin.

## Agent

For an AI agent doing this for a person.

- The request: "Build me a small notes API, with its settings in an env file, that fits the team's pattern, pattern-web, with a staging and a live copy."
- Write the app and its `.env` in `notes/`, then `cub mini adopt notes`. It makes the base, staging and live copies on `pattern-web`, with live behind the person's approval.
- When `cub mini set` or `cub mini upload` says a value breaks a rule, tell the person which rule and ask whether to change the value or have the rule's owner change the limit. Do not work around the rule.
- Never approve production's starting values yourself; end with the command for the person: `cub mini approve notes-base/adopt`.
- Done when `cub mini receipts notes --setup` names the three copies and the approval for live.

## Testing

This proves: the settings were stored in the hub on the team's pattern, and a value that breaks a rule was refused by `cub mini pull` while a valid one was written to a local folder. What was really used: confighub mini on this computer; no service runs.

A correct agent result has the notes app on `pattern-web`, with staging and a live copy behind approval. The checks below hold right after step 3. The checks below can be run by hand, in bash, in the walkthrough's folder:

<!-- agent-task: adopt after=adopt -->
> Build me a small notes API, with its settings in an env file, that fits the team's pattern, pattern-web, with a staging and a live copy.

<!-- agent-check adopt: test "$(cub unit get app --space notes-base -o jq=.Unit.UpstreamUnitID)" = "$(cub unit get web-service --space pattern-web -o jq=.Unit.UnitID)" && cub space get notes-staging >/dev/null && cub changeworkflow get --space workflows notes-live-approval >/dev/null -->
<!-- agent-check-a adopt: find ~/walkthrough/notes -name .git -prune -o -print | grep -qi staging && find ~/walkthrough/notes -name .git -prune -o -print | grep -qiE 'live|prod' -->
<!-- arms: a,b,c -->

```sh
test "$(cub unit get app --space notes-base -o jq=.Unit.UpstreamUnitID)" = "$(cub unit get web-service --space pattern-web -o jq=.Unit.UnitID)" && cub space get notes-staging >/dev/null && cub changeworkflow get --space workflows notes-live-approval >/dev/null
find ~/walkthrough/notes -name .git -prune -o -print | grep -qi staging && find ~/walkthrough/notes -name .git -prune -o -print | grep -qiE 'live|prod'
```
