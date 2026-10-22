# Architecture and data contracts

~~~mermaid
flowchart LR
  Provider[Explicit Yahoo collection] --> Batch[Unique per-run CSV batch]
  Batch --> Validate[Complete-batch validation]
  Validate --> Atomic[Transactional replacement]
  Atomic --> DB[(SQLite)]
  Demo[Synthetic demo command] --> DB
  DB --> Query[Validated read-only chart queries]
  Query --> UI[ECharts pages]
~~~

## Storage and imports

The active models are in scheduledTask/models.py. Both historical and recent rows contain symbol, UTC market timestamp, and float Open/High/Low/Close fields. Float precision and the absence of ingestion metadata are current limitations.

Historical imports require all files in HISTORICAL_FILE_SYMBOLS, required columns Date/Open/High/Low/Close, parseable UTC timestamps, and finite numeric prices. Incoming duplicate symbol/timestamp rows collapse to the last row. Every previously committed timestamp and per-symbol count must remain present. After backup and review, an operator may explicitly approve a legitimate reduction with allow_data_shrink=True; scheduled jobs never enable it.

Recent imports require exactly the CSV names in RECENT_DATA_FILE_SYMBOLS, with Datetime/Open/High/Low/Close columns. Every file must be nonempty and valid. Duplicate timestamps collapse to the last row. Each successful run replaces the rolling snapshot, so old rows may legitimately leave the recent window. A successful, nonempty but unexpectedly short/stale response currently has no coverage threshold; see the roadmap.

Both imports parse all candidate rows before writing. Deletion and bulk insertion share one transaction. A database error restores the prior committed dataset. This application-level deduplication does not prevent other writers from inserting duplicates: database uniqueness constraints require a separately reviewed migration.

Collectors use unique .batch directories. A failed provider invalidates the run, and jobs import only their collector's returned batch. Old persistent CSV files are not a fallback. Batch cleanup is best effort after completion; interrupted processes may leave ignored .batch directories for operator review.

## Offline demonstration

With DJANGO_DEMO_MODE=1 explicitly enabled, seed_demo generates 90 daily rows and 96 half-hour rows for each of 12 symbols. Values and UTC timestamps are deterministic and synthetic. Both market tables must be empty; there is no force/clear option. Inserts into both tables share one transaction.

The README selects a separate demo database. Never mix demo data and live provider data in one database.

## HTTP chart contract (v0.2)

Existing URLs remain:
- GET /visual/get_historical_chart/?symbol=EUR/USD&start_date=2024-01-01&end_date=2024-01-31
- GET /visual/get_recent_chart/?symbol=EUR/USD&time_range=1d

Successful responses are ECharts JSON objects (previous versions returned a JSON-encoded string). The included frontend accepts both representations. External clients should remove a redundant second JSON.parse.

Historical dates are ISO calendar dates interpreted in UTC. Either bound is optional; the end date includes the entire day. A valid range with no matching timestamps returns an empty chart. Recent ranges are 1d, 3d, 1w and 1m (30 days), measured from the symbol's latest stored market timestamp; omission defaults to 1d.

Malformed or reversed query parameters return HTTP 400 JSON with error and fields. Unknown/no-data symbols return HTTP 404 JSON. Non-GET methods return 405. Pages render an empty state when the database has no rows.

## Scheduling and operator actions

Importing scheduledTask/views.py registers jobs without starting a worker. Django and Cron triggers use UTC. Daily history is registered for weekdays 12:15 UTC; recent refresh is every 30 minutes on weekdays; the legacy training CSV export is hourly at minute 45. UTC differs from the host clock and provider timezone. Collection dates are calculated at call time.

The existing max_instances=1 and coalescing settings apply to one scheduler only. They do not protect against multiple processes or older batches finishing later. Do not start a scheduler in AppConfig.ready or each web worker. A separately supervised singleton worker, locking and run metadata are future work. The legacy training export is experimental and has no validated database import.

For an intentional live run, select the correct database in DJANGO_DB_NAME, back it up, and explicitly invoke the historical/recent job from a Django shell. The wrappers log failures and return 0; this is not a production monitoring interface. This release does not execute live collection automatically.

## Boundaries

SQLite remains the supported store. This is a local research application with no financial account, order execution, strategy, LLM or RAG integration. Data rights, production authentication/rate limits, ingestion provenance, fresh-data monitoring, snapshot ordering, and backup restoration drills need further work before public operation.
