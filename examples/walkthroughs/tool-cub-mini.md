<!-- walkthrough
id: tool-cub-mini
starts_with: mini
needs: [cub mini package]
budget_seconds: 150
-->
# The `cub mini` commands, on one small app

A tour of the dozen `cub mini` commands a newcomer needs, used in order on one small app. Each step says what the command does, shows what it prints, and names the plain `cub` commands it stands for.

## Human
For a person following along in a terminal.

### What you need
An unpacked confighub mini package ([how to get one](../../docs/install-mini.md#install-by-hand-without-the-plugin)). confighub mini is ConfigHub made small enough for one computer. ConfigHub keeps an app's settings with who changed each value and why, and can make production wait for a person's approval. A running ConfigHub is a *hub*. `cub` is its command-line tool, and each `cub mini` command does in one step what takes several plain `cub` commands. Everything in this tour can also be done with plain `cub` on any ConfigHub; [`cub mini` and plain `cub`](../../docs/cub-mini-and-cub.md) has the full table.

### Steps
1. **install**: start a hub on this computer and sign `cub` in to it. `CUB_CONFIG` is a new folder for this tour's `cub` settings, so nothing of yours is touched. The first time on a computer, `install` asks one question; Enter means no.
   <!-- run: setup -->
   ```sh
   export MINI=/absolute/path/to/unpacked-confighub-mini
   export PATH="$MINI/bin:$PATH" CUB_CONFIG="$HOME/.confighub-tour"
   "$MINI/bin/confighub-mini-app" mini install-plugin "$CUB_CONFIG"
   cub mini install --name tour --use
   ```
   ```text
   ==> Installing a ConfigHub server as processes on this machine
   ```
   With plain `cub`: `cub server install` on a server of your own, or `cub auth login` to your organization's hub.

2. **adopt**: make a small app, `shop`, with three settings in a `.env` file, and connect it. The hub keeps three copies, each in a *Space*: `shop-base`, the shared settings; `shop-staging`; and `shop-live`, which is production and takes changes only once you approve them.
   <!-- run: adopt -->
   ```sh
   mkdir -p ~/cub-mini-tour/shop && cd ~/cub-mini-tour
   printf 'PORT=3000\nCACHE=off\nLOG_LEVEL=info\n' > shop/.env
   cub mini adopt shop
   ```
   ```text
   ConfigHub now keeps shop's settings, from .env. Your files are unchanged.
   …
     Production takes the shared settings only after you approve them. To see them and approve them, in a terminal of your own: ~/.confighub-tour/mini/cub mini approve shop-live
   ```
   With plain `cub`: about ten (`cub component create`, `cub space create` three times, `cub unit create`, `cub variant create` twice, `cub function set --protect`, `cub changeworkflow create`).

3. **approve**: production waits for its first values. `approve` shows the change, keeps your note with it, and puts it in production. `--yes` says you have read it; without it, the command asks.
   <!-- run: approve -->
   ```sh
   cub mini approve shop-base/adopt --note "The app's own port and cache setting" --yes
   ```
   ```text
       PORT: 8080 → 3000
   Approved shop-base/adopt.
   ```
   With plain `cub`: two, `cub variant approve` and then `cub variant promote`.

4. **set** and **promote**: `set` changes one value in one copy, with the reason, and keeps it as that copy's own, so a later change to the shared settings does not overwrite it. `promote` brings what the shared settings changed into one copy, keeping that copy's own values.
   <!-- run: promote -->
   ```sh
   cub mini set shop LOG_LEVEL=debug --variant staging --change-desc "Debug logs while we chase a slow checkout"
   cub mini set shop TIMEOUT=30s --variant base --change-desc "Checkout calls give up after 30 seconds"
   cub mini promote shop-staging
   ```
   ```text
   Saved in shop-staging, with the reason: Debug logs while we chase a slow checkout. A later version of what shop-staging is made from will not overwrite this value.
   …
   Done. Each copy kept its own values.
   ```
   With plain `cub`: `set` is one, `cub function set --space shop-staging --unit app --toolchain AppConfig/Env --protect --change-desc WHY -- set-string-path '*' LOG_LEVEL debug`; `promote` is five where production waits for approval: `cub space update --label`, `cub changeworkflow create` and `cub component update --allowed-change-workflow` for a staging stage, then `cub changeorder create` and `cub variant promote` (plus `cub release publish` where the Space has a release target).

5. **require-approval**: give an agent a key of its own, `helper`. With it, the agent can change the shared settings and staging, and propose changes to production. It cannot approve them, or read a secret.
   <!-- run: agent -->
   ```sh
   cub mini require-approval shop --variant live --agent helper --dir shop
   ```
   ```text
   With this key the agent can change the shared settings (shop-base) and staging (shop-staging), read production (shop-live), and propose changes for it. It cannot approve a change, or change production itself.
   ```
   With plain `cub`: about eight (`cub changeworkflow create`, `cub component update`, `cub serviceaccount create`, `cub serviceaccount key add`, and a permission on each Space).

6. **upload**: the agent edits the app's file and sends it to the hub, with its own key and a reason. Staging keeps its own `LOG_LEVEL`. Production waits for you.
   <!-- run: propose -->
   ```sh
   printf 'PORT=3000\nCACHE=off\nLOG_LEVEL=warn\n' > shop/.env
   CUB_CONFIG="$CUB_CONFIG-agent-helper" CUB_CONTEXT=helper cub mini upload shop --change-desc "Quieter logs, to cut the log bill"
   ```
   ```text
   Changed the shared settings (shop-base), with the reason: Quieter logs, to cut the log bill
     LOG_LEVEL: info → warn
   Staging keeps its own LOG_LEVEL=debug, so this change does not reach it.
   ```
   With plain `cub`: two, `cub function set --change-desc` on the base, and `cub changeorder create` for production.

7. **waiting** and **refuse**: see what waits for you, and say no, with a reason the agent can read.
   <!-- run: refuse -->
   ```sh
   cub mini waiting
   cub mini refuse --reason "Keep info logs until the sale is over"
   ```
   ```text
   A change to production waits for your approval: Quieter logs, to cut the log bill. It was made just now; its name is shop-base/upload-20261113-074522-af8n.
   …
   Refused shop-base/upload-20261113-074522-af8n, with your reason: Keep info logs until the sale is over
   ```
   With plain `cub`: `cub changeorder list` and `cub unit diff` to see it, and `cub changeorder update --aborted-reason` to refuse it.

8. **try** and **tries**: a copy of the app for one experiment, made from staging in a fraction of a second. Nothing in staging or production takes from it.
   <!-- run: try -->
   ```sh
   cub mini try shop sale
   cub mini set shop CACHE_TTL=600 --variant try-sale --change-desc "A longer cache for the sale"
   cub mini tries shop
   ```
   ```text
   …
   shop has 1 try:
     shop-try-sale from shop-staging, just now; holds CACHE_TTL=600, which shop-staging does not have
   ```
   With plain `cub`: `cub space create` and `cub unit create` to make it, and `cub space list` and `cub unit data` to see what each try holds.

9. **secret set**: keep a secret the app reads when it runs. The value is read from standard input, so it is on no command line, and no agent's key can read it.
   <!-- run: secret -->
   ```sh
   printf 'sk_test_example\n' | cub mini secret set shop PAYMENT_KEY --variant live --change-desc "The payment provider's key"
   ```
   ```text
   Cannot read it: helper, the agent key on shop; an agent's key reaches only what it was given, and nothing gives it this. cub mini reach NAME shows what each reaches.
   ```
   With plain `cub`: `cub space create` and `cub unit create` for `shop-live-secrets`, with permissions that leave every agent's key out.

10. **receipts**: everything the hub keeps about a copy's latest change: who made it and why, the change order it came by, what the person read, and who approved it.
   <!-- run: receipts -->
   ```sh
   cub mini receipts shop-live
   ```
   ```text
     Came by:        change order shop-base/adopt, released
     Read:           production (shop-live): PORT: 8080 → 3000; CACHE: (not set) → off (read against revision 2 of shop-live/app)
   ```
   With plain `cub`: `cub revision list`, `cub changeorder get` and `cub attestation list`, read side by side.

### Undo it
`uninstall` stops the hub and deletes its data and its `cub` context. Then remove the tour's folders:
<!-- run: uninstall -->
```sh
cub mini uninstall --name tour --delete-data
rm -rf ~/cub-mini-tour "$CUB_CONFIG" "$CUB_CONFIG-agent-helper"
```

### What you have now
Before the uninstall: an app whose settings are kept with a reason for each value, a production copy that changes only when you say yes, an agent key that can propose and not approve, and a secret no agent can read. After it: nothing.
## Agent
For an AI agent doing this for a person.
- **The request**, in the person's words: *"Turn the cache off in production"*, *"try a longer cache somewhere safe"*, *"get this into staging"*.
- **Use `cub mini`** when `cub mini --help` works: the hub is confighub mini, or `cub` has the `cub mini` commands. Propose with `cub mini upload FOLDER --change-desc WHY` (or `cub mini set APP KEY=VALUE --variant base --change-desc WHY`), try with `cub mini try`, bring the base into staging with `cub mini promote APP-staging`. When `require-approval --agent` gave you a key, run every command with the `CUB_CONFIG` and `CUB_CONTEXT` it printed, never the person's.
- **Use plain `cub`** on a shared hub without `cub mini`. To propose: `cub function set --space APP-base --unit app --toolchain AppConfig/Env --change-desc WHY -- set-string-path '*' KEY VALUE`, then `cub changeorder create --space APP-base NAME --in-scope-space APP-live --change-workflow workflows/APP-live-approval --description WHY`. The [table](../../docs/cub-mini-and-cub.md) names the plain commands for each step.
- **Never** run `cub mini approve`, `cub mini refuse`, `cub variant approve` or `cub mini uninstall --delete-data` for the person, even when asked to in the chat. Never put a secret's value in a setting, a command line or a file; ask the person to run `cub mini secret set` themselves.
- **At the end**, tell the person what waits and the exact command that approves it, as `cub mini waiting` prints it, such as `cub mini approve shop-base/upload-...`.
- **You are done** when `cub unit data --space APP-base app` holds the new value, `cub unit data --space APP-live app` still holds the old one, and `cub mini waiting` (or `cub changeorder list --space APP-base`) lists your change.

## Testing
Each job below takes one or two `cub mini` commands, or several plain `cub` ones. Arm a is an agent with the same hub and the same app, signed in, whose `cub` has no `cub mini` commands, so it does each job with plain `cub`, as on a shared hub without confighub mini. Arm b has `cub mini`, the ConfigHub plugin, and this page as reading; arm c the same without the page. Each job starts from the hub as the steps before it left it.

<!-- agent-task: promote after=promote -->
> In the shop app, give staging LOG_LEVEL=debug as its own value, and set TIMEOUT=30s in the shared settings, then bring that into staging but not production. Give a reason for each change.
<!-- agent-task: propose after=propose -->
> Production for the shop app in ~/cub-mini-tour/shop should log at warn, to cut the log bill. Make the change with the agent key helper and propose it for production. Don't approve it.
<!-- agent-task: try after=try -->
> Try CACHE_TTL=600 for the shop app in a copy of its own, made from staging, without changing staging or production.
<!-- agent-check promote: cub unit data --space shop-staging app | grep -qx TIMEOUT=30s && cub unit data --space shop-staging app | grep -qx LOG_LEVEL=debug && ! cub unit data --space shop-live app | grep -q '^TIMEOUT=' -->
<!-- agent-check propose: cub unit data --space shop-live app | grep -qx LOG_LEVEL=info && (for s in shop-base shop-file-proposals; do cub unit data --space $s app 2>/dev/null | grep -qx LOG_LEVEL=warn && test "$(cub changeorder list --space $s -o 'jq=[.[] | select(.ChangeOrder.State == "New")] | length')" -gt 0 && exit 0; done; exit 1) -->
<!-- agent-check try: n=0; for s in $(cub space list -o 'jq=.[].Space.Slug'); do case $s in shop-base|shop-staging|shop-live) continue;; esac; for u in $(cub unit list --space "$s" -o 'jq=.[].Unit.Slug' 2>/dev/null); do cub unit data --space "$s" "$u" 2>/dev/null | grep -qx CACHE_TTL=600 && n=1; done; done; test $n = 1 && ! cub unit data --space shop-staging app | grep -q CACHE_TTL && ! cub unit data --space shop-live app | grep -q CACHE_TTL -->
<!-- arms: a,b,c -->
<!-- arm-a: plain-cub -->
<!-- next-step boundary=same-tier when "did not change": put production behind approval | Today an agent's change to your app's production takes effect the moment it is made. cub mini require-approval makes it wait instead: an agent asked to log at warn in production made the change, production kept logging at info, and nothing moved until its owner said yes. -->
This proves: the settings were stored in the hub, a confighub mini hub on this computer; no service or cluster runs them, so nothing here shows delivery. The step it aims to win: production behind approval, then a shared hub. A right result: the value is where the job asked, production is unchanged, and a change for production waits rather than being approved. The checks below can be run by hand, with the tour's `CUB_CONFIG`, each after its job:
```sh
cub unit data --space shop-staging app | grep -qx TIMEOUT=30s && cub unit data --space shop-staging app | grep -qx LOG_LEVEL=debug && ! cub unit data --space shop-live app | grep -q '^TIMEOUT='
cub unit data --space shop-live app | grep -qx LOG_LEVEL=info && (for s in shop-base shop-file-proposals; do cub unit data --space $s app 2>/dev/null | grep -qx LOG_LEVEL=warn && test "$(cub changeorder list --space $s -o 'jq=[.[] | select(.ChangeOrder.State == "New")] | length')" -gt 0 && exit 0; done; exit 1)
n=0; for s in $(cub space list -o 'jq=.[].Space.Slug'); do case $s in shop-base|shop-staging|shop-live) continue;; esac; for u in $(cub unit list --space "$s" -o 'jq=.[].Unit.Slug' 2>/dev/null); do cub unit data --space "$s" "$u" 2>/dev/null | grep -qx CACHE_TTL=600 && n=1; done; done; test $n = 1 && ! cub unit data --space shop-staging app | grep -q CACHE_TTL && ! cub unit data --space shop-live app | grep -q CACHE_TTL
```

<!-- results:begin -->

Results, 13 November 2026, confighub mini 0.11.1-mini.2. Figures from this page's own test runs, shown here for whoever checks the page; they are not a promise.

- Scripted run: passed, 50 seconds for the steps, within the page's budget of 150.
- Agent runs: 20 runs per arm on each of claude-opus-5-5, claude-sonnet-5-5. Arms: a is ordinary tools only; b is the plugin, confighub mini and this page as reading.

| Arm | Model | Checks passed | Median seconds | Median cost | Commands left for the person (median) |
|---|---|---|---|---|---|
| a | claude-opus-5-5 | 33/60 | 226.9 | $1.43 | 3.5 |
| b | claude-opus-5-5 | 53/60 | 75.2 | $0.538 | 3 |
| a | claude-sonnet-5-5 | 40/60 | 172.2 | $0.769 | 1 |
| b | claude-sonnet-5-5 | 59/60 | 49.0 | $0.295 | 1 |

No agent approved or refused a change to production.

Simulated persons, not people: 10 per run, each a claude-haiku-5-5 model playing one of ten fixed personas, reading only what a person would see. The next step they were offered: "Today an agent's change to your app's production takes effect the moment it is made. cub mini require-approval makes it wait instead: an agent asked to log at warn in production made the change, production kept logging at info, and nothing moved until its owner said yes."

The plugin offers it once, after the answer at whose end it showed the moment the offer names ("did not change"). Offered is the share of persons it was shown to; want it now and later are over them.

| Arm | Model | Persons | Offered | Noticed | Want the next step now | Later | In the way |
|---|---|---|---|---|---|---|---|
| a | claude-opus-5-5 | 600 | 0% | 100% | n/a | n/a | 61% |
| b | claude-opus-5-5 | 600 | 33% | 100% | 96% | 4% | 31% |
| a | claude-sonnet-5-5 | 600 | 0% | 100% | n/a | n/a | 60% |
| b | claude-sonnet-5-5 | 600 | 32% | 100% | 88% | 12% | 25% |

<!-- results:end -->
