#!/usr/bin/env bash
set -Eeuo pipefail

# Safe, phased upgrade helper for the persistent WikiMeSH MongoDB volume.
# It never repairs, deletes, or changes ownership of database files.

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
VOLUME="${MONGO_VOLUME:-$ROOT/mongo/volume}"
DUMPS="${MONGO_DUMPS:-$ROOT/mongo/dumps}"
DB="${MONGO_DB:-thedb}"
ENGINE="${CONTAINER_ENGINE:-docker}"
CONTAINER="${MONGO_UPGRADE_CONTAINER:-wikimesh-mongo-upgrade}"

VERSION_7="7.0.40"
VERSION_8="8.0.29"
VERSION_83="8.3.8"
IMAGE_7="docker.io/library/mongo:$VERSION_7"
IMAGE_8="docker.io/library/mongo:$VERSION_8"
IMAGE_83="docker.io/library/mongo:$VERSION_83"

created=0
preserve_container=0
backup_confirmed=0
confirm_fcv=""

usage() {
    cat <<EOF
Usage: $0 COMMAND [options]

Commands:
  preflight            Check the volume, permissions and running containers.
  prepare              Validate 7.0/FCV 7.0 and create a verified logical dump.
  to-8.0               Upgrade binaries to $VERSION_8, keeping FCV 7.0.
  fcv-8.0              Set FCV to 8.0 after the 8.0 burn-in period.
  to-8.3               Upgrade binaries to $VERSION_83, keeping FCV 8.0.
  fcv-8.3              Set FCV to 8.3 after the 8.3 burn-in period.
  status VERSION       Start VERSION (7.0, 8.0 or 8.3) and print status.
  compose-override VERSION
                       Print a temporary Compose override for 8.0 or 8.3 burn-in.

Safety options:
  --backup-confirmed   Confirm a separate, verified cold backup exists.
  --confirm-fcv VALUE  Required for FCV changes; VALUE must be 8.0 or 8.3.

Environment:
  MONGO_VOLUME         Persistent dbPath (default: mongo/volume).
  MONGO_DUMPS          Logical dump directory (default: mongo/dumps).
  MONGO_DB             Application database to validate (default: thedb).
  CONTAINER_ENGINE     Container CLI (default: docker).

Examples:
  sudo $0 preflight
  sudo $0 prepare --backup-confirmed
  sudo $0 to-8.0 --backup-confirmed
  sudo $0 fcv-8.0 --backup-confirmed --confirm-fcv 8.0
  sudo $0 to-8.3 --backup-confirmed
  sudo $0 fcv-8.3 --backup-confirmed --confirm-fcv 8.3
EOF
}

info() { printf '\n==> %s\n' "$*"; }
die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

cleanup() {
    local status=$?
    if (( created )) && (( ! preserve_container )); then
        "$ENGINE" stop "$CONTAINER" >/dev/null 2>&1 || true
        "$ENGINE" rm "$CONTAINER" >/dev/null 2>&1 || true
    fi
    exit "$status"
}
trap cleanup EXIT INT TERM

require_cmd() { command -v "$1" >/dev/null || die "missing command: $1"; }

parse_options() {
    while (($#)); do
        case "$1" in
            --backup-confirmed) backup_confirmed=1 ;;
            --confirm-fcv)
                (($# >= 2)) || die "--confirm-fcv requires a value"
                confirm_fcv="$2"
                shift
                ;;
            -h|--help) usage; exit 0 ;;
            *) die "unknown option: $1" ;;
        esac
        shift
    done
}

require_backup() {
    (( backup_confirmed )) || die \
        "refusing to open the persistent volume without --backup-confirmed"
}

canonicalize() {
    [[ -d "$VOLUME" ]] || die "MongoDB volume not found: $VOLUME"
    VOLUME="$(realpath -e -- "$VOLUME")"
    DUMPS="$(realpath -m -- "$DUMPS")"
    [[ "$DB" =~ ^[A-Za-z0-9_.-]+$ ]] || die "unsafe database name: $DB"
    [[ -f "$VOLUME/WiredTiger.wt" ]] || die "$VOLUME is not a WiredTiger dbPath"
}

container_exists() { "$ENGINE" inspect "$CONTAINER" >/dev/null 2>&1; }

assert_volume_idle() {
    local id name source
    while IFS= read -r id; do
        [[ -n "$id" ]] || continue
        name="$("$ENGINE" inspect --format '{{.Name}}' "$id" | sed 's#^/##')"
        while IFS= read -r source; do
            [[ -n "$source" ]] || continue
            if [[ "$(realpath -m -- "$source")" == "$VOLUME" ]]; then
                die "running container '$name' mounts $VOLUME; stop it cleanly first"
            fi
        done < <("$ENGINE" inspect --format '{{range .Mounts}}{{println .Source}}{{end}}' "$id")
    done < <("$ENGINE" ps -q)

    if command -v fuser >/dev/null && fuser "$VOLUME/WiredTiger.lock" >/dev/null 2>&1; then
        die "WiredTiger.lock is in use by a host process; stop MongoDB first"
    fi
}

assert_access() {
    [[ -r "$VOLUME/WiredTiger.wt" && -w "$VOLUME/WiredTiger.wt" ]] || die \
        "current user cannot read/write WiredTiger.wt; rerun in the correct rootful context (typically sudo). Do not chmod/chown the volume"
}

preflight() {
    require_cmd "$ENGINE"
    require_cmd realpath
    require_cmd stat
    require_cmd df
    require_cmd du
    canonicalize
    assert_volume_idle
    assert_access
    container_exists && die "container '$CONTAINER' already exists; inspect its logs/state before removing it"

    local owner
    owner="$(stat -c '%u:%g' "$VOLUME/WiredTiger.wt")"
    printf 'volume:      %s\n' "$VOLUME"
    printf 'db:          %s\n' "$DB"
    printf 'file owner:  %s\n' "$owner"
    printf 'engine:      %s\n' "$ENGINE"
    printf 'upgrade:     %s -> %s -> %s\n' "$VERSION_7" "$VERSION_8" "$VERSION_83"
    printf 'preflight:   OK\n'
}

is_podman() { "$ENGINE" --version 2>/dev/null | grep -qi podman; }

run_user_args() {
    local uid gid
    if (( EUID == 0 )); then
        IFS=: read -r uid gid < <(stat -c '%u:%g' "$VOLUME/WiredTiger.wt")
        printf '%s\0%s\0' --user "$uid:$gid"
    else
        uid="$(id -u)"; gid="$(id -g)"
        if is_podman; then
            printf '%s\0%s\0%s\0%s\0%s\0' \
                --userns keep-id --user "$uid:$gid" --group-add keep-groups
        else
            printf '%s\0%s\0' --user "$uid:$gid"
        fi
    fi
}

pull_image() {
    info "pulling $1"
    "$ENGINE" pull "$1"
}

start_mongo() {
    local image="$1" args=()
    assert_volume_idle
    container_exists && die "container '$CONTAINER' already exists"
    mapfile -d '' -t args < <(run_user_args)

    info "starting $image on $VOLUME (maintenance mode; no published port)"
    "$ENGINE" run -d \
        --name "$CONTAINER" \
        "${args[@]}" \
        --entrypoint mongod \
        --mount "type=bind,src=$VOLUME,dst=/data/db" \
        "$image" \
        --dbpath /data/db \
        --bind_ip 127.0.0.1 >/dev/null
    created=1
    wait_ready
    assert_standalone
}

exec_mongo() {
    "$ENGINE" exec -e HOME=/tmp "$CONTAINER" mongosh --quiet --eval "$1"
}

wait_ready() {
    local i running
    for ((i=0; i<60; i++)); do
        running="$("$ENGINE" inspect --format '{{.State.Running}}' "$CONTAINER" 2>/dev/null || true)"
        if [[ "$running" != true ]]; then
            printf '\nMongoDB exited during startup:\n' >&2
            "$ENGINE" logs "$CONTAINER" >&2 || true
            preserve_container=1
            die "startup failed; container '$CONTAINER' was left in place for inspection. Do not use --repair"
        fi
        if exec_mongo 'quit(db.adminCommand({ping:1}).ok ? 0 : 2)' >/dev/null 2>&1; then
            return
        fi
        sleep 1
    done
    "$ENGINE" logs "$CONTAINER" >&2 || true
    preserve_container=1
    die "MongoDB did not become ready; container left for inspection"
}

assert_standalone() {
    exec_mongo '
      const h=db.hello();
      if (h.setName || h.msg === "isdbgrid") {
        printjson(h); quit(2);
      }
    ' >/dev/null || die "this helper only supports a standalone mongod"
}

mongo_version() { exec_mongo 'print(db.version())' | tail -1 | tr -d '\r'; }

mongo_fcv() {
    exec_mongo '
      const f=db.adminCommand({getParameter:1,featureCompatibilityVersion:1}).featureCompatibilityVersion;
      if (Object.keys(f).some(k => k !== "version")) { printjson(f); quit(2); }
      print(f.version);
    ' | tail -1 | tr -d '\r'
}

assert_version() {
    local expected="$1" actual
    actual="$(mongo_version)"
    printf 'MongoDB: %s\n' "$actual"
    [[ "$actual" == "$expected" ]] || die "expected MongoDB $expected, got $actual"
}

assert_fcv() {
    local expected="$1" actual
    actual="$(mongo_fcv)"
    printf 'FCV:     %s\n' "$actual"
    [[ "$actual" == "$expected" ]] || die "expected FCV $expected, got $actual"
}

assert_compatibility() {
    exec_mongo '
      let bad=[];
      for (const name of db.adminCommand({listDatabases:1,nameOnly:true}).databases.map(x=>x.name)) {
        const d=db.getSiblingDB(name);
        for (const c of d.getCollectionInfos({name:/^system\.buckets/})) {
          if (!c.options || !c.options.timeseries) bad.push(name+"."+c.name);
        }
      }
      if (bad.length) {
        print("non-time-series system.buckets collections require manual review:");
        bad.forEach(print); quit(2);
      }
    ' || die "compatibility pre-check failed; investigate before upgrading"
}

snapshot() {
    exec_mongo "
      const d=db.getSiblingDB('$DB');
      d.getCollectionInfos({type:'collection'})
        .map(x=>x.name).sort()
        .forEach(name=>print(name+'\t'+d.getCollection(name).countDocuments({})));
    "
}

validate_db() {
    info "validating collections in $DB"
    exec_mongo "
      const d=db.getSiblingDB('$DB');
      for (const {name} of d.getCollectionInfos({type:'collection'})) {
        const r=d.runCommand({validate:name,full:false});
        if (!r.ok || r.valid !== true) { printjson(r); quit(2); }
        print('valid: '+name);
      }
    " || die "collection validation failed"
}

stop_mongo() {
    info "shutting down MongoDB cleanly"
    exec_mongo 'db.adminCommand({shutdown:1})' >/dev/null 2>&1 || true
    local i
    for ((i=0; i<30; i++)); do
        if [[ "$("$ENGINE" inspect --format '{{.State.Running}}' "$CONTAINER" 2>/dev/null || true)" != true ]]; then
            "$ENGINE" rm "$CONTAINER" >/dev/null
            created=0
            return
        fi
        sleep 1
    done
    preserve_container=1
    die "MongoDB did not stop cleanly; container left for inspection"
}

assert_dump_space() {
    mkdir -p -- "$DUMPS"
    local bytes free required
    bytes="$(du -sb -- "$VOLUME" | awk '{print $1}')"
    free="$(df -PB1 -- "$DUMPS" | awk 'NR==2 {print $4}')"
    required=$((bytes + bytes / 5))
    (( free >= required )) || die \
        "not enough free space for the logical backup (need >= $required bytes; set MONGO_DUMPS to another filesystem)"
}

logical_backup() {
    local label="$1" stamp archive tmp
    assert_dump_space
    stamp="$(date -u +'%Y%m%dT%H%M%SZ')"
    archive="$DUMPS/wikimesh-mongo-$label-$stamp.archive.gz"
    tmp="$archive.partial.$$"

    info "creating full logical dump: $archive"
    if "$ENGINE" exec "$CONTAINER" mongodump --archive --gzip >"$tmp"; then
        mv -- "$tmp" "$archive"
    else
        rm -f -- "$tmp"
        die "mongodump failed"
    fi
    [[ -s "$archive" ]] || die "logical dump is empty: $archive"

    info "verifying logical dump with mongorestore --dryRun"
    "$ENGINE" exec -i "$CONTAINER" mongorestore --archive --gzip --dryRun <"$archive" >/dev/null || \
        die "mongorestore dry-run failed for $archive"
    printf 'verified dump: %s\n' "$archive"
}

compare_snapshots() {
    local before="$1" after="$2"
    if ! diff -u -- "$before" "$after"; then
        die "application collection counts changed during the maintenance transition"
    fi
}

transition() {
    local from_image="$1" from_version="$2" expected_fcv="$3" \
          to_image="$4" to_version="$5" label="$6"
    local before after
    before="$(mktemp)"; after="$(mktemp)"

    pull_image "$from_image"
    pull_image "$to_image"

    start_mongo "$from_image"
    assert_version "$from_version"
    assert_fcv "$expected_fcv"
    assert_compatibility
    validate_db
    snapshot >"$before"
    stop_mongo

    start_mongo "$to_image"
    assert_version "$to_version"
    assert_fcv "$expected_fcv"
    assert_compatibility
    validate_db
    snapshot >"$after"
    stop_mongo

    compare_snapshots "$before" "$after"
    rm -f -- "$before" "$after"
    info "$label completed; FCV remains $expected_fcv"
}

prepare() {
    pull_image "$IMAGE_7"
    start_mongo "$IMAGE_7"
    assert_version "$VERSION_7"
    assert_fcv 7.0
    assert_compatibility
    validate_db
    logical_backup 7.0-pre-upgrade
    printf '\nApplication collection counts:\n'
    snapshot
    stop_mongo
    info "7.0 preparation complete"
}

set_fcv() {
    local image="$1" version="$2" from="$3" to="$4"
    [[ "$confirm_fcv" == "$to" ]] || die "FCV $to requires --confirm-fcv $to"
    pull_image "$image"
    start_mongo "$image"
    assert_version "$version"
    assert_fcv "$from"
    assert_compatibility
    validate_db
    logical_backup "pre-fcv-$to"

    info "setting FCV to $to"
    exec_mongo "
      const r=db.adminCommand({setFeatureCompatibilityVersion:'$to',confirm:true});
      if (!r.ok) { printjson(r); quit(2); }
    " >/dev/null || die "FCV change failed"
    assert_fcv "$to"
    validate_db
    stop_mongo
    info "FCV $to enabled"
}

image_for_series() {
    case "$1" in
        7.0) printf '%s\n' "$IMAGE_7" ;;
        8.0) printf '%s\n' "$IMAGE_8" ;;
        8.3) printf '%s\n' "$IMAGE_83" ;;
        *) die "VERSION must be 7.0, 8.0 or 8.3" ;;
    esac
}

version_for_series() {
    case "$1" in
        7.0) printf '%s\n' "$VERSION_7" ;;
        8.0) printf '%s\n' "$VERSION_8" ;;
        8.3) printf '%s\n' "$VERSION_83" ;;
        *) die "VERSION must be 7.0, 8.0 or 8.3" ;;
    esac
}

status_cmd() {
    local series="$1" image version
    image="$(image_for_series "$series")"
    version="$(version_for_series "$series")"
    pull_image "$image"
    start_mongo "$image"
    assert_version "$version"
    printf 'FCV:     %s\n' "$(mongo_fcv)"
    exec_mongo "print('DB:      $DB'); print('collections: '+db.getSiblingDB('$DB').getCollectionInfos({type:'collection'}).length)"
    stop_mongo
}

compose_override() {
    local series="$1" image uid gid userns=""
    case "$series" in
        8.0) image="$IMAGE_8" ;;
        8.3) image="$IMAGE_83" ;;
        *) die "compose-override VERSION must be 8.0 or 8.3" ;;
    esac
    canonicalize
    IFS=: read -r uid gid < <(stat -c '%u:%g' "$VOLUME/WiredTiger.wt")
    if (( EUID != 0 )) && is_podman; then
        userns='    userns_mode: "keep-id"'
    fi
    cat <<EOF
services:
  mongo:
    image: $image
    user: "$uid:$gid"
${userns:+$userns
}    entrypoint: ["mongod"]
    command: ["--dbpath", "/data/db", "--auth", "--bind_ip_all"]
    healthcheck:
      test: ["CMD", "mongosh", "--quiet", "--eval", "quit(db.adminCommand({ping:1}).ok ? 0 : 2)"]
      interval: 5s
      timeout: 5s
      retries: 20
EOF
}

main() {
    local command="${1:-}"
    case "$command" in -h|--help|help|"") usage; exit 0 ;; esac
    shift

    case "$command" in
        compose-override)
            (($# >= 1)) || die "compose-override requires VERSION"
            local series="$1"; shift
            parse_options "$@"
            compose_override "$series"
            ;;
        preflight)
            parse_options "$@"
            preflight
            ;;
        prepare|to-8.0|fcv-8.0|to-8.3|fcv-8.3|status)
            local series=""
            if [[ "$command" == status ]]; then
                (($# >= 1)) || die "status requires VERSION"
                series="$1"; shift
            fi
            parse_options "$@"
            require_backup
            preflight
            case "$command" in
                prepare) prepare ;;
                to-8.0) transition "$IMAGE_7" "$VERSION_7" 7.0 "$IMAGE_8" "$VERSION_8" '8.0 binary upgrade' ;;
                fcv-8.0) set_fcv "$IMAGE_8" "$VERSION_8" 7.0 8.0 ;;
                to-8.3) transition "$IMAGE_8" "$VERSION_8" 8.0 "$IMAGE_83" "$VERSION_83" '8.3 binary upgrade' ;;
                fcv-8.3) set_fcv "$IMAGE_83" "$VERSION_83" 8.0 8.3 ;;
                status) status_cmd "$series" ;;
            esac
            ;;
        *) die "unknown command: $command" ;;
    esac
}

main "$@"
