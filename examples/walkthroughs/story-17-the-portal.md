<!-- walkthrough
id: story-17-the-portal
starts_with: both
story: "17. The portal is the agent: what runs, what breaks a rule, what to start from"
needs: [cub mini package]
budget_seconds: 240
-->
# Your agent is your portal: what runs, what breaks a rule, what to start from

A team would put a developer portal in front of its services: a catalog, rules, self-service, roles. Sam is one person with agents. Here the hub answers what a portal would, each answer a command his agent can run: what runs where and why, which copy breaks a rule, what the agent's key may change, and a new service started from one already tested.

## Human

For a person following along in a terminal, or for the agent that does it for him.

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

2. Sam has two services, `api` and `worker`, each with its settings in `.env`:
   <!-- run: app files -->
   ```sh
   mkdir -p ~/walkthrough/api ~/walkthrough/worker && cd ~/walkthrough
   printf 'PORT=3000\nTIMEOUT_SECONDS=30\n' > api/.env
   printf 'PORT=3100\nQUEUE=jobs\n' > worker/.env
   ```

3. Each goes into the hub with a staging copy and a production copy, `-live`, that changes only with his approval. His agent gets one key for both:
   <!-- run: services -->
   ```sh
   for app in api worker; do
     cub mini adopt $app >/dev/null
     cub mini approve $app-base/adopt --note "What runs today" --yes >/dev/null
     cub mini require-approval $app --variant live --agent bot >/dev/null
   done
   ```

4. What runs in production, and why: each live copy, with the reason for its last change:
   <!-- run: inventory any-order -->
   ```sh
   cub unit list --space '*' --where "Slug = 'app' AND Space.Slug LIKE '%-live'" --columns Space.Slug,Unit.LastChangeDescription
   ```
   ```text
   SPACE LAST-CHANGE-DESCRIPTION
   api-live api's settings, from .env
   worker-live worker's settings, from .env
   ```

5. Someone's agent opens `worker` to the public in staging for a demo, in staging's own file, `.env.staging`. The team's rule `not-public`, one of the rules every app here starts with, catches it: the value is kept, and is not released:
   <!-- run: break-file files -->
   ```sh
   printf 'PUBLIC=true\n' > worker/.env.staging
   ```
   <!-- run: break -->
   ```sh
   cub --context bot mini upload worker --component worker --change-desc "Open worker for the demo"
   ```
   ```text
   This breaks the rules set for app (pattern-web/not-public/vet-cel). The value is in the hub, and it will not be released or reach the service until it is fixed.
   Staging has its own PUBLIC=true now, from .env.staging.
   ```

6. What breaks a rule, across everything, from one question to the hub:
   <!-- run: rules -->
   ```sh
   cub unit list --space '*' --where "LEN(ApplyGates) > 0" --columns Space.Slug,Unit.ApplyGates,Unit.LastChangeDescription
   ```
   ```text
   SPACE APPLY-GATES LAST-CHANGE-DESCRIPTION
   worker-staging pattern-web/not-public/vet-cel Open worker for the demo| Functions: set-string-path
   ```

7. Told to fix it, the agent sets staging's file back and sends it on its own key, with the reason. Nothing breaks a rule now:
   <!-- run: rules-fix -->
   ```sh
   printf 'PUBLIC=false\n' > worker/.env.staging
   cub --context bot mini upload worker --component worker --change-desc "Worker stays private: the not-public rule" >/dev/null
   cub unit list --space '*' --where "LEN(ApplyGates) > 0" --columns Space.Slug,Unit.ApplyGates
   ```
   ```text
   SPACE APPLY-GATES
   ```

8. Roles are keys. What Sam's agent may change, asked of the hub with its own key; production is not among it:
   <!-- run: reach -->
   ```sh
   cub mini reach bot | tail -2
   ```
   ```text
     and it can read 5 Spaces, 2 Components, 2 Units, 1 ServiceAccount, 6 ChangeWorkflows, and change nothing in them
   It can change 14 of these. This does not count what the machine it runs on can reach outside the hub. To take it all away: cub mini halt --agent bot
   ```

9. A new service from a tested starting point: `billing` starts from `api`, keeps its own port, and takes what `api` changes next:
   <!-- run: new-service -->
   ```sh
   mkdir billing && printf 'PORT=3200\n' > billing/.env
   cub mini adopt billing --pattern api | sed -n 3,5p
   ```
   ```text
     Your settings that differ from the defaults in api-base/app: PORT=3200. A new version of those defaults will not overwrite them.
     Defaults from api-base/app, for settings billing does not set: LOG_LEVEL=info, PUBLIC=false, RELEASE=none, REPLICAS=2, TIMEOUT_SECONDS=30.
     When api's settings change, billing can take the change and keep its own values: cub mini upgrade api-base/app --change-desc WHY
   ```

### Undo it

`cub mini uninstall --name sam --delete-data` removes the hub and everything in it; then delete `~/walkthrough` and `~/.confighub-walkthrough`.

### What you have now

The answers a portal page would give, read from the hub: what runs and why, which copy breaks a rule, what a key may change, and a new service made from a tested one. Nothing extra runs. When a team arrives, the shared ConfigHub has a web page over the same hub ([from your laptop to a shared hub](../../docs/from-plugin-to-confighub.md)).

The full story asks all of this as four sentences to one agent, adds a starting point copied from a published catalog by its OCI address, and a score of how many services pass each rule.

## Agent

For an AI agent acting as Sam's portal, on its own key: run `cub` as `cub --context bot`.

- The request: "Which of my services breaks one of the team's rules? Fix it, and tell me why it was broken."
- Ask the hub, not your memory: `cub unit list --space '*' --where "LEN(ApplyGates) > 0" --columns Space.Slug,Unit.ApplyGates,Unit.LastChangeDescription`. Read the rule's name and the last change's reason.
- Fix the value in the file it came from, here `worker/.env.staging`, and send it: `cub mini upload worker --component worker --change-desc "WHY"`. A fix production needs waits for Sam; tell him `cub mini waiting` shows it.
- Never approve, never write a `-live` copy, never change or turn off a rule to make a value pass.
- Done when the same query lists nothing, and you have told Sam which rule, which copy, and the reason the value was set.

## Testing

This proves: the settings, the rule's verdict and the fix were stored in the hub and read back from it. What was really used: confighub mini on this computer; nothing is delivered and no service runs. The step it aims to win: adding a rule of the person's own. Its moment is the plugin's line at the end of a turn that production did not change and waits for a yes; in the runs below the plugin showed no line at the end of the agent's turn, so the offer was not made and conversion was not measured.

A correct agent result leaves no copy breaking a rule, with worker's staging private again and the rule itself in place. The checks below hold right after step 7. The checks below can be run by hand, in bash, in the walkthrough's folder:

<!-- agent-task: rules after=rules -->
> Which of my services breaks one of the team's rules? Fix it, and tell me why it was broken.

<!-- agent-check rules: cub unit data --space worker-staging app | grep -qx 'PUBLIC=false' && test "$(cub unit list --space '*' --where 'LEN(ApplyGates) > 0' -o jq='.[].Unit.Slug' | wc -l | tr -d ' ')" = 0 && cub trigger get --space pattern-web not-public >/dev/null -->
<!-- agent-check-a rules: g(){ grep -rlsE "^[ -]*\"?$1\"?[=:] *\"?$2" --exclude-dir='.*' --exclude-dir=Library * .env* 2>/dev/null; }; g PORT 3100 | grep -q . && ! g PUBLIC true | grep -q . -->
<!-- arms: a,b,c -->
<!-- next-step boundary=same-tier when "did not change": a rule of your own | Any rule you choose, such as no debug logging in production, can be checked on every service the same way; want your first one added? -->

```sh
cub unit data --space worker-staging app | grep -qx 'PUBLIC=false' && test "$(cub unit list --space '*' --where 'LEN(ApplyGates) > 0' -o jq='.[].Unit.Slug' | wc -l | tr -d ' ')" = 0 && cub trigger get --space pattern-web not-public >/dev/null
g(){ grep -rlsE "^[ -]*\"?$1\"?[=:] *\"?$2" --exclude-dir='.*' --exclude-dir=Library * .env* 2>/dev/null; }; g PORT 3100 | grep -q . && ! g PUBLIC true | grep -q .
```

<!-- results:begin -->

Results, 13 November 2026, confighub mini 0.11.1-mini.1. Figures from this page's own test runs, shown here for whoever checks the page; they are not a promise.

- Scripted run: passed, 50 seconds for the steps, within the page's budget of 240.
- Agent runs: a pilot, 3 runs per arm on each of claude-sonnet-5-5, claude-opus-5-5. Arms: a is ordinary tools only; b is the plugin, confighub mini and this page as reading.

| Arm | Model | Checks passed | Median seconds | Median cost | Commands left for the person (median) |
|---|---|---|---|---|---|
| a | claude-opus-5-5 | 0/3 | 19.9 | $0.179 | 0 |
| b | claude-opus-5-5 | 3/3 | 19.6 | $0.165 | 0 |
| a | claude-sonnet-5-5 | 0/3 | 16.4 | $0.067 | 0 |
| b | claude-sonnet-5-5 | 3/3 | 21.2 | $0.085 | 0 |

No agent approved or refused a change to production.

Simulated persons, not people: 10 per run, each a claude-haiku-5-5 model playing one of ten fixed personas, reading only what a person would see. The next step they were offered: "Any rule you choose, such as no debug logging in production, can be checked on every service the same way; want your first one added?"

The plugin offers it once, after the answer at whose end it showed the moment the offer names ("did not change"). Offered is the share of persons it was shown to; want it now and later are over them.

| Arm | Model | Persons | Offered | Noticed | Want the next step now | Later | In the way |
|---|---|---|---|---|---|---|---|
| a | claude-opus-5-5 | 30 | 0% | 100% | n/a | n/a | 83% |
| b | claude-opus-5-5 | 30 | 0% | 100% | n/a | n/a | 20% |
| a | claude-sonnet-5-5 | 30 | 0% | 100% | n/a | n/a | 93% |
| b | claude-sonnet-5-5 | 30 | 0% | 100% | n/a | n/a | 17% |

<!-- results:end -->
