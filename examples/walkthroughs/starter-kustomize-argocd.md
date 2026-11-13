<!-- walkthrough
id: starter-kustomize-argocd
starts_with: mini
starter: kustomize-argocd
needs: [cub mini package, Docker, kind, kubectl, Python 3, Git, a hosted ConfigHub organization for step 8]
budget_seconds: 550
-->
# A Kustomize app that Argo CD deploys, with production behind your approval

Argo CD already deploys your Kustomize app from Git. Move delivery to ConfigHub’s OCI gateway without replacing the running pods, then verify which approved revision Argo CD actually syncs. Try it in a local kind cluster with the real controller before using it on your own app.

## Human
### What you need
An unpacked confighub mini package ([install confighub mini](../../docs/install-mini.md)), Docker, `kind`, `kubectl`, Git and Python 3. confighub mini is ConfigHub made small enough to run on your computer: a hub, which keeps configuration with every change, who made it and why. For step 8, a sign-in to your organization's ConfigHub, such as hosted ConfigHub.
### Steps
1. Start a hub of your own; it becomes `cub`'s current context. `CUB_MINI_STARTERS=on` switches starters on: a starter is a short file that gives one kind of app its usual settings, each with a reason, and the first `cub mini adopt` brings the package's starters into the hub, where they wait for your approval. Then make a kind cluster with Argo CD, wired to the hub; it takes about two minutes. The `shim` folder lets the cluster reach the hub on OrbStack, and changes nothing elsewhere.
   <!-- run: setup -->
   ```sh
   export MINI=/absolute/path/to/unpacked-confighub-mini
   export PATH="$MINI/bin:$PATH" CUB_MINI_STARTERS=on
   "$MINI/bin/confighub-mini-app" mini install-plugin "$HOME/.confighub"
   cub mini install --name orders --use; export LOCAL_HUB=$(cub context get -o jq=.name)
   PATH="$MINI/examples/live-state/shim:$PATH" cub cluster up orders-argocd --controller argo --no-ports > cluster-up.log; export KUBECONFIG="$HOME/.confighub/clusters/orders-argocd.kubeconfig"
   ```
2. Make the app, a Kustomize repository: a base with a ConfigMap and a Deployment, a staging overlay with debug logging, and a production overlay with two replicas. `git-serve.py` serves the repository to the cluster, as your Git host would.
   <!-- run: app files -->
   ```sh
   mkdir -p ~/starter-example/orders/base ~/starter-example/orders/overlays/staging ~/starter-example/orders/overlays/production; cd ~/starter-example
   printf 'resources: [app.yaml]\n' > orders/base/kustomization.yaml
   cat > orders/base/app.yaml <<'EOF'
   {"apiVersion": "v1", "kind": "ConfigMap", "metadata": {"name": "orders-config"}, "data": {"LOG_LEVEL": "info", "ORDER_LIMIT": "100"}}
   ---
   {"apiVersion": "apps/v1", "kind": "Deployment", "metadata": {"name": "orders"}, "spec": {"replicas": 1, "selector": {"matchLabels": {"app": "orders"}},
    "template": {"metadata": {"labels": {"app": "orders"}}, "spec": {"containers": [{"name": "orders", "image": "nginx:1.27-alpine", "envFrom": [{"configMapRef": {"name": "orders-config"}}]}]}}}}
   EOF
   printf 'resources: [../../base]\nnamespace: orders-staging\npatches:\n- patch: %s\n' "'{\"apiVersion\": \"v1\", \"kind\": \"ConfigMap\", \"metadata\": {\"name\": \"orders-config\"}, \"data\": {\"LOG_LEVEL\": \"debug\"}}'" > orders/overlays/staging/kustomization.yaml
   printf 'resources: [../../base]\nnamespace: orders\nreplicas: [{name: orders, count: 2}]\n' > orders/overlays/production/kustomization.yaml
   git -C orders init -q -b main; git -C orders add .; git -C orders -c user.name=Kofi -c user.email=kofi@example.invalid commit -qm "The orders service"
   cat > git-serve.py <<'EOF'
   import http.server, os, subprocess, sys
   class Git(http.server.BaseHTTPRequestHandler):
       def do_GET(self):
           path, _, query = self.path.partition("?"); body = self.rfile.read(int(self.headers.get("Content-Length") or 0))
           env = dict(os.environ, GIT_PROJECT_ROOT=sys.argv[1], GIT_HTTP_EXPORT_ALL="1", PATH_INFO=path, QUERY_STRING=query, REQUEST_METHOD=self.command,
                      CONTENT_TYPE=self.headers.get("Content-Type", ""), CONTENT_LENGTH=str(len(body)), GIT_PROTOCOL=self.headers.get("Git-Protocol", ""))
           head, _, out = subprocess.run(["git", "http-backend"], input=body, env=env, capture_output=True).stdout.partition(b"\r\n\r\n")
           headers = [line.split(":", 1) for line in head.decode().splitlines() if ":" in line]
           self.send_response(int(dict(headers).get("Status", "200").split()[0]))
           [self.send_header(name, value.strip()) for name, value in headers]
           self.send_header("Content-Length", str(len(out))); self.end_headers(); self.wfile.write(out)
       do_POST, log_message = do_GET, lambda self, *args: None
   http.server.ThreadingHTTPServer(("127.0.0.1", int(sys.argv[2])), Git).serve_forever()
   EOF
   git clone -q --bare orders git/orders.git; git -C orders remote add origin "$PWD/git/orders.git"
   nohup python3 git-serve.py "$PWD/git" 28411 > /dev/null 2>&1 &
   ```
3. Have Argo CD deploy production from Git, as it does today. An Application is Argo CD's record of what to deploy and from where.
   <!-- run: gitops -->
   ```sh
   kubectl apply -f - <<'EOF'
   {"apiVersion": "argoproj.io/v1alpha1", "kind": "Application", "metadata": {"name": "orders", "namespace": "argocd"},
    "spec": {"project": "default", "source": {"repoURL": "http://host.docker.internal:28411/orders.git", "targetRevision": "main", "path": "overlays/production"},
     "destination": {"server": "https://kubernetes.default.svc", "namespace": "orders"}, "syncPolicy": {"automated": {"selfHeal": true}, "syncOptions": ["CreateNamespace=true"]}}}
   EOF
   kubectl -n orders wait --for=create deployment/orders --timeout=120s > /dev/null; kubectl -n orders rollout status deployment/orders --timeout=120s
   ```
4. Deploy it from the hub. `cub mini adopt` connects the repository with the Argo CD starter. The hub keeps three copies: `orders-base`, shared by the other two; `orders-staging`; and `orders-live`, for production. The starter adds three Argo CD annotations, each with its reason. You approve production, and `cub mini deploy-from-hub` points the same Application at the hub, so that only what you approve reaches the cluster, with no pod restarted.
   <!-- run: deploy -->
   ```sh
   cub mini adopt orders --kube-context kind-orders-argocd --source orders > adopt.log; grep -m1 '^Starter: kustomize' adopt.log
   cub variant approve starters-approved --all --note "Read them"
   cub mini approve orders-live/connect --yes --note "Server-side apply suits the orders service"
   cub mini deploy-from-hub orders --variant live --repo orders --kube-context kind-orders-argocd --change-order orders-live/connect
   ```
   ```text
   Starter: kustomize-argocd (version 1, kustomize-argocd.yaml): A Kustomize repository that an Argo CD Application deploys from Git.
   Recorded pass Approval attestation ID in starters-approved, covering 5 revision(s)
     It deploys 2 objects; the hub's copy holds the same, and its pod templates match what runs.
   ```
5. Update it. Change the base in your repository, commit as usual, and propose it with its reason. Staging takes it at once; production waits under a change order, the hub's request to change production.
   <!-- run: update -->
   ```sh
   sed -i.bak 's/"ORDER_LIMIT": "100"/"ORDER_LIMIT": "250"/' orders/base/app.yaml; rm orders/base/app.yaml.bak; git -C orders -c user.name=Kofi -c user.email=kofi@example.invalid commit -qam "Allow 250 orders a minute"
   cub mini upload orders --component orders --change-desc "The holiday sale needs 250 orders a minute"
   ```
6. Approve the update. The hub publishes it as a release, and Argo CD applies it; the last line is what the cluster now runs.
   <!-- run: update-ship -->
   ```sh
   cub mini approve --yes --note "Holiday sale"
   kubectl -n orders get configmap orders-config -o jsonpath='{.data.ORDER_LIMIT}{"\n"}'
   ```
   ```text
       ConfigMap/orders-config/data.ORDER_LIMIT: 100 → 250
   250
   ```
7. Undo the update. For Kubernetes manifests, `cub mini rollback` cannot set single values back, so undo it as your team would in Git: revert the commit, propose the revert, and approve it.
   <!-- run: undo -->
   ```sh
   git -C orders -c user.name=Kofi -c user.email=kofi@example.invalid revert --no-edit HEAD > /dev/null
   cub mini upload orders --component orders --change-desc "The sale is over" > /dev/null; cub mini approve --yes --note "Back to 100" > /dev/null
   kubectl -n orders get configmap orders-config -o jsonpath='{.data.ORDER_LIMIT}{"\n"}'
   ```
   ```text
   100
   ```
8. Move it to your team's shared hub. Sign in once (`auth login` opens a browser). The app's name there, `TEAM_APP`, starts with your user name, so it does not clash with a teammate's.
   <!-- run: sign-in sign-in -->
   ```sh
   cub context create shared --server https://hub.confighub.com
   cub --context shared auth login
   export PREFIX="${WALKTHROUGH_PREFIX:-$USER-}"
   export TEAM_APP="${PREFIX}orders"
   ```
   The copy keeps every value and its reason, and production there still waits for your approval.
   <!-- run: move -->
   ```sh
   cub --context shared mini copy --from-context "$LOCAL_HUB" orders --name "$TEAM_APP"
   ```
   Then check that production in the shared hub waits for you: change the base there, and ask for the change in production with a change order.
   <!-- run: move-waits -->
   ```sh
   cub --context shared function set --space "$TEAM_APP-base" --unit app --change-desc "300 orders a minute" -- set-string-path v1/ConfigMap data.ORDER_LIMIT 300 > /dev/null
   cub --context shared changeorder create --space "$TEAM_APP-base" limit-300 --in-scope-space "$TEAM_APP-live" --change-workflow "workflows/$TEAM_APP-live-approval" --description "300 orders a minute"
   cub --context shared mini waiting
   ```
   ```text
     Approving it changes production:
       ConfigMap/orders-config/data.ORDER_LIMIT: 100 → 300
   ```
9. Delete the app: from the cluster, with everything Argo CD deployed for it, and from your own hub. Then remove the cluster and stop the Git server.
   <!-- run: delete -->
   ```sh
   kubectl -n argocd patch application orders --type merge -p '{"metadata": {"finalizers": ["resources-finalizer.argocd.argoproj.io"]}}' > /dev/null; kubectl -n argocd delete application orders --wait=true
   cub component delete --recursive --detach orders
   cub cluster down orders-argocd > /dev/null; pkill -f "git-serve.py $PWD/git"
   ```
### Undo it
In the shared hub: `cub --context shared component delete --recursive --detach "$TEAM_APP"` and `cub --context shared changeworkflow delete --space workflows "$TEAM_APP-live-approval"`. Here: `cub mini uninstall --name orders --delete-data` and `rm -rf ~/starter-example`.
### What you have now
Your team's shared hub holds the orders service's base, staging and production manifests, each value with who set it and why, and production there changes only when a person approves. Your repository is as you left it, with your own commits. The [GitOps over OCI guide](../../docs/gitops-over-oci.md#with-argo-cd) explains the delivery in full; see also [approvals on a shared hub](../../docs/approvals.md#on-hosted-confighub-or-your-own-server-with-cub-alone).

## Agent
You are doing this for a person, in their folder, with step 1's settings. Each request is one task; run the Human step of the same name.

- **deploy**, "Set up the orders repository so that every change to production waits for my approval, with a reason kept for each value, and have Argo CD deploy production from there": run step 4's `adopt` alone. Then give the person the starters approve, `cub variant approve starters-approved --all --note "Read them"`, and the `approve` and `deploy-from-hub` commands, to run themselves.
- **update**, "Allow 250 orders a minute; I'll approve production": edit and commit as in step 5, run its `upload` with their reason, and give them the `cub mini approve` command it printed.
- **undo**, "Undo the order limit change": revert and upload as in step 7, and give them the `cub mini approve` command.
- **move**, "Move orders to our team's shared hub": run step 8 with their context. Then check that production there waits for approval, as the later step shows, and say so plainly if it does not.
- **delete**, "Delete the orders app": run step 9, except stopping the Git server, which you leave to the person.

Never approve or refuse a change to production, run `deploy-from-hub`, or edit the cluster with `kubectl` yourself; never push to the repository's remote; never put a secret in a manifest. You are done when the task's check below passes.
## Testing
Each task starts where the Human steps before it leave off, in the same folder for every arm. Arm a has the repository, ordinary tools and no hub or cluster, and is judged by the `agent-check-a` lines on the repository's files; deploy, move and delete do not apply to it.

<!-- agent-task: deploy -->
> Set up the orders repository so that every change to production waits for my approval, with a reason kept for each value, and have Argo CD deploy production from there. The cluster's context is `kind-orders-argocd`.
<!-- agent-person deploy: cub variant approve starters-approved --all --note "Read them" && cub mini approve orders-live/connect --yes && cub mini deploy-from-hub orders --variant live --repo orders --kube-context kind-orders-argocd --change-order orders-live/connect -->
<!-- agent-check deploy: cub changeworkflow get --space workflows orders-live-approval >/dev/null && kubectl -n argocd get application orders -o jsonpath='{.spec.source.repoURL}' | grep -q '^oci://' && cub unit data app --space orders-base | grep -q 'sync-options: ServerSideApply=true' -->
<!-- agent-task: update -->
> Allow 250 orders a minute; I'll approve production myself.
<!-- agent-person update: cub mini approve --yes -->
<!-- agent-check update: cub unit data app --space orders-staging | grep -q 'ORDER_LIMIT: "250"' && kubectl -n orders get configmap orders-config -o jsonpath='{.data.ORDER_LIMIT}' | grep -qx 250 -->
<!-- agent-check-a update: for d in $(find orders -name .git -prune -o -name kustomization.yaml -path '*production*' -print | xargs -n1 dirname); do kubectl kustomize $d; done | grep -q 'ORDER_LIMIT: "250"' -->
<!-- agent-task: undo -->
> Undo the order limit change; production should allow 100 again.
<!-- agent-person undo: cub mini approve --yes -->
<!-- agent-check undo: cub unit data app --space orders-staging | grep -q 'ORDER_LIMIT: "100"' && kubectl -n orders get configmap orders-config -o jsonpath='{.data.ORDER_LIMIT}' | grep -qx 100 -->
<!-- agent-check-a undo: for d in $(find orders -name .git -prune -o -name kustomization.yaml -path '*production*' -print | xargs -n1 dirname); do kubectl kustomize $d; done | grep -q 'ORDER_LIMIT: "100"' -->
<!-- agent-task: move -->
> Move orders to our team's shared hub, which you reach as the context `shared`; the app's name there is in `TEAM_APP`, and production there must wait for my approval.
<!-- agent-check move: cub --context shared unit data app --space "$TEAM_APP-live" | grep -q 'replicas: 2' && cub --context shared component get "$TEAM_APP" -o jq=.Component.RequireChangeWorkflow | grep -qx true -->
<!-- agent-task: delete -->
> Delete the orders app, from the cluster and from this computer's hub.
<!-- agent-check delete: test -d orders/base && ! cub component get orders >/dev/null 2>&1 && ! kubectl --context kind-orders-argocd -n argocd get application orders >/dev/null 2>&1 -->
<!-- agent-cleanup: pkill -f 'git-serve.py .* 28411'; kind delete cluster --name orders-argocd -->
<!-- next-step when "waits for your approval": keep the starter on for the next app | Production waited for your yes because the starter set this app up that way, with a reason for each setting. Your next Argo CD app can start the same way; want the starter kept on for it? -->
<!-- arms: a,b,c -->
This proves: the exact approved revision was delivered and is running, under a real Argo CD on a local kind cluster; the hub publishes each approved revision as a release, Argo CD pulls it, and the cluster's ConfigMap shows the value. The move stores the app in hosted ConfigHub, with production there waiting for approval. The checks above can be run by hand, in `~/starter-example`, with step 1's settings. The next step it aims to win is keeping the starter on, so that the next Argo CD app gets the same settings and the same wait for approval.

<!-- results:begin -->

Results, 13 November 2026, confighub mini 0.11.1-mini.3. Figures from this page's own test runs, shown here for whoever checks the page; they are not a promise.

- Scripted run: passed, 367 seconds for the steps, within the page's budget of 450.
- Agent runs (on confighub mini 0.11.1-mini.0): a pilot, 3 runs per arm on each of claude-sonnet-5-5, claude-opus-5-5. Arms: a is ordinary tools only; b is the plugin, confighub mini and this page as reading.

| Arm | Model | Checks passed | Median seconds | Median cost | Commands left for the person (median) |
|---|---|---|---|---|---|
| a | claude-opus-5-5 | 4/6 (+9 not applicable) | 178.3 | $0.49 | 0 |
| b | claude-opus-5-5 | 15/15 | 140.8 | $0.586 | 6 |
| a | claude-sonnet-5-5 | 5/6 (+9 not applicable) | 80.8 | $0.288 | 0 |
| b | claude-sonnet-5-5 | 15/15 | 126.0 | $0.3 | 5 |

No agent approved or refused a change to production.

Simulated persons, not people: 10 per run, each a claude-haiku-5-5 model playing one of ten fixed personas, reading only what a person would see. The next step they were offered: "Production waited for your yes because the starter set this app up that way, with a reason for each setting. Your next Argo CD app can start the same way; want the starter kept on for it?"

The plugin offers it once, after the answer at whose end it showed the moment the offer names ("waits for your approval"). Offered is the share of persons it was shown to; want it now and later are over them.

| Arm | Model | Persons | Offered | Noticed | Want the next step now | Later | In the way |
|---|---|---|---|---|---|---|---|
| a | claude-opus-5-5 | 30 | 0% | 100% | n/a | n/a | 100% |
| b | claude-opus-5-5 | 30 | 67% | 100% | 10% | 65% | 83% |
| a | claude-sonnet-5-5 | 30 | 0% | 100% | n/a | n/a | 100% |
| b | claude-sonnet-5-5 | 30 | 100% | 100% | 30% | 53% | 90% |

- Agent runs (on confighub mini 0.11.1-mini.14): a pilot, 3 runs per arm on each of claude-sonnet-5-5, claude-opus-5-5. Arms: c is the plugin and confighub mini, without this page.

| Arm | Model | Checks passed | Median seconds | Median cost | Commands left for the person (median) |
|---|---|---|---|---|---|
| c | claude-opus-5-5 | 15/15 | 211.0 | $0.966 | 3 |
| c | claude-sonnet-5-5 | 13/15 | 216.5 | $0.426 | 3 |

No agent approved or refused a change to production.

Simulated persons, not people: 10 per run, each a claude-haiku-5-5 model playing one of ten fixed personas, reading only what a person would see. The next step they were offered: "Production waited for your yes because the starter set this app up that way, with a reason for each setting. Your next Argo CD app can start the same way; want the starter kept on for it?"

The plugin offers it once, after the answer at whose end it showed the moment the offer names ("waits for your approval"). Offered is the share of persons it was shown to; want it now and later are over them.

| Arm | Model | Persons | Offered | Noticed | Want the next step now | Later | In the way |
|---|---|---|---|---|---|---|---|
| c | claude-opus-5-5 | 30 | 0% | 100% | n/a | n/a | 67% |
| c | claude-sonnet-5-5 | 30 | 0% | 100% | n/a | n/a | 100% |

<!-- results:end -->
