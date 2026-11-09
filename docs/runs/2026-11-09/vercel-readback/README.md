# Vercel project-setting read-back

The plugin can show three distinct facts: an agent recorded `RATE_LIMIT_PER_MIN` set to 600 for Tuesday’s launch, the Vercel project setting now says 900, and `.env.local` says 60. The [retained output](production.txt) and [ten passing contract checks](result.json) show this distinction.

In your linked app, request it explicitly:

```sh
/path/to/plugins/confighub/bin/confighub mini changes --why RATE_LIMIT_PER_MIN --vercel production
```

With confighub mini 0.10.7-mini.14 or later, `cub mini changes` accepts the same flags. Use `--dir APP` from elsewhere, or choose `preview` or `development`. Your installed, signed-in Vercel CLI supplies access; the nearest `.vercel/project.json` within the Git repository supplies explicit project and organization IDs. Normal history and hooks make no service request.

The read-back calls `vercel env ls --environment ENV --json --project ID --scope ORG`. It withholds credentials, values marked secret and their known aliases, compares the linked app’s top-level env files, and retains no downloaded file or snapshot. CLI responses are bounded to 1 MiB in memory and the request to 20 seconds. Errors return no inferred or cached value, and do not repeat raw CLI output. Values in local files use the existing parser, without shell expansion; inaccessible or oversized local files are omitted.

Reproduce the contract check without an account:

```sh
python3 docs/runs/2026-11-09/vercel-readback/run /path/to/plugins/confighub /new/record/folder
```

It runs the actual plugin with scripted hooks and a local CLI fixture. It checks project/environment selection, different history/current/local values, redaction, preview isolation, refetch, error handling and unchanged files and recorded entries. Only its disposable files are removed. The [check output](check.txt) and [withheld fields](redacted.txt) are retained.

The installed Vercel CLI inspected was 65.12.1; `whoami` reported logged out. The fixture follows the [official CLI JSON output](https://github.com/vercel/vercel/blob/84878e532142f0ac584953695658b324eb9e5b80/packages/cli/src/commands/env/ls.ts) and [secret metadata](https://github.com/vercel/vercel/blob/84878e532142f0ac584953695658b324eb9e5b80/packages/cli/src/util/env/env-var-config-secret-ui.ts). This is not a signed-in service proof, a model session or outside-user evidence. It reads project settings, not the environment of a running deployment. Custom environments, branch-specific preview settings and other hosted providers are not read back. Earlier history is not rewritten by read-back.
