# Adding a terminology

WikiMeSH can ingest another multilingual terminology without changing the application schema. The terminology is imported into `mesh`, its Wikipedia matches are computed into `wikimesh`, and the existing `mesh_view` joins both collections for the Explorer and statistics pages.

This document describes the current pipeline as implemented by `backend/src/mesh_parser.py` and `backend/src/db_feeder.py`.

## 1. Data model

A terminology concept is stored as:

- a stable concept ID;
- an `identifier` naming the terminology (`MeSH`, `DECS`, `ICD11`, `SNOMED`, ...);
- one preferred term (`pt`) per available language;
- zero or more synonyms (`syns`) per language.

For terminologies other than `MeSH`, the importer prefixes MongoDB `_id` values with the terminology identifier. For example, source ID `1234` imported with `-i DECS` becomes `DECS_1234`. This prevents IDs from two terminologies colliding in the shared collections.

## 2. Prepare the CSV

The importer expects UTF-8 CSV with four logical fields:

```csv
ID,lang,label,type_label
1234,en,Heart disease,PT
1234,en,Cardiac disease,SYN
1234,fr,Cardiopathie,PT
1234,fr,Maladie cardiaque,SYN
5678,en,Example preferred term,PT
```

The first column is always interpreted as the concept ID. The remaining headers must resolve to `lang`, `label`, and `type_label` after lower-casing.

### Ordering requirements

The current parser is intentionally simple and relies on input order:

1. all rows belonging to one concept ID must be contiguous;
2. within each concept/language pair, the **first row is the preferred term**;
3. subsequent rows for that language are treated as synonyms.

`type_label` is currently required by the CSV structure but is not used to choose PT versus synonym. Therefore the row ordering above is authoritative.

Language values should use the same language codes used by Wikimedia projects, normally ISO-style codes such as `en`, `fr`, `de`, `es`, etc. Rows with `lang=N/A` are ignored.

## 3. Validate before production import

Before touching production data:

- test the terminology on a development/staging database when possible;
- verify the CSV encoding and row ordering;
- choose one stable identifier and keep it unchanged across imports;
- ensure the terminology is not already present under that identifier;
- make and verify a current MongoDB backup.

The current importer is append-oriented. Re-importing the same IDs does not update existing concepts cleanly and can produce duplicate-key errors. Do not use `--force` as a replacement/update mechanism.

## 4. Make the source file visible to the backend

Production mounts the host `backend/` directory at `/app/backend/` in `wikimesh_app`. A convenient location is therefore:

```text
backend/data/<terminology>.csv
```

For example:

```text
backend/data/Decs_wikimesh.csv
```

The source CSV is input data, not application state. Decide separately whether it should be committed, archived outside Git, or removed after the import depending on its license and provenance.

## 5. Import the terminology concepts

With the normal production stack running:

```bash
sudo docker exec wikimesh_app \
  python -m backend.src.mesh_parser \
  --identifier DECS \
  /app/backend/data/Decs_wikimesh.csv
```

`-i DECS` is equivalent to `--identifier DECS`.

For a non-MeSH terminology, always pass `--identifier`. Omitting it would create an invalid/ambiguous identifier and ID prefix.

### Historical DECS command

The DECS dataset was imported in 2023 with a command recorded as:

```bash
python -m backend.src.mesh_parser \
  --source flavien \
  -i DECS \
  backend/data/Decs_wikimesh.csv
```

The important parts of that command remain valid: the `DECS` identifier and the source CSV. The current `mesh_parser.py` no longer exposes a `--source` option, so **do not add `--source flavien` to current commands**. The current equivalent is simply:

```bash
python -m backend.src.mesh_parser \
  -i DECS \
  backend/data/Decs_wikimesh.csv
```

when running Python directly on a correctly configured host/dev environment, or the `docker exec` form above in the normal containerized deployment.

### Check the import

Open MongoDB with the project helper:

```bash
./run.sh connect-db root
```

Then, in `mongosh`:

```javascript
use thedb

db.mesh.countDocuments({identifier: "DECS"})
db.mesh.findOne({identifier: "DECS"})
```

Check that:

- the count matches the expected number of concepts;
- `_id` is prefixed as expected;
- `langs` contains the expected preferred terms and synonyms.

## 6. Resolve concepts against Wikipedia

The feeder queries Wikipedia using preferred terms first and synonyms second, across the terminology languages. It stores the resulting cross-language Wikipedia titles in `wikimesh`.

Run:

```bash
sudo docker exec wikimesh_app \
  python -m backend.src.db_feeder \
  --identifier DECS
```

or, in a correctly configured host/dev Python environment:

```bash
python -m backend.src.db_feeder -i DECS
```

This second form matches the DECS command that was actually used in 2023:

```bash
python -m backend.src.db_feeder -i DECS
```

The normal, non-force mode only processes terminology concepts that do not yet have a corresponding document in `wikimesh`, so an interrupted first import can be resumed by running the same command again.

The feeder currently starts many worker processes and can generate substantial Wikimedia traffic and CPU/network activity. Run a large import in a controlled window and monitor both the host and Wikimedia/API errors.

Do **not** use `--force` for a routine rerun: the current writer uses inserts rather than safe replacement semantics for already-existing `_id` values.

### Historical `data_fetcher` command

The same 2023 shell history also contains:

```bash
python -m backend.src.data_fetcher
```

There is no `backend/src/data_fetcher.py` in the current codebase. Do not include this command in a new import procedure. The current Wikimedia-fetching stage is `backend.src.db_feeder`, which explicitly filters by terminology identifier and writes the resulting matches into `wikimesh`.

The historical sequence also included:

```bash
./run.sh dev --build
```

That command rebuilt/restarted the development stack of the time. It is not part of the terminology data model and is not required between `mesh_parser` and `db_feeder` when the current application/container already sees the CSV and current code. Use it only when you independently need to rebuild the development environment.

## 7. Verify the generated matches

In `mongosh`:

```javascript
db.wikimesh.countDocuments({identifier: "DECS"})
db.wikimesh.findOne({identifier: "DECS"})
db.mesh_view.countDocuments({identifier: "DECS"})
```

`mesh_view` is a MongoDB view joining `mesh` and `wikimesh`, so it automatically exposes newly matched concepts; it does not need to be rebuilt for every terminology.

Useful fields in a `wikimesh` result include:

- `origin`: whether the successful search phase used a preferred term (`pt`) or synonym (`syn`);
- `langs`: Wikipedia page titles by language;
- `identifier`: the terminology identifier.

## 8. Refresh the application caches

Some identifier/statistics endpoints are cached in the application process. After a successful production import, restart the backend process so the new terminology is immediately visible everywhere:

```bash
sudo docker restart wikimesh_app
```

Then verify:

```bash
curl -fsS https://wikimesh.mikaeldusenne.com/api/identifiers
curl -fsS https://wikimesh.mikaeldusenne.com/ready
```

Finally check the UI:

1. the terminology appears in the Explorer identifier selector;
2. searches return expected concepts;
3. the Statistics page exposes the new identifier;
4. several manually known concepts link to the expected Wikipedia pages/languages.

## 9. Acceptance checklist

A terminology import is complete when all of the following hold:

- [ ] source provenance and license are known;
- [ ] CSV rows follow the required grouping/order;
- [ ] a current MongoDB backup exists and has been verified;
- [ ] `mesh` contains the expected number of concepts;
- [ ] `wikimesh` processing completed or expected misses were reviewed;
- [ ] `mesh_view` exposes the new terminology;
- [ ] Explorer works for representative concepts;
- [ ] Statistics load for the terminology;
- [ ] manual spot checks confirm Wikipedia matches are semantically correct;
- [ ] application logs contain no persistent Wikimedia or database errors.

## 10. Updating an existing terminology

The current pipeline is designed much better for **adding** a new identifier than for replacing an existing terminology release. `mesh_parser.py` inserts documents, and `db_feeder.py` also inserts generated matches.

Do not turn a production terminology refresh into an ad-hoc sequence of `deleteMany`, `drop`, or filesystem operations. For a refresh, first define an explicit replace/upsert workflow with backup and validation gates. A future improvement should make terminology loading idempotent and transactional at the identifier level.

## 11. Current matching methodology

Today, `db_feeder.py` searches Wikipedia page titles using each preferred term and then synonyms. `wiki_fetcher.py` asks the MediaWiki Action API for the page's interlanguage links, and the feeder combines those titles into one multilingual result.

This works without terminology-specific Wikimedia configuration, but it is lexical rather than semantic: a matching page title does not prove that the Wikipedia page represents the same biomedical concept. For terminologies that have identifiers represented in Wikidata, resolving the external identifier to a Wikidata item first is a stronger future approach; the item's sitelinks can then provide the Wikipedia pages in each language.
