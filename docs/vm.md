# A service on a VM, fed from the hub

This page is for someone whose service runs on a VM, bare or in a cloud, reads its settings from files such as an `.env` and a `config.toml`, and whose agents change those settings. What you get: the service's files are written from the hub on a timer, only the values a person approved reach them, and the agents hold a hub key and no SSH key.

## What goes wrong without it

An agent with SSH to the VM edits the file and restarts the service; nothing says what it changed or why, and the next agent, or the next deploy, writes over it. An agent without SSH asks you to make the change, and you make it by hand.

## What you end up with

- The service's settings are a Component in a hub, with a copy for each place it runs: `api-staging`, `api-live`.
- On the VM, `cub mini pull` writes a copy's files into the service's directory and restarts the service only when a file changed, every 30 seconds, as a systemd timer. The key it runs with can read that one copy and nothing else.
- A change reaches `api-live` only by a change order a person approved. An agent changes the base with its own key and asks; its own approval is refused.
- A file edited by hand on the VM is named, with what differed, and written over at the next pull.

## The steps

On the laptop, with [confighub mini installed](install-mini.md) and the service's folder uploaded ([a first run](try-confighub-mini.md)):

```
cub variant create live api-base
cub mini require-approval api --variant live --agent bot
cub mini pull-key vm-live api --variant live
```

`pull-key` makes a service account for the VM with the right to read `api-live` and nothing else, and prints the commands for the VM. Copy its private key there, then on the VM, with `cub` and confighub mini unpacked:

```
cub auth login --new-context --private-key=vm-live.jwk --server http://HUB
CUB_CONTEXT=vm-live cub mini pull api --variant live --dir /etc/api --restart "systemctl restart api" --timer 30s
```

A hub on a laptop listens on that machine only; the VM reaches it through a tunnel you open, or through your organization's ConfigHub once the work is copied up. `pull-key` says so when that is the case.

## An app platform on the hub

With a `staging` and a `live` copy, each pulled by its own key, and a restart hook that takes the release the settings name, the same hub is an app platform: an agent proposes a release by its digest, you approve it to staging and then to live, and rollback is one change order given up and demoted. Each step reaches the service within the timer's 30 seconds.

## Verify the service

Pull keeps each file's Unit revision and content hash in `.cub-mini-pull.json` beside it. That is a record of the files on disk, not proof that a running process loaded them. Compare the service's loaded settings with those files as well as checking its health.

Before approving a change, check that live's configuration revision, the VM's files and the service's behavior stay unchanged. After approval and the next successful pull, compare the VM's files with the approved values, check the restart result, and call the service's health endpoint. Compare its reported revision, release digest or loaded settings with what was approved. A successful pull alone does not prove the service restarted or loaded the new values. Exercise the release and rollback path above and check the earlier behavior returns.

[`cub mini` and plain `cub`](cub-mini-and-cub.md) says what each command on this page stands for.
