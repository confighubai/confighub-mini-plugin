# Apply one configuration revision through a delivery add-on

**Experimental.** This page proposes a contract for a small program, an add-on, that takes one approved configuration revision from a hub to a provider outside Kubernetes. It is not part of any release and is not provider support. It has been tried only against stand-ins: the reference add-on here uses a directory of files as its provider. No real provider, such as Vercel, AWS or Daytona, has been used with it.

The add-on extends the [snapshot contract](../config-snapshot/README.md), which reads one pinned revision with a scoped reader key. It adds no server feature and no `cub mini` command.

## The contract

An add-on is one program with three commands:

| Command | What it reads | What it does |
|---|---|---|
| `import` | the provider | Writes `.env.staging` and `.env.production`, for an ordinary `cub mini adopt`. |
| `apply` | the hub copy it is given | Reads the copy's head once, fetches that pinned revision, applies it to the provider and writes a local receipt. `--revision N` retries a known revision. |
| `compare` | the hub copy and the provider | Prints the names of the settings that differ, never their values. Exits 1 when any differ. |

The owner's approval workflow decides what the copy holds. A snapshot does not certify that a revision was approved, and the add-on does not claim it. Approval controls this delivery path only: anyone who can write to the provider directly can bypass it, and `compare` then finds the difference.

## Run the contract tests

The reference add-on, `delivery.sh`, is POSIX shell: it needs `cub` and the standard utilities of macOS or Linux, and nothing else. The tests are the only part that needs Python, its standard library alone, and `jq`, which their stand-in for `cub` uses. They use a directory as the provider and that stand-in as the hub:

```sh
cd examples/extensions/delivery
python3 -m unittest discover -s . -v
```

To test an add-on of your own with the same three commands, name it: `DELIVERY_PROGRAM=/path/to/add-on python3 -m unittest discover -s . -v`. The tests also try inputs written to break a shell program: values with spaces, quotes, `$`, backticks or a newline inside quotes, a value or path that starts with `-`, a name with `=`, a path with spaces, and a provider folder that is a symbolic link.

Each test passes on the reference add-on. Each was also seen to fail with a small fault planted in a copy of the add-on, such as "apply writes to the provider every time" or "a setting named twice is taken".

## Use the reference add-on

The owner gives the add-on a reader key for one copy, never an owner or proposer key:

```sh
sh delivery.sh import --provider-root /private/provider --dir /private/app
# Owner: cub mini adopt /private/app --name api
# Owner: cub mini pull-key delivery-reader api --variant live
CUB_CONFIG=/private/reader-config CUB_CONTEXT=delivery-reader \
  sh delivery.sh apply --provider-root /private/provider \
  --target production --space api-live --unit app --receipt /private/receipt.json
CUB_CONFIG=/private/reader-config CUB_CONTEXT=delivery-reader \
  sh delivery.sh compare --provider-root /private/provider \
  --target production --space api-live --unit app
```

The add-on parses no JSON itself. It reads each value it needs from the hub with `cub ... -o jq=...`, which prints it as one plain line, and reads the revision with `cub revision data` through the [snapshot reader](../config-snapshot/README.md), `read.sh`, which it loads from beside it. The stand-in provider keeps one JSON file per target. `compare` and `import` read that file only in the layout `apply` writes, and refuse any other layout, even valid JSON, rather than guess at it.

Run `apply` as the owner, in CI, or on a timer on the owner's machine. There is no daemon. For a hub on your laptop, the add-on runs on that same machine. A real integration would receive its provider credential only in its own process environment: never in configuration, a receipt, a transcript or an agent session.

## Settings and secrets

Each line of the input is a unique name and one shell-quoted value. Blank lines and comments are allowed. Values over several lines are not part of v1.

A secret is written `NAME=secret://STORE/REFERENCE` and carried only as that reference. A setting with a secret-like name, or a value shaped like a credential, is refused unless it is a reference. The stand-in stores references, never resolves them, and compares secrets by presence only. A provider that cannot accept a reference must refuse it rather than copy a secret's value. A sensitive value that the provider cannot read back cannot be imported.

## What each command promises

- **Import** writes files with mode 0600. It never overwrites a different file or a symbolic link. Writing the same files again is a retry and changes nothing.
- **Apply** is idempotent: when the provider already holds the pinned revision, it makes no provider write. A change made on the provider directly is repaired on the next apply.
- **Apply** never reads the head a second time. An update that races it belongs to the next run.
- **A failed read, an unknown revision or an invalid snapshot** makes no provider change. A transient hub error is retried, within the snapshot contract's limit. A denied read is not retried, and its error output is not repeated.
- **A provider write** must be safe to retry after a lost response.

## The receipt

Each successful apply writes a private local receipt:

```json
{
  "contract": "confighub.delivery-receipt/v1",
  "provider": "directory-stand-in",
  "target": "production",
  "space": "api-live",
  "unit": "app",
  "revision": 7,
  "sha256": "hash of the exact snapshot content",
  "result": "applied"
}
```

`result` is `applied` or `unchanged`. The receipt carries no values and no credential, and it is not an authenticated attestation. It is not written in one step with the provider: if writing the receipt fails after the provider was written, run the same pinned revision again to recover it. Keep the provider state and the receipt outside a public checkout.

The reader key cannot attach the receipt to the hub's revision, so the receipt stays a local file. That keeps the reader read-only.

## What has not been shown

- **A real provider.** Only a directory stand-in. A real integration has to state its own credential boundary and use its provider's CLI or API.
- **A running service.** The stand-in holds settings; nothing restarts or reloads.
- **A person.** In the trials so far, the owner's approval was scripted.

The words on this page, such as *hub*, *base* and *change order*, are explained in [the glossary](../../../docs/README.md#words).
