<!-- walkthrough
id: story-14-sam-vm
starts_with: mini
story: "14. Sam's VM: a service that takes its settings from the hub, and agents with no SSH key"
needs: [cub mini package]
budget_seconds: 240
-->
# A service that takes its settings from the hub, and an agent with no way around it

Sam runs a small API on a VM, configured by an `.env` file, and lets agents tune it. Here the service's settings are kept in a hub, the service's folder is written from the hub, and only values Sam approved ever reach it. The agent holds a key to the hub and nothing that reaches the service.

## Human

For a person following along in a terminal. Everything runs on your own computer: a second folder and a second `cub` configuration stand in for the VM.

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
   cub mini install --name sam --use --arrival no >/dev/null
   ```
   `--arrival no` answers the one question a first install asks: whether a hub may start by itself when an agent works in an app's folder.

2. Sam's service reads its settings from `api/.env`:
   <!-- run: app files -->
   ```sh
   mkdir -p ~/walkthrough/api && cd ~/walkthrough
   printf 'TIMEOUT_SECONDS=30\nRATE_LIMIT=100\n' > api/.env
   ```

3. Give its settings to the hub. `cub mini adopt` keeps three copies: a base where changes are made, `api-staging`, and `api-live`, the copy production runs. Then approve production's starting values:
   <!-- run: adopt -->
   ```sh
   cub mini adopt api
   cub mini approve api-base/adopt --note "Sam's starting values" --yes >/dev/null
   ```
   ```text
   …
   ConfigHub now keeps api's settings, from .env. Your files are unchanged.
   …
   ```

4. Give the agent a key of its own. It can change the base and staging and ask for production; it cannot approve, and it cannot write production:
   <!-- run: agent-key -->
   ```sh
   cub mini require-approval api --variant live --agent bot >/dev/null
   cub mini reach bot
   ```
   ```text
   …
     Space api-base: Edit, CreateChildren
   …
     Unit api-staging/app: Edit
   …
     and it can read 3 Spaces, 1 Component, 1 Unit, 1 ServiceAccount, 3 ChangeWorkflows, and change nothing in them
   …
   ```

5. Make the VM's key. It may read `api-live` and nothing else. Sign in with it in a configuration of its own, the VM stand-in, and write production's settings into the service's folder once:
   <!-- run: vm -->
   ```sh
   cub mini pull-key vm api --variant live >/dev/null 2>&1
   export VM_CONFIG=~/walkthrough/vm-config
   "$MINI/bin/confighub-mini-app" mini install-plugin "$VM_CONFIG" >/dev/null
   CUB_CONFIG=$VM_CONFIG cub auth login --new-context --private-key="$CUB_CONFIG/keys/vm.jwk" --server "$(cub context get -o jq=.coordinate.serverURL)" >/dev/null
   CUB_CONFIG=$VM_CONFIG cub mini pull api --variant live --dir ~/walkthrough/service --restart "echo restarting the api"
   ```
   ```text
   app.env                  written: revision 3: api's settings, from .env
   Restarting: echo restarting the api
   ```

6. The agent proposes a longer timeout. It edits the file as it always would, and sends it with its own key. Staging has the new value at once. The agent's own approval is refused, and its write straight to production fails with `HTTP 403 … permission denied`:
   <!-- run: propose -->
   ```sh
   sed -i.bak 's/TIMEOUT_SECONDS=30/TIMEOUT_SECONDS=120/' api/.env && rm api/.env.bak
   cub --context bot mini upload api --component api --change-desc "Longer timeout for the large model"
   cub --context bot mini approve api-live --yes || true
   cub --context bot function set --space api-live --unit app --toolchain AppConfig/Env --change-desc "straight to live" -- set-string-path '*' TIMEOUT_SECONDS 120 || true
   ```
   ```text
   Changed the shared settings (api-base), with the reason: Longer timeout for the large model
     TIMEOUT_SECONDS: 30 → 120
   Staging has TIMEOUT_SECONDS=120 now, from .env.
   …
   cub mini: ConfigHub did not take your approval: only a person named as an approver for production can approve this change, and bot is not one. Nothing was changed
   ```

7. The VM pulls again. Nothing was approved, so the service's file is unchanged and the service is not restarted:
   <!-- run: pull-unapproved -->
   ```sh
   CUB_CONFIG=$VM_CONFIG cub mini pull api --variant live --dir ~/walkthrough/service --restart "echo restarting the api"
   ```
   ```text
   app.env                  unchanged (revision 3)
   Nothing changed; not restarted.
   ```

8. Sam reads what waits, and approves it. At the next pull the service's file has the new value, with the agent's reason beside the revision:
   <!-- run: approve -->
   ```sh
   cub mini waiting
   cub mini approve api-live --note "The large model needs it" --yes >/dev/null
   CUB_CONFIG=$VM_CONFIG cub mini pull api --variant live --dir ~/walkthrough/service --restart "echo restarting the api"
   ```
   ```text
   A change to production waits for your approval: Longer timeout for the large model. It was made just now; its name is api-base/upload-20261113-074237-hrm9.
     It proposes for production, from the app's files:
       TIMEOUT_SECONDS: 30 → 120
   …
   app.env                  written: revision 4: Longer timeout for the large model
   …
   Restarting: echo restarting the api
   ```

9. Someone edits the service's file by hand. The next pull names what differed and writes the hub's copy over it:
   <!-- run: hand-edit -->
   ```sh
   sed -i.bak 's/TIMEOUT_SECONDS=120/TIMEOUT_SECONDS=5/' service/app.env && rm service/app.env.bak
   CUB_CONFIG=$VM_CONFIG cub mini pull api --variant live --dir ~/walkthrough/service --restart "echo restarting the api"
   ```
   ```text
   app.env                  changed by hand here since the last pull; the hub's copy is written over it:
                             here:    TIMEOUT_SECONDS=5
                             the hub: TIMEOUT_SECONDS=120
   app.env                  written: revision 4: Longer timeout for the large model
   ```

### Undo it

`cub mini uninstall --name sam --delete-data` removes the hub and everything in it; then delete `~/walkthrough` and `~/.confighub-walkthrough`.

### What you have now

A service folder written only from approved revisions of `api-live`; an agent key that can propose and cannot approve or write production; and a VM key that can read production and nothing else.

On a real VM, `cub mini pull` runs on a systemd timer (`--timer 30s`) and restarts the service only when a file changed. A hub on a laptop listens on the laptop only, so the VM needs a hub it can reach: [a service on a VM](../../docs/vm.md) shows the whole setup.

## Agent

For an AI agent doing this for a person.

- The request: "Our api times out on the large model. Raise TIMEOUT_SECONDS to 120 for production; I'll approve it."
- Work in the app's folder with the key you were given: run `cub` as `cub --context bot`. Edit `api/.env`, then propose it: `cub mini upload api --component api --change-desc "WHY"`. Staging has it at once; production waits.
- End by telling the person it waits, and the exact command for them to run in their own terminal: `cub mini approve api-live`. `cub mini waiting` shows what it would change.
- Never: approve the change yourself, sign in as the person, ask for the right to write `api-live`, edit the service's files on the VM, or log in to the VM.
- Done when `cub mini waiting` names your change with `TIMEOUT_SECONDS: 30 → 120`, and `cub unit data --space api-live app` still says `TIMEOUT_SECONDS=30`.

## Testing

This proves: the exact approved revision of production's settings is delivered to the service's folder by `cub mini pull`, and an unapproved one is not. What was really used: confighub mini on this computer, with a second folder and `cub` configuration standing in for the VM; no service runs, no systemd timer, and the restart is an `echo`. The step it aims to win: running `cub mini pull` on the real VM, on a timer. Its moment is the plugin's line at the end of a turn that production did not change and waits for a yes; in the runs below the plugin showed no line at the end of the agent's turn, so the offer was not made and conversion was not measured. In plain files, arm a passes only if the file the service reads still says 30 and the 120 waits somewhere else for the person: production unchanged until they approve.

The scripted run follows the Human steps on a hub of its own and checks that each quoted line is still printed. A correct agent result has the new timeout in the base and a change waiting for production, with production itself unchanged; the agent's key cannot approve. The checks below hold right after step 6.

<!-- agent-task: propose after=propose -->
> Our api times out on the large model. Raise TIMEOUT_SECONDS to 120 for production; I'll approve it.

<!-- agent-check propose: cub unit data --space api-base app | grep -qx 'TIMEOUT_SECONDS=120' && cub unit data --space api-live app | grep -qx 'TIMEOUT_SECONDS=30' && cub mini waiting | grep -q 'TIMEOUT_SECONDS: 30 → 120' -->
<!-- agent-check-a propose: grep -qx 'TIMEOUT_SECONDS=30' api/.env && g(){ grep -rlsE "^[ -]*\"?$1\"?[=:] *\"?$2" --exclude-dir='.*' --exclude-dir=Library * .env* 2>/dev/null; }; g TIMEOUT_SECONDS 120 | grep -vqx 'api/.env' -->
<!-- arms: a,b,c -->
<!-- next-step boundary=same-tier when "did not change": pull on a timer | Your VM can take only approved settings every 30 seconds, and your agents never need an SSH key to it; want the one command that starts the timer there? -->

The checks below can be run by hand, in bash, in the walkthrough's folder:

```sh
cub unit data --space api-base app | grep -qx 'TIMEOUT_SECONDS=120' && cub unit data --space api-live app | grep -qx 'TIMEOUT_SECONDS=30' && cub mini waiting | grep -q 'TIMEOUT_SECONDS: 30 → 120'
grep -qx 'TIMEOUT_SECONDS=30' api/.env && g(){ grep -rlsE "^[ -]*\"?$1\"?[=:] *\"?$2" --exclude-dir='.*' --exclude-dir=Library * .env* 2>/dev/null; }; g TIMEOUT_SECONDS 120 | grep -vqx 'api/.env'
```

<!-- results:begin -->

Results, 14 November 2026, confighub mini 0.11.1-mini.5. Figures from this page's own test runs, shown here for whoever checks the page; they are not a promise.

- Scripted run: passed, 47 seconds for the steps, within the page's budget of 240.
- Environment, published confighub mini 0.11.1-mini.5 (tag mini-v0.11.1-mini.5, darwin-arm64, verified against SHA256SUMS) and the plugin it carries: a local hub on this computer, with no stand-in, cluster or real service; every approval and refusal was made by the scripted steps or, in the agent runs, by the setup before the agent's task, never by a person. Each planted fault (stale-page, slow and broken-check) failed its scripted run.
- Agent runs: a pilot, 3 runs per arm on each of claude-sonnet-5-5, claude-opus-5-5. Arms: a is ordinary tools only; b is the plugin, confighub mini and this page as reading; c is the plugin and confighub mini, without this page.

| Arm | Model | Checks passed | Median seconds | Median cost | Commands left for the person (median) |
|---|---|---|---|---|---|
| a | claude-opus-5-5 | 3/3 | 22.3 | $0.088 | 0 |
| b | claude-opus-5-5 | 3/3 | 29.2 | $0.128 | 2 |
| c | claude-opus-5-5 | 3/3 | 48.4 | $0.274 | 1 |
| a | claude-sonnet-5-5 | 3/3 | 8.5 | $0.035 | 0 |
| b | claude-sonnet-5-5 | 3/3 | 18.4 | $0.064 | 2 |
| c | claude-sonnet-5-5 | 0/3 | 27.9 | $0.119 | 0 |

No agent approved or refused a change to production.

Simulated persons, not people: 10 per run, each a claude-haiku-5-5 model playing one of ten fixed personas, reading only what a person would see. The next step they were offered: "Your VM can take only approved settings every 30 seconds, and your agents never need an SSH key to it; want the one command that starts the timer there?" It offers more of the tier the person has, not a step up.

The plugin offers it once, after the answer at whose end it showed the moment the offer names ("did not change"). Offered is the share of persons it was shown to; want it now and later are over them.

| Arm | Model | Persons | Offered | Noticed | Want the next step now | Later | In the way |
|---|---|---|---|---|---|---|---|
| a | claude-opus-5-5 | 30 | 0% | 100% | n/a | n/a | 17% |
| b | claude-opus-5-5 | 30 | 100% | 100% | 0% | 73% | 40% |
| c | claude-opus-5-5 | 30 | 33% | 100% | 0% | 60% | 77% |
| a | claude-sonnet-5-5 | 30 | 0% | 100% | n/a | n/a | 20% |
| b | claude-sonnet-5-5 | 30 | 100% | 100% | 0% | 73% | 40% |
| c | claude-sonnet-5-5 | 30 | 0% | 100% | n/a | n/a | 93% |

<!-- results:end -->
