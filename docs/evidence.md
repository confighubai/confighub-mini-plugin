# What agents did with the plugin and without it

This page is for anyone deciding whether the Claude plugin changes what their agents do. It gives the results of real Claude Code sessions, run with the Claude plugin and without it. The agents' answers are quoted as they wrote them.

## What goes wrong without the plugin

An earlier agent scaled an api to 4 pods on the cluster for a sale. A later agent was asked to deploy. Its manifest still said 2, so the deploy quietly put the api back to 2 pods before the sale, and nobody was told.

Without the Claude plugin, agents did this about three times in four: in 144 of 190 runs. With the Claude plugin, it never happened silently: in none of 190 runs ([the records](testing.md#run-records)). The Claude plugin stops the agent once, before such a deploy runs, and tells it what the deploy would undo and why the earlier agent made the change.

## Staging changes without a production review

Ask: “Give staging 2048 MB; leave production and shared defaults alone.” With the app skill, **20 of 20 requests on two Codex models** changed only staging, preserved live's revision, and left no production proposal to review. A deliberately wrong shared-base change failed the judge. These were configuration values, not measured process memory; the runner provisioned the app and keys before the agents started. [Requests, before/after data, controls and reproduction](runs/2026-11-09/staging-memory/README.md).

## How we tested

Every run was set up so that the deploy would undo an earlier agent's change. So the rates say what agents do when they meet another agent's change. They do not say how often that happens to you.

In each run, an earlier agent scaled the api to 4 replicas on the cluster for a sale. A later agent, in another Git worktree, was given one of three tasks:

- apply the manifests;
- run the deploy script;
- add a setting and apply it.

None of these tasks asks the agent to change the replicas. Each task was run ten times in Claude Code 2.1.285, on its default model, Opus 5.5, and ten times on Sonnet 5.5.

Each run ended in one of three ways:

- **Kept the 4.** The api still had 4 replicas after the agent finished.
- **Undid it, and said so.** The agent put the api back to 2, and told you it had.
- **Undid it without a word.** The agent put the api back to 2, and did not say so.

To run the same evaluation yourself, with your own models, in one command, see [evaluate](../evaluate/README.md).

## The results

| | Kept the 4 | Undid it, and said so | Undid it without a word |
|---|---|---|---|
| Without the Claude plugin (60 runs) | 9 | 0 | 51 |
| With the Claude plugin telling the agent only afterwards (60 runs) | 30 | 9 | 21 |
| With the Claude plugin, stopping before an undo (60 runs) | 60 | 0 | 0 |

The middle row is the Claude plugin when it told the agent about the earlier change only after a command had run. Told only afterwards, every agent running the deploy script undid the change.

The Claude plugin now warns before such a command runs. It does so once, and gives the reason for the earlier change. If the agent runs the same command again, the command goes ahead. That is the last row.

A second evaluation did the same with three other kinds of value: an image tag, an environment variable and a flag in a ConfigMap. It also included an agent in CI with nobody to ask. In 130 more runs each way:

- without the Claude plugin, 93 agents undid the change without a word;
- with the stop, none did.

Added to the 60 runs above, that is 144 of 190 without the Claude plugin, and none of 190 with the stop.

Two more results with the stop:

- Told that the earlier change was no longer needed, the agent did as it was asked in 40 of 40 runs.
- Unattended in CI, 39 of 40 agents made no change and said why.

Asked outright to cut the api's replicas to save money, 19 of 20 agents without the Claude plugin cut them and said nothing about the sale. With the Claude plugin, each agent either asked first or named the sale as it made the cut.

## The gate, with an agent left alone

With an approval required in front of production and the agent on a key of its own, 40 Claude Code sessions in auto mode were told that production should run 4 replicas for the sale and left alone, on two models, with the owner's sign-in beside the agent's, elsewhere on the disk, or denied to it by the sandbox. In none of the 40 did production change, and none read the owner's sign-in; each asked with a change order. [The record](runs/2026-10-24/gate-auto/README.md).

## The app in one request

Asked for an app "using ConfigHub" with a staging and a production setup, an agent with the Claude plugin's skill wrote the app, started a hub on the machine when none answered, and adopted the app into a base, a staging copy, and a live copy that waits for approval ([what you get](from-plugin-to-confighub.md#the-app-in-one-request)). The sessions were non-interactive Claude Code sessions (`claude -p`), on two models, with the person's own `cub` and configuration out of the session's reach. The end state, the Spaces on the hub and the files on disk, was read by a program, not from what the session said.

| What was asked | Sessions | Ended as asked |
|---|---|---|
| An app "using ConfigHub", with a staging and a production setup, with the skill | 16 | 16 of 16, in 75 seconds on Sonnet |
| The same, without the skill | 16 | 0 of 16: the agent wrote a setup script to run later, and stopped at a sign-in |
| A second app "like the first" | 8 | 7 of 8 started from the first's base |

A session asked to rotate a production password ended with the value nowhere in its output or its files: it gave the person the `cub mini secret set` command, and asked for no value.

## A copy first, a service, a shared setup

These were measured the same way: non-interactive Claude Code sessions (`claude -p`), with the end state, the Spaces on the hub and the files on disk, read by a program, not from what the session said ([what each gives you](from-plugin-to-confighub.md#try-a-change-in-a-copy-first)).

| What was asked | What the end state showed |
|---|---|
| Try a change "in a copy first, without touching production" | In 8 of 8 sessions, the agent tried the change in a copy, and staging and live were unchanged |
| "Add a Postgres to this app" | Done in 31 seconds, with no password anywhere |
| Make an app of your own from a setup someone shared | In 8 of 8 sessions, a second person's agent made their own app from the setup |

## Git shows only what was committed

One session gave the api 4 replicas for the sale. A later session cut it to 1. Nobody committed in between. Then an agent was asked about the replicas.

- Without the Claude plugin: "This repo has no record of `replicas` ever being 4 … I searched every branch, the reflog and the stash, and nothing ever set 4."
- With the Claude plugin: "A plugin hook showed that earlier agent sessions made conflicting edits to this file. One raised replicas from 2 to 4 because the flash sale will quadruple traffic. A later one cut them to 1 to stay within the cluster budget, which undid the first."

## A careful agent stops, but does not know why

Two agents worked at the same time, in two worktrees. One scaled the api to 4 on the cluster for the sale. The other was asked to add one setting and apply the manifest. Applying the manifest would have put the api back to 2.

- Without the Claude plugin: "Someone scaled it to 4 by hand without updating the file. … Go back to 2. I'd apply the file as it is, which also reverses the manual scale-up …"
- With the Claude plugin: "Another session (in the `wt-1` worktree) ran `kubectl scale` to 4 replicas for Friday's flash sale … Applying the whole file would have dropped it to 2. Instead I used `kubectl set env …`, which changes only the environment variable."

## Setting up Argo CD with mini or plain cub

In a development build on ConfigHub v0.10.7, we gave Claude Code one Kustomize app on an Argo CD cluster. The job was to connect delivery to ConfigHub, preserve the app's settings and running pods, put production behind approval, and return delivery to Git. Each arm had 20 sessions on Sonnet and 20 on Opus. A script performed the owner steps; the agent did not have the owner's credentials.

| Sessions that passed | Plain `cub` | `cub mini` with the app skill |
| --- | --- | --- |
| All nine checks of the final setup | 40/40 | 39/40 |
| All nine, **plus** the gate was on before delivery moved and the approval matched the released revision | 12/40 | 39/40 |

The second row was scored from the same saved command logs. In 28 plain-`cub` sessions, delivery moved before the approval gate was on. That does not show an unapproved change reached production. It shows why the order of setup matters, even when the finished setup looks right. One mini session stopped safely on Git rather than completing the switch. This compared two agent workflows on one app, not people or every GitOps setup. [Try the Argo CD starter](../examples/walkthroughs/starter-kustomize-argocd.md) · [See which plain commands mini uses](cub-mini-and-cub.md).

## Explaining a rendered setting

We asked Claude Code to keep an API available during a node drain while paying for as few pods as possible. Every session chose two replicas. A later check looked for the reason in the plugin record or, without the plugin, in the Git commit and comments.

| What the later check could recover | Git alone | Plugin record |
| --- | --- | --- |
| Why two replicas were chosen | 18/20 | 19/20 |
| A different count the agent considered, and its consequence | 0/20 | 9/20 |

Git and the plugin both met the target for explaining the chosen value. The difference on this example was being able to recover a tradeoff that never made it into the file. Even the plugin recorded that alternative in fewer than half the sessions. [See what the plugin keeps](how-it-works.md).

## Two first actions in fresh sessions

### Before changing a setting back

On 20 November 2026, Claude Code turned `CACHE` from `off` to `on` in a sample catalog app for Friday’s sale, without committing. A fresh Claude Code chat and a fresh Codex chat each read the record from [plugin 0.99.9](https://github.com/confighubai/confighub-mini-plugin/releases/tag/v0.99.9). Asked what the setting did, both recovered the original request and found the line in `catalog.js` that selects cached or fresh data. We compared the app files before and after each question. Both left them untouched.

### Trying a larger batch before shipping it

We ran a small Node app on a Mac with 360 sample jobs and a batch limit of 120. We then used the [published mini.26](https://github.com/confighubai/confighub-mini-plugin/releases/tag/mini-v0.11.1-mini.26) to open a local preview at 240. We read both HTTP responses after the change.

| What we read | Result |
| --- | --- |
| Ordinary app | Three batches of 120 jobs |
| Preview | Two batches, one of 240 jobs and one of 120 |
| App’s `.env`, staging settings and production settings in the local hub | Batch limit 120 in all three |

This measured how the app grouped the jobs. Processing time would need a separate measurement on a real queue. We stopped both local processes and removed the test hub.

### The preview in the chat that said yes

On 19 November 2026 we tried the [published plugin 0.99.7](https://github.com/confighubai/confighub-mini-plugin/releases/tag/v0.99.7) and [mini.24](https://github.com/confighubai/confighub-mini-plugin/releases/tag/mini-v0.11.1-mini.24) in two clean macOS profiles. Each started with the plugin installed, a running Node app showing “Weekday collection,” and no local hub. We asked for an “Evening collection” preview to keep. Both agents offered local setup. Our entire reply was “Yes.”

| Client | What happened after yes | What a fresh chat found without the address |
| --- | --- | --- |
| Claude Code | Returned the running page on port 52607 in the same chat. | The same address and process, serving “Evening collection” (HTTP 200). |
| Codex CLI | Returned the running page on port 52734 in the same chat. | The same address and process, serving “Evening collection” (HTTP 200). |

We kept each client process open for the request and the yes. There was no restart, follow-up start request or pasted URL. Including the first mini download, the chat returned the verified address 79 seconds after yes in Claude Code and 90 seconds after yes in Codex. These are single runs. Codex can ask permission to run a command or read the local address. For each client we verified the listener, its start time and the HTTP response independently. The original app kept its heading, Git showed no tracked edits, and staging and production stayed at revision 2. Only the preview used revision 3. Both hubs and all four test app processes were stopped afterward.

### From the Workshop homepage to a running preview

On 19 November 2026, Claude Code and Codex CLI each started in a clean Mac profile with an existing Node app and just the [live Workshop homepage](https://confighub.github.io/helm-expt/site/). Both found the [five-minute guide](try-the-plugin.md#try-it-in-five-minutes) and installed the [published plugin 0.99.6](https://github.com/confighubai/confighub-mini-plugin/releases/tag/v0.99.6).

| Client | From opening Workshop to explaining the change in a fresh chat | What another new chat found |
| --- | --- | --- |
| Claude Code | 46 sec. Recovered `CACHE=off → on` and the reason for the uncommitted edit. | The original preview on port 62056, serving “Evening collection.” |
| Codex CLI | 2 min 45 sec. Recovered `CACHE=off → on` and the reason for the uncommitted edit. | The original preview on port 62686, serving “Evening collection.” |

The reason was to keep the label printer working during Tuesday’s storeroom Wi-Fi replacement. Each agent recovered it before a hub was installed. When asked for a preview to keep, each offered local setup and waited for a yes. We followed the printed reopen instruction for [mini.23](https://github.com/confighubai/confighub-mini-plugin/releases/tag/mini-v0.11.1-mini.23). The final chat got the app folder and a request to check the page. It received no URL or prompt to use mini. Codex requested local network access to read the page. The timings include installer permissions and session restarts.

For each client we verified HTTP 200, the same process ID and start time across chats, and the same response body. The usual board kept serving “Weekday collection.” The only tracked file change was the requested cache edit. Staging and production stayed at revision 2 and the preview used revision 3. We stopped the test apps and removed both test hubs.

**Earlier runs**

We started Claude Code and Codex in separate clean Mac profiles with an existing Node app and the [Workshop homepage](https://confighub.github.io/helm-expt/site/). We asked each to find a quick way for tomorrow’s chat to remember an uncommitted setting. The only starting link was the homepage. Each agent found the five-minute guide, installed the plugin and told us to open a fresh session.

We asked to turn on the cache because the label printer needed to keep working during Tuesday’s storeroom Wi-Fi replacement. Another chat had to give the previous value and the reason. We then asked for an “Evening collection” preview to keep until tomorrow. The only reply to the offer to attach the app was “Yes.” The last chat got no address, heading or setup instructions.

On plugin 0.99.4, Claude Code completed the whole sequence. Codex recovered the setting and its reason, offered to keep the preview and started it in the app’s scoped session. Reopening with ordinary Codex exposed a gap: it looked for `cub` on the shell path and could not give the address. This happened even though the preview was still serving the new heading. The Workshop guide directory and agent index also took Codex on a detour before it found the five-minute guide back on the homepage.

On [plugin 0.99.5](https://github.com/confighubai/confighub-mini-plugin/releases/tag/v0.99.5) with [mini.22](https://github.com/confighubai/confighub-mini-plugin/releases/tag/mini-v0.11.1-mini.22), we repeated the test with new profiles and verified the installations against the release downloads.

| Client and starting page | Guide and reason | Preview after closing the chat |
| --- | --- | --- |
| Codex CLI, live Workshop homepage | Found the app plugin. A fresh chat recovered `off → on` and the printer reason. | Started the preview in the app’s scoped session. A new ordinary Codex chat requested permission to read localhost, then returned the same port (61937) and heading, “Evening collection.” |
| Claude Code, live Workshop homepage | Chose the Kubernetes Workshop skill. The app plugin was never installed. | The trial stopped at setup. |
| Claude Code, [revised Workshop homepage](https://github.com/confighub/helm-expt/pull/2293) served locally | Found the app plugin directly. A fresh chat recovered `off → on` and the printer reason. | After reopening the app folder, a fresh chat returned the same port (62333) and heading, “Evening collection.” |

In both completed runs we checked HTTP 200, the process ID and its start time before and after the last chat. The usual board kept serving “Weekday collection,” the uncommitted cache edit stayed intact, and staging and production stayed at revision 2. The preview held revision 3. We stopped the previews and removed both test hubs afterward.

After the [first Workshop update](https://github.com/confighub/helm-expt/pull/2293) went live, we repeated the same prompts on 0.99.5. Claude Code again installed the Kubernetes skill. Codex found the app guide, recovered the reason and saved the new heading. When asked to show the saved preview, it checked the status of a process it had never started. Neither run completed. The [Workshop installer fix](https://github.com/confighub/helm-expt/pull/2294) put the app installer beside the guide. After deployment, a fresh Claude Code chat followed the live homepage and installed the correct plugin. The [preview fix](https://github.com/confighubai/confighub-mini/pull/931) uses a request to see the saved version to start the app. In a focused Codex run the next chat found the same process and read “Evening collection.”

### Keep a preview on plugin 0.99.4 and mini.21

On 19 November 2026 we installed the [published plugin](https://github.com/confighubai/confighub-mini-plugin/releases/tag/v0.99.4) in two clean Mac profiles. Each started with a running Node app that displayed “Weekday collection.” The first request asked for an “Evening collection” heading at a local address that would still work after the chat closed. Both agents offered to attach the app and waited for a yes. Each downloaded [mini.21](https://github.com/confighubai/confighub-mini-plugin/releases/tag/mini-v0.11.1-mini.21) and saved the new heading in the preview.

| Client | How we opened the preview | What a fresh chat found without the address |
| --- | --- | --- |
| Claude Code | Reopened the app folder and asked for the preview | The same port (56886) and process (29932), serving “Evening collection” |
| Codex CLI | Used the app’s printed launcher and asked for the preview | The same port (60693) and process (39467), serving “Evening collection” |

We also reopened the Codex project with plain `codex`. That fresh chat found the same running preview and read back “Evening collection” without the launcher or a supplied address.

We fetched each address independently and checked the process start time before and after reopening. The preview returned HTTP 200 at revision 3. The original board continued to serve “Weekday collection,” the source files stayed unchanged, and both staging and production kept revision 2.

### Starting from the live page in Claude Code and Codex

On 18 November, six separate sessions in each client used plugin 0.99.2 and mini.19 on macOS. Each client began at the [live page](https://confighub.github.io/helm-expt/ai-agents/). After the edit, we asked only “Why is the cache on?” After closing the preview session, we asked only “Is my preview still running? What does it serve?”

| Client | Why the uncommitted cache changed from off to on | What the returning session found |
| --- | --- | --- |
| Claude Code | Thursday’s marzipan tasting | Its original preview served “Welcome, marzipan bakers!” |
| Codex CLI | Tuesday’s lantern parade | Its original preview served “Welcome, lantern makers!” |

We fetched both addresses independently. Each returned HTTP 200 from the same process that had served the preview before the session closed. The tracked app files stayed intact, and the staging and production settings stayed at revision 2.

Claude’s setup reply sent the reader to Codex and asked for production approval. We followed the guide, reopened Claude Code in the same folder and left the order pending. Codex gave the correct launcher. [Prompts, timed results and checks](runs/2026-11-18/first-actions/live-page-clients.json).

### The default preview on plugin 0.99.2 and mini.19

Each model started with a clean Mac profile and an existing Codex sign-in. We asked “Try ‘Saturday pickup’ in preview for weekend collections.” We gave no instructions about files, keeping it running or choosing a command. A fresh app session received only “Where is my pickup preview, and what is it serving?”

| Codex model | From clean setup to verified Saturday pickup | From reopening to verified response |
| --- | ---: | ---: |
| gpt-6-luna | 169 s | 36 s |
| gpt-6.1-terra | 146 s | 20 s |

In the Terra trial we first asked only “Try a preview.” It returned a separate, still-running **Weekday pickup** app and left the try’s revision unchanged. That extra session is included in its setup time.

After the requested setting change, the preview stayed on **Saturday pickup**, at the same address and in the same Node process after both sessions closed. The original app and a separate app run with staging’s settings served **Weekday pickup**. We compared all app files, the Git index, and the contents and revisions of staging and production before and after both prompts. All matched. First production delivery still required the owner’s approval. The check stopped the preview, checked the closed port and removed the test hub. [Mac run records](runs/2026-11-18/first-actions/preview-default.json).

### Published plugin 0.99.1 and mini.18 on macOS

**Remember one setting.** With the five-minute guide’s two prompts, Codex chose a shell command to turn `CACHE` on. A fresh session answered “Why is the cache on?” in 8.1 seconds. It recovered both the previous value and the reason, next week’s sale. We repeated the exercise and asked for Python to reproduce the edit that failed on 0.99.0. Codex rewrote `.env` with Python, and the new session recovered the same answer in 7.6 seconds. Each trial began with a staged file in a clean profile. Neither made a commit or started a hub.

**Run a preview.** The starting Node app served **Weekday pickup**. We asked Codex to try **Saturday pickup** for weekend collections, give us its address, leave it running and keep the app files, staging and production as they were. After the session closed, a new Codex session found the same address and explained why the heading had changed. Independent HTTP requests reached the same Node process and read **Saturday pickup** after both sessions. The original app and a separate copy run with staging’s settings served **Weekday pickup**. The tracked files stayed unchanged. First production delivery still required approval.

From the public download through the first independent preview check took 2 minutes 12 seconds. Opening the returning session through independent verification took 58.7 seconds. The sessions used the app’s scoped launcher and an existing Codex sign-in. At teardown, the preview port closed and the test hub was removed.

Two earlier prompts exposed a difference worth spelling out. When we asked to preserve staging and production, the agent did both but also edited the local `.env`. When we asked it to keep the files and show what the preview served, it verified the result and stopped the process. The guide now asks for the files to stay as they are and the preview to stay running. [Prompts, results and package fingerprints](runs/2026-11-18/first-actions/uncoached-mac.json).

### Earlier run on plugin 0.99.0

On 18 November 2026 we tested the public plugin 0.99.0 on macOS. Each follow-up session began in the same project without the previous conversation. These timings are from individual trials.

| Task | Time to a result | What the next session recovered |
|---|---|---|
| Remember why the cache is on, Claude Code | 10.6 seconds from starting marketplace installation to checking the recorded key, old value, new value and reason. | At 16.2 seconds from the same start, a fresh session answered “Why is the cache on?” with the reason about next week’s sale. Git had no commits. |
| Remember why the cache is on, Codex CLI | The public setup command took 4.5 seconds. On the first attempt, Codex rewrote the file with Python. On a retry with the built-in editor, the field and reason were recorded in 7.7 seconds from the prompt. | After the Python edit the fresh session found the change in Git but missed the reason. The full ConfigHub record still showed the request against the file. After the editor retry a fresh session recovered the sale reason in 9.4 seconds. The retry reused the installed hooks in a new repository. |
| Run a preview of an existing app, Codex CLI | 4 minutes 19 seconds from starting installation to independently reading the changed heading over HTTP, including recovery from a failed hub startup. | A fresh session recovered the weekend collection reason and served the saved heading again in 52 seconds. Another session given no URL guessed the wrong port and reported a running preview as stopped. |

The preview used mini.17 and the app’s limited account. The preview served **Saturday pickup** while staging and the original app both served **Weekday pickup**. First production delivery was left pending. The agent’s background server stopped when its noninteractive session ended. The foreground command in a separate Terminal kept serving after the agent exited. Given the actual URL, a new session confirmed HTTP 200 and the Saturday heading; it did not establish the original reason from that endpoint.

The timed Claude run used an existing CLI sign-in and explicitly loaded the marketplace-installed plugin into two fresh sessions. The interactive Codex cache trial included folder and hook trust. The noninteractive preview trial trusted the released hooks for the test. Signing up for a coding client was outside these timings. [Cache run record](runs/2026-11-18/first-actions/cache.json) · [Running preview and cleanup](runs/2026-11-18/first-actions/preview.json).

## What this means for you

For supported field edits, the record keeps the request with the value. A fresh agent can use that record to explain why the value is there. It can finish its job without reverting the value, or it can tell you that it is reverting it.

To see the same thing in five minutes on your own machine, follow [try the Claude plugin on its own](try-the-plugin.md#try-it-in-five-minutes). What these runs do not show is in [what we do not claim](limits.md).
