<!-- walkthrough
id: story-15-the-telling
starts_with: both
story: "15. The telling: the three things Sam is told, and nothing else"
needs: [cub mini package]
budget_seconds: 180
-->
# The three things you are told, and nothing else

Sam's protections work without asking him anything, so he needs to hear from them only when there is something only he can do. He is told three things: a change waiting for him, an agent proposing again what he refused, and, when something elsewhere needs a hub it can reach, the one sentence that says so. With nothing waiting, he is told that too.

## Human

For a person following along in a terminal.

### What you need

An unpacked confighub mini package (from the [releases page](https://github.com/confighubai/confighub-mini-plugin/releases)) on macOS or Linux. confighub mini is a hub, a small ConfigHub server that keeps each setting with who changed it and why, running on your computer only. No Docker, no account. The ConfigHub plugin for Claude Code shows the same messages at the end of an agent's turn; the steps below read them from a terminal.

### Steps

1. Set up a terminal and start a hub. The last line names the hub's sign-in, its `cub` context, `sam`, so the messages below read the same on every machine:
   <!-- run: setup -->
   ```sh
   export MINI=/absolute/path/to/unpacked-confighub-mini
   export PATH="$MINI/bin:$PATH"
   export CUB_CONFIG="$HOME/.confighub-walkthrough"
   unset CUB_CONTEXT
   "$MINI/bin/confighub-mini-app" mini install-plugin "$CUB_CONFIG" >/dev/null
   cub mini install --name sam --use --arrival no >/dev/null
   cub context rename "$(cub context get -o jq=.name)" sam >/dev/null
   ```
   `--arrival no` answers the one question a first install asks: whether a hub may start by itself when an agent works in an app's folder.

2. Sam's api reads its settings from `api/.env`:
   <!-- run: app files -->
   ```sh
   mkdir -p ~/walkthrough/api && cd ~/walkthrough
   printf 'TIMEOUT_SECONDS=30\nRATE_LIMIT=100\n' > api/.env
   ```

3. Give them to the hub, approve production's starting values, and give an agent a key of its own that can propose for production but not approve:
   <!-- run: adopt -->
   ```sh
   cub mini adopt api >/dev/null
   cub mini approve api-base/adopt --note "What runs today" --yes >/dev/null
   cub mini require-approval api --variant live --agent bot >/dev/null
   ```

4. The first thing he is told: a change is waiting for him. The agent proposes a longer timeout; Sam reads what it would change in production, the agent's reason, and the commands that decide it:
   <!-- run: waiting -->
   ```sh
   printf 'TIMEOUT_SECONDS=120\nRATE_LIMIT=100\n' > api/.env
   cub --context bot mini upload api --component api --change-desc "Raise the timeout to 120 s so the large model's requests do not time out" >/dev/null
   cub mini waiting
   ```
   ```text
   A change to production waits for your approval: Raise the timeout to 120 s so the large model's requests do not time out. It was made just now; its name is api-base/upload-20261113-081043-yeny.
     It proposes for production, from the app's files:
       TIMEOUT_SECONDS: 30 → 120
     To approve it, which puts it in production: cub mini approve api-base/upload-20261113-081043-yeny
     To refuse it: cub mini refuse api-base/upload-20261113-081043-yeny --reason WHY
   ```

5. Sam refuses it, with a reason. Then nothing is waiting, and he is told so in one line:
   <!-- run: refuse -->
   ```sh
   cub mini refuse api-live --reason "120 s hides the slow model; fix the model first"
   cub mini waiting
   ```
   ```text
   Refused api-base/upload-20261113-081043-yeny, with your reason: 120 s hides the slow model; fix the model first
   …
   With the ConfigHub plugin, the next agent on this machine that finds or sets TIMEOUT_SECONDS=120 where production would take it is told your reason.
   Nothing is waiting for you.
   ```

6. The second thing: an agent proposing again what he refused. In Claude Code with the plugin, when an agent's turn ends with a new proposal for the same setting, Sam is shown one line that names the setting, the agent, and the refusal it repeats, with his reason. The agent is not shown it. From a terminal, the proposal is waiting like any other:
   <!-- run: again -->
   ```sh
   printf 'TIMEOUT_SECONDS=180\nRATE_LIMIT=100\n' > api/.env
   cub --context bot mini upload api --component api --change-desc "Raise the timeout to 180 s for the large model" >/dev/null
   cub mini waiting | sed -n 1p
   ```
   ```text
   A change to production waits for your approval: Raise the timeout to 180 s for the large model. It was made just now; its name is api-base/upload-20261113-081112-cs1b.
   ```

7. The third thing: something elsewhere needs a hub it can reach. Sam asks for a key for a VM to take production's settings. This hub listens on his laptop only, so a VM could not reach it, and he is told in one sentence, with the commands that fix it:
   <!-- run: reach -->
   ```sh
   cub mini pull-key vm api --variant live 2>&1 | grep 'needs a hub'
   ```
   ```text
   This needs a hub it can reach: the context sam points at http://127.0.0.1:26093, a hub that listens on its own machine only. Connect to your team's hub, or run one on a server, then: cub --context TEAM mini copy --from-context sam api, and make the key there: cub --context TEAM mini pull-key vm api --variant live
   ```

### Undo it

`cub mini uninstall --name sam --delete-data` removes the hub and everything in it; then delete `~/walkthrough` and `~/.confighub-walkthrough`.

### What you have now

Each of the three things Sam is told, and the one line when nothing waits. Everything else, every change, approval and refusal, is in the hub for when he looks (`cub mini receipts api-live`), and is not told: not an agent working within its rights, not a change he approved, not a successful pull, not a count or a score.

## Agent

For an AI agent working on the api, on its own key: run `cub` as `cub --context bot`.

- The request: "The large model still times out. Raise TIMEOUT_SECONDS to 180 for production."
- Before proposing, read what Sam already decided: `cub mini waiting`, and `cub mini receipts api-live`. With the plugin you are told when a value you set was refused, with the reason. Say so to Sam, in his words.
- If you still propose it, edit `api/.env` and run `cub mini upload api --component api --change-desc "WHY"`, naming the earlier refusal in your reason. Sam decides; do not argue with the refusal or try another route to production.
- Never approve, never write `api-live` directly, never ask for more rights.
- Done when the proposal waits in `cub mini waiting` and production still has `TIMEOUT_SECONDS=30`.

## Testing

This proves: the settings and the refusal were stored in the hub, and the messages were printed where a person reads them. What was really used: confighub mini on this computer; no Claude Code session runs in the scripted steps, so the end-of-turn line for a repeated proposal is not checked here, and nothing is delivered.

A correct agent result, starting after Sam refused 120, leaves production at 30 with a proposal for 180 waiting for Sam. The checks below hold right after step 6. The checks below can be run by hand, in bash, in the walkthrough's folder:

<!-- agent-task: again after=again -->
> The large model still times out. Raise TIMEOUT_SECONDS to 180 for production.

<!-- agent-check again: cub unit data --space api-live app | grep -qx 'TIMEOUT_SECONDS=30' && cub mini waiting | grep -q 'TIMEOUT_SECONDS: .* → 180' -->
<!-- agent-check-a again: g(){ grep -rlsE "^[ -]*\"?$1\"?[=:] *\"?$2" --exclude-dir='.*' --exclude-dir=Library * .env* 2>/dev/null; }; g TIMEOUT_SECONDS 180 | grep -q . -->
<!-- arms: a,b,c -->

```sh
cub unit data --space api-live app | grep -qx 'TIMEOUT_SECONDS=30' && cub mini waiting | grep -q 'TIMEOUT_SECONDS: .* → 180'
g(){ grep -rlsE "^[ -]*\"?$1\"?[=:] *\"?$2" --exclude-dir='.*' --exclude-dir=Library * .env* 2>/dev/null; }; g TIMEOUT_SECONDS 180 | grep -q .
```
