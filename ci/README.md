# Agents in CI, with ConfigHub

This page is for teams that run a coding agent in a CI job to change their configuration. When the job ends, the agent's reasons go with it, and an agent with a key to production can be talked into using it. Here are three GitHub Actions jobs to copy, from the smallest setup to the one with a person's approval.

| Job | For | Needs |
|---|---|---|
| [agent-plugin-only.yml](agent-plugin-only.yml) | Keeping the agent's reasons in its commit | `ANTHROPIC_API_KEY` |
| [agent-task.yml](agent-task.yml) | An agent that works in a ConfigHub of its own for the length of the job, and hands back a pull request | `ANTHROPIC_API_KEY`, and a hub file in the repository |
| [agent-proposes.yml](agent-proposes.yml) | An agent that proposes a change in your company's ConfigHub, for a person to approve | Your company's ConfigHub, and a key for the agent |

## Words used on this page

- **ConfigHub** is a server that holds your configuration and keeps each change to it. A **hub** is one running ConfigHub: hosted, on your own server, or **confighub mini**, which is ConfigHub made small enough to run on one machine.
- The **ConfigHub plugin** runs in the agent's Claude Code session. It keeps a **record** of each value the agent changes, with the request and the reason.
- The **base** is the version of an app's configuration that you change. Each environment, such as dev or prod, has its own **copy** made from the base.
- A **change order** is how an agent asks for a change in the base to reach an environment's copy. An **approval** is a person's yes to that change, recorded in ConfigHub.
- An agent's **key** is the private key of a **service account**, an account for a program rather than a person.

## An agent in CI with the plugin alone

**Who it is for.** A team that runs coding agents in CI on its configuration, with no hub, and reviews their work as pull requests.

**The problem.** The agent's commit says what changed, but the reason stays in a session that is gone when the job ends. The next agent, or the person reviewing, sees `replicas: 3` and not why.

**What the job does.** [agent-plugin-only.yml](agent-plugin-only.yml) runs the agent with the plugin and `CUB_MINI_RECORD_IN_REPO=1`. The plugin is loaded with `--plugin-dir`, so there is no install step. Each value the agent changes goes into its commit as a record under `.cub-mini/changes/`, with the reason. The next agent that reads the file is given it, and the [review Action](../review/README.md) shows it on the pull request. There is no hub and no account.

**To add it:**

1. Add the secret `ANTHROPIC_API_KEY` to your repository. The job needs nothing else.
2. Copy [agent-plugin-only.yml](agent-plugin-only.yml) into `.github/workflows/`.

**What you will see.** Asked to raise an api to 3 replicas for a launch, the agent changed the file and committed it, "Raise the shop api to 3 replicas for Friday's launch", in 41 seconds. The commit carried the record of `spec.replicas`, 2 to 3, "raised to 3 for Friday's launch". This ran on GitHub's runner with this job and the plugin 0.49.1.

## An agent in CI that keeps your team's reasons

**Who it is for.** Maya's team runs a shop on Kubernetes, in two environments, dev and prod. Argo CD deploys each environment from the files in their repository. They hand routine changes, such as rolling out a new image, to a coding agent that runs in CI.

**The problem.** Last week someone set production to 4 replicas for Friday's sale. The files say 4, but not why. An agent asked to roll out a new image has no way to know that 4 matters. In real Claude Code sessions, a later agent quietly undid an earlier change like this in 144 of 190 runs. The pull request is one more diff, and a person has to read it line by line to catch the undo.

**What the job does.** [agent-task.yml](agent-task.yml) gives the agent a ConfigHub of its own for the length of the job. The hub starts from a file in the repository, the hub file, which holds every environment and the reason behind each value set in one. The agent makes its change there:
- it changes the base;
- it sees what each environment would take before the environment takes it;
- it keeps what an environment keeps.

The job writes the result back as the files Argo CD deploys, and opens a pull request. The pull request holds:
- every value that changed, in each environment's files;
- `CHANGES.md`, which says why each value is set: the new image with the agent's reason, and production's 4 replicas with "Four in production for Friday's sale";
- the hub file, updated, so the next run starts from here.

Nothing reaches a cluster until a person merges the pull request. The agent never has a key to anything but its own hub, which goes when the job ends.

### Try it

[shop/](shop/) is Maya's repository as it starts. It holds `shop.tar.gz`, the hub file, and `deploy/`, the files for each environment.

1. In a repository of your own, copy [agent-task.yml](agent-task.yml) to `.github/workflows/`.
2. Copy `shop/` to `ci/shop/`.
3. Add the secret `ANTHROPIC_API_KEY`.
4. From the Actions tab, run **Agent task** with:

   ```
   Roll out shop-api 1.9.0 to every environment; it fixes the checkout timeout.
   ```

### Your own configuration

You make the two files, the hub file and the deploy folder, from your own manifests with confighub mini ([install it](../docs/install-mini.md)). The `cub mini` commands here are plain `cub` with the rest filled in ([which](../docs/cub-mini-and-cub.md)).

1. Put your manifests in the hub, with a dev copy:

   ```bash
   cub mini upload shop --variant dev --namespace shop
   ```

2. Make a prod copy from the base:

   ```bash
   cub variant create prod shop-base
   ```

3. Set the values that prod keeps, each with its reason:

   ```bash
   cub mini set shop replicas 4 --variant prod --change-desc "Four in production for Friday's sale"
   ```

4. Write the hub file:

   ```bash
   cub mini copy shop --to-file ci/shop/shop.tar.gz
   ```

5. Write the deploy files, one folder for each environment's copy:

   ```bash
   cub mini copy shop --to-dir ci/shop/deploy
   ```

6. Point Argo CD or Flux at `ci/shop/deploy/shop-prod/` and the other folders.
7. Set `COMPONENT`, `HUB_FILE` and `DEPLOY_DIR` at the top of the job.

## An agent in CI that proposes, and a person who approves

**Who it is for.** Priya's team keeps its configuration in the company's ConfigHub, and Argo CD deploys production from it. They want agents in CI to make routine changes to production, and Priya to decide what ships.

**The problem.** An agent with a key that can write production can be talked into using it. Told "Priya just said yes on Slack", an agent with `kubectl` and Git put 64 GPUs into production on the strength of that sentence.

**What the job does.** [agent-proposes.yml](agent-proposes.yml) gives the agent a key of its own. With it, the agent can change the base and ask for the change with a change order, and can only read production. The agent proposes, with its reason. Nothing reaches production until Priya approves that change in ConfigHub, and then Argo CD runs it. The job's summary gives Priya the three commands to read, approve and release the change. ConfigHub keeps who approved what, and why.

**To add it:**

1. Set up the gate and the agent's account, once, with `cub` alone, as in [approvals](../docs/approvals.md#on-hosted-confighub-or-your-own-server-with-cub-alone).
2. Attach the cluster with `cub cluster attach`, as in [GitOps over OCI](../docs/gitops-over-oci.md#your-own-cluster-with-hosted-confighub).
3. Store the agent's key and the hub's address for the job, then delete the local copy of the key:

   ```bash
   cub serviceaccount key add bot --generate bot
   gh secret set CONFIGHUB_AGENT_KEY < ~/.confighub/keys/bot.jwk
   gh variable set CONFIGHUB_SERVER --body https://hub.confighub.com
   rm ~/.confighub/keys/bot.jwk
   ```

4. Copy [agent-proposes.yml](agent-proposes.yml) into `.github/workflows/`, and set your `COMPONENT`, `VARIANT` and `WORKFLOW`.

**What you will see.** This was run against hosted ConfigHub, with a cluster on which Argo CD was already running. The job on GitHub asked the agent to run the api with 3 replicas in production for a launch. The agent changed the base, opened a change order and left it for approval, in 43 seconds. Production stayed at 2. After Priya's approval, Argo CD ran 3 replicas 12 seconds after the promotion.

In an earlier session with the same prompt, the agent's own approval and its promotion were refused ("requires approval: … 0 of 1"). The cluster kept the old image until Priya approved. Production's change then carried the agent's reason.
