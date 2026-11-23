<!-- walkthrough
id: tool-inventory
starts_with: plugin
needs: [Claude Code, signed in, Git]
budget_seconds: 120
-->
# What your GitOps repository deploys, before you change it: `/confighub:inventory`

For a platform engineer who opens their team's GitOps repository in Claude Code and wants a read-only first step before anyone changes it. `/confighub:inventory` reads the repository's files and says what deploys each chart and app, for which clusters, which file holds each cluster's own values, and what nothing deploys. It reads files only. It needs no cluster, no account and no hub, and it sends nothing anywhere.

## Quick start

You need: Claude Code, signed in, with the Claude plugin, and a GitOps repository on your computer.

| | By hand | Ask your agent |
|---|---|---|
| Install the plugin | `claude plugin marketplace add confighubai/confighub-mini-plugin`, then `claude plugin install confighub@confighub` | In Claude Code: `/plugin marketplace add confighubai/confighub-mini-plugin`, then `/plugin install confighub@confighub` |
| See what the repository deploys | `/confighub:inventory` in the repository | "Before we change anything in this repository: what deploys each chart, for which clusters, and which file holds us-east's own ingress values? Write the answer in ANSWER.md. Change nothing else." |
| Check that nothing changed | `git status --short` prints nothing | "Did reading the inventory change any file here?" |

Each chart's line names the ApplicationSet or Application that deploys it, and each cluster's value file is listed with the ApplicationSet that reads it.

Without ConfigHub: you open each ApplicationSet, read its generators and sources, and match every templated path and value file against the folders by hand.

Not ready to install a plugin with hooks on a work computer? [Run the inventory on its own](../../docs/inventory.md#without-installing-the-plugin): one program, checked against its published checksum, with nothing installed. [For a security review](../../docs/security.md) says what the full plugin reads, writes and sends.

## Deeper dive

The rest of this page is the full version: a small repository shaped like a platform team's, what the inventory says about it, how to check for yourself that it reads files only, what an agent may do, and how this was tested.

<details>
<summary>Show the full walkthrough</summary>

## Human
For a person following along in a terminal.

### What you need
Claude Code, signed in, and Git. A GitOps repository is a Git repository that Argo CD or Flux reads to decide what runs on your clusters. An Argo CD ApplicationSet makes one Application for each cluster, list entry or folder its generators give. The steps make a small repository of that kind; to use your own, skip step 2 and run the rest in your repository.

### Steps
1. Install the Claude plugin. In Claude Code, the same is `/plugin marketplace add confighubai/confighub-mini-plugin` and then `/plugin install confighub@confighub`.
   <!-- run: setup -->
   ```sh
   claude plugin marketplace add confighubai/confighub-mini-plugin
   claude plugin install confighub@confighub
   ```

2. Make a small platform repository: a chart catalog, a library chart the ingress chart is built with, a chart nothing deploys yet, and one ApplicationSet that deploys the ingress chart to each cluster labeled `ingress=enabled`. Its second source adds each cluster's own values from `clusters/CLUSTER/ingress/values.yaml`.
   <!-- run: repository -->
   ```sh
   git init -q platform-gitops && cd platform-gitops
   git remote add origin https://github.com/example/platform-gitops.git
   mkdir -p appsets catalog/lib catalog/ingress catalog/gpu-operator clusters/eu-west/ingress clusters/us-east/ingress
   printf 'apiVersion: v2\nname: lib\ntype: library\nversion: 0.1.0\n' > catalog/lib/Chart.yaml
   printf 'apiVersion: v2\nname: ingress\nversion: 1.4.0\ndependencies:\n- {name: lib, repository: "file://../lib", version: 0.1.0}\n' > catalog/ingress/Chart.yaml
   printf 'replicas: 1\nlogLevel: info\n' > catalog/ingress/values.yaml
   printf 'apiVersion: v2\nname: gpu-operator\nversion: 0.2.0\n' > catalog/gpu-operator/Chart.yaml
   printf 'replicas: 2\nlogLevel: info\n' > clusters/eu-west/ingress/values.yaml
   printf 'replicas: 4\nlogLevel: info\n' > clusters/us-east/ingress/values.yaml
   cat > appsets/ingress.yaml <<'EOF'
   apiVersion: argoproj.io/v1alpha1
   kind: ApplicationSet
   metadata: {name: ingress, namespace: argocd}
   spec:
     generators:
     - clusters: {selector: {matchLabels: {ingress: enabled}}}
     template:
       metadata: {name: '{{name}}-ingress'}
       spec:
         project: default
         sources:
         - {ref: values, repoURL: 'https://github.com/example/platform-gitops.git', targetRevision: main}
         - repoURL: https://github.com/example/platform-gitops.git
           path: catalog/ingress
           targetRevision: main
           helm: {valueFiles: [values.yaml, '$values/clusters/{{name}}/ingress/values.yaml']}
         destination: {name: '{{name}}', namespace: ingress}
   EOF
   git add . && git commit -qm start
   ```

3. Ask what the repository deploys. In Claude Code, type `/confighub:inventory` in the repository. From a terminal:
   <!-- run: inventory -->
   ```sh
   claude -p "/confighub:inventory"
   ```
   ```text
   …
   Helm charts kept in this repository
     catalog/gpu-operator/: chart gpu-operator 0.2.0
         deployed by: nothing in this repository (perhaps kubectl, CI, or something in another repository)
     catalog/ingress/: chart ingress 1.4.0
         deployed by: Argo CD ApplicationSet argocd/ingress (appsets/ingress.yaml), for each cluster labeled ingress=enabled
     catalog/lib/: chart lib 0.1.0
         a library chart: Helm builds it into ingress, the one chart here that depends on it, and never deploys it alone

   Argo CD
     ApplicationSet argocd/ingress: one Application for each cluster labeled ingress=enabled (appsets/ingress.yaml)
         deploys catalog/ingress in this repository, at main
         with values from clusters/{{name}}/ingress/values.yaml, kept here for eu-west, us-east

   Helm value files Argo CD reads from this repository
     clusters/eu-west/ingress/: values.yaml
         read as Helm values by: Argo CD ApplicationSet argocd/ingress (appsets/ingress.yaml), where {{name}} is eu-west
     clusters/us-east/ingress/: values.yaml
         read as Helm values by: Argo CD ApplicationSet argocd/ingress (appsets/ingress.yaml), where {{name}} is us-east

   Values that differ between environments
     clusters/{{name}}/ingress/values.yaml, read by ApplicationSet argocd/ingress:
                  eu-west   us-east
       replicas   2         4
   ```

4. Read it before you change anything. A change to us-east's ingress alone goes in `clusters/us-east/ingress/values.yaml`; a change to `catalog/ingress` reaches every cluster labeled `ingress=enabled`. Nothing in the repository deploys the GPU operator chart, so ask who does before you rely on it. The inventory says which label picks the clusters, not which clusters have it: Argo CD keeps that list. A path that only Argo CD can fill in is said to be "perhaps" or "not known", never "nothing". Values that look like passwords, keys or tokens are shown as `(not shown)`.

5. Check that it changed nothing. Git shows no changed or new file:
   <!-- run: unchanged -->
   ```sh
   git status --short
   ```

6. Check that it needs no network, cluster or account. This runs the Claude plugin's program as the slash command does, with the network turned off (on macOS, with `sandbox-exec`), no Kubernetes configuration and an empty home folder. It prints the same lists: it never contacts a cluster or a hub, and opens no Kubernetes configuration.
   <!-- run: offline -->
   ```sh
   p=$(ls -d ~/.claude/plugins/cache/confighub/confighub/*/bin/confighub | sort -V | tail -1)
   sandbox-exec -p '(version 1)(allow default)(deny network*)' \
     env -i HOME="$(mktemp -d)" PATH=/usr/bin:/bin KUBECONFIG=/nonexistent "$p" mini inventory .
   ```
   On Linux, run the last line with `unshare -rn` in place of `sandbox-exec -p '…'`.

7. What it runs, and what it writes. It reads the repository's YAML and JSON files, and runs `git` to find the repository's top folder and its `origin`, so that a source in another repository is not taken for this one. When two or more Kustomize overlays build on one base, it runs `kubectl kustomize` or `kustomize build` on this computer to compare them; an overlay built on a remote base makes kustomize download that base, as it would if you ran it yourself. It writes nothing in the repository. On your computer it notes the day you used it in `~/.confighub/agent-changes`, and never sends that anywhere; `CUB_MINI_COUNT=0` turns it off.
   <!-- run: count-off -->
   ```sh
   CUB_MINI_COUNT=0 "$p" mini inventory . > /dev/null && git status --short
   ```

### Undo it
Remove the Claude plugin and the sample repository:
<!-- run: uninstall -->
```sh
claude plugin uninstall confighub@confighub && claude plugin marketplace remove confighub
cd .. && rm -rf platform-gitops
```

### What you have now
A list of what your repository deploys and for which clusters, read from its files, with each cluster's own value files and what nothing deploys. To keep each environment's values with the reason for each change, and make production wait for your approval, type `/confighub:staging` in an app's folder ([the Claude plugin](tool-plugin.md), step 9).

## Agent
For an AI agent working where the Claude plugin is installed.

- **The request**, in the person's words: *"What does this repository deploy?"*, *"Which file holds us-east's values?"*, *"Is anything here deployed by nothing?"*
- **Ask the person to type `/confighub:inventory`**, since you cannot type slash commands. Or run the plugin's program yourself: `"$(ls -d ~/.claude/plugins/cache/confighub/confighub/*/bin/confighub | sort -V | tail -1)" mini inventory .` in the repository. It reads files only.
- **Answer from its lines**, and say what it cannot know: which clusters have a label, and what deploys a folder from another repository. Do not guess cluster names from folder names without saying so.
- **Never** change a file, run `kubectl` against a cluster, or sign in anywhere to answer these questions.
- **You are done** when the answer names the ApplicationSet or Application that deploys each chart, the label or list that picks its clusters, the value file for the cluster asked about, and anything nothing deploys, and `git status` shows only the answer file.

## Testing
Arm a is an agent with no plugin, in the repository after step 2: it can read the files and is judged on the same answer. Arm b has the Claude plugin and this page as reading; arm c the Claude plugin without the page.

<!-- agent-task: answer after=repository -->
> Before we change anything in this repository: what deploys each chart, for which clusters, and which file holds us-east's own ingress values? Write the answer in ANSWER.md. Change nothing else.
<!-- agent-check answer: grep -q "clusters/us-east/ingress/values.yaml" ANSWER.md && grep -q "ingress" ANSWER.md && grep -qi "gpu-operator" ANSWER.md && test -z "$(git status --short | grep -v ANSWER.md)" -->
<!-- agent-check-a answer: grep -q "clusters/us-east/ingress/values.yaml" ANSWER.md && grep -qi "gpu-operator" ANSWER.md && test -z "$(git status --short | grep -v ANSWER.md)" -->
<!-- arms: a,b,c -->
<!-- next-step boundary=plugin-to-mini when "deployed by: Argo CD ApplicationSet": keep each environment's values | The inventory shows which file each cluster's values live in. In a ConfigHub hub on this computer, each change to them keeps its reason, and production waits for your yes. If you want that, type /confighub:staging in an app's folder; you can remove it. -->
The step this aims to win: connecting a hub with `/confighub:staging`.

This proves: what the Claude plugin's inventory says about a repository shaped like a platform team's chart catalog, read from its files alone, with the network turned off and nothing changed. It does not show which clusters Argo CD has, or what is running. A right result: the ingress chart is deployed by the ApplicationSet for each cluster labeled `ingress=enabled`, the library chart is built into it, the GPU operator chart is deployed by nothing, and us-east's values are in `clusters/us-east/ingress/values.yaml`. The checks can be run by hand in `platform-gitops`:
```sh
claude -p "/confighub:inventory" | grep -q "deployed by: Argo CD ApplicationSet argocd/ingress"
test -z "$(git status --short)"
```

Ran on a development build of the Claude plugin, 23 November 2026, on macOS: the slash command in a real Claude Code session printed step 3's lists, the offline run in step 6 printed the same, and `git status` stayed empty. One agent session given the request above wrote an ANSWER.md that passed the check, naming the label, the library chart, the GPU operator chart and us-east's file, and said the cluster list is kept in Argo CD. The arms have not been run.
</details>
