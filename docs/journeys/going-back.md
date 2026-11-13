# Going back: from a hub to plain files, and removing each part

This page is for anyone who added the ConfigHub plugin, confighub mini or a hub as a source, and wants to undo one step or all of them. Each step can be undone on its own. Nothing here asks you to keep ConfigHub to keep your work: it comes out as plain files, with the reason for each value.

The words on this page, such as *hub*, *base* and *change order*, are explained in [the glossary](../README.md#words).

## What to undo, and how

| What you added | To undo it | What stays |
|---|---|---|
| A change that waits for you | `cub mini refuse APP-base/ORDER --reason "WHY"` | Your reason, which the agent can read |
| A change live already has | Ask the agent to set the value back. It proposes that, and you approve it. Going back is a change like any other | Both changes, with their reasons |
| The agent's key | `cub mini revoke-agent APP-agent`. Its sessions lose their rights at once, those already signed in too. Then delete `.claude/settings.local.json` in the repository, or take out what the agent setup added to it | What the agent did, in the hub |
| Every agent session, at once | `touch ~/.confighub/halt` stops every Claude Code session with the plugin at its next tool call. Remove the file to let them run again | A process an agent already started keeps running |
| The hub as the source for an app on Argo CD or Flux | Write the app back to Git and point the controller at Git again ([hand it back to Git](gitops-app.md#hand-it-back-to-git)) | The same Deployment and pods, and a `CHANGES.md` in Git |
| A hub that starts by itself | For one folder, `cub mini changes --arrival off`. For the machine, `cub mini install --arrival no` | What the hub already holds, until you remove confighub mini |
| confighub mini | Take your apps out as plain files ([below](#take-an-app-out-as-plain-files)), then `cub mini stop`, or `cub mini uninstall --delete-data` | The files you wrote out. Your app's own files, which the hub never changed |
| The plugin | `claude plugin uninstall confighub@confighub` | The record, in `~/.confighub/agent-changes`, removed after 30 days without use. Nothing in your repository, unless you turned on a setting that writes there |

## Take an app out as plain files

1. Write the app's copies as files, one folder for each copy:

   ```bash
   cub mini copy APP --to-dir DIR
   ```

   `--variant live` writes only the live copy and the copies it was made from.

2. Read `DIR/CHANGES.md`. It lists each value changed in the hub, its reason, who changed it and when, and, for live, the change order and who approved it. It starts:

   ```
   # What this directory is

   Configuration written out of a ConfigHub hub (growl-cub) as plain files, one directory for each Space. It is what the hub held when this was written. Nothing here needs the hub.

   Settings files keep their native format, with ConfigHub bookkeeping removed. Have your application read the files for its environment using its normal configuration loader. Kubernetes resources can still be delivered by Argo CD or Flux. Writing these files does not start a service.

   If your repository makes its files from something else, Helm values or Kustomize overlays, those do not know about the changes below. The files here do. To keep working from values or overlays, put the changes you care about back there.
   ```

3. Commit the files where you want them. If your repository makes its files from Helm values or Kustomize overlays, put the changes you want to keep back there, as the file says.

For an app you attached, your own `.env`, `.tfvars` or Kustomize files were never changed by the hub. A change an agent proposed went through those files first. What lives only in the hub is the reasons, the approvals, and any value set with `cub mini set`.

## Remove confighub mini

1. Stop the hub, keeping its data, so that `/confighub:install-mini` can start it again later:

   ```bash
   cub mini stop
   ```

2. Or remove the hub and its data:

   ```bash
   cub mini uninstall --delete-data
   ```

   Without `--delete-data`, it refuses and says what would be lost. A hub holds the record of someone's choices.

3. Delete `.confighub-app` from each app's repository.

## Leave your organization's ConfigHub

`cub mini copy` copies an app between any two hubs your `cub` can reach, base and copies together, with each kept value's reason. It reads the hub it copies from and changes nothing there. To bring an app down to confighub mini, make confighub mini the current `cub` context and run `cub mini copy --from-context ORG APP`, where `ORG` is your organization's context. To disconnect a cluster from ConfigHub, `cub cluster detach CLUSTER` leaves the cluster as it is ([your own cluster](../gitops-over-oci.md#your-own-cluster-with-hosted-confighub)).
