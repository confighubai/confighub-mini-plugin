# A Next.js app on Vercel

Connect an app that already runs on Vercel. Give your agent a staging copy of its settings and review what goes to production.

## Connect and approve with two commands

You need Claude Code or Codex CLI with the [ConfigHub plugin](../README.md#install), a signed-in Vercel CLI, and an app folder already linked to a running Vercel project with `vercel link`. Try this on a disposable project with a readable, non-secret setting such as `APP_BANNER`.

1. **Connect.**
   - **Claude Code:** In the app folder, run `/confighub:staging` (or ask `Attach ConfigHub to this Vercel app so production settings wait for my approval`), then **open a fresh Claude Code session** in the same folder to pick up the agent’s scoped key.
   - **Codex CLI:** Ask `Attach ConfigHub to this Vercel app so production settings wait for my approval.` Then open a fresh session with the printed `run-codex` launcher.
2. **Ask for a change.** Ask: `Set APP_BANNER to coral in staging. Propose the same change for production and show me the approval command.` This updates the hub’s staging settings while production waits.
3. **Review and deliver.** In your own terminal, paste the exact command your agent printed, including the name of the change order. On the first delivery you’ll confirm two things:
   - **Approve the change:** verify the old and new values.
   - **Authorize delivery:** confirm the Vercel project name once for future approved deliveries (every production change still requires its own approval).

When the command reports **Live on Vercel**, check your running app or its settings endpoint for the new value. See [what ran on a real Hobby project](../examples/walkthroughs/starter-vercel.md#testing).

## Use the Next.js starter and try Vercel Preview

Use this path when building a Next.js app from scratch, testing on a Vercel Preview deployment before approving production, or sharing the setup with a second app.

<details>
<summary><strong>Step-by-step manual starter &amp; Vercel Preview setup</strong></summary>

You’ll need a [local hub](install-mini.md) on your `PATH`.

1. Create a Next.js app with `next` in `package.json` and an `/api/settings` route that reads a non-secret setting such as `APP_BANNER` at request time.
2. Link a disposable Vercel project: `vercel link --yes --scope SCOPE --project APP`. Vercel requires a project’s first deployment to use Production; you can stage a placeholder build with `vercel deploy --prod --skip-domain` ([Vercel staged deployments](https://vercel.com/docs/deployments/promoting-a-deployment)).
3. Put `APP_BANNER=preview-coral` in `.env.staging` and `APP_BANNER=baseline` in `.env.production`. Keep secrets in your existing secret store and exclude `.env.local` from deployment uploads.
4. Enable starters (`export CUB_MINI_STARTERS=on`) and run `cub mini adopt . --name APP --live`. The plan applies `nextjs-vercel` after `vercel` and leaves values you already set untouched.
5. Update staging when needed: `cub mini set APP APP_BANNER=preview-coral --variant staging --change-desc "Show the coral banner in Preview"` (inspect with `cub unit data app --space APP-staging`).
6. Test on a Vercel Preview URL: `vercel deploy --environment preview --env APP_BANNER=preview-coral`, then verify with `vercel curl /api/settings --deployment PREVIEW_URL`.
7. Inspect pending production changes with `cub mini waiting`, then review the exact production order in your own terminal. Check the proposed value and the Vercel project before authorizing delivery. A staging-only edit creates no production proposal. Ask for that proposal when you want to ship it. Run `cub mini deliver APP --compare` at any time to check for drift ([Vercel production delivery](../examples/walkthroughs/starter-vercel.md)).

**Second app from the same setup:** Run `cub mini adopt ./second-app --name SECOND --pattern APP` to reuse the shared settings while giving the second app its own `APP_BANNER` and approval gate.

</details>
