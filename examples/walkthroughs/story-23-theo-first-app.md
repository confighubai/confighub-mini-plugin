<!-- walkthrough
id: story-23-theo-first-app
starts_with: plugin
story: "23. Theo's first app: the setup travels with it from the first prompt"
needs: [Claude Code, the ConfigHub plugin, git]
budget_seconds: 60
-->
# The reasons for your app's settings, kept from the first prompt

Theo starts apps by asking Claude Code for them, sometimes from a copy of someone else's repository. Weeks later he wants to know why each setting is what it is and where the app came from. With the ConfigHub plugin, every value the agent writes is kept with the request behind it, from the first file, along with the repository the app started from. No hub and no account are needed.

## Human

For a person following along. Steps 2 to 6 happen in Claude Code.

### What you need

Claude Code, Git, and the ConfigHub plugin.

### Steps

1. Theo's folder is a copy of someone else's starting point, a Git repository with its own remote. Make one like it, and install the plugin if you have not:
   <!-- run: setup files -->
   ```sh
   mkdir -p ~/walkthrough/yoga && cd ~/walkthrough/yoga
   git init -q && git remote add origin https://github.com/example/yoga-bookings.git
   printf '# Yoga bookings\n' > README.md && git add README.md && git -c user.email=theo@example.com -c user.name=Theo commit -qm start
   ```
   ```sh
   claude plugin marketplace add confighubai/confighub-mini-plugin
   claude plugin install confighub@confighub
   ```

2. Start Claude Code in `~/walkthrough/yoga` and ask for the app, with the reason for its one limit:

   `Build me a booking page for my yoga studio, with a limit of 20 bookings a day: the room fits 20 mats.`

3. The agent writes the app and its settings file. At the end of its turn, one line says that the plugin kept a record of the settings it changed, and why.

4. Ask, in the same session or a later one, where a value came from: `/confighub:why` followed by the setting's name, such as the bookings limit the agent wrote. It shows each change to that value with the request behind it, quoted.

5. Ask what agents changed here, and where the app started: `/confighub:changes`, or `cub mini changes --dir .` in a terminal. It names the repository and commit the folder started from, as first seen, then each setting with the request behind it. Shortened, from a real session:
   ```text
   Starting point: github.com/example/yoga-bookings at 0dff5f1f… (first observed …)
   Asked: Build me a booking page for my yoga studio, with a limit of 20 bookings a day: the room fits 20 mats.
     .env (Settings file)
       MAX_BOOKINGS_PER_DAY                         (none) → 20
   ```

6. Weeks later, ask an agent to raise the limit. Before it changes the value, it is told why the value is 20, and says so; you decide.

### Undo it

Delete `~/walkthrough/yoga`. The plugin's record is kept in `~/.confighub/agent-changes` and removed after 30 days without use; `claude plugin uninstall confighub@confighub` removes the plugin.

### What you have now

An app whose settings each carry the request that set them, and a note of where the app came from, with nothing to run. The full story adds taking the origin's next version while keeping your changes, carrying the reasons into Kubernetes manifests, and sharing a setup that has held; those are not built yet. [Try the plugin on its own](../../docs/try-the-plugin.md) explains the record.

## Agent

For an AI agent asked to build the app.

- The request: "Build me a booking page for my yoga studio, with a limit of 20 bookings a day: the room fits 20 mats."
- Build it as you normally would, with its settings in a settings file such as `.env`. Say in your answer what you set and why, in the person's words; the plugin keeps that with each value.
- Never remove or rewrite the repository's remote or history.
- Done when the app runs and its settings file sets the limit.

## Testing

This proves: what the plugin kept about each value an agent wrote, read from its record with `cub mini changes`. What was really used: Claude Code with the plugin from the confighub mini package; no hub and nothing delivered. This story has no offer moment in its agent task: the plugin shows the person no line at the end of the turn, so the next step below is not offered and conversion is not measured; the simulated persons still say whether they noticed the result and whether anything was in the way. In plain files, arm a passes only if the reason is kept as data in a settings file, a key with the reason as its value, not as a comment beside the limit.

The scripted run makes only the folder; the rest needs a Claude Code session, so the checks are judged in the agent runs. A correct result in arm b has the starting repository and the limit's request in the record; in arm a, a visible file has the limit next to its reason. The checks below can be run by hand, in bash, in the app's folder:

<!-- agent-task: build -->
> Build me a booking page for my yoga studio, with a limit of 20 bookings a day: the room fits 20 mats.

<!-- agent-check build: /absolute/path/to/unpacked-confighub-mini/bin/confighub-mini-app mini changes --dir . 2>/dev/null | tr '\n' ' ' | grep -q 'example/yoga-bookings.*20 bookings a day' -->
<!-- agent-check-a build: grep -rhsE --include='.env*' --include='*.env' --include='*.json' --include='*.yaml' --include='*.yml' --include='*.toml' --exclude-dir='.*' --exclude-dir=node_modules '^[^#;/]*[:=][^#]*(mats?|room)' * .env* | grep -q . -->
<!-- arms: a,b,c -->
<!-- next-step boundary=same-tier when "did not change": keep the plugin on | Your next app can keep the reason for each setting from its first file, so nobody has to guess later why a value is what it is; want the plugin kept on for it? -->

```sh
cub mini changes --dir . | tr '\n' ' ' | grep -q 'example/yoga-bookings.*20 bookings a day'
grep -rhsE --include='.env*' --include='*.env' --include='*.json' --include='*.yaml' --include='*.yml' --include='*.toml' --exclude-dir='.*' --exclude-dir=node_modules '^[^#;/]*[:=][^#]*(mats?|room)' * .env* | grep -q .
```

<!-- results:begin -->

Results, 14 November 2026, confighub mini 0.11.1-mini.5. Figures from this page's own test runs, shown here for whoever checks the page; they are not a promise.

- Environment, published confighub mini 0.11.1-mini.5 (tag mini-v0.11.1-mini.5, darwin-arm64, verified against SHA256SUMS) and the plugin it carries: Claude Code with the plugin on this computer, with no hub needed for the record, no stand-in, cluster or real service, and no approvals. The scripted run only makes the folder; its check needs a Claude Code session, so it is judged in the agent runs only. Arm a was run again the same day on the same package with a tightened file-level judge (the reason kept as data, not as a comment); arms b and c are from the first mini.5 pilot.
- Agent runs: a pilot, 3 runs per arm on each of claude-sonnet-5-5, claude-opus-5-5. Arms: a is ordinary tools only; b is the plugin, confighub mini and this page as reading; c is the plugin and confighub mini, without this page.

| Arm | Model | Checks passed | Median seconds | Median cost | Commands left for the person (median) |
|---|---|---|---|---|---|
| a | claude-opus-5-5 | 0/3 | 83.7 | $0.355 | 0 |
| a | claude-sonnet-5-5 | 0/3 | 47.1 | $0.16 | 0 |
| b | claude-opus-5-5 | 3/3 | 60.3 | $0.286 | 0 |
| c | claude-opus-5-5 | 1/3 | 81.9 | $0.355 | 0 |
| b | claude-sonnet-5-5 | 3/3 | 63.9 | $0.19 | 0 |
| c | claude-sonnet-5-5 | 2/3 | 39.1 | $0.108 | 0 |

No agent approved or refused a change to production.

Simulated persons, not people: 10 per run, each a claude-haiku-5-5 model playing one of ten fixed personas, reading only what a person would see. The next step they were offered: "Your next app can keep the reason for each setting from its first file, so nobody has to guess later why a value is what it is; want the plugin kept on for it?" It offers more of the tier the person has, not a step up.

The plugin offers it once, after the answer at whose end it showed the moment the offer names ("did not change"). Offered is the share of persons it was shown to; want it now and later are over them.

| Arm | Model | Persons | Offered | Noticed | Want the next step now | Later | In the way |
|---|---|---|---|---|---|---|---|
| a | claude-opus-5-5 | 30 | 0% | 80% | n/a | n/a | 0% |
| a | claude-sonnet-5-5 | 30 | 0% | 90% | n/a | n/a | 20% |
| b | claude-opus-5-5 | 30 | 0% | 100% | n/a | n/a | 0% |
| c | claude-opus-5-5 | 30 | 0% | 80% | n/a | n/a | 0% |
| b | claude-sonnet-5-5 | 30 | 0% | 100% | n/a | n/a | 23% |
| c | claude-sonnet-5-5 | 30 | 0% | 93% | n/a | n/a | 3% |

<!-- results:end -->
