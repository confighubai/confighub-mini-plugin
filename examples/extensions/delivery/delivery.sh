#!/bin/sh
# A delivery add-on against a directory stand-in, not a real provider.
#
#   delivery.sh import  --provider-root DIR --dir APP [--staging T] [--live T]
#   delivery.sh apply   --provider-root DIR --target T --space S [--unit U] [--revision N] --receipt FILE
#   delivery.sh compare --provider-root DIR --target T --space S [--unit U] [--revision N]
#
# The owner gates the copy being read. A snapshot itself does not certify
# approval. Only a scoped reader is needed; no operation proposes or approves a
# change. POSIX sh and standard utilities only, beside cub: no JSON parser.
# Values from the hub come from cub's own -o jq= output, one plain line each.
# The provider stand-in keeps one JSON file per target, in the one layout this
# add-on writes; compare and import read that layout and refuse any other.

here=$(cd -- "$(dirname -- "$0")" && pwd) || exit 1
CONFIG_SNAPSHOT_SOURCED=1
# shellcheck source-path=SCRIPTDIR source=../config-snapshot/read.sh
. "$here/../config-snapshot/read.sh"

PROVIDER_NAME='directory-stand-in'
FAILED='Delivery operation failed; check the scoped reader, target and private local files.'

# Reads environment settings from a revision's content, one per line, and
# prints NAME<TAB>P<TAB>VALUE for a plain value or NAME<TAB>S<TAB>REFERENCE for
# a secret reference, each JSON-encoded. The value is read the way Python's
# shlex.split(value, comments=True) reads it, and must be one word. Exits
# non-zero on anything it refuses; prints no value in its refusal.
# shellcheck disable=SC2016 # awk's or jq's own $, not the shell's
SETTINGS_AWK='
function rep(cls, n,   s, i) { s = ""; for (i = 0; i < n; i++) s = s cls; return s }
function h4(n) { return substr(hx, int(n / 4096) % 16 + 1, 1) substr(hx, int(n / 256) % 16 + 1, 1) substr(hx, int(n / 16) % 16 + 1, 1) substr(hx, n % 16 + 1, 1) }
# JSON string body of a byte string already known to be UTF-8.
function enc(s,   out, n, i, c, b, need, cp, k) {
  if (s ~ /^[ -~]*$/ && index(s, "\"") == 0 && index(s, "\\") == 0) return s
  out = ""; n = length(s)
  for (i = 1; i <= n; i++) {
    c = substr(s, i, 1); b = ord[c]
    if (b < 128) {
      if (c == "\"") out = out "\\\""
      else if (c == "\\") out = out "\\\\"
      else if (b == 9) out = out "\\t"
      else if (b == 8) out = out "\\b"
      else if (b < 32 || b == 127) out = out "\\u" h4(b)
      else out = out c
      continue
    }
    if (b >= 240) { need = 3; cp = b - 240 } else if (b >= 224) { need = 2; cp = b - 224 } else { need = 1; cp = b - 192 }
    for (k = 1; k <= need; k++) cp = cp * 64 + ord[substr(s, i + k, 1)] - 128
    i += need
    if (cp >= 65536) { cp -= 65536; out = out "\\u" h4(55296 + int(cp / 1024)) "\\u" h4(56320 + cp % 1024) }
    else out = out "\\u" h4(cp)
  }
  return out
}
function refuse(why) { print why > "/dev/stderr"; failed = 1; exit 2 }
# Words of a value as shlex.split(value, comments=True, posix=True) gives them.
function shlex(s,   n, i, c, state, esc, tok, quoted) {
  nw = 0; tok = ""; quoted = 0; state = " "; n = length(s)
  for (i = 1; i <= n + 1; i++) {
    c = (i <= n) ? substr(s, i, 1) : ""
    if (state == " ") {
      if (c == "" || c == "#") return
      if (c == " " || c == "\t") continue
      if (c == "\\") { esc = "a"; state = "\\"; continue }
      if (c == "\"" || c == "\047") { state = c; continue }
      tok = c; state = "a"; continue
    }
    if (state == "a") {
      if (c == "" || c == "#") { words[++nw] = tok; return }
      if (c == " " || c == "\t") { words[++nw] = tok; tok = ""; quoted = 0; state = " "; continue }
      if (c == "\"" || c == "\047") { state = c; continue }
      if (c == "\\") { esc = "a"; state = "\\"; continue }
      tok = tok c; continue
    }
    if (state == "\\") {
      if (c == "") refuse("A setting ends with an escape")
      if (esc != "a" && c != "\\" && c != esc) tok = tok "\\"
      tok = tok c; state = esc; continue
    }
    quoted = 1
    if (c == "") refuse("A quoted setting is not closed")
    if (c == state) { state = "a"; continue }
    if (c == "\\" && state == "\"") { esc = state; state = "\\"; continue }
    tok = tok c
  }
}
BEGIN {
  hx = "0123456789abcdef"
  for (i = 1; i < 256; i++) ord[sprintf("%c", i)] = i
  nosp = "[^/ \t\n\r\013\014\034\035\036\037]+"
  cred = "gh[pousr]_" rep("[A-Za-z0-9]", 20) "|github_pat_" rep("[A-Za-z0-9_]", 20) "|AKIA" rep("[A-Z0-9]", 16) \
    "|sk-" rep("[A-Za-z0-9_-]", 20) "|://" nosp ":" nosp "@|-----BEGIN .*PRIVATE KEY-----|eyJ[A-Za-z0-9_-]+[.]eyJ[A-Za-z0-9_-]+[.]"
}
{
  # The line breaks Python splitlines() knows, besides newline.
  gsub(/\r|\013|\014|\034|\035|\036|\302\205|\342\200\250|\342\200\251/, "\n")
  np = split($0, parts, "\n")
  for (p = 1; p <= np; p++) {
    line = parts[p]
    if (line ~ /^[ \t\037]*$/ || line ~ /^[ \t\037]*#/) continue
    at = index(line, "=")
    key = at ? substr(line, 1, at - 1) : line
    sub(/^[ \t\037]+/, "", key); sub(/[ \t\037]+$/, "", key)
    # The hub marker that cub mini pull leaves out; it names the config, not a setting.
    if (index(key, "configHub.") == 1) continue
    if (!at || key !~ /^[A-Za-z_][A-Za-z0-9_]*$/ || (key in seen)) refuse("Expected unique environment setting names")
    seen[key] = 1
    shlex(substr(line, at + 1))
    if (nw > 1) refuse("A setting with spaces must be quoted")
    v = nw ? words[1] : ""
    if (index(v, "secret://") == 1) {
      if (v !~ /^secret:\/\/[A-Za-z0-9_.-]+\/[A-Za-z0-9_.\/-]+$/) refuse("Invalid secret reference")
      print key "\tS\t" v
    } else if (toupper(key) ~ /(^|_)(SECRET|PASSWORD|PASSWD|TOKEN|KEY|CREDENTIAL)(_|$)/ || v ~ cred) {
      refuse("Sensitive setting requires a secret reference; no value was recorded")
    } else print key "\tP\t" enc(v)
  }
}
'

# Renders sorted records as the provider file: Python json.dumps(values,
# sort_keys=True, indent=2) and a newline.
# shellcheck disable=SC2016 # awk's or jq's own $, not the shell's
RENDER_AWK='
{ n++; k[n] = $1; t[n] = $2; v[n] = $3 }
END {
  if (!n) { print "{}"; exit }
  print "{"
  for (i = 1; i <= n; i++) {
    comma = i < n ? "," : ""
    if (t[i] == "S") printf "  \"%s\": {\n    \"secret_ref\": \"%s\"\n  }%s\n", k[i], v[i], comma
    else printf "  \"%s\": \"%s\"%s\n", k[i], v[i], comma
  }
  print "}"
}
'

# Reads a provider file in the one layout the add-on writes, and prints its
# records as SETTINGS_AWK does. Each value must be a JSON string in the form
# json.dumps gives it, so that equal values have equal text; anything else,
# though it may be valid JSON, is refused rather than guessed at.
# shellcheck disable=SC2016 # awk's or jq's own $, not the shell's
PROVIDER_AWK='
function canonical(s,   rest, e) {
  rest = s
  while (rest != "") {
    if (substr(rest, 1, 1) != "\\") {
      if (substr(rest, 1, 1) !~ /[ -~]/ || substr(rest, 1, 1) == "\"") return 0
      rest = substr(rest, 2); continue
    }
    e = substr(rest, 2, 1)
    if (e == "\"" || e == "\\" || e == "n" || e == "r" || e == "t" || e == "b" || e == "f") { rest = substr(rest, 3); continue }
    if (e != "u" || substr(rest, 3, 4) !~ /^[0-9a-f][0-9a-f][0-9a-f][0-9a-f]$/) return 0
    e = substr(rest, 3, 4)
    # json.dumps writes printable ASCII as itself and these five by letter.
    if (e ~ /^00[2-7]/ && e != "007f") return 0
    if (e == "0008" || e == "0009" || e == "000a" || e == "000c" || e == "000d") return 0
    rest = substr(rest, 7)
  }
  return 1
}
function bad() { exit 2 }
{ line[NR] = $0 }
END {
  if (NR == 1 && line[1] == "{}") exit 0
  if (NR < 3 || line[1] != "{" || line[NR] != "}") bad()
  last = ""
  for (i = 2; i < NR; i++) {
    l = line[i]
    if (match(l, /^  "[A-Za-z_][A-Za-z0-9_]*": /)) {
      key = substr(l, 4, RLENGTH - 6); rest = substr(l, RLENGTH + 1)
    } else bad()
    if (last != "" && !(last < key)) bad()
    last = key
    if (rest == "{") {
      if (i + 2 >= NR) bad()
      ref = line[i + 1]; close_ = line[i + 2]
      if (ref !~ /^    "secret_ref": ".*"$/) bad()
      v = substr(ref, 20, length(ref) - 20)
      if (!canonical(v)) bad()
      comma = close_ == "  }," ? 1 : close_ == "  }" ? 0 : bad()
      print key "\tS\t" v
      i += 2
    } else {
      comma = rest ~ /,$/ ? 1 : 0
      if (comma) rest = substr(rest, 1, length(rest) - 1)
      if (rest !~ /^".*"$/) bad()
      v = substr(rest, 2, length(rest) - 2)
      if (!canonical(v)) bad()
      print key "\tP\t" v
    }
    if (comma != (i < NR - 1)) bad()
  }
}
'

# Names whose settings differ, the way the Python reference compares them: a
# secret by presence only, anything else by value.
# shellcheck disable=SC2016 # awk's or jq's own $, not the shell's
DIFFERENCES_AWK='
FNR == NR { et[$1] = $2; ev[$1] = $3; all[$1] = 1; next }
{ at[$1] = $2; av[$1] = $3; all[$1] = 1 }
END {
  for (k in all) {
    if (k in et && et[k] == "S") { if (!(k in at)) print k }
    else if (!(k in et) || !(k in at) || et[k] != at[k] || ev[k] != av[k]) print k
  }
}
'

# Lines of an environment file from provider records, each NAME=shlex.quote(value),
# ready for printf %b: bytes outside printable ASCII are octal escapes. Refuses
# a secret-like name or a value shaped like a credential, unless it is a
# reference, and a value over more than one line.
# shellcheck disable=SC2016 # awk's or jq's own $, not the shell's
IMPORT_AWK='
function rep(cls, n,   s, i) { s = ""; for (i = 0; i < n; i++) s = s cls; return s }
# Always three digits: printf %b would take a digit after a shorter escape as its own.
function oct(b) { return sprintf("\\0%03o", b) }
# One code point, as printf %b text and as a stand-in for the checks.
function put(cp,   b) {
  if (cp == 10 || cp == 13) multiline = 1
  if (cp >= 32 && cp < 127) {
    c = sprintf("%c", cp)
    chk = chk c
    b_ = b_ (c == "\\" ? "\\\\" : c == "\047" ? "\047\"\047\"\047" : c)
    return
  }
  if (cp < 128) { chk = chk ((cp >= 9 && cp <= 13) || (cp >= 28 && cp <= 31) ? " " : "\001"); b_ = b_ oct(cp); return }
  # Python counts these as white space in a pattern; anything else is a letter.
  chk = chk ((cp == 133 || cp == 160 || cp == 5760 || (cp >= 8192 && cp <= 8202) || cp == 8232 || cp == 8233 || cp == 8239 || cp == 8287 || cp == 12288) ? " " : "\001")
  if (cp < 2048) b_ = b_ oct(192 + int(cp / 64)) oct(128 + cp % 64)
  else if (cp < 65536) b_ = b_ oct(224 + int(cp / 4096)) oct(128 + int(cp / 64) % 64) oct(128 + cp % 64)
  else b_ = b_ oct(240 + int(cp / 262144)) oct(128 + int(cp / 4096) % 64) oct(128 + int(cp / 64) % 64) oct(128 + cp % 64)
}
function hexval(h,   i, n) { n = 0; for (i = 1; i <= 4; i++) n = n * 16 + index("0123456789abcdef", substr(h, i, 1)) - 1; return n }
function decode(s,   rest, e, cp, lo) {
  chk = ""; b_ = ""; multiline = 0; rest = s
  while (rest != "") {
    e = substr(rest, 1, 1)
    if (e != "\\") { put(ord[e]); rest = substr(rest, 2); continue }
    e = substr(rest, 2, 1)
    if (e != "u") {
      put(e == "n" ? 10 : e == "r" ? 13 : e == "t" ? 9 : e == "b" ? 8 : e == "f" ? 12 : ord[e]); rest = substr(rest, 3); continue
    }
    cp = hexval(substr(rest, 3, 4)); rest = substr(rest, 7)
    if (cp >= 55296 && cp <= 56319 && substr(rest, 1, 2) == "\\u") {
      lo = hexval(substr(rest, 3, 4))
      if (lo >= 56320 && lo <= 57343) { cp = 65536 + (cp - 55296) * 1024 + lo - 56320; rest = substr(rest, 7) }
    }
    # A lone surrogate cannot be written as UTF-8.
    if (cp >= 55296 && cp <= 57343) exit 2
    put(cp)
  }
}
BEGIN {
  FS = "\t"
  for (i = 1; i < 256; i++) ord[sprintf("%c", i)] = i
  nosp = "[^/ \t\n\r\013\014\034\035\036\037]+"
  cred = "gh[pousr]_" rep("[A-Za-z0-9]", 20) "|github_pat_" rep("[A-Za-z0-9_]", 20) "|AKIA" rep("[A-Z0-9]", 16) \
    "|sk-" rep("[A-Za-z0-9_-]", 20) "|://" nosp ":" nosp "@|-----BEGIN .*PRIVATE KEY-----|eyJ[A-Za-z0-9_-]+[.]eyJ[A-Za-z0-9_-]+[.]"
}
{
  decode($3)
  if ($2 == "S") {
    if (chk !~ /^secret:\/\/[A-Za-z0-9_.-]+\/[A-Za-z0-9_.\/-]+$/) exit 2
  } else if (toupper($1) ~ /(^|_)(SECRET|PASSWORD|PASSWD|TOKEN|KEY|CREDENTIAL)(_|$)/ || chk ~ cred) exit 2
  if (multiline) exit 2
  # shlex.quote: as it is when every character is safe, else in single quotes.
  if (chk ~ /^[A-Za-z0-9_@%+=:,.\/-]+$/) print $1 "=" b_
  else print $1 "=\047" b_ "\047"
}
'

# A file path the add-on may write: not a symbolic link, and a regular file if
# anything is there.
output_ok() {
	[ ! -L "$1" ] && { [ ! -e "$1" ] || [ -f "$1" ]; }
}

# Writes a private file (mode 0600) through a temporary file in the same
# folder. Without replace, an identical file is a retry, accepted only if it is
# already private, and a different one is never overwritten: ln makes the path
# only when nothing is there. With replace, the temporary file is renamed over it.
private_write() {
	_path=$1 _bytes=$2 _replace=$3
	output_ok "$_path" || return 1
	if [ -z "$_replace" ] && [ -e "$_path" ]; then
		cmp -s "$_bytes" "$_path" || return 1
		case $(ls -ln -- "$_path") in -rw-------*) return 0 ;; esac
		return 1
	fi
	_dir=$(snapshot_parent "$_path")
	mkdir -p "$_dir" 2>/dev/null || return 1
	_tmp=$(mktemp "$_dir/.delivery-XXXXXX" 2>/dev/null) || return 1
	if cat "$_bytes" >"$_tmp" 2>/dev/null; then
		if [ -n "$_replace" ]; then
			output_ok "$_path" && mv -f "$_tmp" "$_path" 2>/dev/null && return 0
		else
			ln "$_tmp" "$_path" 2>/dev/null && rm -f "$_tmp" && return 0
		fi
	fi
	rm -f "$_tmp"
	return 1
}

provider_file() {
	case $2 in
	'' | [!A-Za-z0-9]* | *[!A-Za-z0-9_.-]*) return 1 ;;
	esac
	printf '%s/%s.json' "$1" "$2"
}

# The provider's records for a target, in a file; none when it has no file.
provider_read() {
	_file=$(provider_file "$1" "$2") || return 1
	output_ok "$_file" || return 1
	: >"$3"
	[ -e "$_file" ] || return 0
	[ "$(tail -c 1 "$_file" | wc -l | tr -d ' ')" = 1 ] || return 1
	LC_ALL=C awk "$PROVIDER_AWK" "$_file" >"$3"
}

# The settings of the revision read, as sorted records.
settings() {
	snapshot_json_string "$1" >/dev/null || return 1
	LC_ALL=C awk "$SETTINGS_AWK" "$1" >"$snapshot_work/unsorted" 2>/dev/null || return 1
	LC_ALL=C sort "$snapshot_work/unsorted" >"$2"
}

import_settings() {
	_out1=$dir/.env.staging _out2=$dir/.env.production
	for _i in 1 2; do
		if [ "$_i" = 1 ]; then _target=$staging; else _target=$live; fi
		provider_read "$provider_root" "$_target" "$snapshot_work/records" || return 1
		LC_ALL=C awk "$IMPORT_AWK" "$snapshot_work/records" >"$snapshot_work/lines" || return 1
		: >"$snapshot_work/env$_i"
		while IFS= read -r _line; do
			printf '%b\n' "$_line" >>"$snapshot_work/env$_i"
		done <"$snapshot_work/lines"
		[ -s "$snapshot_work/env$_i" ] || printf '\n' >"$snapshot_work/env$_i"
	done
	# Both destinations are checked before either environment is written.
	for _path in "$_out1" "$_out2"; do
		output_ok "$_path" || return 1
	done
	if [ -e "$_out1" ]; then cmp -s "$snapshot_work/env1" "$_out1" || return 1; fi
	if [ -e "$_out2" ]; then cmp -s "$snapshot_work/env2" "$_out2" || return 1; fi
	private_write "$_out1" "$snapshot_work/env1" '' || return 1
	private_write "$_out2" "$snapshot_work/env2" ''
}

usage() {
	printf 'usage: delivery.sh {import,apply,compare} --provider-root PROVIDER_ROOT [--dir DIR] [--staging STAGING] [--live LIVE] [--target TARGET] [--space SPACE] [--unit UNIT] [--revision REVISION] [--receipt RECEIPT]\n' >&2
	[ -n "${1:-}" ] && printf 'delivery.sh: error: %s\n' "$1" >&2
	exit 2
}

failed() {
	printf '%s\n' "$FAILED" >&2
	exit 1
}

command=''
provider_root='' dir='' staging=staging live=production target='' space='' unit=app revision='' receipt=''
have_root='' have_revision='' have_dir='' have_target='' have_space='' have_receipt=''
while [ $# -gt 0 ]; do
	case $1 in
	--*=*) _name=${1%%=*} _value=${1#*=} ;;
	--provider-root | --dir | --staging | --live | --target | --space | --unit | --revision | --receipt)
		[ $# -ge 2 ] || usage "argument $1: expected one argument"
		_name=$1 _value=$2
		shift
		;;
	import | apply | compare)
		[ -z "$command" ] || usage 'unrecognized arguments'
		command=$1
		shift
		continue
		;;
	*) usage 'unrecognized arguments' ;;
	esac
	case $_name in
	--provider-root) provider_root=$_value have_root=1 ;;
	--dir) dir=$_value have_dir=1 ;;
	--staging) staging=$_value ;;
	--live) live=$_value ;;
	--target) target=$_value have_target=1 ;;
	--space) space=$_value have_space=1 ;;
	--unit) unit=$_value ;;
	--revision) revision=$_value have_revision=1 ;;
	--receipt) receipt=$_value have_receipt=1 ;;
	*) usage 'unrecognized arguments' ;;
	esac
	shift
done
[ -n "$command" ] || usage 'the following arguments are required: command'
[ -n "$have_root" ] || usage 'the following arguments are required: --provider-root'
if [ -n "$have_revision" ]; then
	case $revision in
	-[0-9]* | [0-9]*) ;;
	*) usage 'argument --revision: invalid int value' ;;
	esac
fi
provider_root=$(snapshot_path "$provider_root")
snapshot_workdir || failed

if [ "$command" = import ]; then
	[ -n "$have_dir" ] || usage 'import requires --dir'
	dir=$(snapshot_path "$dir")
	import_settings || failed
	printf 'Imported environment files; owner can now run cub mini adopt.\n'
	exit 0
fi

[ -n "$have_space" ] && [ -n "$have_target" ] || usage 'apply and compare require --space and --target'
# A space or unit that starts with "-" would be read by cub as an option.
case $space in -*) failed ;; esac
case $unit in -*) failed ;; esac
if [ -n "$have_revision" ]; then
	revision=$(snapshot_revision "$revision") || failed
fi

if [ "$command" = compare ]; then
	snapshot_read "$space" "$unit" "$revision" "$snapshot_work/data" || failed
	settings "$snapshot_work/data" "$snapshot_work/expected" || failed
	provider_read "$provider_root" "$target" "$snapshot_work/actual" || failed
	LC_ALL=C awk -F '\t' "$DIFFERENCES_AWK" "$snapshot_work/expected" "$snapshot_work/actual" | LC_ALL=C sort >"$snapshot_work/different" || failed
	_names=$(sed 's/.*/"&"/' "$snapshot_work/different" | tr '\n' ',' | sed 's/,$//; s/,/, /g')
	printf '{"different_settings": [%s], "secret_comparison": "presence only"}\n' "$_names"
	[ -s "$snapshot_work/different" ] && exit 1
	exit 0
fi

[ -n "$have_receipt" ] || usage 'apply requires --receipt'
receipt=$(snapshot_path "$receipt")
# An invalid receipt destination is refused before any provider change.
output_ok "$receipt" || failed
snapshot_read "$space" "$unit" "$revision" "$snapshot_work/data" || failed
settings "$snapshot_work/data" "$snapshot_work/desired" || failed
LC_ALL=C awk -F '\t' "$RENDER_AWK" "$snapshot_work/desired" >"$snapshot_work/provider.json" || failed
file=$(provider_file "$provider_root" "$target") || failed
output_ok "$file" || failed
# Unchanged when the provider already holds exactly what this revision gives.
if [ -f "$file" ] && cmp -s "$snapshot_work/provider.json" "$file"; then
	result=unchanged
else
	private_write "$file" "$snapshot_work/provider.json" replace || failed
	result=applied
fi
j_target=$(snapshot_json_value "$target") || failed
j_space=$(snapshot_json_value "$space") || failed
j_unit=$(snapshot_json_value "$unit") || failed
printf '{\n  "contract": "confighub.delivery-receipt/v1",\n  "provider": "%s",\n  "result": "%s",\n  "revision": %s,\n  "sha256": "%s",\n  "space": %s,\n  "target": %s,\n  "unit": %s\n}\n' \
	"$PROVIDER_NAME" "$result" "$SNAPSHOT_REVISION" "$SNAPSHOT_SHA256" "$j_space" "$j_target" "$j_unit" >"$snapshot_work/receipt.json"
private_write "$receipt" "$snapshot_work/receipt.json" replace || failed
printf '{"contract": "confighub.delivery-receipt/v1", "provider": "%s", "target": %s, "space": %s, "unit": %s, "revision": %s, "sha256": "%s", "result": "%s"}\n' \
	"$PROVIDER_NAME" "$j_target" "$j_space" "$j_unit" "$SNAPSHOT_REVISION" "$SNAPSHOT_SHA256" "$result"
