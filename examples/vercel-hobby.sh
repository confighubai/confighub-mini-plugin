#!/usr/bin/env bash
set -euo pipefail
umask 077
export CUB_CONFIG="${CUB_CONFIG:-$HOME/.confighub}"
: "${MINI:?set MINI to the unpacked ConfigHub mini package}"
: "${WALKTHROUGH_VERCEL_SCOPE:?set this to your personal Hobby scope or disposable team project scope}"
if ! cub mini adopt --help 2>&1 | grep -- '--vercel-live' >/dev/null; then
  echo "Use a mini package that lists --vercel-live in cub mini adopt --help." >&2
  exit 2
fi
PROJECT="${WALKTHROUGH_PREFIX:-ch-vercel-$(date +%s)-}shop"
export PROJECT
mkdir "$HOME/vercel-proof"
cd "$HOME/vercel-proof"
mkdir -p shop/api
printf '%s\n' 'module.exports = (_, res) => { res.setHeader("Cache-Control", "no-store"); res.json({cache: Reflect.get(process.env, ["EDGE", "CACHE", "SECONDS"].join("_")) || "baseline"}); };' > shop/api/settings.js
printf 'EDGE_REGION=fra1\n' > shop/.env.production
v() { if [ -n "${WALKTHROUGH_VERCEL_CONFIG:-}" ]; then vercel --global-config "$WALKTHROUGH_VERCEL_CONFIG" "$@"; else vercel "$@"; fi; }
v link --cwd shop --scope "$WALKTHROUGH_VERCEL_SCOPE" --project "$PROJECT" --yes
cleanup() {
  v project delete "$PROJECT" --confirm-name "$PROJECT" --scope "$WALKTHROUGH_VERCEL_SCOPE"
}
trap 'cleanup || printf "Remove the disposable Vercel project %s to finish cleanup.\n" "$PROJECT" >&2' EXIT
v deploy --cwd shop --scope "$WALKTHROUGH_VERCEL_SCOPE" --prod --yes --json > baseline.json
URL=$(jq -er '.deployment.productionUrl // .deployment.url' baseline.json)
case "$URL" in https://*) ;; *) URL="https://$URL";; esac
serves() { curl -fsS --retry 5 --retry-all-errors --retry-delay 2 "$URL/api/settings" | jq -e --arg n "$1" '.cache == $n' >/dev/null; }
serves baseline
cub mini adopt shop --vercel-live
cub mini require-approval shop --variant live --agent shop-proposer
cub space update shop-base --permission View:serviceaccount:shop-delivery --permission ViewChildren:serviceaccount:shop-delivery
CUB_CONFIG="$PWD/reader" cub auth login --new-context --private-key="$CUB_CONFIG/keys/shop-delivery.jwk" --server "$(cub context get -o jq=.coordinate.serverURL)" >/dev/null
READER=$(CUB_CONFIG="$PWD/reader" cub context get -o jq=.name)
deliver() {
  CUB_CONFIG="$PWD/reader" "$MINI/starters/addons/vercel/run" --live --dir "$PWD/shop" --scope "$WALKTHROUGH_VERCEL_SCOPE" --project "$PROJECT" --space shop-live --order "$1" --revision "$2" --context "$READER" --keys EDGE_CACHE_SECONDS --vercel-config "${WALKTHROUGH_VERCEL_CONFIG:-}" apply
}
head_rev() { cub unit get app --space shop-live -o jq=.Unit.HeadRevisionNum; }
approve() {
  if [ -t 0 ]; then cub mini approve "$1"; return; fi
  printf '%s\n' "$1" > "$PWD/owner-approval"
  printf 'Waiting for owner approval of %s\n' "$1"
  for _ in $(seq 1 300); do
    if [ "$1" != shop-live/connect ] && ! cub changeorder get "${1#*/}" --space "${1%/*}" -o jq=.ChangeOrder.State | grep -qx Released; then
      sleep 2; continue
    fi
    if cub attestation list --space "${1%/*}" -o json | jq -e --arg order "$1" 'any(.[]; .Attestation.Type=="Approval" and .Attestation.Result=="Pass" and .Attestation.Claims["confighub.com/change-order"]==$order)' >/dev/null; then return; fi
    sleep 2
  done
  echo "Owner approval timed out" >&2; return 1
}
ship() {
  deliver "$1" "$2" > receipt.json
  expected=$(jq -er .Deployment receipt.json)
  for _ in $(seq 1 15); do
    if v inspect "$URL" --scope "$WALKTHROUGH_VERCEL_SCOPE" --json | jq -e --arg id "$expected" '.id==$id and .readyState=="READY"' >/dev/null && serves "$3"; then
      printf "Vercel serves %s from approved revision %s\n" "$3" "$2"
      jq -c '{Revision, SHA256, Deployment}' receipt.json
      return
    fi
    sleep 2
  done
  echo "Production alias or served setting did not match the delivery receipt" >&2
  v inspect "$URL" --scope "$WALKTHROUGH_VERCEL_SCOPE" --json | jq '{id,readyState}'
  curl -fsS "$URL/api/settings" || true
  return 1
}
propose() {
  printf 'EDGE_CACHE_SECONDS=%s\n' "$1" > shop/.env
  CUB_CONFIG="$CUB_CONFIG-agent-shop-proposer" CUB_CONTEXT=shop-proposer cub mini upload shop --component shop --change-desc "$2"
  ORDER="shop-base/$(cub changeorder list --space shop-base -o json | jq -er --arg why "$2" '[.[].ChangeOrder | select(.Description | startswith($why))] | if length==1 then .[0].Slug else error("expected one proposal") end')"
}
refuses() {
  if deliver "$1" "$2" > refused.log 2>&1; then
    echo "Vercel delivery accepted an unapproved order" >&2
    return 1
  fi
  grep -E 'delivery refused: .*approval|delivery refused: .*completed release' refused.log
}
ORDER=shop-live/connect; REV=$(head_rev)
refuses "$ORDER" "$REV"
serves baseline
echo "Vercel serves the baseline while connect awaits approval"
approve "$ORDER"
ship "$ORDER" "$REV" 60
propose 30 'Prices must show within thirty seconds during the sale'
cub unit data app --space shop-staging | grep -qx EDGE_CACHE_SECONDS=30
cub unit data app --space shop-live | grep -qx EDGE_CACHE_SECONDS=60
refuses "$ORDER" "$((REV+1))"
serves 60
echo "Vercel still serves 60 while the update awaits approval"
approve "$ORDER"; REV=$(head_rev); ship "$ORDER" "$REV" 30
propose 60 'Restore the cache after the sale'
refuses "$ORDER" "$((REV+1))"
serves 30
echo "Vercel still serves 30 while rollback awaits approval"
approve "$ORDER"; REV=$(head_rev); ship "$ORDER" "$REV" 60
cleanup
trap - EXIT
