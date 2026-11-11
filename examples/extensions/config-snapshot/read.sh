#!/bin/sh
# An extension that reads one pinned configuration revision with cub.
#
#   read.sh --space SPACE --unit UNIT [--revision N] --out FILE
#
# Uses the caller's CUB_CONFIG/CUB_CONTEXT. No owner login or new authentication.
# Writes a versioned JSON snapshot; a retry with the same revision is
# byte-identical. POSIX sh and standard utilities only: no JSON parser. The one
# value read from JSON, the listed head, comes from cub's own -o jq= output.
#
# The delivery add-on sources this file for its reads; it then sets
# CONFIG_SNAPSHOT_SOURCED=1 so that nothing below runs on its own.

# Bytes, not characters, for every utility: a UTF-8 locale makes some of them
# fail on bytes that are not UTF-8 instead of letting the check below refuse them.
LC_ALL=C
export LC_ALL
SNAPSHOT_CONTRACT='confighub.config-snapshot/v1'
SNAPSHOT_TIMEOUT=30
SNAPSHOT_READ_FAILED='cub could not read the requested revision; check its scoped key, coordinates and connectivity'
SNAPSHOT_NO_REVISION='A positive revision is required; no unversioned data is read'
# The head as a positive whole number, or "none": cub prints a string as it is.
SNAPSHOT_HEAD_JQ='(.Unit // .) | .HeadRevisionNum | if type == "number" and . >= 1 and . == floor then tostring else "none" end'

# JSON-encodes a file's bytes as one JSON string, the way Python's json.dumps
# does (non-ASCII as \u escapes), and refuses bytes that are not UTF-8.
# ord[] is filled per byte, so awk runs with LC_ALL=C.
# shellcheck disable=SC2016 # awk's or jq's own $, not the shell's
SNAPSHOT_JSON_AWK='
function h4(n) { return substr(hx, int(n / 4096) % 16 + 1, 1) substr(hx, int(n / 256) % 16 + 1, 1) substr(hx, int(n / 16) % 16 + 1, 1) substr(hx, n % 16 + 1, 1) }
function put(s,   n, i, c, b, need, cp, k, b2) {
  if (s ~ /^[ -~]*$/ && index(s, "\"") == 0 && index(s, "\\") == 0) { printf "%s", s; return }
  n = length(s)
  for (i = 1; i <= n; i++) {
    c = substr(s, i, 1); b = ord[c]
    if (b < 128) {
      if (c == "\"") printf "\\\""
      else if (c == "\\") printf "\\\\"
      else if (b == 10) printf "\\n"
      else if (b == 13) printf "\\r"
      else if (b == 9) printf "\\t"
      else if (b == 8) printf "\\b"
      else if (b == 12) printf "\\f"
      else if (b < 32 || b == 127) printf "\\u%s", h4(b)
      else printf "%s", c
      continue
    }
    if (b >= 194 && b <= 223) { need = 1; cp = b - 192 }
    else if (b >= 224 && b <= 239) { need = 2; cp = b - 224 }
    else if (b >= 240 && b <= 244) { need = 3; cp = b - 240 }
    else exit 3
    for (k = 1; k <= need; k++) {
      b2 = ord[substr(s, i + k, 1)]
      if (b2 < 128 || b2 > 191) exit 3
      cp = cp * 64 + b2 - 128
    }
    if ((need == 2 && cp < 2048) || (need == 3 && cp < 65536) || cp > 1114111 || (cp >= 55296 && cp <= 57343)) exit 3
    i += need
    if (cp >= 65536) { cp -= 65536; printf "\\u%s\\u%s", h4(55296 + int(cp / 1024)), h4(56320 + cp % 1024) }
    else printf "\\u%s", h4(cp)
  }
}
BEGIN { hx = "0123456789abcdef"; for (i = 1; i < 256; i++) ord[sprintf("%c", i)] = i; printf "\"" }
{ if (NR > 1) printf "\\n"; put($0) }
END { if (endnl) printf "\\n"; printf "\"" }
'

snapshot_fail() {
	SNAPSHOT_ERROR=$1
	return 1
}

# A path that starts with "-" is made ./-... so that no utility reads it as an option.
snapshot_path() {
	case $1 in
	-*) printf './%s' "$1" ;;
	*) printf '%s' "$1" ;;
	esac
}

# The folder a path is in, without dirname, which loses trailing newlines.
snapshot_parent() {
	case $1 in
	*/*)
		_p=${1%/*}
		[ -n "$_p" ] || _p=/
		printf '%s' "$_p"
		;;
	*) printf . ;;
	esac
}

# A private folder for what is read; removed on exit.
snapshot_workdir() {
	[ -n "${snapshot_work:-}" ] && return 0
	snapshot_work=$(mktemp -d "${TMPDIR:-/tmp}/snapshot.XXXXXX") || return 1
	trap 'rm -rf "$snapshot_work"' EXIT
	trap 'exit 1' HUP INT TERM
}

# Runs cub with its output in the file named first. Retries only a read that
# was refused by a transient transport or server fault; never denied access,
# missing objects or arbitrary errors. A read that takes longer than
# SNAPSHOT_TIMEOUT seconds is stopped and fails. What cub printed on its error
# output is never repeated: it can carry private material.
snapshot_cub() {
	_out=$1
	shift
	_attempt=0
	while :; do
		cub "$@" >"$_out" 2>"$snapshot_work/stderr" &
		_pid=$!
		(
			sleep "$SNAPSHOT_TIMEOUT" &
			_sleep=$!
			trap 'kill "$_sleep" 2>/dev/null; exit 0' TERM
			wait "$_sleep"
			kill "$_pid" 2>/dev/null
		) >/dev/null 2>&1 &
		_watch=$!
		wait "$_pid"
		_status=$?
		kill "$_watch" 2>/dev/null
		wait "$_watch" 2>/dev/null
		[ "$_status" -eq 0 ] && return 0
		if [ "$_attempt" -ge 2 ] || ! grep -q -F -e 'HTTP 429' -e 'HTTP 502' -e 'HTTP 503' -e 'connection refused' -e 'connection reset' "$snapshot_work/stderr"; then
			snapshot_fail "$SNAPSHOT_READ_FAILED"
			return 1
		fi
		if [ "$_attempt" -eq 0 ]; then _pause=0.25; else _pause=0.5; fi
		sleep "$_pause" 2>/dev/null || sleep 1
		_attempt=$((_attempt + 1))
	done
}

# Prints a positive whole number without leading zeros, or fails.
snapshot_revision() {
	case $1 in
	'' | *[!0-9]*) return 1 ;;
	esac
	_r=${1#"${1%%[!0]*}"}
	[ -n "$_r" ] && [ "${#_r}" -le 18 ] || return 1
	printf '%s' "$_r"
}

snapshot_sha256() {
	if command -v sha256sum >/dev/null 2>&1; then
		_sum=$(sha256sum <"$1") || return 1
	else
		_sum=$(shasum -a 256 <"$1") || return 1
	fi
	_sum=${_sum%%[!0-9a-f]*}
	[ "${#_sum}" -eq 64 ] || return 1
	printf '%s' "$_sum"
}

# Writes a file's bytes as one JSON string; fails on bytes that are not UTF-8,
# and on a NUL byte, which awk cannot carry.
snapshot_json_string() {
	# shellcheck disable=SC2094 # both only read the file
	tr -d '\000' <"$1" | cmp -s - "$1" || return 1
	_endnl=0
	[ -s "$1" ] && [ "$(tail -c 1 "$1" | wc -l | tr -d ' ')" = 1 ] && _endnl=1
	LC_ALL=C awk -v endnl="$_endnl" "$SNAPSHOT_JSON_AWK" "$1"
}

# A string as JSON, by way of a file.
snapshot_json_value() {
	printf '%s' "$1" >"$snapshot_work/value"
	snapshot_json_string "$snapshot_work/value"
}

# Reads one revision of a unit into the file named last. With no revision,
# reads the listed head once and pins it. Sets SNAPSHOT_REVISION and
# SNAPSHOT_SHA256.
snapshot_read() {
	_space=$1 _unit=$2 _revision=$3 _data=$4
	if [ -z "$_revision" ]; then
		snapshot_cub "$snapshot_work/head" unit get "$_unit" --space "$_space" -o "jq=$SNAPSHOT_HEAD_JQ" || return 1
		_revision=$(cat "$snapshot_work/head")
	fi
	SNAPSHOT_REVISION=$(snapshot_revision "$_revision") || {
		snapshot_fail "$SNAPSHOT_NO_REVISION"
		return 1
	}
	snapshot_cub "$_data" revision data "$_unit" "$SNAPSHOT_REVISION" --space "$_space" || return 1
	SNAPSHOT_SHA256=$(snapshot_sha256 "$_data") || {
		snapshot_fail 'Could not hash the revision read'
		return 1
	}
}

# Writes the snapshot only where nothing is, through a temporary file and a
# hard link: ln makes the destination only when it does not exist, so a racing
# writer is never overwritten. An identical existing snapshot is a retry.
snapshot_write() {
	_out=$(snapshot_path "$1") _bytes=$2
	if [ -L "$_out" ]; then
		snapshot_fail 'Output is a symbolic link'
		return 1
	fi
	if [ -e "$_out" ]; then
		[ -f "$_out" ] && cmp -s "$_bytes" "$_out" && return 0
		snapshot_fail 'Output already contains different data; choose a new path'
		return 1
	fi
	_dir=$(snapshot_parent "$_out")
	mkdir -p "$_dir" 2>/dev/null || {
		snapshot_fail 'Could not create the output folder'
		return 1
	}
	_tmp=$(mktemp "$_dir/.snapshot-XXXXXX" 2>/dev/null) || {
		snapshot_fail 'Could not write the output folder'
		return 1
	}
	if cat "$_bytes" >"$_tmp" && ln "$_tmp" "$_out" 2>/dev/null; then
		rm -f "$_tmp"
		return 0
	fi
	rm -f "$_tmp"
	snapshot_fail 'Output already contains different data; choose a new path'
	return 1
}

snapshot_usage() {
	printf 'usage: read.sh --space SPACE --unit UNIT [--revision N] --out FILE\n' >&2
	[ -n "${1:-}" ] && printf 'read.sh: error: %s\n' "$1" >&2
	exit 2
}

snapshot_main() {
	_space='' _unit='' _rev='' _have_rev='' _outfile='' _have_space='' _have_unit='' _have_out=''
	while [ $# -gt 0 ]; do
		case $1 in
		--space=*) _space=${1#*=} _have_space=1 ;;
		--unit=*) _unit=${1#*=} _have_unit=1 ;;
		--revision=*) _rev=${1#*=} _have_rev=1 ;;
		--out=*) _outfile=${1#*=} _have_out=1 ;;
		--space | --unit | --revision | --out)
			[ $# -ge 2 ] || snapshot_usage "argument $1: expected one argument"
			case $1 in
			--space) _space=$2 _have_space=1 ;;
			--unit) _unit=$2 _have_unit=1 ;;
			--revision) _rev=$2 _have_rev=1 ;;
			--out) _outfile=$2 _have_out=1 ;;
			esac
			shift
			;;
		-h | --help) snapshot_usage ;;
		*) snapshot_usage "unrecognized argument" ;;
		esac
		shift
	done
	[ -n "$_have_space" ] && [ -n "$_have_unit" ] && [ -n "$_have_out" ] || snapshot_usage 'the following arguments are required: --space, --unit, --out'
	# A name that starts with "-" would be read by cub as an option.
	case $_space in -*) snapshot_usage 'a space or unit cannot start with -' ;; esac
	case $_unit in -*) snapshot_usage 'a space or unit cannot start with -' ;; esac
	if [ -n "$_have_rev" ]; then
		case $_rev in
		-[0-9]* | [0-9]*) ;;
		*) snapshot_usage "argument --revision: invalid int value" ;;
		esac
		_rev=$(snapshot_revision "$_rev") || {
			printf '%s\n' "$SNAPSHOT_NO_REVISION" >&2
			exit 1
		}
	fi
	snapshot_workdir || exit 1
	if ! snapshot_read "$_space" "$_unit" "$_rev" "$snapshot_work/data"; then
		printf '%s\n' "$SNAPSHOT_ERROR" >&2
		exit 1
	fi
	_content=$(snapshot_json_string "$snapshot_work/data") || {
		printf 'The revision read is not UTF-8 text\n' >&2
		exit 1
	}
	{
		printf '{\n  "content": %s,\n' "$_content"
		printf '  "contract": "%s",\n' "$SNAPSHOT_CONTRACT"
		printf '  "revision": %s,\n' "$SNAPSHOT_REVISION"
		printf '  "sha256": "%s",\n' "$SNAPSHOT_SHA256"
		printf '  "space": %s,\n' "$(snapshot_json_value "$_space")"
		printf '  "unit": %s\n}\n' "$(snapshot_json_value "$_unit")"
	} >"$snapshot_work/snapshot.json"
	if ! snapshot_write "$_outfile" "$snapshot_work/snapshot.json"; then
		printf '%s\n' "$SNAPSHOT_ERROR" >&2
		exit 1
	fi
	printf '%s: %s/%s revision %s -> %s\n' "$SNAPSHOT_CONTRACT" "$_space" "$_unit" "$SNAPSHOT_REVISION" "$_outfile"
}

if [ "${CONFIG_SNAPSHOT_SOURCED:-}" != 1 ]; then
	snapshot_main "$@"
fi
