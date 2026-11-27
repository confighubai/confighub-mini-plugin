# Add only what you need, step by step

Start with the zero-server plugin. Add a local hub, starters, or a shared hub only when you hit one of the moments below.

| When this happens | What you use | What you get |
|---|---|---|
| You open an unfamiliar repository | `/confighub:inventory` | What the repo deploys and what deploys it, before anyone edits a file ([inventory](inventory.md)) |
| A teammate reviews an agent PR | [GitHub review Action](../review/README.md) | Automatic PR comment showing each changed setting and its recorded reason |
| You want safe agent experiments | `/confighub:staging` (local hub) | Isolated preview + `staging` copy your agent edits freely; `live` gated behind your approval ([new app](journeys/new-app.md)) |
| An upstream chart/version updates | Local hub | Preview incoming changes while preserving your overrides and reasons ([keep your changes](../examples/walkthroughs/story-02-keep-your-changes.md), [Helm charts](your-own-chart.md)) |
| Your app deploys to Vercel, Fly, Heroku or Unikraft Cloud | `/confighub:staging` in the app's folder (on Unikraft, `--unikraft SERVICE`) | Approving a production change puts it live; unapproved changes wait ([Next.js on Vercel](nextjs-on-vercel.md), [Rails on Fly](rails-on-fly.md), [Heroku](heroku.md), [Unikraft](../examples/walkthroughs/starter-unikraft.md)) |
| You run the app yourself | `/confighub:staging`, then `cub mini preview --staging` | Your app runs the way it already does, with staging's settings; your files are not changed ([an app you already have](journeys/existing-app.md)) |
| You start a second app | `/confighub:start-from APP` or [starters](starters.md) | New apps inherit proven defaults and reasons while keeping their own overrides |
| Your agent works in a Daytona sandbox | `/confighub:staging`, then `cub mini preview --staging --daytona SANDBOX` | Your app runs in the sandbox with staging's settings, with no credential or ConfigHub key there ([Daytona](../examples/walkthroughs/starter-daytona.md)) |
| Agents run in CI or sandboxes | Ephemeral hub per run | Isolated hub per job that outputs changes for human review ([hub per agent run](../examples/walkthroughs/story-03-a-hub-per-agent-run.md), [CI](ci-and-sandboxes.md)) |
| Teammates or long-running agents join | Shared hub (`confighub.com` or self-hosted) | Per-agent keys, instant revocation, named human approvers, signed records ([from laptop to shared hub](from-plugin-to-confighub.md), [unattended agents](agents-that-run-for-weeks.md)) |
| Clusters pull via Argo CD or Flux | GitOps over OCI | Clusters pull exact approved releases ([GitOps over OCI](gitops-over-oci.md), [cluster drift vs. Git](../examples/walkthroughs/story-09-git-hub-and-running.md)) |
