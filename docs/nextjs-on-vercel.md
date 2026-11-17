# A Next.js app on Vercel

Connect an app that already runs on Vercel. Give your agent a staging copy of its settings and review what goes to production.

## Connect and approve with two commands

You need Claude Code with the [ConfigHub plugin](../README.md#install) 0.97.0 or later, a signed-in Vercel CLI, and an app folder already linked to a running Vercel project with `vercel link`. Try this on a disposable project with a readable, non-secret setting such as `APP_BANNER`.

1. **Connect.** In the app folder in Claude Code, type `/confighub:staging`. ConfigHub installs and starts the local hub if needed. **Start a new Claude Code session in the same folder** to pick up the agent’s key.
2. **Ask for a change.** “Set `APP_BANNER` to `coral` in staging. Propose the same change for production and show me the approval command.” This updates the hub’s staging settings. Try them on Vercel with the Preview step below.
3. **Review and deliver.** In your own terminal, paste the printed approval command, such as `~/.confighub/mini/cub mini approve SPACE/ORDER`. On the first delivery you’ll confirm two things:
   - **Approve the change.** Check the old and new values.
   - **Authorize delivery.** Check the Vercel project name. That permission applies to future delivery to the same project. Each production change still needs approval.

When the command reports **Live on Vercel**, ask the agent to check the running app or its settings endpoint for the new value. See [what ran on a real Hobby project](../examples/walkthroughs/starter-vercel.md#testing).

## Use the Next.js starter and try Vercel Preview

Use this path if you’re building a Next.js app from scratch or want the starter’s defaults as a setup you can reuse. You’ll need a [local hub](install-mini.md).

1. Create a Next.js app with `next` in its package dependencies. For a quick check, give it an `/api/settings` route that reads a non-secret setting such as `APP_BANNER` at request time.
2. From the app folder, link the project with `vercel link --yes --scope SCOPE --project APP`. Use a disposable project for this walkthrough. Vercel requires a project's first deployment to use its Production environment. An owner preparing a project can stage a placeholder build with `vercel deploy --prod --skip-domain` to leave the production domain unassigned. [Vercel staged deployments](https://vercel.com/docs/deployments/promoting-a-deployment).
3. Put `APP_BANNER=preview-coral` in `.env.staging` and `APP_BANNER=baseline` in `.env.production`. Keep secrets in your existing secret store, and exclude `.env.local` from deployment uploads.
4. With the local hub running, turn on starters with `export CUB_MINI_STARTERS=on`. Run `cub mini adopt . --name APP --live`. The plan selects `nextjs-vercel` after `vercel` and shows what it adds and what you set yourself.
5. If the app is already connected, set its staging banner with `cub mini set APP APP_BANNER=preview-coral --variant staging --change-desc "Show the coral banner in Preview"`. Check the staging copy with `cub unit data app --space APP-staging`. For this example, look for `APP_BANNER=preview-coral`.
6. Run `vercel deploy --environment preview --env APP_BANNER=preview-coral`. This passes the staging value explicitly. Check the hosted response with `vercel curl /api/settings --deployment PREVIEW_URL`.
7. Run `cub mini waiting` to read what would change in production, then `cub mini approve APP` in your own terminal. The approval puts production’s approved settings live on the Vercel project and prints the deployment. The first time, it asks you once whether approved settings should go to that project from now on. Secrets are left in Vercel as they are. `cub mini deliver APP --compare` writes nothing and says whether the project still holds what you approved. [Vercel production delivery](../examples/walkthroughs/starter-vercel.md).

For a second app that uses the first app's setup, use `cub mini adopt ./second-app --name SECOND --pattern APP`. Give the second app its own banner and keep the shared settings in the first app's base.
