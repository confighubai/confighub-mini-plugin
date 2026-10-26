# An agent in CI that keeps your team's reasons

**Who.** Maya's team runs a shop on Kubernetes, in two environments, dev and prod. Argo CD deploys each from the files in their repository. They hand routine changes, such as rolling out a new image, to a coding agent that runs in CI.

**What goes wrong without it.** Last week someone set production to 4 replicas for Friday's sale. The files say 4, but not why, and the agent asked to roll out a new image has no way to know that 4 matters. In real Claude Code sessions, a later agent quietly undid an earlier change like this in 144 of 190 runs, and the pull request is one more diff that a person has to read line by line to catch it.

**What they get.** [agent-task.yml](agent-task.yml) gives the agent a ConfigHub of its own for the length of the job, started from a file in the repository that holds every environment and the reason behind each value set in one. The agent makes its change there: it changes the base, sees what each environment would take before it takes it, and keeps what an environment keeps. The job writes the result back as the files Argo CD deploys, and opens a pull request. In it:

- every value that changed, in each environment's files;
- `CHANGES.md`, which says why each value is set: the new image with the agent's reason, and production's 4 replicas with "Four in production for Friday's sale";
- the hub file, updated, so the next run starts from here.

Nothing reaches a cluster until a person merges the pull request. The agent never has a key to anything but its own hub, which goes when the job ends.

## Try it

[shop/](shop/) is Maya's repository as it starts: `shop.tar.gz`, the hub file, and `deploy/`, the files for each environment. Copy [agent-task.yml](agent-task.yml) to `.github/workflows/` and `shop/` to `ci/shop/` in a repository of your own, add the secret `ANTHROPIC_API_KEY`, and run **Agent task** from the Actions tab with:

```
Roll out shop-api 1.9.0 to every environment; it fixes the checkout timeout.
```

## Your own configuration

Make the two files from your own manifests with confighub mini ([install it](../docs/install-mini.md)), one folder per environment's copy:

```bash
cub mini upload shop --variant dev --namespace shop
cub variant create prod shop-base
cub mini set shop replicas 4 --variant prod --change-desc "Four in production for Friday's sale"
cub mini copy shop --to-file ci/shop/shop.tar.gz
cub mini copy shop --to-dir ci/shop/deploy
```

and point Argo CD or Flux at `ci/shop/deploy/shop-prod/` and the others. Set `COMPONENT`, `HUB_FILE` and `DEPLOY_DIR` at the top of the job.
