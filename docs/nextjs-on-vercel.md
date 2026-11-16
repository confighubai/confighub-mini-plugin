# A Next.js app on Vercel

Build a Next.js app with your agent, try its settings in Vercel Preview, and review the first production delivery when you are ready. ConfigHub keeps the app's setup and its reasons, so you can start the next app from it.

## Quick start

You need: a local hub running with starters switched on, and a Next.js app linked to a disposable Vercel project with `vercel link`.

| | By hand | Ask your agent |
|---|---|---|
| Connect the app | `cub mini adopt . --name APP --live` | Ask it to set up the app so production settings wait for your approval. |
| Change staging | `cub mini set APP APP_BANNER=preview-coral --variant staging --change-desc "Show the coral banner in Preview"` | Your agent can run the same command. |
| Try it in Preview | `vercel deploy --environment preview --env APP_BANNER=preview-coral` | Your agent can run the same command. |
| Review production | `cub mini waiting` | You approve it yourself. |

Without ConfigHub: your agent passes settings to Vercel directly with `vercel deploy`, production included, and the next session has no record of why.

## Deeper dive

The numbered steps below give each command in full, from linking the Vercel project to leaving the first production order for review.

1. Create a Next.js app with `next` in its package dependencies. For a quick check, give it an `/api/settings` route that reads a non-secret setting such as `APP_BANNER` at request time.
2. From the app folder, link the project with `vercel link --yes --scope SCOPE --project APP`. Use a disposable project for this walkthrough. Vercel requires a project's first deployment to use its Production environment. An owner preparing a project can stage a placeholder build with `vercel deploy --prod --skip-domain` to leave the production domain unassigned. [Vercel staged deployments](https://vercel.com/docs/deployments/promoting-a-deployment).
3. Put `APP_BANNER=preview-coral` in `.env.staging` and `APP_BANNER=baseline` in `.env.production`. Keep secrets in your existing secret store, and exclude `.env.local` from deployment uploads.
4. With the local hub running, turn on starters with `export CUB_MINI_STARTERS=on`. Run `cub mini adopt . --name APP --live`. The plan selects `nextjs-vercel` after `vercel` and shows what it adds and what you set yourself.
5. If the app is already connected, set its staging banner with `cub mini set APP APP_BANNER=preview-coral --variant staging --change-desc "Show the coral banner in Preview"`. Check the staging copy with `cub unit data app --space APP-staging`. For this example, look for `APP_BANNER=preview-coral`.
6. Run `vercel deploy --environment preview --env APP_BANNER=preview-coral`. This passes the staging value explicitly. Check the hosted response with `vercel curl /api/settings --deployment PREVIEW_URL`.
7. Run `cub mini waiting`. Leave the `APP-live/connect` order for the owner to review before delivering to production. [Vercel production delivery](../examples/walkthroughs/starter-vercel.md).

For a second app that uses the first app's setup, use `cub mini adopt ./second-app --name SECOND --pattern APP`. Give the second app its own banner and keep the shared settings in the first app's base.
