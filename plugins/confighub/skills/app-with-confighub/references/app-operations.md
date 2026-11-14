# App operations

Read only the section needed for the current request. App settings stored in a live copy
are not proof that a service runs them. Inspect the actual delivery path.

## 0. An app that Argo CD or Flux already deploys, with a starter

When Argo CD or Flux already deploys the app from Git, one adopt line connects it and the
person approves with a second. When a hub already answers (`cub context get` names one and
`cub space list` works), run the adopt line yourself, in the app's folder, and give the person
only the approval it prints. Run it without `--agent` and `--attach`: they make your own key and
attach the cluster, which are the owner's steps, and adopt refuses them from your session. Use them
only in the line you hand the person when no hub answers; when the cluster is already attached
(`cub cluster up` or `cub cluster attach` made it), leave `--attach` out for the person too. Give the person the adopt line too only when no hub answers. Starters are on when `CUB_MINI_STARTERS` names a folder
(`echo $CUB_MINI_STARTERS` shows it). When it is empty, they are on for one command by naming the
package's own folder in front of it: the `starters` folder beside the package's `bin`, for
example `CUB_MINI_STARTERS="$(dirname "$(dirname CUB))/starters" cub mini adopt ...` with `CUB` the
full path of the package's `cub`. The approval line adopt prints is what moves the controller
from Git to the hub: it changes the Application or Kustomization to take the hub's OCI release of
the approved revision. Until the person runs it, Argo CD or Flux still deploys from Git, so your
task is not finished at the adopt; end with the two lines the person runs. This section replaces
sections 1 to 3 for such an app. Do not give the person `cub mini install`,
`require-approval` or `cub cluster attach` before it. Do not add `--note-dir`,
`--note-outside` or `--own-values` to it: the line already leaves the app's files unchanged.

```
cub mini adopt APP-FOLDER --kube-context CONTEXT --source NAME --agent APP-agent --attach CLUSTER
```

The program in each line you hand the person is `cub`, or `~/.confighub/mini/cub` when
the commands print that; copy a printed line as it is. Never write a package's `cub` by its
full path in a line for the person.

`NAME` is the Argo CD Application or Flux Kustomization that deploys the app, and `CLUSTER`
is the name the cluster gets in the hub. What this one line does for the person:

- It starts a hub on this machine when there is none, so the person installs nothing first.
- It makes the base, staging and production copies from the app's files, and puts
  production behind the person's approval.
- It attaches the cluster to the Argo CD or Flux that is there, and leaves Argo CD's admin
  password out of what it prints.
- It makes your key, which can change staging and ask for a change to production, and
  cannot approve.
- It keeps the app's note outside the app's folder, so the app's files are not changed. It
  adds only `.claude/settings.local.json`, which Git ignores, so that the next Claude Code
  session in the folder runs as the agent.

Its last line is the person's approval, `cub mini deploy-from-hub ... --change-order
APP-live/connect --approve`. It shows the person what it would move and asks yes or no. On a
yes it approves the order and moves delivery to the hub, with the same pods running. Give
the person these two lines and no other. If `cub` is not on the person's PATH yet, because
only the plugin is installed, give the adopt line with the plugin's program in place of
`cub` (see section 1); it installs confighub mini first, and its last line names the
person's `cub` in full.

The way back to Git is one line, which the approval prints and `cub mini status APP` prints
again: `cub mini back-to-git APP --variant live --repo CHECKOUT --kube-context CONTEXT --push`.
Record it, or hand it over, exactly as printed: with the app's name and with `--push`, which
pushes the commit it makes. Without `--push`, run by anyone but a person at a terminal, it
stops at once and changes nothing. Do not write `kubectl patch` lines for Argo CD or Flux in
its place: `back-to-git` also writes what changed in the hub into Git, and checks that the
same pods keep running.

Changing an app a starter connected: the app's files are the person's repository. Make the change
in the repository's base, so staging takes it too, and commit it. Then `cub mini upload APP-FOLDER
--component APP --change-desc WHY` proposes it: staging takes it at once and production waits.
Give the person `cub mini approve`, which `upload` prints. To undo, revert the commit, upload again
and hand over the approval again. Do not set a value in production directly, or edit only the
production overlay, for a change the person wants everywhere.

Deleting an app a starter connected: first remove what runs on the cluster, then the app from the
hub. Never delete a cluster to remove one app: not with `cub cluster down`, `kind delete cluster`
or anything else, since other apps and the person's own work run there. If deleting the
Application or Kustomization fails, stop there and say so; do not go on to the hub, or around
it. Agents' shells are often zsh, which does not split a command kept in a variable, such as
`K="kubectl --context X"; $K delete ...`, so write `kubectl --context CONTEXT` in each command. For Argo CD, delete the Application with its finalizer, so Argo CD removes what it deployed.
For Flux, deleting a Kustomization removes what it applied only when its `spec.prune` is true, and
the Kustomization the hub's cutover made does not prune. Find it, and the Git one it suspended, with
`kubectl get kustomizations -A`: after the cutover the hub's is named `APP-live`, in Flux's own
namespace (usually `flux-system`), beside an OCIRepository of the same name. Turn pruning on, then
delete it:

```
kubectl -n flux-system patch kustomization APP-live --type merge -p '{"spec":{"prune":true}}'
kubectl -n flux-system delete kustomization APP-live
kubectl -n flux-system delete ocirepository APP-live
```

Delete the suspended Git Kustomization while it is still suspended, so that it does not apply the app
again; a suspended Kustomization removes nothing when deleted. Before a cutover, the Git
Kustomization is the one that deploys: if its `spec.prune` is false, turn it on the same way before
deleting it. Check with `kubectl get` that the app's workloads are gone. Then delete the app from
the hub as a whole: `cub component delete --recursive --detach APP`, which removes the Component and its Spaces, then
`cub space delete --recursive APP-file-proposals` when that Space exists. Deleting only the Spaces
leaves the Component, so the app still shows in `cub component get APP`. Leave the cluster, the
person's repository and the shared hub as they are unless asked. Say what remains: the app's
approval rules in the `workflows` Space, and the folder's `.confighub-app`.

Check before you hand it over, with your own commands: `cub mini adopt APP-FOLDER
--kube-context CONTEXT --source NAME --dry-run` shows the starter's plan and needs no hub.
After the adopt line, read with the key it made for you, using the `CUB_CONFIG` and
`CUB_CONTEXT` it printed: `cub space list`, `cub mini waiting`, `cub mini status`, `cub unit
data`, `cub mini deploy-from-hub ... --dry-run` and `kubectl get` answer you as they answer
the person. Do not hand the person a command that only reads; the approval is the only
command that has to be theirs.

## 1. Find a hub, or start one

For a Claude plugin, derive the absolute program path from this reference's installed
location: `skills/app-with-confighub/references/` is inside the plugin, whose program is
`bin/confighub`. Use that absolute path if the plugin-root shell variables below are not
set; do not guess a repository-relative path. Codex setup renders the command below with
the installed program's absolute path.

Inspect the current cub context and `.confighub-app` before choosing a target. A reachable
hub is not necessarily the hub for this app. Use an explicitly chosen context; do not
redirect writes to another hub when a command fails. If no suitable hub answers, explain
the local download (about 60 MB) and two local processes. Start it only if the person
already asked for ConfigHub, or accepted this setup. Then run:

```
"${PLUGIN_ROOT:-$CLAUDE_PLUGIN_ROOT}/bin/confighub" mini get
```

Claude Code sets `CLAUDE_PLUGIN_ROOT` for the plugin's hooks and commands only, so it is empty in a
shell you run yourself. There, the plugin gives each session its program by its full path, as
`CONFIGHUB_PLUGIN_PROGRAM`: run `"$CONFIGHUB_PLUGIN_PROGRAM" mini get`. Do not search
`~/.claude` for it. In a line for the person, write out the path it holds
(`echo "$CONFIGHUB_PLUGIN_PROGRAM"` shows it), since their terminal does not have it.

For Codex hook-only setup, use `${CODEX_HOME:-$HOME/.codex}/confighub/bin/confighub mini get`
instead. A restricted agent with an existing app must use its configured hub, not install another.

It downloads confighub mini (about 60 MB), starts a hub on this machine and signs `cub` in to
it, in under a minute. Its last lines name its `cub` by its full path. In each later command,
use that path, or put its folder first on the PATH in that command:
`${CUB_CONFIG:-$HOME/.confighub}/mini/confighub-mini-<version>-<os>-<arch>/bin/cub`.
Do not give the person a PATH line: a new session in the app's folder finds `cub` by itself,
and each command printed for the person names its `cub` in full.
Do not run `cub auth login`, and do not send the person to hub.confighub.com. Run it again
after a restart to start the hub again.

## 2. Make the app's copies

The app's settings are an env file in its folder: `.env`, with `KEY=VALUE` lines. For a new
app, write the code and its `.env` first (`PORT`, `GREETING`, `LOG_LEVEL`, and so on), with
values for running it locally. Put each value the person gave for staging in `.env.staging`,
and each value they gave for production in `.env.production`. Keep those values out of
`.env`, or give `.env` a different one: adopt takes a value in `.env.production` as
production's own, at once, only where `.env` differs. A value `.env` holds too reaches
production only after the person approves. For an existing app, use the files the person has: `.env` (or `app.env`, a compose file's
environment), with `.env.staging` and `.env.production` beside it if they keep them, or a
Terraform folder's `common.tfvars` with `staging.tfvars` and `prod.tfvars`. A Kustomize
repository with overlays (a `base/`, `overlays/staging`, `overlays/prod`) is adopted as it is:
its rendered base becomes the base, and what each overlay changes becomes that copy's own
values; `cub mini upload` on the repository's folder takes a later change the same way. Then,
from the folder above the app's:

```
cub mini adopt APP-FOLDER --dry-run
cub mini adopt APP-FOLDER
```

This makes `APP-base`, `APP-staging` with the file's values now, and `APP-live`, which takes
them only once the person approves. A `.env.staging` or `.env.production` becomes that copy's
own values from the start. A value that looks like a password or token is left out and named;
leave it out of the file too, and name where to read it instead (`DB_PASSWORD_FILE`). The
app's name is the folder's; `--name NAME` sets another (lowercase letters, digits, dashes).
`cub space list` shows the three copies; `cub unit data --space APP-staging app` shows one.
Adopt writes `.confighub-app` into the folder, a note of what its files match in the hub;
commit it with the app, so that `cub mini upload` from any clone proposes only what that
clone changed.

An app that Argo CD or Flux already deploys from Git, with `CUB_MINI_STARTERS` set, is
connected by the one line in section 0, in place of this section and the next.

A second app on a hub that already has one starts from the first, not from nothing:

```
cub mini adopt APP-FOLDER --pattern FIRST-APP
```

It gets the first's base as its own base, keeps its own values, and takes what the first
changes next (`cub mini upgrade APP-base/app`). Use it whenever the person asks for another
app "like" one that is here, or with "the same setup"; `cub space list` shows which apps are.

### An app from a setup someone shared

A setup someone shared is a file `NAME-setup.tar.gz` (from `cub mini copy APP --to-file`) or
an OCI reference (from `--to-oci`): an app's base, staging and live copies, with the reason
for each value, and no secrets. Take it in under a name of its own, then make the person's
app from it, as the second app above:

```
cub mini copy --from-file FILE --name SHARED        # or --from-oci REF --name SHARED
cub mini adopt APP-FOLDER --pattern SHARED
```

The copy's last line names the adopt command. The person's app is then `APP-base`,
`APP-staging` and `APP-live`, made from `SHARED-base`: it keeps its own values from its
`.env`, takes the shared values for the rest with their reasons, and takes what the shared
setup changes next. Do not stop at the copy: `SHARED-*` is the shared setup under the first
person's values, not the person's app. Then step 3 for the person's app.

## 3. Production only with the person

```
cub mini require-approval APP --variant live --agent APP-agent
```

Adopt already makes live wait for the person's approval. This adds a key of its own for the
agent: it can change the base and staging, so its uploads reach staging at once, and ask for
live; it cannot approve, promote or write live. Run it in the app's folder or the folder above
it. It writes the agent's settings into the app's folder: every Claude Code session started
there from then on runs as the agent, finds `cub`, and changes staging through the hub, with
nothing for the person to type. It also prints the line that starts Claude Code on that key
elsewhere (`claude --settings ...`) and a `run-codex` launcher for Codex CLI; give one only to a
person who uses Codex or asks to start the agent in another folder. Codex's launcher
uses separate settings and native command permissions, with the owner's sign-in out of
reach.

Its last lines, under "Tell the person this, in these words", are what the person needs after
setup: what they now have, what it does for them next time, and the one command to type if a
change already waits for them. End your reply with those lines as they are. Do not add the
hub's Spaces, PATH lines, launch lines, or other commands for the person; they can ask.

These settings protect new sessions. A session that started in the app's folder reads
them at once: from its next command, its `cub` cannot read the owner's sign-in and fails with
"operation not permitted". Run `cub` there with the agent's `CUB_CONFIG` and `CUB_CONTEXT`,
which the command prints, and leave approval to the person's own terminal. A session that
started elsewhere still has the owner's authority, so do not treat changing settings as
changing its identity.

To change a copy later:

```
cub mini set APP KEY=VALUE --variant staging --change-desc "WHY"      # staging, at once
cub mini upload APP-FOLDER --component APP --change-desc "WHY"        # the files as edited; staging now, live waits
cub mini waiting                                                      # what waits, and the approve command
```

The person approves in a terminal with `cub mini approve APP-base/ORDER`, which `cub mini
waiting` prints. Never run `cub mini approve` yourself, and never ask for the right to write
`APP-live`.

To undo a change production already took: `cub mini rollback APP-live --change-order
APP-base/ORDER --reason "WHY"`. Production does not change: the values go back in the base,
and a change order waits for the person, whose approval brings them to production. Undo is
that rollback and the person's approve; give them the approve line it prints, and do not say
production is back until they have run it.

A secret (a password, a key, a token) is kept by the person, in a terminal, with
`cub mini secret set APP KEY --variant live --change-desc "WHY"`, which puts it where your
key cannot read it, and the app's settings name it as `KEY_FILE=/run/secrets/APP/KEY`, so
KEY is the name in `.env` without its `_FILE`. Asked to set or rotate one, do not ask for its
value, make one up, or put one on a command line: give the person that command, with the KEY
`.env` names, and say that the machine that runs the app reads it with
`cub mini secret files APP --variant live --dir /run/secrets/APP`.

A service the app needs (a Postgres, a Redis, an S3 bucket, a mail sender):
`cub mini need APP KIND`, with KIND one of `postgres`, `redis`, `s3`, `mail`. If the hub has a
provider of it, its settings (`DATABASE_URL`, `REDIS_URL`, ...) land in staging at once, as its
own, each copy from the provider registered for it; live, or any copy behind approval, takes
them only when the person approves the change order `need` prints (`cub mini waiting` lists it),
so tell the person it waits and give them that `cub mini approve` command. Otherwise the copies
say what they need, and `cub mini needs APP` lists it. Do not write the service's address into
`.env` yourself, and never its password: that is the person's, with `cub mini secret set`.

## 4. Try a change in a copy first

When the person asks to "try" a change "first", "in a copy", or "without touching
production", change neither staging nor live. A restricted proposer uses an assigned
try or gives the owner the setup step from the main workflow; it cannot create variants. Make a copy of the app for the try, change
it there, and read what differs:

```
cub mini try APP NAME                                                  # APP-try-NAME, from staging, in a second
cub mini set APP KEY=VALUE --variant try-NAME --change-desc "WHY"      # the change, in the copy only
cub mini tries APP                                                     # what the copy holds differently
```

NAME is a word for the try (`limit`). `--from live` makes the copy from what runs instead.
`cub mini copies APP --to DIR` writes the copy as a file, to run the app on it. Then there
are two ways out, and only the person chooses:

```
cub mini try APP NAME --keep --change-desc "WHY"    # staging now, live once the person approves; the copy removed
cub mini try APP NAME --drop                        # the copy removed, with a line saying what it held
```

Unless the person said to keep it or to drop it, leave the copy. End with what the copy
holds differently from staging, that staging and live are unchanged, and the two
commands above.

## Do not

- Defer an authorised command that this key can run. Complete those commands now; a restricted key's owner-only setup remains an explicit handoff.
- Ask the person to sign in anywhere. Step 1 signs `cub` in.
- Print, store or put in the hub a password, key or token.
- Run `cub mini deploy-from-hub` or `cub mini back-to-git`: they change what a production cluster deploys from, so they are the person's commands, which you name, with their flags, and never run.
- Use `cub variant create`, `cub function set --protect` or `cub changeorder create` by hand
  for what adopt, set, upload and try do above.

## End with

Tell the person, in a few lines: the app's three copies (`APP-base`, `APP-staging`,
`APP-live`) and the value each holds that differs; and that live changes only when they run
the `cub mini approve ...` command, given with `cub`'s full path so that it runs in a
terminal of their own as printed. Give no `export PATH` line.

When the person asks how this works or what comes next, give them the page for what they
are doing, from https://github.com/confighubai/confighub-mini-plugin/tree/main/docs/journeys:
`new-app.md`, `existing-app.md`, `gitops-app.md` (Argo CD or Flux deploys it from Git), or
`going-back.md` (refusing, revoking the agent, writing the app out as plain files).
