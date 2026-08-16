# MongoDB upgrade runbook

This runbook upgrades the persistent WikiMeSH MongoDB standalone in controlled
phases. The database files stay in `mongo/volume`; each phase starts the same
`dbPath` with one explicitly pinned MongoDB image.

The volume has been identified as MongoDB 7.0.14 with FCV 7.0. The supported
path used here is:

```text
7.0.14 / FCV 7.0
  -> 7.0.40 / FCV 7.0
  -> 8.0.29 / FCV 7.0   [burn-in]
  -> 8.0.29 / FCV 8.0
  -> 8.3.8  / FCV 8.0   [burn-in]
  -> 8.3.8  / FCV 8.3
```

MongoDB 8.3 is the current minor release. This guide deliberately keeps binary
upgrades and FCV changes separate: MongoDB recommends a burn-in period before
enabling backwards-incompatible features after both the 7.0 -> 8.0 and
8.0 -> 8.3 upgrades.

## Safety model

**Do not run this procedure without a separate, verified cold backup.** A restore
test is strongly recommended before the maintenance window.

The helper is intentionally conservative:

- it never runs `mongod --repair`;
- it never deletes, renames, chmods or chowns database files;
- it refuses to continue when a visible running container mounts `mongo/volume`;
- it also checks `WiredTiger.lock` with `fuser` when available;
- it publishes no network port while doing maintenance;
- it bypasses the image entrypoint so the image cannot recursively chown the bind mount;
- it runs `mongod` with the existing host UID/GID of the database files in a rootful context;
- it validates every application collection around binary transitions;
- it compares application collection counts before and after each binary transition;
- it makes a complete compressed logical dump and verifies it with
  `mongorestore --dryRun` before the upgrade and before each FCV change;
- FCV changes require an additional exact `--confirm-fcv` argument.

If MongoDB fails to start, the helper leaves its maintenance container in place
and prints its logs. Inspect the error before doing anything else. Do **not**
respond to a startup error by running `--repair` or deleting lock files.

## Prerequisites

Run the upgrade during a maintenance window with WikiMeSH stopped.

You need:

- `docker` (Podman through the Docker-compatible CLI is supported);
- `realpath`, `stat`, `du`, `df` and standard GNU userland;
- enough free space for a conservative full logical dump;
- a separate, verified cold backup of `mongo/volume`;
- exclusive access to the volume.

The helper defaults to `mongo/dumps` for logical archives. To put them on a
separate filesystem:

```bash
sudo MONGO_DUMPS=/srv/backups/wikimesh ./mongo/upgrade.sh prepare --backup-confirmed
```

### Permissions and rootless Podman

Run first:

```bash
./mongo/upgrade.sh preflight
```

If it reports that the current user cannot read and write `WiredTiger.wt`, run
the migration in the corresponding rootful context instead, normally:

```bash
sudo ./mongo/upgrade.sh preflight
```

Do not change the ownership or mode of the database to make the script pass.
When run rootfully, the helper reads the existing UID/GID from `WiredTiger.wt`
and runs `mongod` as exactly that numeric user/group.

## 1. Stop WikiMeSH and run preflight

Stop every stack that can use MongoDB, then check:

```bash
sudo ./mongo/upgrade.sh preflight
```

Expected final line:

```text
preflight:   OK
```

The script refuses to proceed if its own maintenance container already exists.
If that happens after a failed attempt, inspect it first:

```bash
sudo docker logs wikimesh-mongo-upgrade
sudo docker inspect wikimesh-mongo-upgrade
```

Only remove that container after understanding the failure. Removing the
container does not remove the bind-mounted database files.

## 2. Prepare the 7.0 volume and make a verified logical dump

```bash
sudo ./mongo/upgrade.sh prepare --backup-confirmed
```

This starts the volume on MongoDB 7.0.40, requires FCV 7.0, checks standalone
mode, performs compatibility checks, validates the application collections,
creates a full compressed `mongodump`, dry-runs that archive with
`mongorestore`, prints collection counts, and shuts MongoDB down cleanly.

Do not continue unless this phase succeeds.

## 3. Upgrade the binary to MongoDB 8.0

```bash
sudo ./mongo/upgrade.sh to-8.0 --backup-confirmed
```

The helper opens the volume with 7.0.40, snapshots and validates it, shuts it
down, then opens the same volume with 8.0.29. It requires FCV to remain 7.0 and
compares application collection counts across the transition.

At this point the intended state is:

```text
MongoDB 8.0.29
FCV 7.0
```

Do **not** enable FCV 8.0 immediately.

## 4. Burn in MongoDB 8.0 with FCV 7.0

Generate a temporary Compose override:

```bash
sudo ./mongo/upgrade.sh compose-override 8.0 > /tmp/wikimesh-mongo-8.0.yml
```

Start the normal WikiMeSH stack with that override appended after the usual
Compose files. For production, for example:

```bash
sudo docker-compose \
  -f docker-compose.yml \
  -f production.yml \
  -f /tmp/wikimesh-mongo-8.0.yml \
  up
```

The override pins MongoDB 8.0.29, bypasses the legacy image entrypoint, enables
authentication, preserves the database-file UID/GID, and replaces the old
healthcheck shell with `mongosh`.

Exercise normal application behavior before changing FCV. At minimum verify:

- the web application starts and becomes healthy;
- Explorer reads/searches expected data;
- statistics load;
- any normal controlled write workflow still works;
- a normal backup can be produced;
- MongoDB logs show no repeated WiredTiger, catalog or assertion errors.

There is no useful universal fixed duration for this phase. Keep FCV 7.0 until
you are satisfied that a binary downgrade is unlikely to be needed.

Stop the stack cleanly before continuing.

## 5. Enable FCV 8.0

This is a separate gate because enabling backwards-incompatible 8.0 features
makes downgrade more constrained.

```bash
sudo ./mongo/upgrade.sh \
  fcv-8.0 \
  --backup-confirmed \
  --confirm-fcv 8.0
```

Before setting FCV, the helper creates and dry-runs another full logical dump.
It then sets FCV 8.0 with MongoDB's required `confirm: true`, verifies the new
FCV, validates collections, and stops cleanly.

## 6. Upgrade the binary to MongoDB 8.3

MongoDB documents direct upgrade from an 8.0-series standalone to 8.3 once the
8.0 instance has FCV 8.0.

```bash
sudo ./mongo/upgrade.sh to-8.3 --backup-confirmed
```

The intended state after this command is:

```text
MongoDB 8.3.8
FCV 8.0
```

Again, the helper validates and compares application collection counts across
the binary transition.

## 7. Burn in MongoDB 8.3 with FCV 8.0

```bash
sudo ./mongo/upgrade.sh compose-override 8.3 > /tmp/wikimesh-mongo-8.3.yml
```

Run the application with this override in the same way as for 8.0, then repeat
the application and backup checks. Keep FCV at 8.0 until the deployment has
been exercised enough that a downgrade is unlikely.

Stop the stack cleanly before continuing.

## 8. Enable FCV 8.3

```bash
sudo ./mongo/upgrade.sh \
  fcv-8.3 \
  --backup-confirmed \
  --confirm-fcv 8.3
```

The helper takes another verified logical dump immediately before the FCV
change, enables FCV 8.3, revalidates the application database and stops cleanly.

Final verification:

```bash
sudo ./mongo/upgrade.sh status 8.3 --backup-confirmed
```

Expected state:

```text
MongoDB: 8.3.8
FCV:     8.3
```

## Recovery and failures

If a phase fails:

1. stop and inspect the maintenance-container logs;
2. do not run `--repair`;
3. do not delete `mongod.lock`, `WiredTiger.lock`, journal files or WiredTiger metadata;
4. do not try a newer image just to see whether it starts;
5. if recovery is required, restore from the verified cold backup into a clean
   location rather than improvising destructive changes on the only working copy.

After an FCV change, downgrade restrictions are stronger. Consult the MongoDB
downgrade documentation for the exact current server/FCV pair before attempting
any downgrade.

## After the migration

Until the repository's normal Compose configuration is updated, use the 8.3
temporary override to run the final database version.

After the live migration is validated, update the normal deployment in a
separate PR to:

- pin `docker-compose.yml` to MongoDB 8.3.8;
- use `mongosh` in the healthcheck and `run.sh connect-db`;
- update the backup image/tooling;
- validate dump/restore with the final deployment configuration.

Keeping this deployment change separate prevents a normal application start
from jumping the persistent volume to a new MongoDB major before the migration
runbook has been executed.

## Upstream references

- MongoDB 7.0 -> 8.0 standalone upgrade:
  https://www.mongodb.com/docs/manual/release-notes/8.0-upgrade-standalone/
- MongoDB 8.0 -> 8.3 standalone upgrade:
  https://www.mongodb.com/docs/manual/release-notes/8.3-upgrade-from-8.0-standalone/
- MongoDB 7.0 release notes:
  https://www.mongodb.com/docs/manual/release-notes/7.0/
- MongoDB 8.0 release notes:
  https://www.mongodb.com/docs/manual/release-notes/8.0/
- MongoDB 8.3 release notes:
  https://www.mongodb.com/docs/manual/release-notes/8.3/
- `mongodump`:
  https://www.mongodb.com/docs/database-tools/mongodump/
- `mongorestore`:
  https://www.mongodb.com/docs/database-tools/mongorestore/
