# A Vault secret supplied by the owner and read only by the runtime

9 November 2026: twelve checks passed on real Vault 2.2.1 in development mode, pinned by the image digest in result.json. Calls were scripted; no model session or outside person was evaluated.

The owner reads Vault KV version 1 and supplies its value to cub mini secret set through standard input. The ordinary app settings contain only a file reference; the command does not print the value. The proposal key cannot read or rotate the hub secret. The runtime's key writes the correct value to a mode-0600 file but cannot rotate it. After the owner copies Vault KV version 2, the runtime's next explicit fetch receives the rotated value. Cleanup removes the test's own hub, container, keys and files. No token or secret value is retained in this record.

With Docker, Python 3 and an unpacked mini.13 package:

```sh
python3 ./run /path/to/package /new/record/folder \
  --image hashicorp/vault@sha256:962a92876e168d68eaaa24b0b8b49bbce1cb63024060a67bba95cd158a366fc2
```

This uses the standard [KV v2 API](https://developer.hashicorp.com/vault/api-docs/secret/kv/kv-v2) and existing cub mini secret commands. It is an explicit owner copy and runtime fetch, not a live Vault provider or automatic synchronization. The check uses random fixtures and [development-server mode](https://developer.hashicorp.com/vault/docs/concepts/dev-server); production authentication, TLS, policy, leases and hostile access to the host Docker daemon are not tested. The development-server log is not saved because it prints the root token.
