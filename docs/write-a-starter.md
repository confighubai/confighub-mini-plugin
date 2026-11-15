# Write and check a starter

A starter gives a kind of app defaults and records why each value was chosen. Start with an app folder you can inspect and a setting the app already reads. Use the [local hub package](install-mini.md) and Python 3 to check your starter on a disposable hub.

## Write the YAML

Save this as `team-api.yaml` in a directory for your starters. This example is for a team's Node APIs that read `API_TIMEOUT_SECONDS` from `.env`. It builds on the packaged Web starter. Change the file checks to fit your app and name the setting your app actually uses.

```yaml
starter: team-api
version: 1
about: A Node API that reads its settings from .env.
after: [web]
looks_for:
  files: [package.json, .env]
owns: [API_]
defaults:
  - key: API_TIMEOUT_SECONDS
    value: "10"
    reason: Bound an API call so a slow dependency frees the worker after ten seconds.
wires:
  approval: live
```

Every starter requires `wires.approval: live`, including a starter without a hosting provider. Keep each match specific enough that an unrelated app will miss at least one check. Give each default a reason the next developer can act on. When an app already sets a value, its own value takes priority. See the [starter fields](starters.md#what-a-starter-is).

## Check it on a disposable hub

Set `MINI` to the unpacked package folder and run this beside `team-api.yaml`:

```sh
"$MINI/examples/starter-check/check" ./team-api.yaml --package "$MINI"
```

The check tries matching and non-matching app folders, checks that a person's values survive adoption, and verifies that connecting again writes nothing. It stops and removes the disposable hub when finished.

For a starter that delivers to a hosting provider, start with the kit's Netlify example. Run the full check against its stand-in with `--check-addon`, which exercises import, delivery of an approved revision, and readback. See the [provider contract and kit example](starters.md#a-new-provider-an-add-on-and-a-starter).

```sh
"$MINI/examples/starter-check/check" \
  "$MINI/examples/starter-check/example-provider/netlify.yaml" \
  --package "$MINI" --check-addon
```

## Ask an agent to write one

> Write a ConfigHub starter for this app using the author guide. Check the files to find an existing setting and a match specific to this app. Keep any value the app already sets. Run the kit against a disposable local hub and tell me which checks passed.

Share the YAML, a small matching app folder, and the check result. Include an example of a folder that should not match when the distinction matters. See [how to contribute](../CONTRIBUTING.md).
