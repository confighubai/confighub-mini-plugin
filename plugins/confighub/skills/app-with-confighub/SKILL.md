---
name: app-with-confighub
description: Use when the person asks for an app "using ConfigHub" or "with confighub", asks to attach or add ConfigHub to an existing app or folder, wants a staging and a production setup where the agent proposes changes to production and cannot change it without the person, or asks to set, change or rotate a password, key, token or other secret of an app whose folder has a .confighub-app file. Starts a hub on this machine if none answers, and makes the base, staging and production copies with cub mini.
---

# An app with ConfigHub: base, staging, production

A hub is a ConfigHub server. Here it runs on this machine, as two processes, with no account.
The app's settings live there as a base, a staging copy that takes changes at once, and a
live copy (the person's production) that changes only when the person approves. Every
command below was run as written; do not read `cub --help` first.

## 1. Find a hub, or start one

Run `cub space list`. If it answers with a table, use that hub. If it fails, or `cub` is not
installed, run:

```
"${CLAUDE_PLUGIN_ROOT}/bin/confighub" mini get
```

It downloads confighub mini (about 60 MB), starts a hub on this machine and signs `cub` in to
it, in under a minute. Its last lines print the `export PATH="...:$PATH"` line for its `cub`;
run that line in each later command, or use the path directly:
`${CUB_CONFIG:-$HOME/.confighub}/mini/confighub-mini-<version>-<os>-<arch>/bin/cub`.
Do not run `cub auth login`, and do not send the person to hub.confighub.com. Run it again
after a restart to start the hub again.

## 2. Make the app's copies

The app's settings are an env file in its folder: `.env`, with `KEY=VALUE` lines. For a new
app, write the code and its `.env` first (`PORT`, `GREETING`, `LOG_LEVEL`, and so on). For an
existing app, use the files the person has: `.env` (or `app.env`, a compose file's
environment), with `.env.staging` and `.env.production` beside it if they keep them, or a
Terraform folder's `common.tfvars` with `staging.tfvars` and `prod.tfvars`. A Kustomize
repository with overlays (a `base/`, `overlays/staging`, `overlays/prod`) is adopted as it is:
its rendered base becomes the base, and what each overlay changes becomes that copy's own
values. Then, from the folder above the app's:

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

A second app on a hub that already has one starts from the first, not from nothing:

```
cub mini adopt APP-FOLDER --pattern FIRST-APP
```

It gets the first's base as its own base, keeps its own values, and takes what the first
changes next (`cub mini upgrade APP-base/app`). Use it whenever the person asks for another
app "like" one that is here, or with "the same setup"; `cub space list` shows which apps are.

## 3. Production only with the person

```
cub mini require-approval APP --variant live --agent APP-agent
```

Adopt already makes live wait for the person's approval. This adds a key of its own for the
agent: it can change the base and ask, and cannot approve, promote or write live. It prints
the line that starts the agent's sessions on that key (`claude --settings ...`); give that
line to the person as it is.

To change a copy later:

```
cub mini set APP KEY=VALUE --variant staging --change-desc "WHY"      # staging, at once
cub mini upload APP-FOLDER --component APP --change-desc "WHY"        # the files as edited; live waits
cub mini waiting                                                      # what waits, and the approve command
```

The person approves in a terminal with `cub mini approve APP-base/ORDER`, which `cub mini
waiting` prints. Never run `cub mini approve` yourself, and never ask for the right to write
`APP-live`.

A secret (a password, a key, a token) is kept by the person, in a terminal, with
`cub mini secret set APP KEY --variant live --change-desc "WHY"`, which puts it where your
key cannot read it, and the app's settings name it as `KEY_FILE=/run/secrets/APP/KEY`, so
KEY is the name in `.env` without its `_FILE`. Asked to set or rotate one, do not ask for its
value, make one up, or put one on a command line: give the person that command, with the KEY
`.env` names, and say that the machine that runs the app reads it with
`cub mini secret files APP --variant live --dir /run/secrets/APP`.

## Do not

- Write a setup script to run later. Run the commands, now, and show their output.
- Ask the person to sign in anywhere. Step 1 signs `cub` in.
- Print, store or put in the hub a password, key or token.
- Use `cub variant create`, `cub function set --protect` or `cub changeorder create` by hand
  for what adopt, set and upload do above.

## End with

Tell the person, in a few lines: the app's three copies (`APP-base`, `APP-staging`,
`APP-live`) and the value each holds that differs; that live changes only when they run
`cub mini approve ...`; and the `export PATH` line for `cub` if step 1 installed it.
