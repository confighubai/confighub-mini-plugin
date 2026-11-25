# For a security review: what the Claude plugin does on a computer

This page is for a platform or security team deciding whether people may install the ConfigHub plugin for Claude Code on work computers. It says what the plugin reads, what it writes, what it sends and to where, what it can change in an agent's behavior, and how to turn each part off. For the ConfigHub hub server itself (local `confighub mini` or self-hosted in your cluster), see [For a security review: the ConfigHub hub](security-hub.md). Each setting below is an environment variable. To set one for every session, put it in the `env` block of Claude Code's `settings.json`, for example `{ "env": { "CUB_MINI_RECORD": "0" } }`.

If you want to see what the plugin's program does before anyone installs it, [run the inventory without installing the plugin](inventory.md#without-installing-the-plugin). That is one program, checked against its published checksum, run on one of your repositories with no hooks and nothing installed.

## What the plugin is

The plugin has three parts:

- **Hooks.** Claude Code runs the plugin's program at the start and end of each session and turn, and before and after each tool the agent uses. This is how the plugin keeps a record of what agents changed in configuration files, and why.
- **Commands.** The slash commands, such as `/confighub:changes` and `/confighub:inventory`, run only when a person types them. An agent cannot start them.
- **One program.** It is built for macOS and Linux, on Intel and ARM, and kept compressed in the plugin's `bin` folder. On first use, the plugin's launcher script unpacks the program for your computer next to the compressed copy. If it cannot write there, it unpacks it to `~/.confighub/plugin-programs`.

## What it reads

- **The files the agent works on**, in the folder Claude Code is open in. When the agent reads or edits a configuration file, the plugin reads that file to see which values changed.
- **Earlier Claude Code sessions in the same folder, once.** The first time the plugin works in a folder, it reads Claude Code's own transcripts of that folder's sessions from the last 30 days. Claude Code keeps these files in `~/.claude/projects`. From them it records which configuration values those sessions changed, and the request behind each change. `CUB_MINI_EARLIER_SESSIONS=0` turns this off. Set it before the plugin first opens a folder.
- **The current session's transcript**, at the end of each turn, to count the tokens and note the model used.
- **Claude Code's `settings.json`**, when a person types `/confighub:permissions`. That command reads earlier transcripts only after the person agrees.
- **The name of the current Kubernetes context**, from the `current-context:` line of your Kubernetes configuration, so the record can say which cluster a `kubectl` command was aimed at. It does not read credentials from that file. It does not contact a cluster unless you turn that on (see the list below).

## What it writes

- **The record**, in `~/.confighub/agent-changes`, with one folder for each project and session. It holds:
  - each value an agent changed, from what to what;
  - the commands the agent ran, but not their output;
  - the person's request, and the agent's last message of each turn, each cut to 1,500 characters.
- **Credentials are never written down.** A value whose name looks like a credential, and every value in a Kubernetes Secret, is recorded only as "changed". Before a request or a command is stored, credentials are taken out of it: values written as `NAME=value` under such a name, passwords inside URLs, and tokens known by their form. Those forms are GitHub, OpenAI-style, Slack and AWS keys, and JSON web tokens. A secret pasted with no name, in a form that is not known, is kept as it was written.
- **Retention.** A session's records are removed once they are 30 days old, counted from their last change, the next time a session starts in that folder. `cub mini changes --forget` removes a folder's whole record at once.
- **Small files beside the record.** An error log, a count of which commands were used on which days (`CUB_MINI_COUNT=0` turns this off), and a key that signs each turn's record (`CUB_MINI_SIGN=0` turns this off).
- **Nothing in your repository by default.** It writes there only when you turn on one of these:
  - keeping the record in the repository (`CUB_MINI_RECORD_IN_REPO=1`);
  - `/confighub:permissions --apply --yes`, which writes `.claude/settings.local.json` and keeps a backup.

## What it sends, and to where

In an ordinary session, it sends nothing. The record stays on the computer. It sends something only in these cases.

**Without being turned on, but only after a step the person or the agent took:**

- **When the agent changes a ConfigHub hub with `cub`**, the plugin adds that turn's model name and token counts to the change, in the hub `cub` is signed in to. That can be a hub on another computer. `CUB_MINI_USAGE=0` turns this off.
- **After the agent proposes a change on a hub**, the plugin reads that proposal back from the same hub, to tell the agent and the person where it stands. `CUB_MINI_TELL=0` turns this off.
- **When the person answers yes to the plugin's offer to install the local hub**, it downloads confighub mini from this repository's GitHub releases. The download is checked against checksums built into the program. If the person sets `CUB_MINI_TIPS=0`, the offer is never made.

**When the person types a command:**

- `/confighub:staging` and `/confighub:start-from` download confighub mini from GitHub if it is not installed, and start a local hub. For an app on Vercel, Fly.io, Heroku or Unikraft, they read the app's settings with that service's own command-line tool.
- `/confighub:to-hub --yes` sends the record to the hub `cub` is signed in to.

**Only when you turn it on:**

| Setting | What is sent, and to where |
|---|---|
| `CUB_MINI_OTEL=1` | The record, to the OpenTelemetry endpoint you name |
| `CUB_MINI_PULL_REQUEST=1` | A table of changed values and reasons, written into the pull request on GitHub with `gh` |
| `CUB_MINI_READ_CLUSTER=1` | A `kubectl get` against the current cluster, before an apply |
| `CUB_MINI_KEEP_IN_HUB=1` | Each change, to a hub running on this computer |
| `CUB_MINI_NOTIFY` | Each notice, to the command you give |

**Through Claude Code itself.** What a command prints, and what the hooks add to the agent's context, becomes part of the conversation. Claude Code sends the conversation to the model, as it does with every file the agent reads.

## What it can change in the agent's behavior

- **It adds text to what the agent sees.** When the agent reads a file that earlier sessions changed, it is told what they changed and why, including the requests, marked as quotes. `CUB_MINI_HISTORY=0` turns this off.
- **It refuses some tool calls once.** A command that would undo a change an earlier session made directly on a cluster is refused once, and the agent is told why. If it is still right, the agent runs it again. `CUB_MINI_STOP_BEFORE_UNDO=0` turns this off. A command that changes production directly on a host, such as `fly secrets set` on the production app, `heroku config:set`, `vercel env add NAME production` or `unikraft instances run -e`, is also refused once, and the agent is told to ask the person, or to propose the change to the hub where the app is kept in one. Run again, it goes ahead. `CUB_MINI_HOLD_PRODUCTION=0` turns this off. For calls to MCP servers, the default is to record them only. The stricter levels are described in [how it works](how-it-works.md).
- **It stops all agents on request.** While the file `~/.confighub/halt` exists, every tool call is refused.
- **What it quotes comes from people who can commit.** If a team keeps the record in the repository, anyone who can commit there can write text that agents are later shown as an earlier request. That text is marked as a quote, not as an instruction to follow now.

## Programs it runs

- `git`, for local commands only, such as finding the repository's top folder and its `origin`.
- `kubectl kustomize` or `kustomize build`, for `/confighub:inventory`, to compare environments.
- `cub` and the program of confighub mini, when a hub is in use.
- `gh`, only with `CUB_MINI_PULL_REQUEST=1`.

The words you type after a slash command are passed to the plugin's program as you typed them. Only a person can type those commands, so this is your own text.

## Checking the program

Each plugin release publishes the four programs and a `SHA256SUMS` file. The same file is in the plugin's `bin` folder. The programs are not code-signed.

## Turning it all off

`CUB_MINI_RECORD=0` makes every hook return at once. Nothing is recorded, no earlier session is read, nothing is added to what the agent sees, and nothing is downloaded or started in the background. The commands still work, on what was recorded before. The halt file still stops agents. To remove the plugin and its record, see [going back](journeys/going-back.md).

| Setting | What it turns off |
|---|---|
| `CUB_MINI_RECORD=0` | Everything the hooks do |
| `CUB_MINI_EARLIER_SESSIONS=0` | Reading earlier Claude Code sessions |
| `CUB_MINI_HISTORY=0` | Telling the agent what earlier sessions changed |
| `CUB_MINI_STOP_BEFORE_UNDO=0` | Refusing an undo once |
| `CUB_MINI_HOLD_PRODUCTION=0` | Refusing a direct change to production once |
| `CUB_MINI_USAGE=0` | Adding token counts to a hub the agent changed |
| `CUB_MINI_TELL=0` | Reading back a change the agent proposed on a hub |
| `CUB_MINI_TIPS=0` | The offer to install the local hub, and the lines about it |
| `CUB_MINI_COUNT=0` | Counting which commands were used |
| `CUB_MINI_SIGN=0` | Signing the record |
