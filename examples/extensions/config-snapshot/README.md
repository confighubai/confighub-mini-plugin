# Read one revision from a small extension

`read.py` is an executable example of an extension using the existing `cub` interface. It reads one unit in one space and writes a JSON snapshot. It does not deploy an app or approve a change.

Run the complete setup, access checks and cleanup from [R4](../../roadmap/README.md#r4-read-a-pinned-revision-from-a-small-extension). To use a previously provisioned reader context:

```sh
CUB_CONFIG=/path/to/reader-config CUB_CONTEXT=reader \
  python3 read.py --space notes-live --unit app --out snapshot.json
```

The owner provisions a scoped reader with `cub mini pull-key extension-reader notes --variant live` and gives the extension only that reader's key. Keep owner credentials outside the extension's environment. A reader has no permission to propose, write or approve. An extension that needs to propose changes needs a separately scoped proposer; it must not receive approval rights.

## Contract v1

```json
{
  "contract": "confighub.config-snapshot/v1",
  "space": "notes-live",
  "unit": "app",
  "revision": 7,
  "sha256": "SHA-256 of the UTF-8 content bytes",
  "content": "PORT=3000\n"
}
```

The fields above are required. `revision` is a positive integer. `content` is the exact UTF-8 data returned by `cub revision data`, including ConfigHub metadata if present. The hash covers those bytes, not the JSON representation. There is no timestamp, so the same coordinates and revision produce identical bytes.

Consumers must check `contract`, validate required fields and verify the content hash. Additive fields may appear within v1; an incompatible field or meaning needs a new contract identifier. This snapshot carries configuration content and coordinates. It does not include blame/history or certify that a revision is approved. The owner's workflow must gate updates to the variant the extension reads.

With no `--revision`, the extension reads the listed head once, validates it and fetches that pinned revision. A concurrent update cannot change which revision is fetched. Use `--revision 7` to retry a known revision. An unknown revision fails; no unversioned fallback is used.

Reads retry at most twice for the listed transient transport/server errors (429, 502, 503, connection refused/reset). Access denial and missing objects fail immediately. Timeouts fail. Errors do not echo potentially private command output.

The output has mode 0600. An identical existing snapshot is an idempotent retry. A different file, symlink or racing writer is never overwritten. Remove the output when no longer needed; it can contain private configuration. The extension creates no hub or credential and has nothing else to uninstall.

## Compatibility and checks

The example uses `cub unit get -o json` and `cub revision data`; the enclosing R4 run checks these against its pinned package. Run the contract boundary tests with:

```sh
python3 -m unittest discover -s .
```

The R4 integration additionally checks that the provisioned key cannot read base, write live or approve, and that the output contains no owner credentials or configuration-directory paths. These checks apply to this example and key, not to every external add-on.
