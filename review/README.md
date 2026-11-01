# Configuration review

On each pull request, a comment with every configuration value the pull request changes, from what to what, and why, where the record the ConfigHub plugin keeps of what agents change says. A value no record explains is shown as such. For each value it replaces, the comment also says what the value was, the commit that set it, by whom, and why, from the commit's message where no record says. It opens with what merging the pull request would undo: a value put back to what an earlier commit changed, and a value an agent set on the cluster, recorded in the repository, that deploying the pull request's files would put back. It reads Kubernetes files, Helm values, Kustomize, Compose, GitHub Actions workflows, settings files, Terraform variables and agent configuration. No hub, no account, nothing leaves the runner but the comment.

```yaml
name: Configuration review
on: pull_request
permissions:
  contents: read
  pull-requests: write
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: confighubai/confighub-mini-plugin/review@v0
```

`@v0` follows every 0.x release; `@v0.41.0` stays on one.

The "why" comes from the records agents with the plugin keep in the repository (`CUB_MINI_RECORD_IN_REPO=1`). Without them, the review still lists each value changed.

For a repository of Kustomize overlays, the comment also says what each overlay the change reaches renders, before and after, value by value: what each value becomes where that overlay is deployed. A change to a shared base shows in each overlay built on it, and not where an overlay patches over it. It renders with `kubectl kustomize`, which GitHub's runners have. Each Flux HelmRelease the change reaches is rendered the same way, with `helm template`, which the runners also have, when its chart is in the repository or comes from a HelmRepository or OCIRepository defined in it, and so is each Argo CD Application whose chart is a folder of the repository or comes from a Helm repository (tested on charts made for the tests, not yet on a real Argo CD estate); the comment says why when one is not rendered, for example a source that needs credentials. A value the chart makes anew each time it renders, such as a random password, is named and not compared.
