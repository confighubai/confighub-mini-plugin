# A service on a VM, fed from the hub

This page is for someone whose service runs on a VM, bare or in a cloud, reads its settings from files such as an `.env` and a `config.toml`, and whose agents change those settings. The service's files are written from the hub, only the values a person approved reach them, and the agents hold a hub key and no SSH key to the VM.

The steps, with every command and what it prints, are in the walkthrough [a service that takes its settings from the hub](../examples/walkthroughs/story-14-sam-vm.md), with a folder on your computer standing in for the VM. With a `staging` and a `live` copy, each pulled by its own key, and a restart hook that takes the release the settings name, the same hub is an app platform: [releases you approve and roll back](../examples/walkthroughs/story-16-app-platform.md) shows it. This page adds what changes on a real VM.

## On a real VM

On the laptop, `cub mini pull-key vm-live api --variant live` makes a service account for the VM, with the right to read `api-live` and nothing else, and prints the commands for the VM. Copy its private key there. Then, on the VM, with confighub mini unpacked:

```
cub auth login --new-context --private-key=vm-live.jwk --server http://HUB
CUB_CONTEXT=vm-live cub mini pull api --variant live --dir /etc/api --restart "systemctl restart api" --timer 30s
```

`--timer 30s` makes the pull a systemd timer: every 30 seconds it writes the copy's files into the service's directory, and restarts the service only when a file changed. A file edited by hand on the VM is named, with what differed, and written over at the next pull.

A hub on a laptop listens on that machine only. The VM reaches it through a tunnel you open, or through your organization's ConfigHub once the work is copied up ([from your laptop to a shared hub](from-plugin-to-confighub.md)); `pull-key` says so when that is the case.

The package's [VM service example](../examples/vm-service/README.md) runs the same on an existing Linux VM with user systemd, as a check: real HTTP requests to a staging and a production copy, a failed restart retried, and a rollback that waits for a fresh approval.

## Verify the service

Pull keeps each file's revision and content hash in `.cub-mini-pull.json` beside it. That is a record of the files on disk, not proof that the running process loaded them. After an approval and the next pull, check the restart result and the service's health endpoint, and compare what it reports, its revision, release digest or loaded settings, with what was approved ([verify the result](approvals.md#verify-the-result)).

[`cub mini` and plain `cub`](cub-mini-and-cub.md) says what each command on this page stands for.
